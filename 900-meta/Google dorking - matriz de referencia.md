---
tipo: meta
aliases:
  - Google dorking
  - dorks
  - Google hacking
  - GHDB
tags:
  - meta/referencia
  - dominio/red
---

# Google dorking - matriz de referencia

> [!info] Referencia pura, no un zettel
> Operadores de búsqueda para encontrar, **sin tocar el objetivo**, lo que quedó expuesto e indexado: archivos, paneles, config, fugas. Es recon pasivo/OSINT; el criterio de fase, en [[MOC - Reconocimiento web]] § recon pasivo. Hermanas: [[Footprinting pasivo - matriz de referencia]] (whois/ASN/shodan) y [[Enumeración pasiva de subdominios - matriz de referencia]] (CT/DNS). GitHub dorking y Shodan dorking son primos, sin nota propia todavía.

`objetivo.com` es el dominio de ejemplo. Sin datos de objetivo real — regla del vault. Los operadores valen igual en Bing/DuckDuckGo con sintaxis parecida.

## Operadores

| Operador | Qué hace | Ejemplo |
|---|---|---|
| `site:` | limita a un dominio o subdominios | `site:objetivo.com` · `site:*.objetivo.com` |
| `-site:` | excluye | `site:*.objetivo.com -site:www.objetivo.com` |
| `inurl:` | término en la URL | `inurl:admin` |
| `intitle:` | término en el `<title>` | `intitle:"index of"` |
| `intext:` | término en el cuerpo | `intext:"DB_PASSWORD"` |
| `filetype:` / `ext:` | por extensión | `filetype:pdf` · `ext:sql` |
| `cache:` | versión cacheada por Google | `cache:objetivo.com` |
| `"..."` | frase exacta | `"internal use only"` |
| `*` | comodín de palabra | `"password *"` |
| `OR` / `( )` | alternativa / agrupar | `(inurl:admin OR inurl:login)` |
| `AROUND(n)` | dos términos a ≤ n palabras | `usuario AROUND(3) contraseña` |

Se combinan: `site:objetivo.com filetype:env intext:"API_KEY"`.

## Dorks por objetivo

| Busco | Dork |
|---|---|
| Documentos filtrados | `site:objetivo.com filetype:pdf OR filetype:xlsx OR filetype:docx` |
| Config / secretos | `site:objetivo.com ext:env OR ext:conf OR ext:ini OR ext:yml` |
| Bases de datos / dumps | `site:objetivo.com ext:sql OR ext:bak OR ext:db` |
| Logs | `site:objetivo.com ext:log` |
| Listado de directorios | `site:objetivo.com intitle:"index of"` |
| Paneles de login | `site:objetivo.com (inurl:admin OR inurl:login OR intitle:"login")` |
| `.git` expuesto | `site:objetivo.com inurl:"/.git"` |
| Credenciales en texto | `site:objetivo.com intext:"password" filetype:txt` |
| Errores que filtran stack | `site:objetivo.com intext:"sql syntax near" OR intext:"Warning: mysql_"` |
| Subdominios indexados | `site:*.objetivo.com -www` |
| Tecnología concreta | `site:objetivo.com inurl:"/wp-content/"` · `intitle:"phpMyAdmin"` |
| Documentos con metadata | `site:objetivo.com filetype:pdf` → después `exiftool` para autores/rutas |

## Ejemplo — de dork a conclusión

`site:*.objetivo.com -site:www.objetivo.com`
Devuelve subdominios indexados que no son el principal. Cada host nuevo es superficie que el escaneo activo todavía no vio — se pasa a [[Fuzzing de subdominios y vhosts - matriz de referencia]] para completar, y a [[MOC - Servicios de red]] cuando se resuelvan a puertos.

`site:objetivo.com ext:env`
Un `.env` indexado suele traer `DB_PASSWORD`, `API_KEY`, `SECRET`. Si aparece, es acceso directo — y a la vez señal de que el deploy expone archivos que no debería.

## Google Hacking Database

El catálogo mantenido de dorks por categoría: [exploit-db.com/google-hacking-database](https://www.exploit-db.com/google-hacking-database). Se filtra por "Files Containing Passwords", "Sensitive Directories", "Web Server Detection", etc.

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| CAPTCHA / bloqueo tras varias | Google detecta automatización | espaciar, rotar, o usar la GHDB a mano |
| El dork no filtra nada | operador mal escrito (espacio tras `site:`) | pegar sin espacio: `site:objetivo.com`, no `site: objetivo.com` |
| Resultado viejo / caído | índice desactualizado | `cache:` para ver la copia, o Wayback |
| Un hallazgo "demasiado fácil" | posible honeypot / canary token | validar antes de reportar; abrirlo puede alertar al defensor |

> [!warning] Pasivo hasta que hacés clic
> Buscar no toca al objetivo; **abrir** un resultado sí lo toca y puede disparar un canary token. El sigilo del dorking termina en el momento en que visitás lo que encontraste.
