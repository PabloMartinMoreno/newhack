---
tipo: tradecraft
clase: "[[T1046 - Network Service Discovery]]"
eje: sondeo
implementacion: "Enviar SYN y clasificar por la respuesta sin completar el handshake, abortando con RST"
opsec: ruidoso
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Sysmon EID 1 - ProcessCreate]]"]
requisitos: [raw-sockets, root-o-administrador]
coste: bajo
alternativas: ["[[Escaneo - sondeos de bandera anómala]]", "[[Escaneo - sondeo de puertos UDP]]"]
probado: nunca
contexto: [lab-ad, linux-sin-firewall-de-salida]
aliases:
  - SYN scan
  - half-open scan
  - sondeo medio abierto
tags:
  - dominio/red
---

# Escaneo - sondeo SYN de puertos TCP

## Cuándo lo elijo

Es el caso base y el que se usa salvo que algo lo impida. Manda un `SYN`, lee la respuesta y aborta con `RST` sin completar el handshake: clasifica en abierto, cerrado y filtrado a una ida y vuelta por puerto.

Lo elijo cuando tengo privilegios para abrir *raw sockets*. Cuando no los tengo —una shell sin privilegios en un host comprometido es el caso típico— la alternativa es el sondeo por `connect()`, que le pide el handshake completo al sistema operativo. No es una versión peor por sigilo sino por **coste y por rastro**: completa la conexión, así que llega a la aplicación y puede quedar registrada por el servicio.

Que el `SYN` sea "medio abierto" **ya no lo hace sigiloso**. Esa reputación viene de cuando lo único que registraba conexiones era la aplicación; hoy el firewall registra el intento igual. Sigue siendo el mejor sondeo, pero por rápido y por preciso, no por invisible.

## Por qué funciona

Porque la pila está obligada a contestar y a contestar distinto según el estado: `SYN-ACK` si hay alguien escuchando, `RST` si no. El sondeo no explota nada, lee la máquina de estados descrita en [[TCP - respuestas a segmentos inesperados]] y en [[TCP - establecimiento de la conexión]].

La tercera respuesta —el silencio— no la produce el host sino el camino, y por eso *filtrado* es información sobre el firewall, no sobre el puerto.

## Cómo falla

- **Contra hosts con limitación de tasa**, los resultados se degradan a *filtrado* falso y hace falta bajar la velocidad, que es de donde sale casi todo el tiempo de un escaneo grande.
- **Contra firewalls que responden `RST` en nombre del host**, todo aparece cerrado y el escaneo miente con confianza.
- **Sin privilegios no corre**, y la caída a `connect()` cambia la huella: deja conexión completa y, en varios servicios, línea de log.
- **Es visible por volumen**: el abanico de destinos desde un mismo proceso es exactamente la firma de [[Abanico de conexiones fallidas desde un host]].

## Coste

El más bajo del dominio por puerto sondeado. El coste que importa es de calendario: barrer los 65535 puertos de un rango grande a velocidad prudente lleva horas, y ese es el motivo real por el que casi todo el mundo escanea los mil por defecto y se pierde lo que está en el resto.
