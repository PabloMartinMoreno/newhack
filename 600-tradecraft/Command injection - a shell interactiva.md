---
tipo: tradecraft
clase: "[[CWE-78 - OS Command Injection]]"
eje: impacto
implementacion: "Convertir la ejecución de un comando por petición en una sesión interactiva"
opsec: quemado
telemetria: ["[[Proceso hijo del servidor web]]", "[[Consulta DNS saliente]]"]
requisitos: [ejecucion-confirmada]
coste: medio
alternativas: ["[[Webshell]]", "[[Command injection - canal directo]]"]
probado: 2026-08-06
contexto: [php8-linux]
aliases:
  - reverse shell desde command injection
  - upgrade a shell
tags:
  - dominio/web
---

# Command injection - a shell interactiva

## Cuándo lo elijo

Cuando ejecutar un comando por petición deja de alcanzar. El umbral es concreto y conviene reconocerlo antes de cruzarlo: hace falta **estado entre comandos** —directorio de trabajo, variables, una sesión de base de datos—, o hay que correr algo interactivo, o el volumen de comandos vuelve absurdo el ida y vuelta por HTTP.

Antes de saltar acá hay que preguntarse si el objetivo real no se cumple sin sesión. Enumerar, leer configuración y sacar credenciales se hace perfectamente con [[Command injection - canal directo]], sin abrir una conexión que va a quedar registrada. **La shell interactiva es el paso que convierte una vulnerabilidad web en un incidente visible.**

La alternativa intermedia es [[Webshell]]: mantiene el acceso sin conexión saliente y sin proceso colgando, a cambio de dejar un archivo en disco.

## Por qué funciona

La ejecución de comandos ya está; lo que falta es persistencia de sesión. Se consigue lanzando un proceso que conecta hacia el atacante y entrega la entrada y salida estándar de un intérprete a ese socket. El servidor deja de ser quien responde y pasa a ser quien llama, lo que además resuelve el problema de que casi nunca hay un puerto entrante alcanzable.

Sobre la dirección de la conexión: la reversa —el objetivo conecta hacia afuera— funciona en casi todos lados, porque el egress suele estar menos filtrado que el ingress. La conexión directa, con el objetivo escuchando, solo sirve si hay un puerto alcanzable desde fuera, cosa rara detrás de NAT o de un firewall perimetral, y encima deja un puerto abierto que cualquier escaneo encuentra.

## Cómo falla

- **Egress filtrado por puerto** — se prueban 443 y 80 antes que cualquier puerto alto: son los que casi siempre salen. Un puerto arbitrario suele estar cerrado.
- **Inspección TLS o proxy explícito** — el tráfico no cifrado se ve entero, y si el egress solo pasa por proxy HTTP, una conexión cruda no sale.
- **La shell muere con la petición** — si el proceso padre termina, se lleva al hijo. Hay que desacoplarlo del proceso de la petición.
- **Sin TTY** — sin terminal no funcionan `sudo`, `ssh`, ni ningún programa a pantalla completa, y un `Ctrl-C` mata la sesión entera en vez del comando. Casi siempre hay que promover la shell a TTY completo antes de trabajar en serio.
- **Sin los binarios esperados** — en contenedores mínimos falta `bash`, `nc`, `python`. Hay que usar lo que haya.
- **La conexión se cae y no vuelve** — sin mecanismo de reintento, un corte de red termina el acceso y obliga a reexplotar.

## Coste

Bajo en esfuerzo y **el más alto del dominio en opsec**. Por eso `opsec: quemado`: no es que la técnica esté obsoleta, es que no existe forma sigilosa de hacerlo. Una conexión saliente desde un servidor web hacia una IP externa, con un intérprete colgando de ella, es lo que todo EDR y toda detección de red buscan por diseño.

## Huella esperada

- [[Proceso hijo del servidor web]] con un intérprete como hijo del servidor y **redirecciones a un descriptor de red** en la línea de comandos. Es de los indicadores de mayor fidelidad que existen: casi no tiene falsos positivos.
- Conexión saliente de larga duración desde la IP del servidor de aplicación hacia una IP externa. Un servidor web establece conexiones salientes hacia poquísimos destinos conocidos; ésta no está en la lista.
- Un proceso hijo del servidor que sobrevive a la petición que lo creó — la vida del proceso, por sí sola, es señal.
- [[Consulta DNS saliente]] si el destino se especificó por nombre en vez de por IP.

Los payloads por lenguaje y binario, y la promoción a TTY completo, están en [[Command injection impacto - matriz de referencia]].
