---
tipo: teoria
habilita: ["[[LSASS - volcado vía comsvcs.dll MiniDump]]", "[[DCSync]]", "[[MOC - AD volcado de credenciales]]"]
relacionadas: ["[[Windows - proceso de autenticación]]"]
aliases:
  - SAM
  - NTDS
  - Credential Manager
  - SYSKEY
tags: []
---

# Windows - almacenamiento de credenciales

## Dónde viven las credenciales

Cuatro lugares, y cada uno es un objetivo de volcado distinto:

| Almacén | Qué guarda | Dónde | Requisito para leerlo |
|---|---|---|---|
| **SAM** | cuentas **locales**, hashes LM/NTLM | `%SystemRoot%\system32\config\SAM` (reg. `HKLM\SAM`) | SYSTEM |
| **NTDS.dit** | cuentas de **dominio** (user/grupo/equipo + hashes), GPOs | `%SystemRoot%\NTDS\ntds.dit` en el DC (replicado, salvo RODC) | acceso al DC o replicación |
| **LSASS (memoria)** | credenciales de sesiones **activas**: hashes, tickets | RAM del proceso `lsass.exe` | SYSTEM |
| **Credential Manager** | credenciales guardadas por el usuario (red, web, apps) | `%LOCALAPPDATA%\Microsoft\[Vault\|Credentials]\` | el perfil de ese usuario |
| **LSA Secrets** | contraseñas de servicios, cuenta de máquina, auto-logon | reg. `HKLM\SECURITY\Policy\Secrets` | SYSTEM |
| **Cacheadas de dominio** (DCC2) | último logon validado, para entrar **sin** DC | reg. `HKLM\SECURITY\Cache` | SYSTEM |

Equipo en **grupo de trabajo** → autentica contra su SAM local. Equipo en **dominio** → el DC valida contra `ntds.dit`. El SSO mantiene además lo de la sesión viva en memoria de LSASS — ver [[Windows - proceso de autenticación]].

Los hashes del SAM se guardan como **LM** (heredado, débil) o **NTLM**. **SYSKEY** (desde NT 4.0) cifra parcialmente el SAM en disco con una clave del sistema, para que robar el archivo suelto no alcance.

Dos matices que cambian cómo se usa cada store:

- El **Credential Manager** cifra con **DPAPI** (clave derivada de la contraseña del usuario, con copia de respaldo en el dominio). Por eso se descifra desde el contexto de ese usuario, no con SYSTEM a secas.
- Las **cacheadas de dominio** (DCC2 / mscash2) **no son reusables**: no sirven para [[Pass-the-hash]], solo se crackean offline y son lentas a propósito ([[Cracking offline - matriz de referencia]] `-m 2100`). Por eso se dejan para el final.

## Dónde el diseño abre superficie

Todo lo que el sistema guarda para no re-pedir la contraseña es volcable con el privilegio adecuado: SYSTEM abre SAM y la memoria de LSASS; el control del DC (o derechos de replicación) abre NTDS; el propio perfil abre el Credential Manager. La credencial en reposo o cacheada es el precio del SSO y de la gestión centralizada.

## Qué habilita

- **[[LSASS - volcado vía comsvcs.dll MiniDump]]** — la memoria de LSASS trae los hashes/tickets de las sesiones activas.
- **SAM / NTDS** — los hashes locales y los de todo el dominio; **[[DCSync]]** pide la replicación en vez de tocar el disco del DC. Todo el árbol de opciones, en [[MOC - AD volcado de credenciales]].
- El formato (LM/NTLM) decide el modo de [[Cracking offline - matriz de referencia]] (`-m 1000` NTLM, `-m 3000` LM).

## Cómo se ve en la práctica

Leer el SAM o la memoria de LSASS pide SYSTEM y deja rastro: el acceso a `lsass.exe` es [[Sysmon EID 10 - ProcessAccess]]; la replicación de NTDS por DCSync es [[Windows 4662 - Directory object operation]] sobre el objeto del dominio. El Credential Manager se descifra desde el contexto del usuario, sin tocar LSASS.

## Fuente

- Microsoft Docs — SAM, Active Directory Domain Services (NTDS.dit), Credential Manager / Windows Vault.
