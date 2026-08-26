---
tipo: moc
dominio: web
aliases:
  - MOC Host header
  - host header attacks
tags:
  - dominio/web
---

# MOC - Host header

> [!abstract] Nota de referencia paraguas
> Inyectar el Host, en [[Host header inyección - matriz de referencia]]. Acá vive **la decisión**.

Dominio de capa, como [[MOC - OAuth]] y [[MOC - WebSocket]]: cada nota cuelga de su clase real, unidas por un hilo común. Acá el hilo es que **el `Host` y las cabeceras de reenvío las controla el cliente, y la aplicación confía en ellas** para tres cosas distintas —construir enlaces, enrutar, decidir acceso—. Cada uso mal hecho es una vulnerabilidad de una clase distinta.

| Uso del Host | `clase:` | Nota |
|---|---|---|
| Construir el enlace de reset | `CWE-640` | [[Host header - envenenamiento del restablecimiento]] |
| Enrutar la petición | `CWE-918` | [[Host header - SSRF por enrutamiento]] |
| Decidir acceso o confianza | `CWE-290` | [[Host header - bypass de acceso por confianza]] |
| Clave de caché | `CWE-349` | ya cubierto en [[MOC - Web cache]] |

Solo `CWE-290` es nueva; las otras dos reusan Autenticación y SSRF, y el envenenamiento de caché por `Host` ya lo cubre el dominio de web cache —se referencia, no se duplica—. Es el mismo patrón que OAuth: un vector transversal cuyas ramas son clases conocidas.

| Eje | Valores |
|---|---|
| Uso del Host | enlace · enrutamiento · decisión de acceso |
| Vector de inyección | `Host` directo · `X-Forwarded-Host` · doble Host · URL absoluta → matriz |
| Cabecera de confianza | `X-Forwarded-For` · `X-Real-IP` · `X-Original-URL` → matriz |

**El uso del Host es el eje raíz**, porque decide de qué clase es el problema y qué se consigue. El vector de inyección —cómo se cuela el Host malicioso— es ortogonal y va a matriz.

## Árbol de decisión — para qué usa el Host la aplicación

```
¿El Host (o una cabecera de reenvío) influye en algo?  → [[Host header inyección - matriz de referencia]] § 0
└─ Sí — ¿en qué?
   │
   ├─ Construye el enlace del correo de reset
   │     → [[Host header - envenenamiento del restablecimiento]]   ← el de mayor impacto: toma de cuenta
   │       X-Forwarded-Host es el vector más frecuente
   │
   ├─ Enruta la petición a un backend
   │     → [[Host header - SSRF por enrutamiento]] → [[MOC - SSRF]]
   │       URL absoluta o Host con nombre interno
   │
   ├─ Decide acceso / confía en la IP de una cabecera
   │     → [[Host header - bypass de acceso por confianza]]
   │       X-Forwarded-For: 127.0.0.1 contra /admin
   │
   └─ Se cachea reflejado
         → envenenamiento por Host → [[MOC - Web cache]], no acá
```

Tres cosas que este orden codifica:

**El reset poisoning va primero porque termina en toma de cuenta.** Es el uso más directo del Host y el de mayor impacto: un enlace de reset con dominio del atacante captura el token de la víctima. Las otras ramas dan acceso interno o SSRF, serias pero no toma de cuenta directa.

**`X-Forwarded-Host` es el vector que más rinde.** La aplicación valida el `Host` real —parece segura— pero construye el enlace o decide con la cabecera de reenvío, que no valida. Es el agujero más común y el menos auditado, porque el `Host` directo sí está protegido.

**Confiar en `X-Forwarded-For` rompe el control y su detección a la vez.** Es la observación defensiva del dominio: si la app cuenta intentos por la IP de esa cabecera, rotarla evade el límite **y** las reglas de fuerza bruta por IP, porque cada intento parece de otra IP. La cabecera spoofeada envenena la telemetría que debería detectarla.

## Árbol de decisión — qué consigo por uso

```
¿Qué gobierna el Host?
├─ El enlace de reset → token de la víctima → toma de cuenta → [[MOC - Autenticación]]
├─ El enrutamiento → red interna, metadatos de instancia → [[MOC - SSRF]]
├─ El acceso → panel admin, bypass de límite → [[MOC - Broken access control]]
└─ La clave de caché → envenenamiento masivo → [[MOC - Web cache]]
```

## Cheatsheets — entrada directa

