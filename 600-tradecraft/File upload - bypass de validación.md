---
tipo: tradecraft
clase: "[[CWE-434 - Unrestricted File Upload]]"
eje: validacion-evadida
implementacion: "Evadir la capa de validación que rechaza el archivo peligroso"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Escritura de archivo en la raíz web]]", "[[Registro del WAF]]"]
requisitos: [funcion-de-subida, validacion-incompleta]
coste: bajo
alternativas: ["[[File upload + LFI]]"]
probado: 2026-08-06
contexto: [php8]
aliases:
  - upload bypass
  - file upload bypass
tags:
  - dominio/web
---

# File upload - bypass de validación

## Cuándo lo elijo

Cuando hay una función de subida y quiero meter un archivo ejecutable que la validación debería rechazar. El trabajo es identificar **qué capa** valida y evadir esa: extensión, `Content-Type`, magic bytes o contenido.

Método: subir una webshell `.php` cruda y leer el mensaje de error. El error dice qué capa la rechazó, y eso decide el bypass. Ver el árbol de [[MOC - File upload]].

## Por qué funciona

Cada señal que la app usa para decidir si un archivo es "seguro" la controla el cliente: la extensión es parte del nombre, el `Content-Type` es un header, los magic bytes son los primeros bytes del contenido. Ninguna prueba de verdad qué es el archivo. La validación robusta combina varias capas + renombrado + almacenamiento fuera del webroot; basta que falte una.

## Cómo falla

- **Lista blanca de extensiones estricta** + el server no ejecuta nada más — corta las vías de extensión; queda el combo con LFI.
- **Renombrado del archivo** a un nombre aleatorio — mata el path traversal en el nombre y hace difícil ubicarlo.
- **Almacenamiento fuera del webroot** y sin ejecución — no hay RCE directo; se pasa a [[File upload + LFI]].
- **Reprocesamiento de la imagen** (recompresión) que destruye el PHP embebido en un polyglot.

## Coste

Bajo: es prueba y error de bypasses conocidos, una petición cada uno. El costo aparece cuando la validación es multicapa y hay que combinar (extensión + magic bytes + Content-Type a la vez).

## Huella esperada

- El `POST` multipart con la extensión/nombre sospechoso en el [[Log de acceso del servidor web]].
- El archivo subido queda **en disco** — evidencia persistente que un defensor puede encontrar.

Payloads en [[File upload bypass - matriz de referencia]]. El payload que subís, en [[Webshells - matriz de referencia]].
