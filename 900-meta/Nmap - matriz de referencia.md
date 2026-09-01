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
> Sintaxis y comandos. El criterio —qué sondeo elegir y por qué— está en [[MOC - Reconocimiento de red]]; qué manda cada sondeo y qué significa cada respuesta, en [[Sondeos de red - matriz de referencia]]; el porqué protocolar, en [[TCP - respuestas a segmentos inesperados]].
>
> Los ejemplos usan `10.10.10.0/24` y un dominio `corp.local` inventados, y las salidas van recortadas a lo que se lee. Nunca datos de un objetivo real: eso va al vault de engagements.

## 1. La escalera — los cuatro comandos que se corren de verdad

En este orden. Cada uno se apoya en la salida del anterior.

```sh
# 1. Qué existe (dentro del segmento; ARP, exacto, segundos)
nmap -sn -PR 10.10.10.0/24 -oA 1-vivos

# 2. Qué escucha, TODOS los puertos, sin identificar nada todavía
nmap -sS -p- --min-rate 2000 -Pn -n -oA 2-puertos 10.10.10.5

# 3. Identificar SOLO lo que apareció abierto
PUERTOS=$(grep -oP '\d+(?=/open)' 2-puertos.gnmap | sort -un | paste -sd,)
nmap -sS -sV -sC -p "$PUERTOS" -oA 3-servicios 10.10.10.5

# 4. La mitad que nadie mira
nmap -sU --top-ports 50 -Pn -oA 4-udp 10.10.10.5
```

**Por qué en dos pasos y no `-A -p-` de una:** identificar versión sobre 65535 puertos tarda horas y toca todo lo que hay. La pasada rápida es un `SYN` puro contra todo; la lenta es sólo contra la docena que abrió. Es la diferencia entre veinte minutos y una tarde.

`--min-rate 2000` es lo que acelera de verdad — más que `-T4`, que ajusta varias cosas a la vez y no fija el piso de paquetes por segundo.

## 2. Cómo leer la salida

Nmap imprime seis estados, no tres. Confundir los tres de en medio es el error de lectura más caro.

| Estado | Qué pasó | Qué hacer |
|---|---|---|
| `open` | Alguien contestó aceptando | Identificar servicio |
| `closed` | Llegó `RST`: el host existe, nadie escucha | El host está vivo — dato útil |
| `filtered` | Nada volvió, o volvió ICMP prohibido | Reintentar por otra vía, `--reason` |
| `unfiltered` | Llegó `RST` a un `-sA`: pasa el filtro, estado desconocido | Volver con `-sS` |
| `open\|filtered` | Silencio, y en este sondeo el silencio es ambiguo | Típico de UDP y de FIN/NULL/Xmas |
| `closed\|filtered` | Sólo del `-sI` (idle scan) | — |

`--reason` agrega por qué: `syn-ack`, `reset`, `no-response`, `admin-prohibited`, `host-unreach`. Distingue *filtrado porque nadie contestó* de *filtrado porque un firewall lo dijo*, y eso cambia la conclusión.

> [!example] El host que el descubrimiento dio por muerto
> `-sn` no devolvió nada para `10.10.10.7`, así que se insiste con `-Pn --reason`:
>
> ```
> $ nmap -Pn -p 22,80,443,445 --reason 10.10.10.7
>
> PORT    STATE    SERVICE  REASON
> 22/tcp  filtered ssh      no-response
> 80/tcp  filtered http     admin-prohibited from 10.10.10.1
> 443/tcp closed   https    reset ttl 63
> 445/tcp filtered microsoft-ds no-response
> ```
>
> Tres conclusiones que la tabla de estados sola no da:
>
> - **El host existe.** El `reset` del 443 salió de él, no de un intermediario. El descubrimiento se equivocó y `-Pn` era obligatorio.
> - **Hay un firewall en `10.10.10.1`** y se identificó solo: el `admin-prohibited` del 80 lleva la dirección de quien lo dijo.
> - **El 22 y el 445 no son lo mismo que el 80.** Silencio no es lo mismo que prohibición: pueden estar bloqueados en otro punto, o el host puede estar descartando. Vale reintentarlos con `--source-port 53` o desde otro origen.
>
> Sin `--reason` los tres `filtered` se leían igual y el `ttl 63` —un salto de router— tampoco aparecía.

