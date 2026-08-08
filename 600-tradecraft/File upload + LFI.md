---
tipo: tradecraft
clase: "[[CWE-434 - Unrestricted File Upload]]"
eje: impacto
implementacion: "Subir un archivo que no ejecuta y ejecutarlo vía LFI"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Escritura de archivo en la raíz web]]"]
requisitos: [subida-que-no-ejecuta, lfi-disponible]
coste: medio
alternativas: ["[[File upload - bypass de validación]]", "[[LFI - de lectura a RCE]]"]
probado: 2026-08-06
contexto: [php8]
aliases:
  - upload + LFI
  - combo LFI upload
tags:
  - dominio/web
---

# File upload + LFI

## Cuándo lo elijo

El combo: cuando **ninguna de las dos vulnerabilidades alcanza sola** pero juntas dan RCE.

- La subida acepta mi archivo con código, pero cae fuera del webroot o con una extensión que no se ejecuta → subir no basta.
- La LFI ejecuta lo que incluye, pero no encuentro un archivo envenenable confiable → la LFI sola se queda en lectura.

Se unen: **subo el archivo con la webshell** (aunque no ejecute donde cae) y lo **incluyo con LFI** apuntando a su ruta. La LFI lo ejecuta.

## Por qué funciona

`include` ejecuta cualquier archivo con PHP, sin importar su extensión ni dónde esté. Un `.jpg` con `<?php ... ?>` adentro es inofensivo servido como imagen, pero incluido por LFI ejecuta. La subida me da un archivo con contenido controlado y ruta conocida; la LFI me da la ejecución.

Variante sin escribir en el webroot: usar `zip://` o `phar://` sobre el archivo subido — ver [[LFI wrappers - matriz de referencia]].

## Cómo falla

- **No sé dónde cayó el archivo** — sin la ruta, no puedo incluirlo. A veces la respuesta de la subida la revela.
- **Renombrado aleatorio** que hace impredecible la ruta.
- **`open_basedir`** que impide que la LFI llegue al directorio de subidas.
- Cualquiera de las dos vulnerabilidades no está — el combo necesita las dos.

## Coste

Medio: hay que encadenar dos bugs y averiguar la ruta del archivo subido. Una vez alineado, la ejecución es directa.

## Huella esperada

- El `POST` de la subida **y** el `GET` de inclusión con la ruta al archivo subido, correlacionables en el [[Log de acceso del servidor web]].
- El archivo malicioso en el directorio de subidas — evidencia persistente.

Payloads: [[File upload bypass - matriz de referencia]] (subir), [[Webshells - matriz de referencia]] (el contenido), [[LFI wrappers - matriz de referencia]] (incluir con `zip://`/`phar://`).
