---
tipo: meta
aliases:
  - Subdominios pasivo - matriz
  - passive subdomain enum
tags:
  - meta/referencia
  - dominio/red
---

# Enumeración pasiva de subdominios - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Pasiva = no se toca la infra del objetivo**: todo sale de fuentes de terceros (OSINT). Sin ruido, ideal para recon externo y bug bounty. El brute **activo** (que sí consulta al DNS del objetivo) vive en [[DNS - matriz de referencia]]. Criterio de recon en [[MOC - Reconocimiento de red]].

`dominio` es el objetivo (ej. `ejemplo.com`).

## Agregadores (una línea)

Cada uno consulta decenas de fuentes por vos.

| Herramienta | Comando |
|---|---|
| subfinder | `subfinder -d dominio -all -silent` |
| amass (pasivo) | `amass enum -passive -d dominio` |
| assetfinder | `assetfinder --subs-only dominio` |
| findomain | `findomain -t dominio -q` |

`subfinder -all` usa todas las fuentes configuradas; muchas requieren API key (abajo).

## Certificate Transparency

Los logs de certificados listan subdominios que sacaron un cert — fuente riquísima y sin tocar al objetivo.

| Fuente | Comando |
|---|---|
| crt.sh | `curl -s 'https://crt.sh/?q=%25.dominio&output=json' \| jq -r '.[].name_value' \| sort -u` |
| certspotter | `curl -s 'https://api.certspotter.com/v1/issuances?domain=dominio&include_subdomains=true&expand=dns_names' \| jq` |

El `%25` es `%` URL-encoded (comodín en crt.sh).

## Desde archivos y crawls históricos

| Herramienta | Comando |
|---|---|
| waybackurls | `echo dominio \| waybackurls \| unfurl -u domains \| sort -u` |
| gau | `gau --subs dominio \| unfurl -u domains \| sort -u` |

Sacan subdominios de URLs archivadas (Wayback, Common Crawl) — aparecen hosts que ya no están enlazados.

## Servicios y APIs

| Fuente | Cómo |
|---|---|
| Chaos (ProjectDiscovery) | `chaos -d dominio` (API key) |
| SecurityTrails · VirusTotal | por API o web (`virustotal.com/gui/domain/`); subfinder las integra |
| Shodan · Censys | `shodan domain dominio`; búsqueda por org/cert en Censys |
| domain.glass | `domain.glass` — intel de dominio (infra, tecnologías) en la web |

Adyacente (no subdominios, pero misma superficie externa): `buckets.grayhatwarfare.com/files` busca buckets S3/cloud públicos del objetivo.

## Buscadores y dorking

| Fuente | Cómo |
|---|---|
| Google | `site:*.dominio -www` |
| GitHub | buscar `dominio` en código: subdominios en configs y variables |

## De dominio a IPs (pivote pasivo)

`whois` da registrante, netblocks y contactos; resolver los subdominios y pasar cada IP por Shodan da servicios y puertos **sin escanear**.

| Tarea | Comando |
|---|---|
| WHOIS del dominio o IP | `whois dominio` · `whois <ip>` · `whois -h <server> <consulta>` |
| Resolver subdominios a IPs | `for s in $(cat subs.txt); do host $s \| grep "has address" \| cut -d" " -f4; done \| sort -u > ips.txt` |
| Servicios de cada IP (Shodan) | `for ip in $(cat ips.txt); do shodan host $ip; done` |

## Consolidar y validar

El paso final: unir todo, deduplicar y **resolver** para quedarse con lo que vive (esto ya es activo).

```sh
cat subs_*.txt | sort -u > all_subs.txt
dnsx -silent -l all_subs.txt        # cuáles resuelven
httpx -silent -l all_subs.txt       # cuáles tienen web viva
```

## API keys (más fuentes)

| Archivo | Para |
|---|---|
| `~/.config/subfinder/provider-config.yaml` | Keys de subfinder (SecurityTrails, VirusTotal, Censys, Shodan…) |
| `~/.config/amass/config.ini` (o `datasources.yaml`) | Keys de amass |

Sin keys funcionan igual, pero con menos fuentes: cargarlas multiplica los resultados.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| pocos resultados | sin API keys | cargar las keys de subfinder/amass |
| crt.sh vacío o timeout | el servicio se satura | reintentar, o usar certspotter |
| duplicados y wildcards | varias fuentes solapan; hay comodines DNS | `sort -u`, y filtrar wildcards al resolver con `dnsx` |
