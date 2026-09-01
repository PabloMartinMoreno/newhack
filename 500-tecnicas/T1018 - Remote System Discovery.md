---
tipo: tecnica
taxonomia: attack
identificador: T1018
tacticas: [discovery]
aliases:
  - T1018
  - Remote System Discovery
  - descubrimiento de hosts
tags:
  - dominio/red
---

# T1018 - Remote System Discovery

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Reconocimiento de red]]; la variante, en [[Escaneo - descubrimiento de hosts]].

## Qué es

Averiguar qué máquinas existen y responden en un rango, antes de preguntarle a ninguna qué servicios tiene.

## Por qué es un paso propio y no el principio del escaneo de puertos

Porque **la respuesta cambia según dónde estés parado**, y esa diferencia decide la herramienta:

- **Dentro del segmento**, la pregunta se resuelve en la capa de enlace: si una dirección no contesta el ARP, no hay nadie. Es exacto y no hay firewall que lo filtre, porque el firewall está por encima. Ver [[ARP - resolución de direcciones en el segmento]].
- **Fuera del segmento**, hay que preguntar por IP o por TCP, y ahí cualquier equipo del camino puede mentir por omisión. Un host que no contesta puede no existir o puede estar detrás de una regla que descarta en silencio — la ambigüedad de [[ICMP - el canal de error de IP]].

De ahí sale la decisión que define la fase: cuándo confiar en el descubrimiento y cuándo saltearlo y tratar todo el rango como vivo.

## Por qué se sub-detecta

El descubrimiento dentro del segmento es el peor caso para el defensor: **ARP no lo registra nadie**. La telemetría de endpoint arranca por encima de esa capa, así que un barrido ARP completo de una /24 no deja rastro en el visor de eventos ni en Sysmon. Fuera del segmento la situación mejora sólo si hay telemetría de flujo.

## La mitigación real

Segmentar, para que el barrido barato —el de capa 2— alcance poco. Y aceptar que si el atacante ya está en el segmento, esta fase es invisible: lo que se detecta es la siguiente.

## Referencias canónicas

- [T1018](https://attack.mitre.org/techniques/T1018/)
- [T1046](https://attack.mitre.org/techniques/T1046/) — el paso que sigue
