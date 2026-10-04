---
tipo: entidad
clase-entidad: herramienta
tecnicas: []
aliases: []
tags:
  - dominio/post-explotacion
---

# hashcat

## Qué es

El cracker de hashes acelerado por **GPU**: el más rápido para romper offline un hash capturado. Soporta cientos de modos (`-m`) y varios tipos de ataque (`-a`: diccionario, reglas, máscara, combinador).

## Qué técnicas implementa

- Cracking offline: [[Cracking offline - matriz de referencia]] — modos, ataques, reglas y máscaras.
- El dominio y de dónde salen los hashes: [[MOC - Ataques de contraseña]].

## Cuándo NO usarla

Cuando el formato no está entre sus modos, o no hay GPU que la haga valer la pena → [[john]] (CPU, más formatos). Para **adivinar contra un servicio vivo** (online) no sirve: hashcat es offline sobre un hash ya capturado — eso es hydra/nxc, distribuido en las matrices de servicio y [[MOC - Autenticación]].

## Estado

Mantenido y estándar. Lo que un informe da por sentado para medir la fuerza de una contraseña.

## Notas relacionadas

[[Cracking offline - matriz de referencia]] · [[MOC - Ataques de contraseña]] · [[john]]
