---
tipo: tradecraft
clase: "[[CWE-78 - OS Command Injection]]"
eje: canal-de-extraccion
implementacion: "El comando inyectado envía los datos a un servidor propio, fuera de la respuesta HTTP"
opsec: ruidoso
telemetria: ["[[Consulta DNS saliente]]", "[[Proceso hijo del servidor web]]"]
requisitos: [shell-invocada, egress-de-red]
coste: bajo
alternativas: ["[[Command injection - canal ciego]]", "[[Command injection - canal temporal]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - command injection OOB
  - out-of-band command injection
tags:
  - dominio/web
---

# Command injection - canal fuera de banda

## Cuándo lo elijo

En cuanto se confirma ejecución y la salida no vuelve, **antes** de bajar a ciego o temporal. Es la primera alternativa del árbol de [[MOC - Command injection]] cuando el canal directo no existe, porque devuelve datos completos en una sola petición en vez de un bit por vez.

También es la única opción cuando la ejecución es **asíncrona**: si el comando corre en una cola y la respuesta HTTP ya volvió, no hay respuesta que observar ni retardo que medir, pero la conexión saliente llega igual cuando el trabajo se procesa. Ese caso rompe todos los demás canales y este lo cubre solo.

## Por qué funciona

El host ejecuta un comando que abre una conexión hacia un servidor controlado por el atacante y le entrega los datos. La respuesta HTTP deja de ser el canal: el canal es la red.

DNS es la vía preferida y la razón es de política de red, no técnica. HTTP saliente está filtrado en cualquier entorno que se tome el egress en serio; **la resolución DNS casi siempre sigue funcionando**, porque romperla rompe el servidor. El dato se codifica dentro del nombre de dominio consultado y aparece en el log del servidor autoritativo.

El precio de DNS es la capacidad: límite de etiqueta y de nombre completo, hay que trocear, y el conjunto de caracteres válidos obliga a codificar. Si HTTP saliente funciona, es preferible por volumen.

## Cómo falla

- **Egress bloqueado por completo** — sin salida no hay canal. Se cae a temporal.
- **Resolvedor interno sin recursión externa** — la consulta se hace pero nunca llega al servidor autoritativo del atacante. Es el corte más frecuente y el menos evidente: parece que no hay ejecución.
- **Caché de DNS** — repetir la misma consulta no genera tráfico nuevo. Cada exfiltración necesita un subdominio único, o los resultados se pierden en silencio.
- **Faltan los binarios** — sin `curl`, `wget`, `nslookup` ni `dig` en un contenedor mínimo, hay que construir la conexión con lo que haya.
- **Es la técnica más ruidosa del dominio.** Una consulta DNS a un dominio externo desde un servidor de aplicación es precisamente lo que busca cualquier detección de exfiltración, y queda registrada en un tercero: el resolvedor.
- **Infraestructura atribuible** — el dominio usado para recibir los datos apunta a quien lo registró.

## Coste

Bajo en peticiones —un volcado entero puede salir en una— y alto en preparación: hace falta un dominio con servidor autoritativo controlado, o un servicio de interacción externo, que a su vez implica que los datos exfiltrados pasan por un tercero.

## Huella esperada

- [[Consulta DNS saliente]] con etiquetas largas y de aspecto aleatorio, hacia un dominio sin historial. La entropía del subdominio es el indicador, más que el dominio en sí.
- [[Proceso hijo del servidor web]] con el binario de red y la URL completa en la línea de comandos.
- Correlación: la consulta DNS ocurre a segundos de una petición HTTP entrante, desde un host que normalmente solo resuelve un puñado de nombres conocidos.

Las primitivas de red por shell, la codificación y el troceo están en [[Command injection ciego - matriz de referencia]] § Fuera de banda.
