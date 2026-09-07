---
tipo: meta
aliases:
  - DNS - matriz
  - dns cheatsheet
tags:
  - meta/referencia
  - dominio/red
---

# DNS - matriz de referencia

> [!info] Referencia pura, no un zettel
> **Puertos: 53/udp** (consultas) y **53/tcp** (respuestas grandes y **transferencia de zona**). Recon y enumeración de DNS. La teoría —cómo resuelve— en [[DNS - resolución recursiva]]; DNS como canal de exfil, en [[Exfiltración por canal encubierto]]. Criterio de recon en [[MOC - Reconocimiento de red]].

`dominio` y `NS` son marcadores (el dominio objetivo y su servidor de nombres).

> [!warning] `@NS` no es opcional en zonas internas
> `dig ... @10.129.14.128` pregunta **a ese server**; sin `@`, usás tu resolutor por defecto (`/etc/resolv.conf`). Una zona interna o de lab (`.htb`, dominios privados) **no existe en internet**, así que el resolutor por defecto devuelve `NXDOMAIN`. Para verla hay que preguntarle al server que la hostea: `@<IP-del-objetivo>`.

## Consultas básicas

| Tarea | dig | host | nslookup |
|---|---|---|---|
| Registro A | `dig A dominio` | `host dominio` | `nslookup dominio` |
| Tipo puntual | `dig MX dominio` | `host -t MX dominio` | `nslookup -type=MX dominio` |
| Todos (ANY) | `dig ANY dominio` | `host -a dominio` | `nslookup -type=ANY dominio` |
| Contra un server | `dig @1.1.1.1 dominio` | `host dominio 1.1.1.1` | `nslookup dominio 1.1.1.1` |
| Reverso (PTR) | `dig -x IP` | `host IP` | `nslookup IP` |
| Solo el dato | `dig +short dominio` | — | — |
| Versión del server (fingerprint) | `dig CH TXT version.bind @NS` | — | — |

La última es una consulta clase CHAOS: muchos BIND responden su versión, que orienta el resto.

Recon estándar de una, con `dnsrecon`: `dnsrecon -d dominio -n NS` recolecta registros (SOA/NS/MX/A/TXT/SRV) e intenta la transferencia de zona. Buen primer disparo antes de ir a lo puntual. (dnsrecon también hace AXFR y fuerza bruta — abajo.)

## Registros que importan

| Tipo | Qué da |
|---|---|
| `A` / `AAAA` | IPv4 / IPv6 del nombre |
| `NS` | Servidores de nombres del dominio — objetivos de la transferencia de zona |
| `MX` | Servidores de correo — superficie y nombres internos |
| `TXT` | SPF, DKIM, verificaciones — a veces filtran infra y software |
| `SOA` | Autoritativo primario y datos de la zona |
| `CNAME` | Alias — pista de subdominios y de takeover |
| `SRV` | Servicios: en AD, `_ldap._tcp.dc._msdcs.dominio` ubica los DC |
| `PTR` | Reverso IP→nombre |


## Transferencia de zona (AXFR)

El error jugoso: un `NS` que permite transferir la zona entera vuelca **todos** los registros.

| Herramienta | Comando |
|---|---|
| dig | `dig axfr @NS dominio` |
| host | `host -l dominio NS` |
| dnsrecon | `dnsrecon -d dominio -t axfr` |

Probá AXFR contra **cada `NS`** y contra las **zonas internas** que descubras (`dig axfr internal.dominio @NS`): la transferencia suele quedar mal cerrada justo en las zonas internas.


## Enumeración de subdominios

| Enfoque | Comando |
|---|---|
| Fuerza bruta (dnsenum) | `dnsenum --dnsserver NS --enum -p 0 -s 0 -f wordlist.txt -o out.txt dominio` |
| Fuerza bruta (fierce) | `fierce --domain dominio` |
| Fuerza bruta (dnsrecon) | `dnsrecon -d dominio -D wordlist.txt -t brt` |
| Fuerza bruta (gobuster) | `gobuster dns -d dominio -w wordlist.txt` |
| Pasivo (sin tocar el objetivo) | `subfinder -d dominio` · `amass enum -passive -d dominio` |

En `dnsenum`, `-p 0 -s 0` apagan el scraping de Google y el whois/reverse: queda fuerza bruta pura por wordlist, más rápida y sin tocar terceros.
La wordlist recomendada para la ocasión es: `/opt/useful/seclists/Discovery/DNS/subdomains-top1million-110000.txt`

Sin herramientas, solo con `dig` contra el server objetivo:
```sh
for s in $(cat wordlist.txt); do
  dig +short "$s.dominio" @NS | grep -q . && echo "$s.dominio"
done
```

## Configuración (con acceso al host)

| Archivo | Qué tiene |
|---|---|
| `/etc/bind/named.conf` · `named.conf.local` | Config de BIND: zonas, `allow-transfer`, recursión |
| Archivos de zona (`/var/lib/bind/`, `/etc/bind/db.*`) | Todos los registros de la zona — mapa interno |
| `/etc/resolv.conf` | Qué resolutor usa el host — pista de la infra interna |
| `/etc/hosts` | Resolución estática local, previa a DNS |


### Directivas peligrosas en `named.conf`

| Directiva | Por qué importa |
|---|---|
| `allow-transfer { any; }` | Cualquiera transfiere la zona entera (AXFR de arriba) → vuelca todos los registros |
| `allow-recursion { any; }` | Resolutor abierto: sirve recursión a cualquiera → amplificación DDoS y superficie de envenenamiento de caché |
| `allow-query { any; }` | Cualquiera consulta el server; sobre zonas internas, expone nombres que no debían salir |
| `recursion yes` (global, sin `allow-recursion`) | Recursión abierta por defecto — el mismo riesgo que `allow-recursion { any; }` |
| `zone-statistics yes` | Bajo riesgo: junta estadísticas por zona; solo filtran patrones de consulta si el `statistics-channels` está expuesto |

El par que más rinde en un pentest: `allow-transfer { any; }` (te da la zona completa) y `allow-recursion { any; }` (resolutor abierto).

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| AXFR: `Transfer failed` | el `NS` no permite transferencia (lo normal) | probar cada `NS`, o pasar a fuerza bruta |
| `connection timed out; no servers could be reached` | UDP 53 filtrado | `dig +tcp`, o probar otro resolutor |
| `NXDOMAIN` en todo | dominio o resolutor equivocado | `dig @<NS-autoritativo>` directo |
| respuesta trunca (`;; Truncated`) | pasó el límite de UDP | `dig +tcp` |

