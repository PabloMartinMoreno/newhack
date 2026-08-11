---
tipo: tradecraft
clase: "[[CWE-918 - Server-Side Request Forgery]]"
eje: destino
implementacion: "Petición al servicio de metadatos de la instancia para robar credenciales del rol"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]"]
requisitos: [ssrf-con-retorno, instancia-en-nube, imds-alcanzable]
coste: bajo
alternativas: ["[[SSRF - escaneo de la red interna]]"]
probado: nunca
contexto: [aws-ec2]
aliases:
  - IMDS
  - robo de credenciales de instancia
  - cloud metadata SSRF
tags:
  - dominio/web
---

# SSRF - metadatos de instancia cloud

## Cuándo lo elijo

Primero, siempre, si el objetivo corre en la nube. Es el destino de mayor retorno del dominio y por lejos el más rápido: **una petición y se sale con credenciales**.

La razón por la que va antes que cualquier otro destino es de rentabilidad. Escanear la red interna cuesta cientos de peticiones y devuelve topología; el servicio de metadatos cuesta una y devuelve identidad. Con credenciales del rol, el ataque deja de ser web y pasa a ser de la cuenta de nube entera — con el alcance que tenga ese rol, que en la práctica suele ser mucho más de lo que la aplicación necesita.

Requiere retorno: sin ver la respuesta no hay credencial que copiar. En SSRF ciego este destino no sirve, salvo para confirmar que la instancia está en la nube por diferencia de tiempo.

## Por qué funciona

Toda instancia de nube expone un servicio de metadatos en una dirección de enlace local, alcanzable **solo desde la propia instancia** y sin autenticación de ningún tipo. Su modelo de seguridad completo es "si podés llegar, sos la instancia".

Ese modelo es exactamente la premisa que rompe un SSRF: la petición sale desde la instancia, así que es indistinguible de una legítima. Y lo que sirve ese endpoint no son datos de configuración: son **credenciales temporales del rol asociado**, que la nube rota sola y entrega a quien pregunte.

Las direcciones, rutas y cabeceras por proveedor están en [[SSRF destinos - matriz de referencia]] § Metadatos.

## Cómo falla

- **IMDSv2 obligatorio.** Es la mitigación que de verdad funciona y por eso es la primera pared. Exige obtener un token con un `PUT` y una cabecera antes de leer nada. Un SSRF que solo controla la URL no puede hacer ninguna de las dos cosas, así que queda cerrado. Solo cae si además se controla el método y las cabeceras — cosa que pasa en algunos proxies mal configurados y en `gopher`.
- **Cabecera obligatoria en GCP y Azure.** `Metadata-Flavor: Google` y `Metadata: true` cumplen el mismo papel: sin control de cabeceras, no hay lectura.
- **El endpoint está bloqueado a nivel de red** — por regla de firewall de host o por política de la plataforma. Cada vez más común.
- **La instancia no tiene rol asociado** — hay metadatos y no hay credenciales. Queda información útil de todos modos: identificadores, red, y a veces datos de arranque con secretos dentro.
- **Es un contenedor, no una instancia** — en Kubernetes el equivalente es el token de la cuenta de servicio, montado en el sistema de archivos. Ahí el camino no es este: es `file://` o lectura local.
- **Redirecciones no seguidas** — muchos bypass de lista negra dependen de una redirección; sin ella hay que atacar la validación por otro lado.

## Coste

Bajísimo en esfuerzo. Altísimo en consecuencias, y conviene tenerlo presente antes de ejecutarlo: **usar las credenciales obtenidas es actuar sobre la cuenta de nube del cliente**, y eso suele exceder el alcance de una prueba web. Obtenerlas demuestra el impacto; usarlas es otra conversación y otro permiso.

## Huella esperada

- [[Conexión saliente del servidor de aplicación]] hacia la dirección de enlace local del servicio de metadatos. Es de los indicadores de **mayor fidelidad que existen en web**: una aplicación pide metadatos al arrancar, no en medio de una petición de usuario, y casi nunca pide las rutas de credenciales.
- Del lado de la nube, el uso posterior de esas credenciales aparece en el registro de auditoría —CloudTrail y equivalentes— **desde una IP que no es la de la instancia**. Esa discrepancia es la señal más limpia de todo el dominio: la credencial de una instancia usada desde fuera de ella no tiene explicación legítima.
- Correlación fuerte: petición HTTP entrante, seguida en segundos de una conexión al servicio de metadatos.

Las rutas por proveedor, el flujo de IMDSv2 y qué pedir después están en [[SSRF destinos - matriz de referencia]].
