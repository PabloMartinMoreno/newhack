---
tipo: meta
aliases:
  - Rustscan - flags
  - rustscan cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# Rustscan - matriz de referencia

> [!info] Referencia pura, no un zettel
> Sintaxis. Qué cubre la herramienta y cuándo estorba, en [[rustscan]]; el criterio de sondeo, en [[MOC - Reconocimiento de red]]; los flags de la segunda mitad, en [[Nmap - matriz de referencia]].
>
> Los ejemplos usan `10.10.10.5` de laboratorio.

## 1. Cómo se usa

Todo lo que va **después de `--`** es nmap. Rustscan barre, encuentra los abiertos y se los pasa.

```sh
rustscan -a 10.10.10.5 -- -sV -sC
```

> [!warning] Rustscan agrega `-Pn -vvv -p $PORTS` por su cuenta
> Se los mete al nmap que construye, siempre. Dos consecuencias: **nunca hace descubrimiento de host** —trata todo como vivo, que suele ser lo correcto—, y no tiene sentido escribir `-p` después de `--`, porque lo pisa con los puertos que encontró.

## 2. Objetivos y puertos

| Flag | Qué hace |
|---|---|
| `-a`, `--addresses` | IPs, hosts o CIDR separados por coma, o un archivo |
| `-p`, `--ports` | Lista: `80,443,8080` |
| `-r`, `--range` | Rango: `1-1000` |
| `--top` | Los 1000 más frecuentes |
| `-e`, `--exclude-ports` | Puertos a saltear |
| `-x`, `--exclude-addresses` | Hosts o CIDR a saltear |
| `--udp` | Modo UDP |
| `--resolver` | Resolutores DNS propios, por coma o archivo |
| `--scan-order` | `serial` (por defecto) o `random` |

Sin `-p`, `-r` ni `--top` barre **los 65535**. Es al revés que nmap, donde el default son 1000 — acá el default es el exhaustivo.

## 3. Velocidad y fiabilidad

Es la sección que importa: el modo de falla de rustscan es de ajuste, no de uso.

| Flag | Default | Qué controla |
|---|---|---|
| `-b`, `--batch-size` | 4500 | Puertos en vuelo a la vez |
| `-t`, `--timeout` | 1500 | Milisegundos antes de darlo por cerrado |
| `--tries` | 1 | Reintentos antes de darlo por cerrado |
| `-u`, `--ulimit` | — | Sube el límite de descriptores del proceso |

**El batch no puede superar el `ulimit`**, porque cada puerto en vuelo es un descriptor de archivo. Si lo supera, los sockets fallan al abrirse y esos puertos se reportan cerrados — sin error visible.

> [!example] Todo cerrado, y no era verdad
> ```
> $ ulimit -n
> 1024
>
> $ rustscan -a 10.10.10.5
> [!] File limit is lower than default batch size. Consider upping with --ulimit.
> Open 10.10.10.5:22
> ```
>
> Un solo puerto en una máquina que tiene cuatro. El aviso aparece, pero como el escaneo **termina bien y devuelve resultados**, es fácil leerlo como completo.
>
> ```sh
> rustscan -a 10.10.10.5 -u 5000 -b 4500     # subir el límite
> rustscan -a 10.10.10.5 -b 500 -t 2000      # o bajar el lote, en redes lentas
> ```
>
> La regla: `--batch-size` por debajo del `ulimit`, y si la red tiene latencia, lote chico y timeout largo antes que lo contrario. Un `-t` corto sobre un enlace lento devuelve **falsos cerrados**, que es el mismo error con otra causa.

## 4. Motor de scripts

| Valor de `--scripts` | Qué corre |
|---|---|
| `none` | Nada: sólo la lista de puertos |
| `default` | El nmap embebido: `nmap -vvv -p <puertos> -<4\|6> <ip>` |
| `custom` | Lo que declare `~/.rustscan_scripts.toml` |

Un script propio lleva su metadata en comentarios TOML en la cabecera:

| Campo | Para qué |
|---|---|
| `call_format` | Plantilla de ejecución con `{{script}}`, `{{ip}}`, `{{port}}` |
| `port` | Puerto que lo dispara |
| `ports_separator` | Carácter que une varios puertos (por defecto `,`) |
| `tags` | Categorías, para filtrar |
| `developer` | Autor |

Acepta Python, Lua y shell. Es la razón para usar rustscan por encima de un `nmap` a secas: dispara herramientas propias por puerto sin escribir el pegamento.

## 5. Configuración y salida

| Flag | Qué hace |
|---|---|
| `-c`, `--config-path` | Archivo de configuración propio |
| `--no-config` | Ignorar `~/.rustscan.toml` |
| `-g`, `--greppable` | Sólo `ip:puertos`, sin llamar a nmap |
| `--no-banner` | Sin el banner |
| `--accessible` | Sin lo que estorba a un lector de pantalla |

`-g` es el que sirve para encadenar:

```sh
rustscan -a 10.10.10.0/24 -g --no-banner | tee puertos.txt
```

> [!tip] El archivo de configuración es el que muerde
> `~/.rustscan.toml` se aplica **solo**, sin decir nada. Un `batch_size` viejo ahí adentro explica escaneos que dan distinto en dos máquinas con el mismo comando. Ante resultados raros: `--no-config` y volver a probar.
