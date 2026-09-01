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

Frente rápido de [[nmap]]. Barre los 65535 puertos en segundos y le pasa a nmap **sólo los que abrieron**, para que haga la identificación. No reemplaza nada: automatiza la escalera de dos pasadas de [[Nmap - matriz de referencia]] § 1, y agrega un motor de scripts que dispara herramientas propias por puerto.

Sintaxis completa en [[Rustscan - matriz de referencia]].

## Qué técnicas implementa

- [[Escaneo - sondeo SYN de puertos TCP]] en su pasada propia. Todo lo demás lo hereda de nmap.
- No hace descubrimiento: agrega `-Pn` al nmap que construye. Para eso, [[Escaneo - descubrimiento de hosts]].

## Cuándo NO usarla

Cuando la red es lenta o frágil. El lote por defecto son 4500 puertos en vuelo, y sobre un enlace con latencia eso devuelve **falsos cerrados** que no se distinguen de un resultado bueno. El mismo error aparece si el lote supera el `ulimit` del proceso.

Cuando hace falta control fino del sondeo —evasión, temporización, UDP con carga por protocolo—: ahí se escribe el nmap a mano y rustscan sólo agrega una capa que pisa parámetros.

Y cuando el objetivo está monitoreado: 4500 puertos simultáneos desde un origen es la firma más ruidosa del dominio después de [[masscan]]. Ver [[Abanico de conexiones fallidas desde un host]].

## Estado

Mantenida. Conveniencia, no capacidad: todo lo que hace se puede escribir con nmap y dos líneas de shell. Lo que sí es propio es el motor de scripts.

> [!tip] Por qué esta nota es corta
> El vault **no se organiza por herramienta**. El criterio vive en [[MOC - Reconocimiento de red]] y la sintaxis en su matriz; esta nota sólo mapea qué cubre rustscan y cuándo estorba.
