---
tipo: tradecraft
clase: "[[CWE-918 - Server-Side Request Forgery]]"
eje: retorno
implementacion: "La petición sale pero la respuesta no vuelve; se infiere por tiempo, estado o interacción externa"
opsec: ruidoso
telemetria: ["[[Conexión saliente del servidor de aplicación]]", "[[Consulta DNS saliente]]"]
requisitos: [url-controlada, sin-respuesta-reflejada]
coste: alto
alternativas: ["[[SSRF - canal directo]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - blind SSRF
  - SSRF ciego
tags:
  - dominio/web
---

# SSRF - canal ciego

## Cuándo lo elijo

Cuando la petición sale y la respuesta no vuelve por ningún lado. Es lo habitual en webhooks, en trabajos en segundo plano y en cualquier flujo donde la app solo registra si la URL "funcionó".

El primer objetivo acá no es leer: es **demostrar que la petición sale**. Un servidor de interacción externo lo confirma en una petición —el destino recibe la conexión y eso ya prueba el SSRF— aunque nada vuelva al atacante.

De ahí en más el trabajo es de inferencia, y conviene ser honesto sobre el techo: un SSRF ciego rara vez lee datos. Lo que sí hace, y bien, es **mapear**: qué hosts existen, qué puertos están abiertos, qué responde y qué no. Ver [[SSRF - escaneo de la red interna]].

Excepción importante: si el esquema `gopher` está disponible, el canal ciego alcanza para RCE sin leer una sola respuesta, porque los protocolos de texto sin autenticación no necesitan que el atacante vea la contestación. Ver [[SSRF - gopher a servicio interno]].

## Por qué funciona

La respuesta HTTP deja de ser el canal y lo reemplaza un efecto lateral observable. Hay tres, de mejor a peor:

**Interacción externa.** El destino es un servidor propio; la conexión que llega es la señal. Confirma con certeza y sin ambigüedad, pero solo prueba egress: no dice nada de lo interno.

**Diferencia de estado o de error.** "URL inválida" y "tiempo de espera agotado" son mensajes distintos, y esa diferencia es un bit. Es el mejor oráculo para lo interno, porque distingue un puerto abierto de uno cerrado.

**Diferencia de tiempo.** Un puerto cerrado rechaza al instante; uno filtrado agota el tiempo de espera; uno abierto responde rápido. Es el mismo mecanismo de [[La latencia como canal de datos]], con el mismo problema de ruido.

## Cómo falla

- **Todo devuelve el mismo mensaje genérico** — sin diferencia observable no hay oráculo, y solo queda la interacción externa. Contra destinos internos, eso deja el canal en nada.
- **La petición es asíncrona** — corre en una cola, la respuesta HTTP ya volvió y no hay tiempo que medir. La interacción externa llega igual, minutos después, y es lo único que funciona.
- **Tiempos de espera uniformes** — si el cliente HTTP corta a los N segundos pase lo que pase, el oráculo temporal se anula.
- **Reintentos** — el cliente reintenta y ensucia tanto la medición como el conteo de interacciones.
- **Caché de DNS** — repetir el mismo nombre no genera consulta nueva y la interacción no llega. Cada prueba necesita un subdominio único.
- **Egress bloqueado** — sin salida no hay confirmación externa, y hay que apoyarse solo en estado y tiempo.

## Coste

Alto: un bit por petición, y las peticiones son lentas porque muchas esperan un tiempo de espera completo. Mapear un rango interno son cientos de peticiones. Es rentable igual, porque lo que se obtiene —topología interna— no se consigue de ninguna otra forma desde afuera.

## Huella esperada

- [[Consulta DNS saliente]] hacia un dominio sin historial, con subdominio único por prueba. Es el rastro más visible: cada intento de confirmación deja uno.
- [[Conexión saliente del servidor de aplicación]] con muchísimos intentos fallidos y de corta vida hacia puertos y hosts variados. **El patrón de fallos es la firma**, más que cualquier conexión individual.
- Barrido secuencial de IP o de puertos, con marcas de tiempo regulares — perfil que ninguna aplicación legítima produce.

Los oráculos y la lógica de inferencia están en [[SSRF evasión - matriz de referencia]] § Confirmar sin respuesta.
