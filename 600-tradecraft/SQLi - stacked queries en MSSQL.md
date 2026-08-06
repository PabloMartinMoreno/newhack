---
tipo: tradecraft
clase: "[[CWE-89 - SQL Injection]]"
eje: impacto
implementacion: "Apilar una segunda consulta con ; y llegar a xp_cmdshell"
opsec: quemado
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [driver-permite-apilar, cuenta-sysadmin]
coste: bajo
alternativas: ["[[SQLi - lectura de archivos en MySQL]]"]
probado: 2026-08-06
contexto: [mssql2019]
aliases:
  - SQLi stacked MSSQL
  - xp_cmdshell
tags:
  - dominio/web
---

# SQLi - stacked queries en MSSQL

## Cuándo lo elijo

Cuando el driver permite apilar consultas con `;` y la cuenta es `sysadmin`. Es la vía más directa de SQLi a **ejecución de comandos** en el SO: no extraigo datos, ejecuto.

Es el impacto máximo del lado infra: una inyección web se convierte en shell en el servidor de base de datos, que suele estar en un segmento más interno que el frontend.

## Por qué funciona

MSSQL permite terminar una consulta con `;` y correr otra a continuación en la misma petición. Con `sysadmin`, esa segunda consulta puede reconfigurar el servidor (`sp_configure`) para habilitar `xp_cmdshell`, un procedimiento extendido que ejecuta comandos del SO con la cuenta de servicio de SQL Server.

## Cómo falla

- **El driver no apila** — muchas librerías mandan una sola sentencia por llamada; el `;` da error. Es la precondición dura.
- **La cuenta no es `sysadmin`** — `sp_configure` falla; sin eso no se habilita xp_cmdshell.
- **xp_cmdshell removido o bloqueado por política** — endurecimiento común.
- **EDR en el servidor** — `sqlservr.exe` lanzando `cmd.exe`/`powershell.exe` es una de las cadenas más firmadas que existen. `opsec: quemado`.

## Coste

Bajo en peticiones, altísimo en detección. La cadena `sqlservr → cmd → tu comando` la marca cualquier EDR. En un entorno monitoreado se usa una sola vez, con cuidado, o se busca otra vía. Sirve garantizado en labs y entornos sin EDR.

## Huella esperada

- `EXEC xp_cmdshell` y `sp_configure` legibles en el [[Log de acceso del servidor web]].
- Proceso hijo de `sqlservr.exe` — el evento de host más ruidoso posible (equivalente MSSQL de lo que en Windows ve [[Sysmon EID 10 - ProcessAccess]] para otras cadenas).

Payloads en [[SQLi impacto - matriz de referencia]] § Stacked queries.
