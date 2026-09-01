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

Un host con todo `filtered` menos dos puertos `closed` **está vivo**, aunque el descubrimiento lo haya dado por muerto.

## 3. Tipos de sondeo

| Flag | Sondeo |
|---|---|
| `-sS` | `SYN`, medio abierto |
| `-sT` | `connect()` completo |
| `-sU` | UDP |
| `-sA` | `ACK` |
| `-sF` `-sN` `-sX` | `FIN`, sin banderas, Xmas |
| `-sn` | Sin escaneo de puertos |
| `-Pn` | Sin descubrimiento |
| `-6` | IPv6 |

## 4. Objetivos y puertos

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

## 5. Descubrimiento

| Flag | Sondeo | Atraviesa |
|---|---|---|
| `-PR` | ARP | Todo, dentro del segmento |
| `-PS22,80,443` | `SYN` a esos puertos | Filtros que descartan ICMP |
| `-PA80` | `ACK` | Firewalls sin estado |
| `-PE` | Echo ICMP | Poco: es lo primero que se bloquea |
| `-PP` | Marca de tiempo ICMP | A veces, donde el echo no |
| `-PU40125` | UDP a un puerto improbable | Reglas que sólo miran TCP |

`-PR` es exacto y no lo filtra nadie: el firewall vive por encima de la capa de enlace. Fuera del segmento se combinan varios — basta que uno vuelva.

## 6. Identificación

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

## 7. Temporización y evasión

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

## 8. NSE por servicio

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

## 9. Qué hacer con lo que encontraste

El enrutamiento de puerto abierto → dominio del vault no es de nmap: sirve igual si el puerto lo encontró [[masscan]] o un `for` en bash. Vive en [[Sondeos de red - matriz de referencia]] § 8.

Lo que sí es de nmap: `ssl-cert` en el 443 de un controlador de dominio suele dar el FQDN y el dominio, y es la entrada más barata a [[MOC - AD enumeración]].

## 10. Salida y reanudación

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

En gnmap los puertos **no** están al principio de línea —van después de `Ports:`—, así que anclar con `^` devuelve vacío en silencio. Es el error que hace parecer que el escaneo no encontró nada.

## 11. Cargas UDP por puerto

Un datagrama vacío casi nunca obtiene respuesta. Nmap manda una carga válida por protocolo cuando la conoce — por eso `-sV` sobre UDP mejora tanto el resultado.

Los que vale la pena barrer, en orden de retorno:

| Puerto | Servicio | Qué se saca |
|---|---|---|
| 161 | SNMP | Con `public`: interfaces, procesos, usuarios |
| 53 | DNS | Versión, recursión abierta, transferencia de zona |
| 137 | NetBIOS | Nombre de máquina y de dominio, sin credencial |
| 88 | Kerberos | Confirma controlador de dominio |
| 500 | IKE | VPN, y a veces modo agresivo |
| 623 | IPMI | Gestión fuera de banda; hashes sin autenticar |
| 69 | TFTP | Archivos sin autenticación |
| 123 | NTP | `monlist`: lista de pares que hablaron |
| 1900 | SSDP | Inventario de dispositivos de la red |

## 12. Cuando nmap no alcanza

| Situación | Ir a |
|---|---|
| Rango enorme, /16 para arriba | [[masscan]] |
| Un host y quiero los abiertos ya | [[rustscan]] |
| No se puede subir un binario al host | [[Sondeos de red - matriz de referencia]] § sondeo sin herramienta |

Cada una tiene su nota con su sintaxis y su cuándo-no. Acá sólo el desvío.
