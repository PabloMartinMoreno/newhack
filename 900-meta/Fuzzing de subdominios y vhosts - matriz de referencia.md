---
tipo: meta
aliases:
  - Fuzzing subdominios y vhosts - matriz
  - vhost discovery - matriz
  - fuzzing subdominios
  - vhost fuzzing
tags:
  - meta/referencia
  - dominio/red
---

# Fuzzing de subdominios y vhosts - matriz de referencia

> [!info] Referencia pura, no un zettel
> Fuerza bruta de nombres con `ffuf`/`gobuster` — las mismas herramientas para dos cosas que **se confunden pero encuentran distinto**. La enum pasiva (OSINT) está en [[Enumeración pasiva de subdominios - matriz de referencia]]; las herramientas DNS-nativas (dnsenum, dnsrecon), en [[DNS - matriz de referencia]]. Criterio de recon en [[MOC - Reconocimiento de red]].

> [!warning] Subdominio ≠ vhost
> **Subdominio** = concepto de **DNS**: un nombre (`blog.ejemplo.com`) con registro que **resuelve a una IP** — puede apuntar a cualquier server. Está en el directorio público; cualquiera lo resuelve.
> **Vhost** = concepto del **servidor web**: una IP sirve varios sitios y elige cuál según la cabecera **`Host`** de la petición. Cada sitio es un vhost.
> Se solapan —un subdominio suele ser también vhost de esa IP—, pero son independientes: un subdominio puede apuntar a **otra** IP, y un **vhost puede no tener DNS** (interno, staging): el server lo sirve si mandás ese `Host`, pero no figura en el directorio público.
> Por eso las dos técnicas: el brute de subdominios pregunta *"¿qué nombres existen en DNS?"* (capa DNS); el fuzz de vhosts, *"¿qué sirve esta IP aunque no esté en DNS?"* (capa HTTP). Cada uno ve lo que el otro no.

`IP` es el objetivo; `dominio` el dominio base; `FUZZ` el marcador de la palabra.

## Fuzzing de subdominios (capa DNS)

Encuentra nombres que **resuelven**. Requiere que el `dominio` resuelva por tu resolutor (o `-r` apuntando al DNS del objetivo).

| Herramienta | Comando |
|---|---|
| ffuf | `ffuf -u https://FUZZ.dominio -w wordlist.txt` |
| gobuster | `gobuster dns -d dominio -w wordlist.txt --append-domain` |

Si el `dominio` es interno/lab (`.htb`), apuntá la resolución al DNS del objetivo: `ffuf ... ` con `/etc/hosts` o `gobuster dns -r NS`. Las herramientas DNS-nativas (dnsenum/dnsrecon/fierce) y el brute contra un `NS` puntual están en [[DNS - matriz de referencia]].

## Fuzzing de vhosts (capa HTTP)

Encuentra sitios servidos por la IP según el `Host`, tengan DNS o no.

1. **Baseline**: pedir con un `Host` inexistente y anotar el tamaño/estado por defecto.
2. **Fuzzear** el `Host` filtrando ese baseline. Lo que sobra son vhosts reales.

```sh
# baseline: qué devuelve ante un host que no existe
curl -s -H "Host: noexiste123.dominio" http://IP | wc -c
```

| Herramienta | Comando |
|---|---|
| ffuf | `ffuf -u http://IP -H "Host: FUZZ.dominio" -w wordlist.txt -fs <baseline>` |
| gobuster | `gobuster vhost -u http://IP -w wordlist.txt --append-domain` |
| wfuzz | `wfuzz -H "Host: FUZZ.dominio" --hw <baseline> -w wordlist.txt http://IP` |

El `-fs` (filter size) de ffuf es la clave: sin filtrar el baseline **todo matchea**. También `-fc` (código), `-fw` (palabras), `-fl` (líneas).

### HTTPS y SNI

| Caso | Comando |
|---|---|
| Sobre TLS | `ffuf -u https://IP -H "Host: FUZZ.dominio" -w wordlist.txt -fs <baseline>` |
| Puerto puntual | `-u http://IP:8080`, y `Host: FUZZ.dominio:8080` si el redirect lo exige |

En TLS puede importar el **SNI**: algunos servers responden según el SNI, no solo el `Host`. Si el fuzz por `Host` no rinde, probar con el nombre en el SNI.

## Confirmar y usar

Encontrado un nombre/vhost, mapearlo a la IP para navegarlo:

```sh
echo "IP vhost.dominio" | sudo tee -a /etc/hosts
curl -s http://vhost.dominio/
```

Wordlists: `/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt`, o listas de vhosts de SecLists.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| vhost: todo matchea (miles de hits) | no filtraste el baseline | agregar `-fs`/`-fw` con el tamaño por defecto |
| vhost: nada matchea | baseline dinámico (tamaño variable) | filtrar por palabras/líneas (`-fw`/`-fl`) |
| subdominio: `.htb` no resuelve | el fuzz de subdominios usa tu resolutor, que no conoce el lab | apuntar al DNS del objetivo (`-r NS`), o usar el fuzz de vhost |
| el vhost redirige a otro | el server responde `Location` por `Host` | seguir el redirect y ajustar el filtro |
| en 443 no cambia nada | el server enruta por SNI | poner el nombre en el SNI, no solo en el `Host` |
