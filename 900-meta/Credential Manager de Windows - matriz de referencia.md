---
tipo: meta
aliases:
  - cmdkey
  - runas savecred
  - Windows Vault
tags:
  - meta/referencia
  - dominio/post-explotacion
  - plataforma/windows
---

# Credential Manager de Windows - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué guarda el Credential Manager, cómo se enumera y las tres formas de aprovecharlo. Qué **es** el store (vaults, `Policy.vpol`, AES bajo DPAPI, Credential Guard): [[Windows - almacenamiento de credenciales]].
> El criterio y la decisión, en [[MOC - AD volcado de credenciales]]. Ver también: [[AD volcado de credenciales - matriz de referencia]] § 4 para la maquinaria DPAPI genérica.

## 0. Qué hay y dónde

El Credential Manager es la API de cara al usuario; los secretos viven cifrados en carpetas de vault bajo el perfil:

`%LocalAppData%\Microsoft\[Vault|Credentials]\` · `%AppData%\Microsoft\Vault\` · `%ProgramData%\Microsoft\Vault\` · el vault de `systemprofile` para SYSTEM.

Cada vault trae un `Policy.vpol` con claves AES-128/256 protegidas por DPAPI; esas claves cifran las credenciales. Credential Guard (VBS) mueve las masterkeys DPAPI a un enclave y rompe la extracción desde memoria. Dos tipos:

| Tipo | Qué guarda | Lo usa |
|---|---|---|
| Web Credentials | logins de sitios y cuentas online | IE y Edge heredado |
| Windows Credentials | tokens de servicios (OneDrive), usuarios de dominio, recursos de red, shares | el SSO de Windows |

## 1. Enumerar — sin privilegio especial

Corre en el contexto del usuario actual, no pide admin:

`cmdkey /list`

| Campo | Qué dice |
|---|---|
| `Target` | recurso o cuenta: un host, un dominio, o un identificador especial |
| `Type` | `Generic` (app/servicio) o `Domain Password` (logon de dominio) |
| `User` | cuenta asociada |
| `Persistence` | `Local machine persistence` = sobrevive reinicios |

Cómo leer la salida:

- `Target: WindowsLive:target=virtualapp/didlogical` con user aleatorio → credencial interna de cuenta Microsoft/Live. **Ruido, se ignora.**
- `Target: Domain:interactive=SRV01\mcharles`, `Type: Domain Password` → credencial de dominio **reusable**. `interactive` = sesión interactiva. Es la que sirve.

## 2. Reusar sin crackear — la vía barata

Si hay una credencial de dominio marcada reusable, **no hace falta tocar LSASS ni romper nada**: Windows ya la tiene y la inyecta.

`runas /savecred /user:SRV01\mcharles cmd`

Abre un proceso como ese usuario con la credencial guardada. Es el camino más limpio cuando aparece en `cmdkey /list`; la extracción del § 3 es el plan B cuando `runas` no alcanza (querés el secreto en claro, o reutilizarlo fuera de la máquina).

> [!warning] `runas /savecred` no es gratis en telemetría
> Dispara [[Windows 4624 - Successful logon]] con `Logon Type 2` (interactivo) desde un proceso ya logueado, y un [[Sysmon EID 1 - ProcessCreate]] con `cmd`/`powershell` colgando de `runas.exe`. Barato en esfuerzo, visible en logs.

## 3. Extraer el secreto en claro

Cuando el reuso no alcanza. El material está cifrado con DPAPI, así que hay dos enfoques:

**Desde la memoria de LSASS** (pide admin + `SeDebugPrivilege`):

`mimikatz # privilege::debug`
`mimikatz # sekurlsa::credman`

Lista las credenciales del Credential Manager de las sesiones activas, con `Username`/`Domain`/`Password` en claro. Abre un handle a `lsass.exe`, así que deja la misma huella que cualquier `sekurlsa`: [[Sysmon EID 10 - ProcessAccess]].

**Descifrando los blobs con DPAPI** (sin tocar LSASS, desde el contexto del usuario o con su masterkey):

`mimikatz # dpapi::cred /in:C:\Users\u\AppData\Local\Microsoft\Credentials\<id>`

El árbol completo de DPAPI —`sekurlsa::dpapi`, `dpapi.py`, masterkeys— está en [[AD volcado de credenciales - matriz de referencia]] § 4; no se repite acá.

Otras herramientas que enumeran y descifran estos vaults sin mimikatz: SharpDPAPI (C#, en host), LaZagne (barrido local de muchos stores), DonPAPI (remoto y en masa).

## 4. Export a `.crd`

`rundll32 keymgr.dll,KRShowKeyMgr`

Abre el diálogo de respaldo del Panel de Control: exporta los vaults a un `.crd` cifrado con una contraseña que elige el usuario, importable en otro Windows. Útil para mover credenciales entre hosts; poco sigiloso (es GUI) y la contraseña del `.crd` la ponés vos, no descifra el secreto original.
