---
tipo: deteccion
tecnicas: ["[[T1105 - Ingress Tool Transfer]]"]
telemetria: ["[[Sysmon EID 1 - ProcessCreate]]"]
forma: evento
estado: idea
fidelidad: media
logica: kql
validada: 
aliases:
  - LOLBin download
tags:
  - dominio/post-explotacion
---

# Descarga de herramienta por utilidad del sistema

## Qué detecta

Una utilidad firmada de Windows —`certutil`, `bitsadmin`, `mshta`, `curl.exe`— ejecutándose con una **URL o IP en la línea de comando**. Es la firma del ingress por LOLBin: esos binarios existen para otra cosa, y bajar un archivo de un host externo casi nunca es su uso legítimo. Cubre [[Traer herramientas al objetivo]].

## Forma

`evento` — un solo `Process Create` con un patrón en `CommandLine` alcanza. No hace falta correlacionar ni ventana: la anomalía está en el evento mismo.

## Lógica

Sobre [[Sysmon EID 1 - ProcessCreate]] (o `4688` con línea de comando):

- `Image` termina en `certutil.exe`, `bitsadmin.exe`, `mshta.exe`, `curl.exe`, `wget.exe`, o `powershell.exe`
- **y** `CommandLine` contiene `http://`, `https://`, `ftp://` o una IP literal
- para `certutil`, además `-urlcache` o `-split` o `-f`

Ejemplo (KQL, Defender/Sentinel):

```kql
DeviceProcessEvents
| where FileName in~ ("certutil.exe","bitsadmin.exe","mshta.exe","curl.exe")
| where ProcessCommandLine has_any ("http://","https://","ftp://")
| project Timestamp, DeviceName, AccountName, FileName, ProcessCommandLine
```

## Qué la evade

- Renombrar el binario — pero Sysmon guarda `OriginalFileName`, así que la regla robusta ancla ahí, no en `Image`.
- Descargar con un intérprete no listado (Python, un binario propio traído por otra vía) — fuera del alcance de esta firma; ahí la señal es la conexión saliente, no el nombre del proceso.
- Ejecución en memoria (`IEX ... DownloadString`) — no siempre deja el archivo en disco, pero sí deja `powershell` con una URL en la línea de comando, que esta regla ve si se incluye PowerShell.

## Fidelidad

Media. `certutil`/`bitsadmin` con URL tienen pocos usos legítimos y dan buena señal; incluir `powershell` con URL sube la cobertura pero también los falsos positivos (scripts de administración). Conviene la regla estrecha (certutil/bitsadmin/mshta) de alta fidelidad, y `powershell` como regla aparte de menor prioridad.
