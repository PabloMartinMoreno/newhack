---
tipo: meta
aliases:
  - Enumeración AD
  - consultas LDAP
  - SharpHound
  - userAccountControl
tags:
  - meta/referencia
  - dominio/ad
---

# AD enumeración - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué se pregunta al directorio y con qué. El criterio —cuándo conviene enumerar y qué pierde el que se saltea este paso— está en [[Enumeración LDAP del directorio]]. Las herramientas SMB (nxc/smbclient/smbmap/rpcclient) por tarea, en [[SMB - matriz de referencia]].

## 0. Qué tengo

La enumeración se abre en dos mundos y conviene saber en cuál estás antes de tirar comandos.

| Lo que tengo | Qué se puede preguntar |
|---|---|
| Nada, solo acceso a la red | Nombre del dominio, controladores, política de contraseñas a veces, y validez de nombres de usuario |
| Una credencial de dominio, cualquiera | **Todo el directorio en lectura**. Un usuario sin privilegios lee usuarios, grupos, ACL, delegaciones y plantillas de certificado |

Ese salto es el más grande de AD: la primera credencial no da acceso a nada nuevo, da **el mapa entero**.

## 1. Sin credencial

`nxc smb 10.0.0.0/24`
Barrido. Devuelve nombre del host, dominio, versión y si exige firma SMB. El que no exige firma es candidato a relay.

`nslookup -type=SRV _ldap._tcp.dc._msdcs.dominio.local`
Los controladores de dominio, desde DNS. No necesita credencial ni toca LDAP.

`nxc smb 10.0.0.10 -u '' -p '' --shares`
Sesión nula. Casi siempre cerrada desde 2003, y cuesta una petición comprobarlo.

`nxc smb 10.0.0.10 -u 'guest' -p '' --rid-brute 10000`
RID cycling. Cuando la sesión nula está cerrada pero `guest` no lo está, saca la lista de usuarios recorriendo identificadores relativos.

`kerbrute userenum --dc 10.0.0.10 -d dominio.local usuarios.txt`
Enumeración por Kerberos. Pregunta un TGT por cada nombre: el error es distinto si el usuario no existe (`KDC_ERR_C_PRINCIPAL_UNKNOWN`) que si existe y falla la contraseña.

> [!warning] Esto no es silencioso
> `kerbrute userenum` genera un `4768` fallido por cada nombre probado. Es la fase más ruidosa de todo AD y la única que un defensor detecta sin esfuerzo. Ver [[Windows 4768 - Kerberos TGT requested]].

`nxc smb 10.0.0.10 -u 'usuario' -p '' --pass-pol`
Política de contraseñas. Se necesita antes de cualquier spraying: el umbral de bloqueo decide cuántos intentos por ventana.

## 2. Con una credencial — el volcado completo

`bloodhound-python -d dominio.local -u user -p 'pass' -c All -ns 10.0.0.10`
Recolector desde Linux. `-c All` incluye sesiones y ACL; `-c DCOnly` solo consulta LDAP contra el controlador y **no toca ninguna otra máquina**, que es lo que conviene cuando importa el ruido.

`SharpHound.exe -c All --zipfilename out.zip`
Recolector desde Windows. `--stealth` limita a una consulta por objeto y evita el barrido de sesiones.

`nxc ldap 10.0.0.10 -u user -p 'pass' --bloodhound -c All --dns-server 10.0.0.10`
Lo mismo desde netexec, sin instalar el recolector aparte.

| Método de recolección | Qué agrega | Ruido |
|---|---|---|
| `DCOnly` | Usuarios, grupos, ACL, confianzas, delegaciones, GPO | Consultas LDAP al DC nada más |
| `Session` | Quién tiene sesión iniciada en cada máquina | Se conecta a **todas** las máquinas |
| `LoggedOn` | Igual pero por registro remoto, más fiable | Necesita admin local |
| `All` | Todo lo anterior | El barrido completo |

El grafo de sesiones es lo que convierte una lista de usuarios en una ruta a Domain Admin. También es lo que hace que el recolector hable con doscientas máquinas en dos minutos, que es la firma más obvia que deja un atacante en AD.

## 3. Consultas LDAP puntuales

Cuando ya sabés qué buscás, una consulta cuesta una petición y no doscientas.

