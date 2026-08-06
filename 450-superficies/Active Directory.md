---
tipo: superficie
plataforma: [windows]
tecnicas: ["[[T1003.001 - LSASS Memory]]"]
telemetria: ["[[Sysmon EID 10 - ProcessAccess]]"]
aliases:
  - AD
tags:
  - dominio/ad
---

# Active Directory

Mapa de decisión: [[MOC - Active Directory]].

## Qué es y qué expone

Servicio de directorio y autenticación centralizada. Su superficie de ataque no está en un servicio puntual sino en las **relaciones** entre objetos: quién puede hacer qué sobre quién, y qué credenciales quedan en memoria en cada máquina como consecuencia.

## Superficie de ataque

| Componente | Qué expone | Técnica |
|---|---|---|
| LSASS en cada host | Credenciales de sesiones activas | [[T1003.001 - LSASS Memory]] |
| Kerberos (SPN) | Tickets cifrables offline | [[T1558.003 - Kerberoasting]] |
| LDAP | Enumeración completa del directorio con cualquier credencial válida | — |
| ACLs del directorio | Escalada por relaciones | — |
| Delegaciones | Suplantación | — |
| ADCS | Escalada por plantillas de certificado | — |

## Telemetría que ofrece

Kerberos `4768`/`4769`, acceso a objetos del directorio `4662`, acceso a recursos compartidos `5145`, y todo lo de host ([[Sysmon EID 10 - ProcessAccess]], `4688`).

La enumeración LDAP es el punto ciego habitual: es tráfico legítimo y casi nadie lo recolecta.

## Controles habituales

PPL, Credential Guard, LAPS, tiering administrativo, firmado de LDAP/SMB, cuentas protegidas.
