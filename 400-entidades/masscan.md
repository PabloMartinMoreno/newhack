---
tipo: entidad
clase-entidad: herramienta
tecnicas: ["[[T1046 - Network Service Discovery]]", "[[T1018 - Remote System Discovery]]"]
aliases: []
tags:
  - dominio/red
---

# masscan

## Qué es

Escáner de puertos asíncrono con pila TCP propia. No usa la del sistema operativo: arma y lee los paquetes por su cuenta, y por eso alcanza tasas que nmap no puede.

## Qué técnicas implementa

- [[Escaneo - sondeo SYN de puertos TCP]], y nada más. No identifica servicio ni versión.
- Descubrimiento sólo como efecto secundario: un host que contesta algo está vivo.

```sh
masscan -p1-65535 10.10.10.0/24 --rate 10000 -oL masscan.txt
masscan -p80,443 0.0.0.0/0 --excludefile excluir.txt --rate 100000
```

## Cuándo NO usarla

Cuando el rango es chico. Por debajo de una /24, [[nmap]] con `--min-rate` alto llega casi igual de rápido y encima identifica servicio en la misma pasada.

Cuando el resultado tiene que ser confiable sin revisar. A tasas altas **pierde puertos**: los paquetes se descartan en la cola y un puerto abierto aparece cerrado, sin que nada lo avise. La tasa es un compromiso entre tiempo y falsos negativos, no un acelerador gratis.

Y cuando importa el ruido: es lo más estruendoso del dominio. Diez mil paquetes por segundo desde un origen es la firma más obvia que existe — ver [[Abanico de conexiones fallidas desde un host]].

## Estado

Mantenida. El uso normal es de frente: masscan barre y **nmap relee** los puertos que encontró.

```sh
masscan -p1-65535 10.10.10.5 --rate 10000 -oL m.txt
nmap -sV -sC -p "$(awk '/^open/{print $4}' m.txt | paste -sd,)" 10.10.10.5
```

> [!tip] Por qué esta nota es corta
> El vault **no se organiza por herramienta**. El criterio vive en [[MOC - Reconocimiento de red]]; esta nota sólo mapea qué cubre masscan y cuándo estorba.
