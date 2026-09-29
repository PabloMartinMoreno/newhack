---
tipo: tradecraft
clase: "[[T1059 - Command and Scripting Interpreter]]"
eje: direccion-de-conexion
implementacion: "El objetivo conecta hacia el atacante y entrega la E/S de un intérprete al socket"
opsec: quemado
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Conexión saliente del servidor de aplicación]]", "[[Proceso hijo del servidor web]]"]
requisitos: [ejecucion-confirmada, egress-hacia-el-atacante]
coste: bajo
alternativas: ["[[Shell - conexión bind]]", "[[Webshell]]"]
probado: nunca
contexto: [ubuntu22-auditd, win2019-defender]
aliases:
  - reverse shell
  - shell reversa
tags:
  - dominio/post-explotacion
---

# Shell - conexión reversa

## Cuándo lo elijo

Casi siempre, cuando ya hay ejecución y quiero **sesión** en vez de comandos sueltos. Es el valor por defecto del eje de dirección: funciona en la mayoría de las redes porque el **egress está menos filtrado que el ingress** —el objetivo detrás de NAT o firewall no acepta conexiones entrantes, pero sí las inicia—.

La alternativa es [[Shell - conexión bind]], que solo tiene sentido cuando **no** hay egress hacia el atacante pero sí un puerto entrante alcanzable —típicamente ya adentro de la red interna, tras un pivote—. Y antes de abrir cualquier socket conviene preguntarse si el objetivo se cumple sin sesión: enumerar, leer config y sacar credenciales se hace por el canal directo del RCE, sin dejar la conexión que todo EDR busca. Cuando no hay egress de ningún tipo, el fallback sin socket es [[Webshell]].

## Por qué funciona

La ejecución ya está; lo que falta es persistencia de sesión. Se consigue lanzando un proceso que conecta hacia el atacante y redirige `stdin`/`stdout`/`stderr` de un intérprete a ese descriptor de red. El objetivo deja de ser quien responde y pasa a ser quien llama, lo que resuelve de paso que casi nunca hay un puerto entrante alcanzable.

Sobre la dirección: la reversa gana porque el tráfico saliente hacia 443/80 se confunde con navegación legítima en la forma, mientras que un puerto en escucha lo encuentra cualquier escaneo. Los one-liners por lenguaje están en [[Reverse y bind shells - matriz de referencia]].

## Cómo falla

- **Egress filtrado por puerto** — se prueban 443 y 80 antes que cualquier puerto alto: son los que casi siempre salen. Un puerto arbitrario suele estar cerrado.
- **Inspección TLS o proxy explícito obligatorio** — el tráfico en claro se ve entero, y una conexión cruda no atraviesa un egress que solo pasa por proxy HTTP.
- **La shell muere con la petición** — si el proceso padre termina, se lleva al hijo. Hay que desacoplarla del proceso de la petición (`setsid`, `nohup`, `&`).
- **Sin TTY** — no andan `sudo`, `ssh` ni nada a pantalla completa, y `Ctrl-C` mata la sesión. Casi siempre hay que promoverla: [[Estabilización de shell - matriz de referencia]].
- **Sin los binarios esperados** — en contenedores mínimos falta `bash`, `nc`, `python`. Se usa lo que haya; la matriz ordena los one-liners por probabilidad de presencia.
- **La conexión se cae y no vuelve** — sin reintento, un corte de red termina el acceso y obliga a reexplotar.

## Coste

Bajo en esfuerzo y **el más alto del dominio en OPSEC**. Por eso `opsec: quemado`: no es que la técnica esté obsoleta, es que no existe forma sigilosa de hacerlo. Una conexión saliente de larga vida desde un servidor, con un intérprete colgando de ella, es lo que toda detección de host y de red busca por diseño.

## Huella esperada

- Conexión saliente de larga duración hacia una IP externa que no está en la lista de destinos conocidos del host — [[Sysmon EID 3 - NetworkConnect]] en Windows, [[Conexión saliente del servidor de aplicación]] en web.
- Un intérprete con **redirección a un descriptor de red** en su línea de comandos, hijo de un proceso que no debería tener hijos-shell — [[Proceso hijo del servidor web]]. Indicador de altísima fidelidad; lo consume [[Intérprete de comandos como hijo del servidor web]].
- El proceso hijo **sobrevive a la petición** que lo creó: la vida del proceso, por sí sola, es señal.
- [[Consulta DNS saliente]] si el destino se dio por nombre en vez de por IP.
