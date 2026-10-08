---
tipo: teoria
habilita: ["[[Pass-the-hash]]", "[[Pass-the-ticket]]", "[[MOC - AD movimiento lateral]]"]
relacionadas: ["[[Windows - almacenamiento de credenciales]]", "[[SMB - dialectos y firma]]"]
aliases:
  - LSASS
  - WinLogon
  - proceso de autenticación de Windows
tags: []
---

# Windows - proceso de autenticación

## Cómo funciona

El inicio de sesión interactivo lo coordinan varios componentes:

- **WinLogon** — proceso de sistema de confianza; es el único que intercepta el login del teclado. Lanza LogonUI, gestiona cambio de contraseña y bloqueo/desbloqueo.
- **LogonUI + proveedores de credenciales** — los *credential providers* son objetos COM (DLLs) que recogen usuario y contraseña.
- **LSASS** (`%SystemRoot%\System32\lsass.exe`) — el guardián: WinLogon le pasa las credenciales (`LSALogonUser`) y LSASS gobierna toda la autenticación, aplica la política local y manda los registros al Event Log.

LSASS no autentica solo: carga **paquetes de autenticación** (DLLs), cada uno un mecanismo:

| Paquete | Rol |
|---|---|
| `Lsasrv.dll` | gestor de paquetes; la función **Negotiate** elige NTLM o Kerberos |
| `Msv1_0.dll` | NTLM / inicio de sesión local |
| `Kerberos.dll` | autenticación Kerberos |
| `Netlogon.dll` | inicio de sesión por red |
| `Samsrv.dll` | cuentas locales (SAM) |
| `Ntdsa.dll` | base de datos de AD (`ntds.dit`) — **solo en los DC** |

El SAM local resuelve el inicio en un equipo de grupo de trabajo; si está unido a dominio, la validación va contra Active Directory en el DC. Dónde viven esas credenciales, en [[Windows - almacenamiento de credenciales]].

## Dónde el diseño abre superficie

LSASS **mantiene en memoria el material de credenciales** —hashes NTLM, tickets de Kerberos y a veces secretos— para no re-pedir la contraseña en cada acceso (single sign-on). Ese caché en memoria es exactamente lo que se vuelca: no hay que romper nada, el sistema lo guarda listo para usar.

Y la función **Negotiate** elige el protocolo: si NTLM y Kerberos ambos sirven, prefiere Kerberos. Que una autenticación salga por **NTLM donde el dominio usa Kerberos** es, por lo tanto, una anomalía observable.

## Qué habilita

- **[[Pass-the-hash]]** — el hash NTLM que LSASS guarda para el SSO autentica igual que la contraseña: con el hash alcanza, no hace falta el texto plano.
- **[[Pass-the-ticket]]** — los tickets de Kerberos cacheados en memoria se roban y se reutilizan tal cual.
- **El modelo NTLM contra Kerberos de [[MOC - AD movimiento lateral]]** — por qué pasar el hash genera NTLM (señal) y pasar el ticket es Kerberos (invisible a nivel protocolo) sale de cómo Negotiate y los paquetes eligen.

## Cómo se ve en la práctica

`lsass.exe` corre como SYSTEM y es el proceso más sensible del host. Tocar su memoria es la firma del volcado — [[Sysmon EID 10 - ProcessAccess]], que ancla [[Acceso a LSASS desde proceso no firmado]]. Los inicios de sesión quedan en [[Windows 4624 - Successful logon]] / [[Windows 4625 - Failed logon]], con el paquete y el tipo de logon en los campos.

## Fuente

- Microsoft Docs — Windows authentication architecture (WinLogon, LSA, security packages).
