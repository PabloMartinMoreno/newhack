---
tipo: meta
aliases:
  - Nmap - flags
  - nmap cheatsheet
  - NSE
tags:
  - meta/referencia
  - dominio/red
---

# Nmap - matriz de referencia

> [!info] Referencia pura, no un zettel
> Sintaxis. El criterio —qué sondeo elegir y por qué— está en [[MOC - Reconocimiento de red]]; el porqué protocolar, en [[TCP - respuestas a segmentos inesperados]].

## 1. Tipos de sondeo

| Flag | Sondeo | Privilegios | Cuándo |
|---|---|---|---|
| `-sS` | `SYN`, medio abierto | root | Caso base |
| `-sT` | `connect()` completo | ninguno | Sin privilegios; deja log en la app |
| `-sU` | UDP | root | Servicios que sólo viven en UDP |
| `-sA` | `ACK` | root | Mapear el firewall, no el puerto |
| `-sF` `-sN` `-sX` | `FIN`, sin banderas, Xmas | root | Sólo si la pila cumple el RFC |
| `-sn` | Sin escaneo de puertos | — | Sólo descubrimiento |
| `-Pn` | Sin descubrimiento | — | Tratar todo el rango como vivo |

`-sS` y `-sT` clasifican igual; la diferencia es el rastro. `-sA` no dice si el puerto está abierto: dice si el `RST` volvió.

## 2. Selección de objetivos y puertos

```
-p-                  los 65535
-p 1-1000            rango
-p 22,80,443,3389    lista
--top-ports 1000     los más frecuentes
-iL objetivos.txt    desde archivo
--exclude 10.0.0.1   excluir
```

Por defecto son **1000 puertos, no todos**: el falso negativo más común del dominio.

## 3. Descubrimiento

```
-PS22,80,443    SYN a esos puertos
-PA80           ACK
-PE             echo ICMP
-PP             marca de tiempo ICMP
-PR             ARP (por defecto dentro del segmento)
-n              sin resolución DNS inversa
```

`-PR` es exacto y no lo filtra nadie: el firewall vive por encima de la capa de enlace. Fuera del segmento, combinar varios sondeos — basta que uno vuelva.

## 4. Identificación

```
-sV                  versión de servicio
--version-intensity 0-9
-O                   sistema operativo
-A                   -sV -O --script=default --traceroute
--reason             por qué nmap clasificó así cada puerto
```

`--reason` es la opción más subestimada: distingue *filtrado porque no vino nada* de *filtrado porque vino un ICMP prohibido*, y eso cambia la conclusión.

`-A` es lo más ruidoso que se puede escribir en una sola letra.

## 5. Temporización y evasión

| Flag | Efecto |
|---|---|
| `-T0`…`-T5` | De paranoico a insensato. `-T4` es el uso normal |
| `--max-rate 50` | Tope de paquetes por segundo |
| `--scan-delay 1s` | Espera entre sondeos |
| `-f` | Fragmentar el sondeo |
| `-D señuelo1,ME,señuelo2` | Señuelos: mezclar el origen real entre falsos |
| `-S dirección` | Origen falsificado (sin respuesta de vuelta) |
| `--source-port 53` | Origen 53: pasa filtros que confían en el puerto |
| `--data-length 25` | Cambiar el largo, romper firmas por tamaño |

En UDP la velocidad **corrompe el resultado**, no sólo hace ruido: la limitación de tasa de ICMP hace que los puertos cerrados dejen de contestar y empiecen a parecer abiertos.

Los señuelos no ocultan nada frente a una detección por agregación en el host que escanea: el proceso local sigue abriendo el mismo abanico. Ver [[Abanico de conexiones fallidas desde un host]].

## 6. NSE

```
--script=default
--script=vuln
--script=smb-enum-shares --script-args=...
--script-help=smb-enum-shares
```

Categorías por orden de agresividad: `safe` · `default` · `discovery` · `intrusive` · `vuln` · `exploit` · `dos`.

`vuln` y `exploit` **no son reconocimiento**: mandan cargas de explotación. Correrlos sin autorización explícita para explotación es salirse del alcance de un engagement de reconocimiento.

## 7. Salida

```
-oA base        los tres formatos a la vez
-oN base.nmap   legible
-oG base.gnmap  grepeable
-oX base.xml    XML
--resume base.nmap
```

`-oA` siempre: rehacer un escaneo largo porque se perdió la salida es el error caro evitable del dominio.

## 8. Cargas UDP por puerto

Un datagrama vacío casi nunca obtiene respuesta. Nmap manda una carga válida por protocolo cuando la conoce — `-sV` sobre UDP mejora mucho el resultado justamente por eso. Los puertos que vale la pena barrer, en orden de retorno: `53` DNS · `161` SNMP · `137` NetBIOS · `88` Kerberos · `500` IKE · `69` TFTP · `123` NTP · `1900` SSDP · `623` IPMI.
