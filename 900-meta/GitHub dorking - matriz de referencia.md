---
tipo: meta
aliases:
  - GitHub dorking
  - github dorks
  - secretos en git
tags:
  - meta/referencia
  - dominio/red
---

# GitHub dorking - matriz de referencia

> [!info] Referencia pura, no un zettel
> Buscar en repos públicos lo que un dev filtró: claves, credenciales, URLs internas, config. Recon pasivo/OSINT; el criterio de fase, en [[MOC - Reconocimiento web]] § recon pasivo. Hermana de [[Google dorking - matriz de referencia]] — la diferencia es el **corpus**: Google indexa lo servido por el sitio; GitHub trae **código fuente e historial de commits**, donde viven los secretos.

`objetivo` = nombre de la org; `objetivo.com` = su dominio. Sin datos de objetivo real — regla del vault. La búsqueda de código pide estar logueado (o token para la API).

> [!tip] El secreto vive en el historial, no solo en HEAD
> Un `git rm` del `.env` no lo borra: sigue en un commit anterior. La búsqueda web ve el código actual; **clonar y escanear todo el historial** (trufflehog, gitleaks) ve lo que se "borró". Los forks y gists tampoco se limpian.

## Qualifiers de búsqueda

| Qualifier | Acota a | Ejemplo |
|---|---|---|
| `org:` | repos de una organización | `org:objetivo` |
| `user:` | repos de un usuario (¡empleados!) | `user:un-dev-de-objetivo` |
| `repo:` | un repo puntual | `repo:objetivo/api` |
| `filename:` | por nombre de archivo | `filename:.env` |
| `path:` | por ruta | `path:.github/workflows` |
| `extension:` / `language:` | por extensión / lenguaje | `extension:sql` · `language:python` |
| `in:file` / `in:path` | dónde matchea el término | `AKIA in:file` |

Se combinan: `org:objetivo filename:.env DB_PASSWORD`.

## Dorks por objetivo

| Busco | Query |
|---|---|
| Archivo de entorno | `org:objetivo filename:.env` |
| Config con credenciales | `org:objetivo filename:config.php OR filename:settings.py` |
| Claves privadas | `org:objetivo "BEGIN RSA PRIVATE KEY"` · `filename:id_rsa` |
| Token de AWS | `org:objetivo AKIA` · `org:objetivo aws_secret_access_key` |
| Tokens genéricos | `org:objetivo authorization bearer` · `org:objetivo api_key` |
| Secretos de CI/CD | `org:objetivo path:.github/workflows secrets` · `filename:.npmrc _auth` · `filename:.dockercfg` |
| URLs/hosts internos | `"objetivo.com" internal` · `"vpn.objetivo.com"` |
| Dumps de base de datos | `org:objetivo extension:sql "INSERT INTO"` |
| Menciones fuera de la org | `"objetivo.com" password` (repos de terceros, no solo `org:`) |

## De la org a las personas

Los secretos más jugosos rara vez están en `org:objetivo`: están en el repo **personal** de un empleado que subió un proyecto con credenciales corporativas. El flujo: sacar nombres/handles por OSINT (LinkedIn, commits de la org, [[Footprinting pasivo - matriz de referencia]]), y repetir los dorks con `user:` sobre cada uno.

## Herramientas

Automatizan lo de arriba y **escanean el historial completo**, que la búsqueda web no cubre. Entran como entidades en `400-entidades/` (pendientes):

| Herramienta | Qué hace |
|---|---|
| trufflehog | clona y escanea todo el historial buscando secretos de alta entropía y patrones conocidos |
| gitleaks | ídem, con reglas por tipo de secreto; corre en CI |
| github-dorks / gitrob | corren un lote de dorks contra una org/usuario |
| git-dumper | reconstruye un repo desde un `.git` **expuesto en la web** (lo encuentra [[Google dorking - matriz de referencia]] o [[Rutas web sensibles - matriz de referencia]]) |

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| La búsqueda de código no devuelve nada | no estás logueado / falta scope | loguearse; para volumen, token en la API de búsqueda |
| Rate limit al automatizar | API sin token o límite bajo | token de acceso personal, y espaciar |
| Clave que no funciona | ya rotada, o de ejemplo (`AKIAEXAMPLE`) | validar contra el servicio antes de reportar |
| Match en un fork ajeno | el secreto es de otro proyecto | confirmar el dueño del repo antes de atribuir |

> [!warning] Pasivo, con el mismo límite que Google dorking
> Buscar no toca al objetivo, pero **usar** un secreto encontrado sí es actividad contra su infraestructura — y puede ser un canary token plantado. Validar con cuidado; ver el aviso de [[Google dorking - matriz de referencia]].
