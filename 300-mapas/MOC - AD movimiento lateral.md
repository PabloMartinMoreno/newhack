---
tipo: moc
dominio: ad
aliases:
  - MOC AD movimiento lateral
tags:
  - dominio/ad
---

# MOC - AD movimiento lateral

> [!abstract] Fase de la kill chain de AD
> Usar el material robado para autenticarse en otra máquina. Hub: [[MOC - Active Directory]]. Cheatsheet: [[AD movimiento lateral - matriz de referencia]]. Clases: [[T1550.002 - Pass the Hash]] · [[T1550.003 - Pass the Ticket]].

Lo que tengo del objetivo decide con qué me muevo, y **qué protocolo genera** — que es la consecuencia defensiva directa.

## Árbol de decisión

```
¿Qué material tengo del objetivo?
├─ Hash NTLM
│  ├─ ¿NTLM habilitado?  → [[Pass-the-hash]]
│  └─ ¿solo Kerberos?    → usar el hash para pedir un ticket (overpass), y pasar a la fila de abajo
├─ Ticket de Kerberos
│  ├─ en memoria de un host que controlo  → [[Pass-the-ticket]]
│  └─ puedo forjarlo (tengo el secreto de firma)  → [[MOC - AD persistencia]] (golden/silver)
└─ Certificado  → [[MOC - ADCS]]   ← el que sobrevive al cambio de contraseña
```

**NTLM contra Kerberos no es solo sintaxis.** Pasar el hash genera NTLM donde el dominio usa Kerberos, y ese desajuste es una señal. Pasar el ticket es Kerberos, o sea invisible a nivel de protocolo. La elección tiene consecuencia defensiva directa.

## Orden de aprendizaje

1. [[Pass-the-hash]] — NTLM, y por qué el desajuste de protocolo delata
2. [[Pass-the-ticket]] — Kerberos legítimo; lo que se detecta es el robo, no el uso

## Cara roja

- [[Pass-the-hash]] · [[Pass-the-ticket]]
- Comandos: [[AD movimiento lateral - matriz de referencia]] — pass-the-hash, pass-the-ticket, overpass, los cinco métodos de ejecución remota y su ruido.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[Pass-the-hash]] | [[Windows 4624 - Successful logon\|4624]] | [[Autenticación NTLM donde el dominio usa Kerberos]] |
| [[Pass-the-ticket]] | [[Sysmon EID 10 - ProcessAccess\|Sysmon 10]] | el paso anterior — [[Acceso a LSASS desde proceso no firmado]] |
| reutilización de admin local | [[Windows 4624 - Successful logon\|4624]] | [[Accesos exitosos contra muchas cuentas desde un origen]] |

**Cuando el uso es invisible, se detecta el paso anterior.** Pasar el ticket es Kerberos legítimo; lo que se ve es el robo del ticket de memoria, que es el mismo acceso a LSASS que ya tiene detección.

## Huecos conocidos

- [x] Hash y ticket, con la lección de protocolo (NTLM delata, Kerberos no)
- [ ] Los cinco métodos de ejecución remota (`wmiexec`, `smbexec`, `psexec`, `atexec`, `dcomexec`) y su ruido viven en la matriz
- [ ] Overpass-the-hash como puente NTLM→Kerberos: matriz, sin nota propia