## 3. Qué sondeo y contra qué

| Flag | Sondeo |
|---|---|
| `-sS` | `SYN`, medio abierto |
| `-sT` | `connect()` completo |
| `-sU` | UDP |
| `-sA` | `ACK` |
| `-sF` `-sN` `-sX` | `FIN`, sin banderas, Xmas |
| `-sI` | Idle scan, por host zombi |
| `-sn` | Sin escaneo de puertos |
| `-Pn` | Sin descubrimiento |
| `-6` | IPv6 |

Qué manda cada uno y qué significa cada respuesta: [[Sondeos de red - matriz de referencia]].

**`-sU` conviene con `-sV`.** Un datagrama vacío casi nunca obtiene respuesta; nmap trae cargas válidas por protocolo y las manda cuando reconoce el puerto, así que la identificación mejora mucho el resultado en vez de sólo agregarle detalle. Los puertos UDP que pagan están en [[Sondeos de red - matriz de referencia]] § 8.

| Flag | Qué hace |
|---|---|
| `-p-` | Los 65535 |
| `-p 1-1000` | Rango |
| `-p 22,80,443,3389` | Lista |
| `-p U:53,161,T:80,445` | UDP y TCP en una corrida |
| `--top-ports 1000` | Los más frecuentes |
| `--open` | Mostrar sólo los abiertos |
| `-iL objetivos.txt` | Desde archivo |
| `-iL <(...)` | Desde la salida de otro comando |
| `--exclude 10.0.0.1` | Excluir |
| `-n` | Sin DNS inversa — mucho más rápido |

Por defecto son **1000 puertos, no todos**: el falso negativo más común del dominio.

## 4. Descubrimiento

| Flag | Sondeo | Atraviesa |
|---|---|---|
| `-PR` | ARP | Todo, dentro del segmento |
| `-PS22,80,443` | `SYN` a esos puertos | Filtros que descartan ICMP |
| `-PA80` | `ACK` | Firewalls sin estado |
| `-PE` | Echo ICMP | Poco: es lo primero que se bloquea |
| `-PP` | Marca de tiempo ICMP | A veces, donde el echo no |
| `-PU40125` | UDP a un puerto improbable | Reglas que sólo miran TCP |

`-PR` es exacto y no lo filtra nadie: el firewall vive por encima de la capa de enlace. Fuera del segmento se combinan varios — basta que uno vuelva.

## 5. Identificación

| Flag | Qué hace | Ruido |
|---|---|---|
| `-sV` | Versión de servicio | Alto |
| `--version-intensity 0-9` | 0 = sólo banner, 9 = todas las sondas | Según el número |
| `-sC` | Igual a `--script=default` | Alto |
| `-O` | Sistema operativo | Medio |
| `--osscan-guess` | Adivinar cuando no está seguro | Medio |
| `-A` | `-sV -O -sC --traceroute` | **El máximo** |
| `--reason` | Por qué clasificó así cada puerto | Ninguno |

`-A` es lo más ruidoso que se puede escribir en una sola letra. `--reason` no manda un paquete de más: sólo imprime lo que ya sabía.

## 6. Temporización y evasión

| Flag | Efecto |
|---|---|
| `-T0`…`-T5` | De paranoico a insensato. `-T4` es el uso normal |
| `--min-rate 2000` | Piso de paquetes por segundo — lo que acelera de verdad |
| `--max-rate 50` | Techo, para no tumbar nada |
| `--scan-delay 1s` | Espera entre sondeos |
| `--max-retries 1` | Menos reintentos: rápido, más falsos `filtered` |
| `--host-timeout 15m` | Abandonar un host que no termina |
| `-f` | Fragmentar el sondeo |
| `-D señuelo1,ME,señuelo2` | Señuelos: mezclar el origen real entre falsos |
| `-S dirección` | Origen falsificado (sin respuesta de vuelta) |
| `--source-port 53` | Origen 53: pasa filtros que confían en el puerto |
| `--data-length 25` | Cambiar el largo, romper firmas por tamaño |
| `--spoof-mac 0` | MAC aleatoria (sólo sirve dentro del segmento) |