`ldapsearch -x -H ldap://10.0.0.10 -D 'user@dominio.local' -w 'pass' -b 'DC=dominio,DC=local' '(objectClass=user)' sAMAccountName`
Todos los usuarios. El `-b` es la base de búsqueda y sale del nombre del dominio.

**Cuentas con nombre de servicio registrado** — el insumo de [[Kerberoasting]]:

`'(&(objectClass=user)(servicePrincipalName=*)(!(sAMAccountName=krbtgt)))'`

Filtrar `krbtgt` no es cosmética: siempre tiene SPN y su contraseña no se rompe.

**Cuentas sin preautenticación de Kerberos** — el insumo de [[AS-REP roasting]]:

`'(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))'`

**Cuentas con delegación sin restricciones**:

`'(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=524288))'`

**Contraseñas en el campo de descripción** — sigue funcionando en 2026:

`'(&(objectClass=user)(description=*))' description sAMAccountName`

**Cuentas cuya contraseña no expira nunca**:

`'(userAccountControl:1.2.840.113556.1.4.803:=65536)'`

> [!tip] El OID raro es una máscara de bits
> `1.2.840.113556.1.4.803` es el comparador AND bit a bit de LDAP en AD. `userAccountControl` es un entero donde cada bit es una propiedad de la cuenta, y esa sintaxis es la única forma de preguntar por un bit suelto. `:=4194304` no significa "vale 4194304": significa "tiene ese bit prendido". Con `1.2.840.113556.1.4.804` la comparación pasa a OR.

| Bit | Decimal | Qué significa |
|---|---|---|
| `ACCOUNTDISABLE` | 2 | Cuenta deshabilitada |
| `DONT_REQ_PREAUTH` | 4194304 | AS-REP roasteable |
| `TRUSTED_FOR_DELEGATION` | 524288 | Delegación sin restricciones |
| `DONT_EXPIRE_PASSWORD` | 65536 | La contraseña no caduca |
| `PASSWD_NOTREQD` | 32 | Puede tener contraseña vacía |

## 4. Desde Windows, sin herramientas

`net group "Domain Admins" /domain`
`net user usuario /domain`
`nltest /dclist:dominio.local`
`nltest /domain_trusts /all_trusts`

Binarios firmados que ya están en la máquina. No levantan nada en las detecciones que buscan herramientas, y a cambio son lentos y devuelven poco.

`Get-ADUser -Filter 'servicePrincipalName -like "*"' -Properties servicePrincipalName`
PowerShell con el módulo de AD, si está instalado. Genera `4104` si el registro de bloques de script está encendido — ver [[PowerShell 4104 - Script block logging]].

## 5. Preguntas de BloodHound que valen

Se pegan en la pestaña de Cypher.

```
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMINIO.LOCAL"})) RETURN p
```
La ruta más corta desde lo que ya controlás hasta administrador de dominio. Es la consulta que justifica todo el paso de recolección.

```
MATCH (u:User {hasspn:true}) RETURN u.name
```
Kerberoasteables.

```
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name
```
Delegación sin restricciones: cualquiera que se autentique contra esa máquina deja su TGT en memoria.

Marcar como `owned` cada cuenta que vas comprometiendo es lo que hace útil la primera consulta. Sin eso, BloodHound es un inventario.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `KDC_ERR_C_PRINCIPAL_UNKNOWN` | El usuario no existe. Es la señal de la enumeración, no un fallo |
| `KDC_ERR_PREAUTH_FAILED` | El usuario **existe** y la contraseña está mal |
| `KDC_ERR_CLIENT_REVOKED` | La cuenta está bloqueada o deshabilitada. Si aparece durante spraying, pasaste el umbral |
| `Clock skew too great` | Más de cinco minutos de diferencia con el DC. `ntpdate` o `faketime` contra el controlador |
| `ldap_bind: Invalid credentials (49)`, `data 52e` | Contraseña incorrecta |
| `data 533` | Contraseña correcta, cuenta deshabilitada |
| `data 775` | Contraseña correcta, cuenta bloqueada |
| `strongerAuthRequired` | El DC exige firma o canal cifrado. Usar `ldaps://` en el 636 |
| BloodHound sin aristas de sesión | Recolectaste con `DCOnly`. Sin sesiones no hay rutas de movimiento lateral |

## Relacionadas

[[MOC - Active Directory]] · [[Enumeración LDAP del directorio]] · [[AD roasting - matriz de referencia]] · [[Autenticación - matriz de referencia]]
