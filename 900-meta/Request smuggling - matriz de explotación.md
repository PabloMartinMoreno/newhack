---
tipo: meta
aliases:
  - explotación de smuggling
  - response queue poisoning
tags:
  - meta/referencia
  - dominio/web
---

# Request smuggling - matriz de explotación

> [!info] Referencia pura, no un zettel
> Qué se hace con una desincronización confirmada. Confirmarla es el paso previo, en [[Request smuggling - matriz de sondeo]]; el criterio, en [[MOC - Request smuggling]].

Confirmada la desincronización, el sobrante controlado se antepone a la siguiente petición. Lo que se consigue depende de a qué se antepone y de qué se pide. En orden de impacto creciente.

## 1. Saltear controles del frente

El uso más simple: esconder en el sobrante una petición a un endpoint que el frente bloquea. El frente solo ve la petición externa —permitida—; el back procesa la escondida.

```
POST / HTTP/1.1
Host: objetivo.com
Content-Length: 60
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: objetivo.com
X: 
```

El frente ve un `POST /`; el back procesa el `GET /admin` que aquel bloqueaba. Sirve contra WAF y contra reglas de autorización puestas en el proxy — que es todo lo que ataca [[MOC - Broken access control]] cuando el control vive en el frente.

## 2. Capturar la petición de otro usuario

Anteponer un prefijo que hace que la petición de la víctima quede **almacenada** en algún lugar que el atacante pueda leer: un campo de comentario, un perfil, un parámetro de búsqueda que se refleje.

```
POST /comentario HTTP/1.1
Host: objetivo.com
Content-Length: 320
Transfer-Encoding: chunked

0

POST /comentario HTTP/1.1
Host: objetivo.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 400

comentario=
```

El `Content-Length: 400` del prefijo hace que el back siga leyendo dentro de la **petición de la víctima** —sus cabeceras, su cookie de sesión— y lo guarde como el comentario. El atacante después lee el comentario y tiene la sesión de la víctima.

Es la vía a robo de sesión sin XSS ni CORS, y la que hace del smuggling un ataque a terceros.

## 3. Envenenar la cola de respuestas

El más potente contra la infraestructura. Si se desincroniza de forma que el back queda con **una respuesta de más en la cola**, cada usuario siguiente recibe la respuesta de la petición **anterior**:

- La víctima pide `/` y recibe la respuesta a una petición del atacante.
- O peor: el atacante pide algo autenticado, y la respuesta —con datos de sesión— se le sirve a la víctima, mientras la víctima recibe otra corrida.

Se logra dejando el back con una petición completa sin consumir, de modo que la correspondencia petición↔respuesta se corre en uno. A partir de ahí toda la conexión sirve respuestas desfasadas hasta que se reinicia.

Es la variante que captura respuestas de otros usuarios en masa, y la que convierte un smuggling en una brecha de datos amplia.

## 4. Encadenar con caché

Si delante hay una caché, una respuesta envenenada del paso 3 —o una redirección a un host del atacante metida por el sobrante— queda **almacenada** y se sirve a todos los que pidan ese recurso. Convierte un ataque momentáneo en persistente.

Se cruza con [[MOC - Cross-site scripting]] cuando lo cacheado es una respuesta con un payload reflejado: el smuggling entrega el XSS a la caché, y la caché a todas las víctimas. Es el puente hacia el envenenamiento de caché, dominio vecino.

## 5. Del lado del cliente

Para [[Request smuggling - desincronización del cliente]], sin proxy. La página del atacante fuerza al navegador de la víctima a mandar el prefijo:

```js
fetch('https://objetivo.com/endpoint-cl0', {
  method: 'POST',
  credentials: 'include',
  body: 'GET /url-del-atacante HTTP/1.1\r\nHost: objetivo.com\r\n\r\n',
  mode: 'no-cors'
});
```

La siguiente petición del navegador a ese origen —con las cookies de la víctima— queda antepuesta por el prefijo. Según a qué apunte:

| Prefijo apunta a | Resultado |
|---|---|
| Un endpoint que refleja | XSS en el origen, sin sink de HTML — ver [[MOC - Cross-site scripting]] |
| Una redirección al atacante | La petición de la víctima, con su cookie, va al atacante |
| Un endpoint que almacena | Igual que el paso 2, pero disparado desde el navegador |

## 6. Qué apuntar, en orden de valor

| Objetivo | Por qué |
|---|---|
| La cookie de sesión de la víctima | Robo de sesión directo, sin XSS |
| Un endpoint administrativo tras el control del frente | Escalada — el control estaba solo adelante |
| La respuesta a una petición autenticada | Fuga masiva por cola de respuestas |
| La caché de un recurso muy pedido | Persistencia y alcance amplio |

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El prefijo salta el control pero no hace nada | El endpoint escondido necesita cuerpo o cabeceras que faltaron |
| La captura trae basura en vez de la petición de la víctima | El `Content-Length` del prefijo no calza con lo que viene. Ajustar |
| Funciona intermitente | La conexión no siempre se reutiliza, o hay varios back. Repetir |
| La respuesta envenenada se sirve a uno mismo | El desfase quedó en la propia conexión. Es esperable al calibrar |
| La caché no guarda | El recurso no era cacheable, o falta la cabecera que lo hace |
| Del lado del cliente no antepone | El navegador no reutilizó la conexión al origen. Forzarla con varias peticiones |

## Relacionadas

[[MOC - Request smuggling]] · [[Request smuggling - matriz de sondeo]] · [[MOC - Cross-site scripting]] · [[Control de acceso - matriz de pruebas]]
