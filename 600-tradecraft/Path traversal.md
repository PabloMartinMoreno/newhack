---
tipo: tradecraft
clase: "[[CWE-98 - File Inclusion]]"
eje: tipo
implementacion: "Salir del directorio previsto con ../ para leer archivos arbitrarios"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [ruta-de-archivo-controlable, lectura-sin-include]
coste: bajo
alternativas: ["[[LFI - inclusión local]]"]
probado: 2026-08-06
contexto: [linux]
aliases:
  - directory traversal
  - path traversal
tags:
  - dominio/web
---

# Path traversal

## Cuándo lo elijo

Cuando la app usa mi input como ruta pero **lee** el archivo (`file_get_contents`, `readfile`, `fopen`, servir una descarga) en vez de incluirlo. No hay ejecución: es divulgación de archivos arbitrarios. Es CWE-22, el hermano de solo-lectura de [[LFI - inclusión local]].

También es el primer paso de LFI: la sintaxis de `../` y sus bypasses es la misma; lo que cambia es qué hace la app con la ruta.

## Por qué funciona

`../` sube un directorio. Encadenando suficientes, se sale del directorio previsto hasta la raíz y se baja a cualquier archivo (`/etc/passwd`, config de la app, claves). La app confiaba en que el input elegía entre archivos de un directorio; nunca restringió el `../`.

## Cómo falla

- **Normalización de la ruta** antes de usarla (`realpath` + verificación de prefijo) — la mitigación correcta.
- **Filtro de `../`** — se evade con encoding, anidado o path absoluto. Ver [[Path traversal - matriz de referencia]] § bypass.
- **`open_basedir` / chroot** que confina el acceso.
- **Extensión forzada** que impide leer lo que quiero (ahí, si es PHP, se pasa a LFI + `php://filter`).

## Coste

Bajo: una petición por archivo. El impacto depende de qué archivos son legibles — la config de la app con credenciales suele ser el premio, no `/etc/passwd`.

## Huella esperada

- `../`, `%2e%2e`, rutas absolutas y objetivos como `/etc/passwd` legibles en el [[Log de acceso del servidor web]].
- Series de peticiones con profundidad creciente de `../` — el sello del ataque.

Payloads y bypasses en [[Path traversal - matriz de referencia]].
