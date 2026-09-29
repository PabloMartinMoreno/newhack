---
tipo: tradecraft
clase: "[[T1059 - Command and Scripting Interpreter]]"
eje: direccion-de-conexion
implementacion: "El objetivo abre un puerto en escucha con un intérprete detrás; el atacante conecta"
opsec: ruidoso
telemetria: ["[[Sysmon EID 1 - ProcessCreate]]", "[[Sysmon EID 3 - NetworkConnect]]", "[[Proceso hijo del servidor web]]"]
requisitos: [ejecucion-confirmada, puerto-entrante-alcanzable]
coste: medio
alternativas: ["[[Shell - conexión reversa]]"]
probado: nunca
contexto: [ubuntu22-auditd, red-interna-tras-pivote]
aliases:
  - bind shell
  - shell bind
tags:
  - dominio/post-explotacion
---

# Shell - conexión bind

## Cuándo lo elijo

Solo cuando la reversa no puede salir **y** hay un puerto del objetivo alcanzable desde donde estoy. Es el caso raro: casi siempre implica estar ya **dentro de la red interna** —tras un pivote, o en el mismo segmento—, porque desde internet el objetivo detrás de NAT o firewall perimetral no acepta entrantes.

La opción por defecto es [[Shell - conexión reversa]]; el bind es su reverso exacto y solo gana cuando el egress está cerrado pero el ingress local no. Si tampoco hay puerto entrante alcanzable, no hay socket: queda [[Webshell]] o seguir por el canal directo del RCE.

## Por qué funciona

En vez de conectar hacia afuera, el objetivo abre un socket en escucha y le entrega la E/S de un intérprete a quien conecte. Invierte la dirección respecto de la reversa: el atacante es el que llama. Sirve cuando el egress está bloqueado pero la ruta atacante→objetivo existe, cosa que en una red interna plana suele darse. Sintaxis en [[Reverse y bind shells - matriz de referencia]] § bind.

## Cómo falla

- **NAT o firewall perimetral** — desde fuera, el puerto en escucha no es alcanzable; por eso el bind casi no sirve como acceso inicial desde internet.
- **El puerto lo encuentra cualquier escaneo** — un socket en escucha nuevo en un servidor es una anomalía que un barrido de red o el propio inventario del host detectan. La reversa no abre puertos; el bind sí.
- **Se lo lleva el firewall de host** — reglas de entrada por defecto (Windows Firewall, `iptables`) bloquean el puerto aunque el proceso escuche.
- **Compite con un puerto en uso** — si el puerto elegido ya está ocupado, el bind falla en silencio.
- **Sin TTY** — igual que la reversa, hay que promoverla: [[Estabilización de shell - matriz de referencia]].

## Coste

Bajo en esfuerzo. En OPSEC es `ruidoso`, no `quemado` como la reversa: no genera la conexión saliente que toda detección de C2 busca, pero **deja un puerto en escucha** que delata el acceso a cualquiera que mire los sockets del host. Cambia una firma de red saliente por una superficie de red entrante.

## Huella esperada

- Un **puerto en escucha nuevo** en el host — la señal más directa, y a la vez el **punto ciego del vault**: no hay artefacto en `550-telemetria/` que modele el estado de los sockets (ni `netstat`, ni Windows 5156/WFP, ni flujo de red). Ver el hueco en [[MOC - Shells]].
- El intérprete lanzado para atender el socket — [[Sysmon EID 1 - ProcessCreate]] / [[Proceso hijo del servidor web]] si el padre es el servicio comprometido.
- La conexión entrante del atacante cuando se establece — [[Sysmon EID 3 - NetworkConnect]], aunque llega **después** de que el puerto ya estaba expuesto.
