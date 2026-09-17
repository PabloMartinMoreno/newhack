---
tipo: meta
aliases:
  - Crawling - matriz
  - crawling cheatsheet
  - spidering - matriz
tags:
  - meta/referencia
  - dominio/red
---

# Crawling web - matriz de referencia

> [!info] Referencia pura, no un zettel
> Recorrer un sitio **siguiendo enlaces** para mapear URLs, endpoints, parámetros y archivos JS. Criterio de recon en [[MOC - Reconocimiento de red]].

> [!warning] Crawling ≠ content discovery
> El crawling encuentra lo que está **enlazado/referenciado** (sigue `href`, `src`, JS). El *content discovery* adivina rutas **no enlazadas** por fuerza bruta (`feroxbuster`, `ffuf` dir, `dirsearch`). Se complementan: lo oculto no se crawlea, lo enlazado no hace falta adivinarlo.

`HOST` es el objetivo.

## Crawlers activos

| Herramienta | Comando |
|---|---|
| katana | `katana -u https://HOST -d 5 -o urls.txt` |
| katana (con JS + headless) | `katana -u https://HOST -jc -headless` |
| hakrawler | `echo https://HOST \| hakrawler` |
| gospider | `gospider -s https://HOST -d 3` |

`katana` es el más completo: `-d` es la profundidad, `-jc` parsea JS, `-headless` renderiza SPAs, `-fs fqdn` limita el alcance al dominio.

## Pasivo (sin recorrer el sitio)

URLs que ya conocen terceros — no genera tráfico contra el objetivo.

| Fuente | Comando |
|---|---|
| gau | `gau HOST` |
| waybackurls | `echo HOST \| waybackurls` |
| robots.txt | `curl -s https://HOST/robots.txt` (rutas que pidieron **no** indexar) |
| sitemap | `curl -s https://HOST/sitemap.xml` |

`robots.txt` es oro barato: lista rutas que el dueño quiso esconder de los buscadores. La lista completa de rutas/archivos que conviene pedir a mano, en [[Archivos y rutas conocidas - matriz de referencia]].

## Extraer de JavaScript

Los JS suelen tener endpoints de API, rutas y a veces secretos.

| Herramienta | Comando |
|---|---|
| katana (JS crawl) | `katana -u https://HOST -jc` |
| LinkFinder | `linkfinder -i https://HOST -o cli` |
| getJS | `getJS --url https://HOST` |

## Descubrir parámetros

| Herramienta | Comando |
|---|---|
| arjun | `arjun -u https://HOST/pagina` |
| paramspider | `paramspider -d HOST` |
| x8 | `x8 -u https://HOST/pagina -w params.txt` |

## Aprovechar el resultado

```sh
cat urls.txt | unfurl -u domains | sort -u     # dominios/subdominios que aparecieron
cat urls.txt | grep '=' | qsreplace FUZZ       # URLs con parámetros, listas para fuzzear
cat urls.txt | nuclei -silent                  # pasar el mapa por plantillas
```

## Errores / notas

| Punto | Detalle |
|---|---|
| Sale del scope | limitar al dominio (`katana -fs fqdn`) para no crawlear terceros |
| SPA sin resultados | el contenido lo pinta JS → usar `-headless`/`-jc` |
| Ruido | los crawlers activos pegan muchas peticiones; el pasivo (gau/wayback) es cero ruido |
| Duplicados | consolidar con `sort -u`; muchas URLs son la misma con distinto query |