En UDP la velocidad **corrompe el resultado**, no sólo hace ruido: la limitación de tasa de ICMP hace que los puertos cerrados dejen de contestar y empiecen a parecer abiertos.

Los señuelos no ocultan nada frente a una detección por agregación en el host que escanea: el proceso local sigue abriendo el mismo abanico. Ver [[Abanico de conexiones fallidas desde un host]].

## 7. NSE por servicio

Lo que paga, por puerto. `-sC` corre la categoría `default`, que ya cubre bastante de esto.

| Puerto | Scripts |
|---|---|
| 21 FTP | `ftp-anon` `ftp-syst` |
| 22 SSH | `ssh-auth-methods` `ssh2-enum-algos` `ssh-hostkey` |
| 25 SMTP | `smtp-commands` `smtp-enum-users` `smtp-open-relay` |
| 53 DNS | `dns-nsid` `dns-zone-transfer` `dns-recursion` |
| 88 Kerberos | `krb5-enum-users` |
| 111 RPC | `rpcinfo` `nfs-showmount` `nfs-ls` |
| 161 SNMP | `snmp-info` `snmp-interfaces` `snmp-win32-services` |
| 389 LDAP | `ldap-rootdse` `ldap-search` |
| 445 SMB | `smb-os-discovery` `smb-enum-shares` `smb-enum-users` `smb-security-mode` |
| 1433 MSSQL | `ms-sql-info` `ms-sql-empty-password` |
| 3306 MySQL | `mysql-info` `mysql-empty-password` `mysql-users` |
| 3389 RDP | `rdp-ntlm-info` `rdp-enum-encryption` |
| 5432 Postgres | `pgsql-brute` |
| 5985 WinRM | `http-title` |
| 6379 Redis | `redis-info` |
| 80/443 HTTP | `http-title` `http-headers` `http-methods` `http-enum` `http-robots.txt` |
| 443 TLS | `ssl-cert` `ssl-enum-ciphers` |

`ssl-cert` y `rdp-ntlm-info` son de los de mayor retorno del reconocimiento entero: regalan nombres de host internos, dominio de AD y nombre de la máquina sin autenticarse.

> [!example] Un puerto RDP que entrega el dominio entero
> ```
> $ nmap -p3389 --script rdp-ntlm-info 10.10.10.5
>
> PORT     STATE SERVICE
> 3389/tcp open  ms-wbt-server
> | rdp-ntlm-info:
> |   Target_Name: CORP
> |   NetBIOS_Domain_Name: CORP
> |   NetBIOS_Computer_Name: DC01
> |   DNS_Domain_Name: corp.local
> |   DNS_Computer_Name: DC01.corp.local
> |_  Product_Version: 10.0.17763
> ```
>
> Sin una credencial y sin tocar nada más: el nombre del dominio (`corp.local`), que la máquina es un controlador (`DC01`), y la versión de Windows (`10.0.17763` = Server 2019).
>
> Con eso ya se puede entrar a [[MOC - AD enumeración]] —hace falta el FQDN del dominio para casi todo— y a [[MOC - AD roasting]], que sólo necesita el dominio y una lista de usuarios para probar AS-REP.
>
> `ssl-cert` sobre el 443 de esa misma máquina suele confirmar lo mismo por otra vía, y a veces agrega nombres de otros hosts en el campo SAN.

```sh
nmap --script-help "smb-enum*"         # qué hace, antes de correrlo
nmap --script-updatedb                 # tras agregar scripts propios
nmap --script smb-enum-shares --script-args smbusername=u,smbpassword=p -p445 IP
```

Categorías, de menos a más agresiva:

