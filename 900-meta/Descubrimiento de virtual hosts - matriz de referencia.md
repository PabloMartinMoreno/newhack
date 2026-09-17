---
tipo: meta
aliases:
  - vhost discovery - matriz
  - virtual hosts - matriz
  - vhost fuzzing
tags:
  - meta/referencia
  - dominio/red
---

# Descubrimiento de virtual hosts - matriz de referencia

> [!info] Referencia pura, no un zettel
> Un servidor web sirve **varios sitios en una misma IP** y elige cuál por la cabecera `Host`. Descubrir vhosts = fuzzear ese `Host` contra la IP y ver qué responde distinto. **No confundir con el fuzzing de subdominios**: aquel trabaja en capa **DNS** (¿qué nombre resuelve?) y vive en [[DNS - matriz de referencia]]; esto trabaja en capa **HTTP** (¿qué sirve esta IP?). Un vhost puede **no tener registro DNS** (interno, staging) y por eso el brute de subdominios no lo ve — solo aparece forzando el `Host`. El mecanismo del `Host`, en [[MOC - Host header]]. Criterio de recon en [[MOC - Reconocimiento de red]].

`IP` es el objetivo; `dominio` el dominio base; `FUZZ` el marcador de la palabra.

## El método

1. **Baseline**: pedir con un `Host` inexistente y anotar el tamaño/estado de la respuesta por defecto.
2. **Fuzzear** el `Host` con una wordlist, **filtrando** ese baseline. Lo que sobra son vhosts reales.
```sh
# baseline: qué devuelve el server ante un host que no existe
curl -s -H "Host: noexiste123.dominio" http://IP | wc -c
```

## Fuzzear el Host

| Herramienta | Comando |
|---|---|
| ffuf | `ffuf -u http://IP -H "Host: FUZZ.dominio" -w wordlist.txt -fs <baseline>` |
| gobuster | `gobuster vhost -u http://IP -w wordlist.txt --append-domain` |
| wfuzz | `wfuzz -H "Host: FUZZ.dominio" --hw <baseline> -w wordlist.txt http://IP` |
| feroxbuster | `feroxbuster -u http://IP -H "Host: FUZZ.dominio" -w wordlist.txt` |

El `-fs` (filter size) de ffuf es la clave: sin filtrar el baseline, **todo matchea** (el server siempre responde algo). También sirven `-fc` (código), `-fw` (palabras), `-fl` (líneas).

## HTTPS y puerto no estándar

| Caso | Comando |
|---|---|
| Sobre TLS | `ffuf -u https://IP -H "Host: FUZZ.dominio" -w wordlist.txt -fs <baseline>` |
| Puerto puntual | `-u http://IP:8080` y `Host: FUZZ.dominio:8080` si el redirect lo exige |

En TLS puede importar el **SNI**: algunos servers responden según el SNI, no solo el `Host`. Si el fuzz por `Host` no rinde, probar con el nombre en el SNI.

## Confirmar y usar

Encontrado un vhost, mapearlo a la IP para navegarlo:
```sh
echo "IP vhost.dominio" | sudo tee -a /etc/hosts
curl -s http://vhost.dominio/    # o el navegador
```
Wordlists: `/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt`, o listas de vhosts de SecLists.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| Todo matchea (miles de "hits") | no filtraste el baseline | agregar `-fs`/`-fw` con el tamaño por defecto |
| Nada matchea | el baseline varía por respuesta (tamaño dinámico) | filtrar por palabras/líneas (`-fw`/`-fl`) en vez de tamaño |
| el vhost redirige a otro | el server responde con `Location` por `Host` | seguir el redirect y ajustar el filtro al nuevo tamaño |
| en 443 no cambia nada | el server enruta por SNI | poner el nombre en el SNI, no solo en el `Host` |

