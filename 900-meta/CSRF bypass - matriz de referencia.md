---
tipo: meta
aliases:
  - bypass de CSRF
  - SameSite
  - double submit
tags:
  - meta/referencia
  - dominio/web
---

# CSRF bypass - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué probar contra cada defensa, en orden de coste. Los payloads están en [[CSRF entrega - matriz de referencia]]; el criterio, en las cuatro notas de `600-tradecraft/`.

## 0. Identificar la defensa antes de atacarla

Cinco peticiones y se sabe contra qué se está.

| Prueba | Si pasa |
|---|---|
| Quitar el parámetro del token | No se valida cuando falta → [[CSRF - token ausente o no ligado]] |
| Poner el token de otra cuenta | No está ligado a la sesión → misma nota |
| Cambiar `POST` por `GET` | La validación depende del método → misma nota |
| Quitar el `Referer` | La defensa es la cabecera → [[CSRF - bypass de validación de origen]] |
| Ninguna pasa, y no hay token | La defensa es la cookie → [[CSRF - bypass de SameSite]] |

Si el token coincide con una cookie del mismo valor, es doble envío y va [[CSRF - double submit y cookie inyectada]].

## 1. Token

`csrf_token=` eliminado del cuerpo
`csrf_token=` presente pero vacío
`csrf_token=abc` valor arbitrario del mismo largo
Token válido de **otra cuenta** del atacante
Token válido pero **caducado**

`POST` → `GET` con los mismos parámetros en la URL
`POST` con `_method=PUT`
`POST` con `X-HTTP-Method-Override: GET`

Si el token viaja en cabecera, probarlo en parámetro y al revés: algunos marcos de trabajo aceptan las dos ubicaciones y solo validan una.

| Comportamiento | Qué significa |
|---|---|
| Sin el parámetro pasa, con valor falso falla | Se valida solo si está presente. El fallo más común |
| El token de otra cuenta pasa | No está ligado a la sesión |
| Solo falla en `POST` | La protección está atada al método |
| El token es igual en dos sesiones distintas | Es global, no por sesión |
| El token cambia en cada carga pero cualquiera vale | Se genera y no se compara |

## 2. `SameSite`

Leer el `Set-Cookie` crudo, sin suponer:

`curl -sI https://objetivo.com/login | grep -i set-cookie`

| Lo que dice | Qué probar |
|---|---|
| `SameSite=None` | Todo el ataque clásico. Nada que evadir |
| Sin atributo | `GET` de nivel superior; y la **ventana de gracia** de dos minutos en Chromium |
| `SameSite=Lax` | `GET` de nivel superior. Sin ventana de gracia: declararlo la desactiva |
| `SameSite=Strict` | Nada de origen cruzado. Salir por subdominio o por XSS |

Vías que sobreviven a `Lax`:

`<meta http-equiv="refresh" content="0; url=...">` — nivel superior
`window.open(...)` — nivel superior
Petición desde `sub.objetivo.com` — **para la cookie no es origen cruzado**
Anulación de método: la acción por `GET` con `_method=POST`

> [!warning] Esta sección caduca
> Depende de decisiones de los navegadores, no de la aplicación. La ventana de gracia ya se recortó una vez. Reconfirmar contra el navegador objetivo antes de construir una cadena encima.

## 3. `Referer` y `Origin`

Suprimir la cabecera:

```html
<meta name="referrer" content="no-referrer">
```
`<img referrerpolicy="no-referrer" src="...">`
Redirección de `https` a `http` — el navegador la borra por política

Satisfacer una comparación mal escrita:

`https://objetivo.com.atacante.com/` — vence `startsWith` sin anclar
`https://atacante.com/?x=https://objetivo.com` — vence `contains`
`https://atacante.com/#https://objetivo.com` — a veces también
`https://objetivo.com@atacante.com/` — vence un parseo ingenuo del host

| Lo que ves | Qué significa |
|---|---|
| Sin `Referer` pasa | Se valida solo si está presente |
| Con dominio de más pasa | Comparación por subcadena |
| `Origin` ausente y pasa | La acción acepta `GET`, donde `Origin` no viaja |
| Falla siempre | Validación con parseo y lista blanca. Cerrar la rama |

## 4. Doble envío

Confirmar el patrón: el valor del campo oculto es idéntico al de una cookie.

Fijar la cookie desde un subdominio bajo control:

```
Set-Cookie: csrf=ATACANTE; Domain=objetivo.com; Path=/
```
```html
<script>document.cookie = "csrf=ATACANTE; domain=objetivo.com; path=/"</script>
```

Y mandar el mismo valor en el cuerpo. Las dos comprobaciones coinciden porque las dos las puso el atacante.

| Vía para escribir la cookie | Qué hace falta |
|---|---|
| Subdominio propio o comprometido | Un XSS, una subida de contenido, o un subdominio olvidado |
| Reflejo en `Set-Cookie` | Un endpoint que copie entrada al encabezado |
| HTTP sin cifrar | Estar en la red, y que la cookie no sea `__Host-` |
| Desbordar el frasco de cookies | Cientos de cookies hasta expulsar la vieja |

El prefijo `__Host-` cierra las cuatro: obliga a `Secure`, `Path=/` y **sin** `Domain`, así que ningún subdominio la puede tocar. Es la mitigación que va en el informe.

## 5. Tipo de contenido

`Content-Type: text/plain` con cuerpo JSON
`Content-Type: application/x-www-form-urlencoded` con `campo=valor`
`Content-Type: multipart/form-data`
`Content-Type:` vacío
`Content-Type: application/json; charset=utf-8` con un carácter de más

| Respuesta | Qué significa |
|---|---|
| `200` con `text/plain` | El analizador ignora la cabecera. Formulario con `enctype="text/plain"` |
| `200` con codificación de formulario | El marco de trabajo mapea los dos formatos |
| `415` en todos | Exige el tipo real. Rama cerrada |
| El control previo aparece | Hay cabecera personalizada obligatoria. Rama cerrada |

## 6. Qué recomendar en el informe

En orden de retorno, no de esfuerzo:

1. **Token ligado a la sesión**, comparado en tiempo constante, en todos los métodos que cambian estado. Es la única defensa que no depende del navegador.
2. **`SameSite=Lax` como mínimo, `Strict` donde el flujo lo permita**, con prefijo `__Host-`. Cierra el doble envío de paso.
3. **Exigir una cabecera personalizada** en las API. No validar su contenido: exigir que exista, porque eso fuerza el control previo.
4. **Reautenticación** en las acciones críticas —cambio de correo, de contraseña, transferencias—. Es lo único que sobrevive a un XSS en el mismo origen.

El punto 4 es el que más veces falta y el que convierte un CSRF de severidad media en uno de toma de cuenta.

## Relacionadas

[[MOC - CSRF]] · [[CSRF entrega - matriz de referencia]] · [[Sesión - matriz de referencia]] · [[Control de acceso - matriz de pruebas]]
