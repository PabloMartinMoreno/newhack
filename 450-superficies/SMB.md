---
tipo: superficie
plataforma: [windows, linux]
tecnicas: ["[[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]]", "[[T1105 - Ingress Tool Transfer]]", "[[T1087.002 - Domain Account Discovery]]"]
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Windows 4624 - Successful logon]]", "[[Windows 5145 - Network share access]]"]
aliases:
  - SMB (445)
  - CIFS
  - Samba
tags:
  - dominio/ad
---

# SMB

Protocolo detrás de casi toda la cadena de AD. La teoría: [[SMB - dialectos y firma]] y [[SMB - sesión nula e IPC$]]. Los ataques viven en [[MOC - Active Directory]] y [[MOC - Transferencia de archivos]] — esta nota es la puerta de entrada, no el mapa de decisión.

## Qué es y qué expone

Compartición de archivos y canalizaciones RPC sobre TCP 445 (Windows nativo; Samba en Linux). No expone una vulnerabilidad puntual sino una **superficie de servicio**: recursos compartidos, sesiones autenticadas reutilizables, y el canal de RPC (IPC$) por el que se administran servicios remotos. Es el transporte del que cuelgan enumeración, movimiento lateral y transferencia.

## Superficie de ataque

| Componente | Qué expone | Técnica |
|---|---|---|
| Autenticación NTLM sin firma requerida | Reenvío de la sesión a un tercero | [[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]] |
| Sesión nula / IPC$ | Enumeración anónima de usuarios, política y shares | [[T1087.002 - Domain Account Discovery]] |
| IPC$ + named pipes | Ejecución remota (psexec/smbexec) — en la matriz de movimiento lateral | — |
| Recurso montado | Traer y sacar archivos | [[T1105 - Ingress Tool Transfer]] |
| Shares mal permisados | Lectura de datos sensibles y caza de credenciales | — |
| SMB1 / dialecto viejo | Fallos de implementación históricos (fuera del alcance actual del vault) | — |

## Telemetría que ofrece

Conexión a 445 en [[Sysmon EID 3 - NetworkConnect]]; el logon en [[Windows 4624 - Successful logon]] tipo 3 —con `ANONYMOUS LOGON` cuando es sesión nula—; el acceso al recurso, con su nombre, en [[Windows 5145 - Network share access]]. El dialecto negociado y el estado de la firma **no** están en el log de endpoint: solo en captura de red, que el vault no modela.

## Controles habituales

Firma SMB **requerida** (corta el relay — ver [[SMB - dialectos y firma]]), SMB1 deshabilitado, `RestrictAnonymous`/`RestrictAnonymousSAM` (cortan la sesión nula), segmentación de 445, y permisos mínimos sobre los shares.

## Notas relacionadas

- Teoría: [[SMB - dialectos y firma]] · [[SMB - sesión nula e IPC$]]
- Ataque: [[MOC - AD envenenamiento y relay]] · [[MOC - AD enumeración]] · [[MOC - AD movimiento lateral]] · [[MOC - Transferencia de archivos]]
- Cheatsheet: [[SMB - matriz de referencia]] — nxc/smbclient/smbmap/rpcclient por tarea
