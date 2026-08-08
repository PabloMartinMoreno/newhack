---
tipo: telemetria
plataforma: [linux, windows]
producto: auditd / Sysmon for Linux / Sysmon / EDR
identificador: "execve"
por-defecto: false
coste: alto
aliases:
  - execve del servidor web
  - proceso hijo de www-data
  - child process of web server
tags:
  - dominio/web
---

# Proceso hijo del servidor web

## Qué lo genera

Cada creación de proceso cuyo padre es el servidor web o el intérprete de la aplicación: `nginx`, `apache2`, `httpd`, `php-fpm`, `w3wp.exe`, `node`, `java`, `python`.

Es **el** artefacto del dominio de inyección de comandos, y el único que lo ve de verdad. [[Log de acceso del servidor web]] ve la petición pero no ve qué ejecutó el servidor; si el payload viaja por POST, ni siquiera ve la petición. Acá se ve el comando.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| Proceso padre | `php-fpm`, `w3wp.exe`, `nginx` | El filtro que convierte esta fuente en señal: un servidor web casi nunca es padre legítimo de una shell |
| Línea de comandos | El comando completo con argumentos | Acá aparece el payload aunque haya viajado por POST |
| Imagen ejecutada | `/bin/sh`, `curl`, `powershell.exe` | La cadena `nginx → sh → curl` es la firma |
| Usuario | `www-data`, `apache`, `IIS APPPOOL\x` | Confirma que corre con la identidad del servidor |
| Árbol de proceso | Ancestros completos | Distingue un `sh` de despliegue de uno nacido de una petición |

## Coste de recolección

Alto. Un servidor con despliegues, cron y scripts de mantenimiento genera muchísimos `execve`. Se vuelve manejable filtrando por **padre**: solo procesos cuyo ancestro sea el servidor web. Ese recorte baja el volumen uno o dos órdenes de magnitud y no pierde nada de este dominio.

## Cómo se activa

- **Linux con auditd** — regla sobre la syscall `execve`. Barata de escribir, cara de leer: el formato es hostil y hay que correlacionar varios registros por evento.
- **Linux con Sysmon for Linux** — EID 1, mismo esquema que Windows, con árbol de proceso ya resuelto. Muy preferible si se puede instalar.
- **Windows** — Sysmon EID 1, o `4688` con `ProcessCommandLine` habilitado por directiva (no viene activado).
- **EDR** — ya lo recolecta siempre; el problema pasa a ser tener acceso a la consulta.

## Limitaciones

- **No ve lo que no crea proceso.** Un payload que se resuelve dentro del intérprete —`eval` de PHP, SSTI, deserialización— no genera `execve`. Ese es el hueco que deja este artefacto, y por eso [[Command injection - canal fuera de banda]] enlaza además a [[Consulta DNS saliente]].
- **Los binarios legítimos son ambiguos.** Muchas apps invocan `convert`, `ffmpeg` o `git` por diseño. La anomalía no es el binario, es el **argumento**.
- **`execve` sin shell no distingue** una invocación legítima de una con argumentos inyectados: es el punto ciego exacto de [[CWE-88 - Argument Injection]], y hay que buscarlo en la línea de comandos, no en el árbol.

## Quién lo emite / quién lo consume

Rojo: [[Command injection - canal directo]] · [[Command injection - canal ciego]] · [[Command injection - canal temporal]] · [[Argument injection - abuso de flags]] · [[Command injection - a shell interactiva]]
Azul: pendiente — ver [[Consultas del vault]] § Huecos defensivos propios
