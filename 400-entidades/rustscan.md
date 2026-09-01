---
tipo: entidad
clase-entidad: herramienta
tecnicas: ["[[T1046 - Network Service Discovery]]"]
aliases: []
tags:
  - dominio/red
---

# rustscan

## Qué es

Frente rápido de [[nmap]]. Barre los 65535 puertos en segundos y **le pasa a nmap** sólo los que abrieron, para que haga la identificación. No reemplaza nada: automatiza la escalera de dos pasadas de [[Nmap - matriz de referencia]].

## Qué técnicas implementa

- [[Escaneo - sondeo SYN de puertos TCP]] en la pasada propia; todo lo demás lo hereda de nmap.

```sh
rustscan -a 10.10.10.5 -- -sV -sC        # lo que va después de -- es nmap
rustscan -a 10.10.10.0/24 -b 500 -t 2000 # lotes y timeout, para redes lentas
```

## Cuándo NO usarla

Cuando la red es frágil o lenta: el paralelismo por defecto satura enlaces chicos y devuelve falsos `filtered`. Se baja con `-b` y se sube el timeout con `-t`.

Cuando hace falta control fino del sondeo —evasión, temporización, UDP—: ahí se escribe el nmap a mano y rustscan sólo estorba.

## Estado

Mantenida. Conveniencia, no capacidad: todo lo que hace se puede escribir con nmap y dos líneas de shell.

> [!tip] Por qué esta nota es corta
> El vault **no se organiza por herramienta**. El criterio vive en [[MOC - Reconocimiento de red]].
