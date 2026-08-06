---
tipo: tradecraft
clase: "[[CWE-98 - File Inclusion]]"
eje: tipo
implementacion: "include/require de PHP sobre una ruta local controlada"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [ruta-local-controlable, include-o-require]
coste: bajo
alternativas: ["[[RFI - inclusión remota]]", "[[Path traversal - matriz de referencia]]"]
probado: 2026-08-06
contexto: [php8]
aliases:
  - LFI
  - local file inclusion
tags:
  - dominio/web
---

# LFI - inclusión local

## Cuándo lo elijo

Cuando la app pasa una ruta controlable a `include`/`require` (PHP) y solo puedo apuntar a archivos **locales** — `allow_url_include` está apagado, así que RFI no va. Es el caso más común de file inclusion en PHP moderno.

La diferencia con path traversal: traversal **lee** el archivo tal cual; LFI lo pasa a `include`, que **ejecuta** el PHP que contenga. Por eso un `.php` incluido no muestra su fuente (se ejecuta) y por eso la LFI escala a RCE.

## Por qué funciona

`include($_GET['page'])` corre el archivo como código PHP. Si controlo la ruta, puedo: leer archivos del sistema (con traversal), leer fuente sin ejecutar (con `php://filter`), o ejecutar código propio metiéndolo en un archivo que el server ya escribe y después incluyéndolo (poisoning).

## Cómo falla

- **Validación por lista blanca** de páginas — la mitigación correcta.
- **Filtro de `../`** — se combina con [[Path traversal - matriz de referencia]] § bypass.
- **Extensión forzada** (`include($p.'.php')`) — se evade con `php://filter` o, en PHP viejo, null byte.
- **`open_basedir`** que confina a un directorio.

## Coste

Bajo. Leer archivos es una petición. Escalar a RCE cuesta un poco más (encontrar un archivo envenenable), pero las vías son conocidas — ver [[LFI - de lectura a RCE]].

## Huella esperada

- `../`, `php://filter`, `/etc/passwd`, `/proc/self` legibles en el [[Log de acceso del servidor web]].
- Si se escala por log poisoning, el propio payload queda escrito en el log incluido — evidencia doble.

Payloads: [[Path traversal - matriz de referencia]] (leer), [[LFI wrappers - matriz de referencia]] (fuente y wrappers), [[LFI a RCE - matriz de referencia]] (escalar).
