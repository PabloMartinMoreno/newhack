---
tipo: meta
aliases:
  - inyección de Host
  - Host header techniques
  - X-Forwarded-Host
tags:
  - meta/referencia
  - dominio/web
---

# Host header inyección - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo hacer que la aplicación acepte un `Host` malicioso. Las cabeceras de confianza y sus objetivos están en [[Host header cabeceras de confianza - matriz de referencia]]; el criterio, en [[MOC - Host header]].

## 0. Confirmar que el Host influye

Cambiar el `Host` y mirar si algo cambia: un reflejo, un enlace, el enrutamiento, un error.

```
Host: canario.com
```

Si `canario.com` aparece en la respuesta —en un enlace, una redirección, un correo— o el backend cambia, el `Host` se usa. Es el paso cero de las tres ramas.

## 1. Host directo

```http
GET / HTTP/1.1
Host: atacante.com
```

Si se acepta y se refleja o enruta, no hay validación. Es la prueba más simple y a veces alcanza.

## 2. X-Forwarded-Host

La más frecuente cuando el `Host` directo se valida pero el reenvío no:

```http
GET / HTTP/1.1
Host: objetivo.com
X-Forwarded-Host: atacante.com
```

La aplicación valida el `Host` real —correcto— pero construye el enlace o toma la decisión con `X-Forwarded-Host`, que no valida. Variantes de la misma idea:

`X-Host: atacante.com`
`X-Forwarded-Server: atacante.com`
`X-HTTP-Host-Override: atacante.com`
`Forwarded: host=atacante.com`

## 3. Doble cabecera Host

Cuando el frente y el back eligen un `Host` distinto de dos:

```http
Host: objetivo.com
Host: atacante.com
```

Uno valida el primero, el otro usa el segundo. Es la misma discrepancia de dos parsers que [[MOC - Request smuggling]], aplicada al `Host`.

## 4. URL absoluta en la línea de petición

Algunos servidores priorizan la URL de la línea de petición sobre el `Host`:

```
GET https://atacante.com/ HTTP/1.1
Host: objetivo.com
```

Y para el enrutamiento interno de [[Host header - SSRF por enrutamiento]]:

```
GET https://servicio-interno/ HTTP/1.1
Host: objetivo.com
```

## 5. Host con puerto, o malformado

```http
Host: objetivo.com:atacante.com
Host: objetivo.com@atacante.com
Host: atacante.com:80
```

El `@` y los dos puntos confunden el parseo del host, como en [[OAuth redirect_uri - matriz de referencia]] § 6 — la validación mira una parte y la construcción usa otra.

## 6. Inyección indentada / envuelta

Algunos parsers tratan una línea que empieza con espacio como continuación de la anterior:

```http
Host: objetivo.com
 Host: atacante.com
```

Raro en servidores modernos, cuesta una petición probarlo.

## 7. Por dónde llega según el objetivo

| Objetivo | Vector preferido |
|---|---|
| Enlace de reset de contraseña | `X-Forwarded-Host`, luego `Host` directo |
| Enrutamiento a interno | URL absoluta, `Host` directo con nombre interno |
| Reflejo en la página | `Host` directo, `X-Forwarded-Host` |
| Envenenamiento de caché | `X-Forwarded-Host` sin clave — ver [[Web cache entradas sin clave - matriz de referencia]] |
| Decisión de acceso | ver [[Host header cabeceras de confianza - matriz de referencia]] |

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El `Host` directo da `400` | Se valida. Probar `X-Forwarded-Host` |
| Nada se refleja ni enruta | El `Host` no se usa; buscar otro vector |
| `X-Forwarded-Host` se refleja | La construcción usa el reenvío sin validar — hallazgo |
| La URL absoluta cambia el backend | Enrutamiento por línea de petición → SSRF, § 4 |
| El doble Host no hace nada | Frente y back eligen el mismo; probar el orden inverso |
| El reflejo va a caché | Cruza con [[MOC - Web cache]]: envenenamiento por Host |

## Relacionadas

[[MOC - Host header]] · [[Host header cabeceras de confianza - matriz de referencia]] · [[Web cache entradas sin clave - matriz de referencia]] · [[OAuth redirect_uri - matriz de referencia]]