- [[Host header inyección - matriz de referencia]] — Confirmar, `Host` directo, `X-Forwarded-Host`, doble Host, URL absoluta, malformados, por objetivo
- [[Host header cabeceras de confianza - matriz de referencia]] — El catálogo de cabeceras de reenvío, acceso interno spoofeado, bypass de límite, saltar controles por ruta

## Orden de aprendizaje

1. [[CWE-290 - Authentication Bypass by Spoofing]] — por qué confiar en una cabecera del cliente es el fallo de fondo
2. [[Host header inyección - matriz de referencia]] — cómo se cuela un Host malicioso, va antes que las ramas
3. [[Host header - envenenamiento del restablecimiento]] — el de mayor impacto
4. [[Host header - SSRF por enrutamiento]] — el Host como vector de SSRF
5. [[Host header - bypass de acceso por confianza]] — la confianza en las cabeceras de reenvío

## Relación con otros dominios

- [[MOC - Autenticación]] — el reset poisoning comparte `clase:` `CWE-640` con [[Autenticación - abuso de recuperación de contraseña]]; allá se abusa la lógica del flujo, acá el dominio del enlace. El bypass de límite de tasa por `X-Forwarded-For` se cruza con [[Autenticación - password spraying]].
- [[MOC - SSRF]] — el enrutamiento por Host es un vector de SSRF sin parámetro de URL; entra en aquel MOC después del primer paso, con su misma economía de destinos.
- [[MOC - Web cache]] — el envenenamiento por `X-Forwarded-Host` es una entrada sin clave, ya cubierta allá. Los dos dominios se referencian: acá el foco es la inyección del Host, allá qué pasa cuando se cachea.
- [[MOC - CORS]], [[MOC - WebSocket]] — la misma familia de "confiar en un valor que el cliente controla": el `Origin` allá, el `Host` acá. Las tres firmas azules son la misma —una cabecera que no matchea la lista blanca—.
- [[MOC - Request smuggling]] — el doble Host y la URL absoluta son discrepancias de parseo entre frente y back, el mismo patrón que el smuggling en otra cabecera.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Reset poisoning | [[Log de acceso del servidor web]] | Pedido de reset con `Host`/`X-Forwarded-Host` externo |
| SSRF por enrutamiento | [[Conexión saliente del servidor de aplicación]] | Conexión a interno, y `Host` con nombre no público |
| Bypass por confianza | [[Log de acceso del servidor web]] | `X-Forwarded-For: 127.0.0.1` **desde afuera** — contradictorio |
| Bypass de límite | — | Cada intento con IP declarada distinta — evade el conteo por IP |

Dos observaciones que este dominio deja:

**Las firmas de este dominio son escribibles y de fuente disponible, como las de CORS y WebSocket.** El `Host` y las cabeceras de reenvío son cabeceras HTTP normales, que se registran más seguido que los cuerpos. Un `Host` fuera de la lista blanca en un pedido de reset, o un `X-Forwarded-For: 127.0.0.1` en tráfico externo, son contradicciones que no ocurren en tráfico legítimo — firmas de alta fidelidad. Es la tercera familia de dominios (con CORS y WebSocket) cuya cara azul es escribible con la fuente actual: la cabecera que no matchea la lista blanca. Sugiere una detección transversal —"cabecera de confianza contradictoria o fuera de lista blanca"— igual que la firma de inyección transversal de las cuatro hermanas.

**Confiar en `X-Forwarded-For` es el caso donde el ataque envenena su propia detección.** Es la vuelta de tuerca del dominio: la cabecera spoofeada no solo salta el control, también engaña a la telemetría que cuenta por IP. La única detección que sobrevive agrupa por algo que el atacante no controla —la sesión, la IP real de la conexión TCP—, y eso hay que decirlo en el informe: no alcanza con detectar, hay que **dejar de confiar en la cabecera** en las dos capas.

Décimo octavo dominio cerrado sin detección nueva, con candidatos escribibles del lado de las firmas de cabecera.

## Huecos conocidos

- [x] Los tres usos del Host con su clase real, más la caché referenciada
- [x] Inyección del Host y catálogo de cabeceras de confianza — dos matrices
- [x] Cara azul de firma — escribible, familia de CORS/WebSocket
- [ ] **La firma de cabecera contradictoria es escribible ya**, transversal a Host, CORS y WebSocket: una cabecera de confianza fuera de lista blanca. Candidato de detección, hueco de trabajo
- [ ] Inyección de CRLF en cabeceras (response splitting, `CWE-113`) como dominio vecino: el Host es un caso, hay otros
- [ ] Inyección en cabeceras de correo (SMTP, `CWE-93`) — misma idea en otro protocolo
