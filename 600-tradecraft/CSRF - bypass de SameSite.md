---
tipo: tradecraft
clase: "[[CWE-352 - Cross-Site Request Forgery]]"
eje: defensa
implementacion: "Llevar la acción a un método o a un origen que el atributo no cubre"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [sesion-por-cookie]
coste: medio
alternativas: ["[[CSRF - token ausente o no ligado]]", "[[CSRF - bypass de validación de origen]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - SameSite bypass
  - Lax bypass
tags:
  - dominio/web
---

# CSRF - bypass de SameSite

## Cuándo lo elijo

Cuando no hay token —o el token no es la defensa efectiva— y lo único que impide el ataque es el atributo de la cookie. Es el caso mayoritario desde que los navegadores tratan una cookie sin atributo como `Lax`: la aplicación nunca implementó nada y aun así el ataque clásico no funciona.

El primer paso es leer el valor real del atributo, no suponerlo. `None`, `Lax` y ausente son tres situaciones distintas y solo una cierra el dominio.

| Valor | Qué permite |
|---|---|
| `None` | Todo. La cookie viaja en peticiones de terceros como antes de 2020 |
| Ausente | Se trata como `Lax`, **pero** con una ventana de gracia en algunos navegadores |
| `Lax` | Navegación de nivel superior con métodos seguros: `GET` |
| `Strict` | Nada de origen cruzado. Hay que salir por otra rama |

## Por qué funciona

`Lax` no bloquea el origen cruzado: bloquea **un subconjunto** de él. Deja pasar la navegación de nivel superior con métodos seguros, que es lo que hace que un enlace de un correo siga funcionando. De esa excepción salen las tres vías:

- **La acción acepta `GET`.** Muchos marcos de trabajo enrutan la misma función a los dos métodos, o aceptan la anulación del método por parámetro (`_method=POST`). Con eso, un `window.open` alcanza — y `Lax` lo permite por diseño.
- **La petición no es de origen cruzado.** Para `SameSite` un subdominio es el mismo sitio. Un XSS o un contenido subido en `cdn.objetivo.com` manda peticiones que la cookie acompaña sin restricción alguna. Es el mismo fallo de granularidad que abusa [[CSRF - double submit y cookie inyectada]].
- **La ventana de gracia.** Las cookies **sin atributo** —no las que declaran `Lax`— quedan exentas durante los primeros dos minutos de vida en los navegadores basados en Chromium, para no romper flujos de autenticación de terceros. Una cadena que fuerza a la víctima a renovar sesión y ataca dentro de esa ventana recupera el `POST` de origen cruzado entero.

La tercera es la más frágil y la más instructiva: la defensa por defecto tiene una excepción por compatibilidad, y la excepción es explotable.

## Cómo falla

Falla contra `Strict`, que no deja pasar nada de origen cruzado. Contra eso queda un solo camino y no es CSRF: conseguir ejecución dentro del sitio, o sea [[XSS - almacenado]] en cualquier página del mismo origen. Ahí la cookie viaja porque la petición ya no es cruzada.

Falla contra `__Host-` combinado con `Strict`, que además cierra la vía del subdominio.

Y falla cuando la ventana de gracia no aplica: si la cookie declara `Lax` explícitamente, no hay período de gracia. Es una diferencia de una palabra en el `Set-Cookie` que cambia por completo la superficie, y por eso el primer paso es leer el encabezado crudo.

> [!warning] Esta rama caduca
> Las tres vías dependen de decisiones de los navegadores, no de la aplicación. La ventana de gracia ya se recortó una vez y está anunciada para desaparecer. Es la rama del vault con más probabilidad de estar desactualizada, y la que hay que reconfirmar contra el navegador objetivo antes de invertir en una cadena.

## Coste

Medio. Comprobar el atributo y probar el cambio de método son dos peticiones. Las otras dos vías son caras: la del subdominio exige encontrar un XSS o una subida de contenido, y la de la ventana de gracia exige encadenar un cierre de sesión con un ataque cronometrado, que es frágil y depende del navegador de la víctima.

Con `Strict` puesto, el coste se vuelve infinito por esta rama y hay que cambiar de dominio. Reconocerlo temprano es lo que evita perder una tarde.

## Huella esperada

La petición llega con la sesión válida, así que del lado de la aplicación no hay nada raro. Las dos señales están en [[Log de acceso del servidor web]]:

- Una acción que cambia estado servida por **`GET`**, con `Referer` de otro origen. Es la firma más limpia del dominio, porque une dos cosas que por separado son normales.
- Peticiones con `_method=POST` o cabeceras de anulación de método sobre endpoints que normalmente reciben `POST` directo.

La vía del subdominio no deja huella de origen cruzado en absoluto: el `Referer` es del propio dominio. Ese caso solo se ve por [[Log de auditoría de la aplicación]] como acción sin la navegación previa que la precede.