| Categoría | Qué hace | En reconocimiento |
|---|---|---|
| `safe` | No altera nada ni tumba nada | Sí |
| `default` | Lo que corre `-sC` | Sí |
| `discovery` | Pregunta más al servicio | Sí |
| `version` | Auxiliares de `-sV` | Sí |
| `auth` | Credenciales por defecto, acceso anónimo | Con cuidado |
| `brute` | Fuerza bruta de credenciales | No, y bloquea cuentas |
| `intrusive` | Puede alterar o hacer caer el servicio | No |
| `vuln` | Comprueba vulnerabilidades conocidas | No |
| `exploit` | **Explota** | No |
| `dos` | Tumba el servicio a propósito | Nunca sin pedido escrito |

> [!warning] `vuln` y `exploit` no son reconocimiento
> Mandan cargas de explotación. Correrlos sin autorización explícita para explotar es salirse del alcance de un engagement de reconocimiento.

## 8. Salida y reanudación

| Flag | Qué da |
|---|---|
| `-oA base` | Los tres formatos a la vez |
| `-oN base.nmap` | Legible |
| `-oG base.gnmap` | Grepeable — el que se parsea |
| `-oX base.xml` | XML, para importar a otra herramienta |
| `--append-output` | No pisar lo anterior |
| `--resume base.nmap` | Retomar un escaneo cortado |
| `-v` / `-vv` | Resultados a medida que aparecen |
| `--packet-trace` | Cada paquete: por qué no sale nada |
| `-d` / `-dd` | Depuración del propio nmap |

`-oA` siempre: rehacer un escaneo largo porque se perdió la salida es el error caro evitable del dominio.

Extraer de la salida:

```sh
grep -oP '\d+(?=/open)' base.gnmap | sort -un | paste -sd,   # puertos abiertos, para -p
grep '/open' base.gnmap | cut -d' ' -f2                      # hosts con algo abierto
awk '/Up$/{print $2}' 1-vivos.gnmap > vivos.txt              # hosts vivos, para -iL
```

> [!example] Por qué anclar con `^` rompe el parseo
> Así se ve un gnmap por dentro — los puertos van **después** de `Ports:`, nunca al principio de línea:
>
> ```
> Host: 10.10.10.5 ()	Status: Up
> Host: 10.10.10.5 ()	Ports: 22/open/tcp//ssh///, 80/open/tcp//http///, 443/closed/tcp//https///, 445/open/tcp//microsoft-ds///
> Host: 10.10.10.9 ()	Status: Up
> ```
>
> ```sh
> $ grep -oP '^\d+(?=/open)' 2-puertos.gnmap | paste -sd,
>                                    # ← vacío, y sin error
>
> $ grep -oP '\d+(?=/open)' 2-puertos.gnmap | sort -un | paste -sd,
> 22,80,445
> ```
>
> El ancla no falla: devuelve nada. Parece que el escaneo no encontró puertos y se pierde la tarde reescaneando.
>
> `sort -un` importa cuando hay varios hosts en el mismo archivo: sin él los puertos repetidos se pasan repetidos a `-p`.

## 9. El XML a HTML legible

→ [[XML de escaneo a HTML]]

`xsltproc` y `lynx` convierten el `-oX` en un informe que se lee. Ahí viven también `--webxml`, `--stylesheet` y `--no-stylesheet`: son flags de nmap, pero sólo importan en el momento de convertir, y la conversión sirve igual para [[masscan]].

## 10. Qué hacer con lo que encontraste

`ssl-cert` en el 443 de un controlador de dominio suele dar el FQDN y el dominio: es la entrada más barata a [[MOC - AD enumeración]].

El enrutamiento completo de puerto abierto → dominio del vault no es de nmap —sirve igual si el puerto lo encontró [[masscan]] o un `for` en bash— y vive en [[Sondeos de red - matriz de referencia]] § 9.

## 11. Cuando nmap no alcanza

| Situación | Ir a |
|---|---|
| Rango enorme, /16 para arriba | [[masscan]] |
| Un host y quiero los abiertos ya | [[rustscan]] |
| No se puede subir un binario al host | [[Sondeos de red - matriz de referencia]] § sondeo sin herramienta |

Cada una tiene su nota con su sintaxis y su cuándo-no. Acá sólo el desvío.
