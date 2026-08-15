---
tipo: meta
aliases:
  - cabeceras de reenvío
  - forwarding headers
  - X-Original-URL
tags:
  - meta/referencia
  - dominio/web
---

# Host header cabeceras de confianza - matriz de referencia

> [!info] Referencia pura, no un zettel
> Las cabeceras que el cliente controla y las aplicaciones confían, y contra qué probarlas. Cómo inyectar el Host está en [[Host header inyección - matriz de referencia]]; el criterio, en [[Host header - bypass de acceso por confianza]].

## 1. El catálogo de cabeceras de reenvío

Todas las pone el cliente y muchas apps las creen del proxy.

| Cabecera | Qué dice la app que es | Se falsifica para |
|---|---|---|
| `X-Forwarded-For` | IP de origen del cliente | Simular IP interna / rotar para saltar límites |
| `X-Real-IP` | Igual, otra convención | Igual |
| `X-Client-IP` | Igual | Igual |
| `X-Forwarded-Host` | Host original | Envenenar enlaces, caché |
| `X-Forwarded-Server` | Nombre del servidor | Igual |
| `X-Forwarded-Proto` | http/https | Forzar redirecciones |
| `X-Original-URL` | Ruta original | Saltar controles por ruta |
| `X-Rewrite-URL` | Igual | Igual |
| `X-Originating-IP` | IP de origen (mail/apps) | Simular interno |
| `True-Client-IP` | IP real (CDN) | Simular interno |
| `Forwarded` | El estándar RFC 7239 | Lo que combine |

## 2. Acceso interno spoofeado

Contra recursos restringidos a "interno" o "localhost":

```
GET /admin HTTP/1.1
Host: objetivo.com
X-Forwarded-For: 127.0.0.1
```

Probar, uno por línea, sobre el recurso restringido:

`X-Forwarded-For: 127.0.0.1`
`X-Forwarded-For: localhost`
`X-Real-IP: 127.0.0.1`
`X-Originating-IP: 127.0.0.1`
`Host: localhost`
`X-Forwarded-Host: localhost`
`X-Forwarded-For: 192.168.0.1`
`X-Forwarded-For: 10.0.0.1`

La IP interna exacta que la app considera "de confianza" a veces hay que adivinarla; `127.0.0.1` y el rango privado cubren la mayoría.

## 3. Bypass de límite de tasa y de bloqueo por IP

Si el control cuenta por IP y la app lee la IP de una cabecera, rotarla anula el conteo:

```
X-Forwarded-For: 1.1.1.1     (intento 1)
X-Forwarded-For: 1.1.1.2     (intento 2)
X-Forwarded-For: 1.1.1.3     (intento 3)
...
```

Cada intento parece de una IP distinta. Se cruza con [[Autenticación - password spraying]]: el spraying con `X-Forwarded-For` rotado evade el bloqueo por IP.

Variante con lista: algunas apps toman el **primer** valor de un `X-Forwarded-For` con varias IP, otras el último. Probar las dos:

```
X-Forwarded-For: 127.0.0.1, real
X-Forwarded-For: real, 127.0.0.1
```

## 4. Saltar controles por ruta

`X-Original-URL` y `X-Rewrite-URL` engañan a un control que filtra por ruta en el frente:

```
GET /permitido HTTP/1.1
X-Original-URL: /admin
```

El frente ve `/permitido` y lo deja pasar; el back procesa `/admin`. Es primo del bypass de [[MOC - Request smuggling]] pero por cabecera, no por desincronización.

## 5. Forzar esquema

`X-Forwarded-Proto: http` puede degradar una decisión que dependía de HTTPS, o disparar un bucle de redirección que se puede cachear — cruza con [[MOC - Web cache]].

## 6. Dónde se confía en cada una

| La app la usa para | Cabecera típica | Impacto |
|---|---|---|
| Registrar / mostrar la IP | `X-Forwarded-For` | Falsear logs, inyección en logs |
| Decidir "interno vs externo" | `X-Forwarded-For`, `Host` | Acceso a admin — [[Host header - bypass de acceso por confianza]] |
| Contar intentos por IP | `X-Forwarded-For` | Saltar límite de tasa |
| Construir URLs | `X-Forwarded-Host` | Reset poisoning, caché |
| Enrutamiento | `Host` | SSRF — [[Host header - SSRF por enrutamiento]] |
| Decidir HTTPS | `X-Forwarded-Proto` | Redirección, downgrade |

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `X-Forwarded-For: 127.0.0.1` no da acceso | La app no confía en esa cabecera, o el proxy la sobrescribe |
| El límite de tasa sigue contando | La app agrupa por la IP real de la conexión, no por la cabecera |
| Da acceso con una IP privada distinta | Adivinar el rango de confianza; probar `10.`, `192.168.`, `172.16.` |
| `X-Original-URL` no cambia la ruta | El back no lo respeta; probar `X-Rewrite-URL` |
| El primer/último valor no funciona | Probar el otro orden en el `X-Forwarded-For` con lista |
| El proxy borra la cabecera | Configuración correcta: la sobrescribe. No hay bypass por acá |

## Relacionadas

[[MOC - Host header]] · [[Host header inyección - matriz de referencia]] · [[Host header - bypass de acceso por confianza]] · [[Control de acceso - matriz de pruebas]]
