---
tipo: entidad
clase-entidad: herramienta
tecnicas: []
aliases:
  - John the Ripper
  - JtR
tags:
  - dominio/post-explotacion
---

# john

## Qué es

John the Ripper (edición **Jumbo**): cracker de hashes por **CPU**, fuerte donde hashcat no llega — formatos raros y el ecosistema `*2john` (`zip2john`, `ssh2john`, `keepass2john`, `office2john`…) que **extrae** el hash de un archivo protegido para después romperlo.

## Qué técnicas implementa

- Cracking offline: [[Cracking offline - matriz de referencia]] § John the Ripper.
- El dominio: [[MOC - Ataques de contraseña]].

## Cuándo NO usarla

Cuando hay GPU y el formato es común (NTLM, Kerberoast, sha512crypt): [[hashcat]] es mucho más rápido. john gana en formatos exóticos, sin GPU, y para los `*2john`.

## Estado

Mantenido (la edición Jumbo de la comunidad es la que trae todos los formatos y scripts).

## Notas relacionadas

[[Cracking offline - matriz de referencia]] · [[MOC - Ataques de contraseña]] · [[hashcat]]
