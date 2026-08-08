---
tipo: tradecraft
clase: "[[CWE-502 - Deserialization of Untrusted Data]]"
eje: vector
implementacion: "phar:// dispara unserialize sobre los metadatos del archivo"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [wrapper-phar-alcanzable, cadena-de-gadgets]
coste: alto
alternativas: ["[[LFI - de lectura a RCE]]", "[[LFI wrappers - matriz de referencia]]"]
probado: 2026-08-06
contexto: [php8]
aliases:
  - phar deserialization
  - phar unserialize
tags:
  - dominio/web
---

# LFI - phar deserialization

## Cuándo lo elijo

Cuando puedo hacer que una función de archivo de PHP toque una ruta `phar://` que yo controlo, y en la app existe una **cadena de gadgets** (clases con métodos mágicos abusables). Es una vía a RCE que no necesita `include` clásico: alcanza con casi cualquier operación de archivo sobre `phar://`.

Es la más avanzada de las vías de [[LFI - de lectura a RCE]]: no depende de envenenar un log, pero sí de que la base de código tenga gadgets. Por eso `coste: alto`.

## Por qué funciona

Al acceder a un archivo por el wrapper `phar://`, PHP **deserializa** los metadatos del archivo phar automáticamente. Si controlo el phar, controlo el objeto deserializado; si en la app hay una clase con un método mágico peligroso (`__destruct`, `__wakeup`) alcanzable, la deserialización dispara la cadena y ejecuta.

Lo potente: no requiere `include`. Funciones como `file_exists`, `fopen`, `getimagesize`, `file_get_contents` sobre `phar://` disparan la deserialización igual. Amplía enormemente dónde aplica una LFI/traversal.

## Cómo falla

- **No hay cadena de gadgets** en la base de código — sin una clase abusable, la deserialización no lleva a nada.
- **PHP 8+** eliminó la deserialización automática de metadatos en varias rutas — reduce la superficie.
- **No puedo subir el phar** ni apuntar a uno controlado.
- Construir el phar y la cadena requiere `phpggc` y conocer el framework: es trabajo, no un one-liner.

## Coste

Alto: encontrar o generar la cadena de gadgets (con `phpggc` para frameworks conocidos) y subir el phar. Contra un framework popular con `phpggc` es directo; contra código custom, es research de gadgets.

## Huella esperada

- El archivo `.phar` (a menudo disfrazado de imagen) en disco.
- El acceso `phar://` en el [[Log de acceso del servidor web]].

Generación del phar: `phpggc Framework/Chain system id -p phar -o mal.phar`. Se sube por [[MOC - File upload]] y se dispara con la función de archivo vulnerable. Wrappers en [[LFI wrappers - matriz de referencia]].
