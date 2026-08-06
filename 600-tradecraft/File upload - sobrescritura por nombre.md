---
tipo: tradecraft
clase: "[[CWE-434 - Unrestricted File Upload]]"
eje: impacto
implementacion: "Path traversal en el nombre del archivo para elegir dónde cae o qué sobrescribe"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [nombre-de-archivo-no-sanitizado]
coste: bajo
alternativas: ["[[File upload + LFI]]"]
probado: 2026-08-06
contexto: [php8]
aliases:
  - upload path traversal
  - sobrescritura por upload
tags:
  - dominio/web
---

# File upload - sobrescritura por nombre

## Cuándo lo elijo

Cuando la validación del **contenido** es buena pero el **nombre** del archivo no se sanitiza. En vez de pelear con qué archivo subo, controlo **dónde cae** metiendo `../` en el nombre. Dos usos: mover un archivo ejecutable al webroot, o **sobrescribir** un archivo existente sensible.

Es el eje del nombre, ortogonal al bypass de validación de tipo. A veces es la única vía cuando el tipo está bien filtrado pero el destino no.

## Por qué funciona

Muchas apps validan el contenido/extensión pero guardan con el nombre original sin normalizarlo. `filename="../../../var/www/html/shell.php"` en el multipart hace que el archivo caiga donde yo diga. Sobrescribir objetivos como `.htaccess`, un `config`, o un script existente cambia el comportamiento del server o inyecta código en un archivo que ya se ejecuta.

## Cómo falla

- **Renombrado** a un nombre aleatorio generado por el server — mata la técnica de raíz.
- **Sanitización del nombre** (quita `../`, toma solo el basename).
- **Permisos**: el usuario del web server no puede escribir en el destino elegido.
- **`open_basedir`** que confina la escritura.

## Coste

Bajo: un solo `POST` con el nombre modificado. El impacto depende de qué se puede sobrescribir — un `.htaccess` para habilitar ejecución, o pisar un archivo del que después se abusa.

## Huella esperada

- El `POST` multipart con un `filename` que contiene `../` en el [[Log de acceso del servidor web]].
- Un archivo aparece **fuera** del directorio de subidas, o uno existente cambia de contenido/fecha — anomalía de integridad de archivos.

Payloads del nombre en [[File upload bypass - matriz de referencia]] § Nombre — path traversal.
