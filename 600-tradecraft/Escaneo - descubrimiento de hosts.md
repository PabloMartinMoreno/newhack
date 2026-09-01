---
tipo: tradecraft
clase: "[[T1018 - Remote System Discovery]]"
eje: alcance
implementacion: "Barrer un rango para saber qué responde, por ARP dentro del segmento o por sondeos ICMP/TCP fuera de él"
opsec: ruidoso
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Sysmon EID 1 - ProcessCreate]]"]
requisitos: [acceso-a-la-red]
coste: bajo
alternativas: ["[[Escaneo - sondeo SYN de puertos TCP]]"]
probado: nunca
contexto: [lab-ad, segmento-plano]
aliases:
  - host discovery
  - ping sweep
  - barrido de red
tags:
  - dominio/red
---

# Escaneo - descubrimiento de hosts

## Cuándo lo elijo

Siempre primero, y la decisión real es **si creerle al resultado**.

Dentro del segmento le creo: el barrido ARP no lo filtra nadie porque el firewall vive una capa más arriba, y una dirección que no contesta el ARP no está. Es exacto, es rápido —una /24 en segundos— y es el único caso del vault donde *no responde* significa de verdad *no existe*.

Fuera del segmento no le creo. La pregunta viaja por IP y cualquier equipo del camino puede descartarla sin avisar, así que un host que calla puede estar apagado o puede estar protegido — y son justamente los protegidos los que interesan. Ahí la decisión es **saltear el descubrimiento** y tratar todo el rango como vivo, pagando el escaneo de puertos contra direcciones vacías.

La regla práctica: descubrimiento por ARP cuando estoy adentro; sin descubrimiento cuando estoy afuera y el rango es chico. El descubrimiento por ICMP solo sirve para acotar un rango grande cuando el tiempo importa más que la exhaustividad.

## Por qué funciona

Porque preguntar es el uso previsto de las dos capas. ARP contesta porque la red local no funciona si no contesta —ver [[ARP - resolución de direcciones en el segmento]]—, y los sondeos de fuera del segmento se apoyan en que algún estado del host es observable: un `echo reply`, un `RST` a un puerto cerrado, un `SYN-ACK` a uno abierto.

Por eso el descubrimiento moderno no es un `ping`: es una combinación de sondeos —eco, marca de tiempo, `SYN` a un puerto probable, `ACK` a otro—, porque cada uno atraviesa filtros distintos y basta que uno vuelva.

## Cómo falla

Falla, y falla en silencio, cuando el entorno descarta lo que se usa para preguntar. Un rango entero puede aparecer vacío y estar lleno: el resultado no distingue *no hay nadie* de *nadie tiene permitido contestarme*. Es el falso negativo más caro del reconocimiento porque no se parece a un error, se parece a un resultado.

También falla al revés: en redes con IP virtuales, balanceadores o respuestas por proxy, aparecen hosts que no existen como máquinas.

Del lado del sigilo, dentro del segmento es lo más silencioso que hay para la telemetría de endpoint —nadie registra ARP— y a la vez lo más visible para un switch con inspección o un sensor pasivo. Fuera del segmento es al revés.

## Coste

Bajo en tiempo y en riesgo. El coste real no es el barrido: es el error de conclusión si se le cree al silencio. Cuando la exhaustividad importa, el descubrimiento se saltea y se paga con tiempo de escaneo de puertos.
