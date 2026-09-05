---
tipo: tecnica
taxonomia: attack
identificador: T1048
tacticas: [exfiltration]
aliases:
  - T1048
  - Exfiltration Over Alternative Protocol
tags:
  - dominio/post-explotacion
---

# T1048 - Exfiltration Over Alternative Protocol

## Qué es

Sacar datos del objetivo por un protocolo **distinto** al del canal de mando: HTTP a un servidor propio, FTP o SMB, o canales encubiertos como DNS e ICMP. El movimiento es **hacia afuera**.

## Por qué existe / qué la habilita

El dato robado tiene que salir, y la salida directa suele estar filtrada. La técnica explota que el perímetro deja pasar **algún** protocolo: si sale 443, va por HTTPS; si solo se resuelve DNS, va codificado en los subdominios; si deja ICMP, va en el payload del echo. Cuanto más restrictivo el egress, más encubierto el canal — y más lento.

## Ejes que la descomponen

Criterio en [[MOC - Transferencia de archivos]]; sintaxis en [[Exfiltración - matriz de referencia]].

| Eje | Valores |
|---|---|
| Restricción del canal | abierto (HTTP/FTP/SMB) · encubierto (DNS/ICMP) |
| Sistema | Windows · Linux |

## Referencias canónicas

- MITRE ATT&CK: [T1048](https://attack.mitre.org/techniques/T1048/)
