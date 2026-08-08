---
tipo: telemetria
plataforma: [linux, windows]
producto: firewall / proxy de egress / netflow / VPC Flow Logs
identificador: "flujo de red saliente"
por-defecto: false
coste: alto
aliases:
  - egress del servidor de aplicación
  - flujo saliente
  - outbound connection
tags:
  - dominio/web
---

# Conexión saliente del servidor de aplicación

## Qué lo genera

Toda conexión TCP o UDP iniciada **por** el servidor de aplicación. Es el artefacto propio de [[MOC - SSRF]]: la vulnerabilidad consiste precisamente en que el servidor pide algo que no debería pedir, y este es el único lugar donde eso se ve.

Se distingue de [[Consulta DNS saliente]] en un punto que decide la detección: **el SSRF hacia un destino interno no genera consulta DNS ni sale del perímetro**. Una petición a `127.0.0.1:6379` o a `169.254.169.254` no cruza ningún resolvedor ni ningún firewall perimetral. Si la telemetría solo mira el borde, el caso más grave del dominio es invisible.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| IP y puerto de destino | A dónde fue | El campo central: `169.254.169.254` o un puerto interno no tienen explicación legítima |
| IP de origen | Quién pidió | Identifica el servidor comprometido |
| Proceso que originó | `php-fpm`, `java`, `node` | Distingue la petición de la app de la de un `apt` o un agente |
| Bytes y duración | Volumen | Una respuesta grande desde un servicio interno sugiere extracción |
| Marca de tiempo | Cuándo | Correlación con la petición HTTP entrante que la disparó |
| Cabeceras y URI | Solo con proxy | Si hay proxy de egress explícito, se ve la URL entera |

## Coste de recolección

Alto. Un servidor de aplicación abre muchísimas conexiones legítimas: base de datos, caché, colas, APIs de terceros, actualizaciones. El volumen se domina con una **lista blanca de destinos habituales** — que en un servidor de aplicación es corta y estable — y alertando solo por lo que cae fuera. Ese recorte es lo que vuelve la fuente usable.

## Cómo se activa

- **Nube** — VPC Flow Logs en AWS, Flow Logs en Azure, VPC Flow Logs en GCP. Es lo más barato de encender y ya cubre el tráfico interno entre subredes. No ve el contenido, solo el flujo.
- **Proxy de egress explícito** — la opción más rica: registra la URL completa, no solo la IP. Exige que las apps estén configuradas para usarlo, cosa que rara vez está completa.
- **Firewall de host** — `nftables` con registro, o el firewall de Windows. Ve todo lo que sale del host, incluido lo que no cruza la red.
- **EDR** — correlaciona la conexión con el proceso que la abrió, que es el campo que más falta en netflow puro.

## Limitaciones

- **Netflow no ve la URL.** Sabe que hubo conexión a una IP y un puerto, no qué se pidió. Para `169.254.169.254` alcanza; para distinguir una llamada legítima de una API de un SSRF al mismo host, no.
- **El tráfico a loopback no cruza la red.** `127.0.0.1` no aparece en netflow ni en logs de firewall de red: hace falta telemetría de host.
- **Sin el proceso de origen es ambiguo.** Muchas fuentes de red dan solo IP:puerto, y ahí se pierde la diferencia entre la app y cualquier agente del sistema.
- **El SSRF ciego se ve igual que el directo.** Esta fuente no distingue si la respuesta volvió al atacante — cosa que sí cambia el impacto.

## Quién lo emite / quién lo consume

Rojo: [[SSRF - canal directo]] · [[SSRF - canal ciego]] · [[SSRF - escaneo de la red interna]] · [[SSRF - metadatos de instancia cloud]] · [[SSRF - gopher a servicio interno]] · [[RFI - inclusión remota]] · [[Command injection - a shell interactiva]]
Azul: pendiente — ver [[Consultas del vault]] § Huecos defensivos propios
