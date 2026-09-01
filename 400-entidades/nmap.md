---
tipo: entidad
clase-entidad: herramienta
tecnicas: ["[[T1046 - Network Service Discovery]]", "[[T1018 - Remote System Discovery]]"]
aliases: []
tags:
  - dominio/red
---

# nmap

## Qué es

Escáner de red: descubrimiento de hosts, estado de puertos TCP y UDP, identificación de servicio y versión, y un motor de scripts (NSE) que extiende todo eso hacia enumeración y comprobaciones de vulnerabilidad.

## Qué técnicas implementa

- Descubrimiento: [[Escaneo - descubrimiento de hosts]]
- Sondeos: [[Escaneo - sondeo SYN de puertos TCP]] · [[Escaneo - sondeo de puertos UDP]] · [[Escaneo - sondeos de bandera anómala]]
- Profundidad: [[Escaneo - identificación de servicio y versión]]
- Sintaxis completa en [[Nmap - matriz de referencia]].

## Cuándo NO usarla

Cuando el requisito es sigilo y el objetivo está monitoreado. Las cargas de `-sV` son fijas y firmadas, `-A` toca todo lo que puede tocar, y las categorías `vuln` y `exploit` de NSE mandan cargas de explotación — que además suelen quedar **fuera del alcance** de un engagement de reconocimiento.

Cuando ya se sabe qué se busca: sondear cinco puertos elegidos a mano no dispara la agregación que sí dispara un barrido, y es la diferencia entre pasar y no pasar por [[Abanico de conexiones fallidas desde un host]].

Y cuando no hay privilegios: sin *raw sockets* cae a `connect()`, que completa el handshake y puede quedar registrado por la aplicación. Conviene saberlo antes, no descubrirlo en el log del cliente.

## Estado

Mantenida y activa. Es el estándar de facto y lo que un informe da por sentado.

Alternativas por si el contexto la descarta: [[masscan]] · [[rustscan]] · el sondeo a mano de [[Sondeos de red - matriz de referencia]] § 7.

> [!tip] Por qué esta nota es corta
> El vault **no se organiza por herramienta**. El criterio vive en [[MOC - Reconocimiento de red]] y la sintaxis en la matriz; esta nota sólo mapea qué cubre nmap y cuándo estorba. Si nmap desaparece mañana, no se pierde nada más que este archivo.
