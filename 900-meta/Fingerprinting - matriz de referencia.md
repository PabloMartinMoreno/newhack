---
tipo: meta
aliases:
  - Fingerprinting - matriz
  - fingerprinting cheatsheet
  - huella digital - matriz
tags:
  - meta/referencia
  - dominio/red
---

# Fingerprinting - matriz de referencia

> [!info] Referencia pura, no un zettel
> Identificar **qué corre y en qué versión** (SO, servidor web, framework, CMS, WAF) para mapearlo a CVEs y elegir el ataque. La versión de servicio por puerto vive en [[Nmap - matriz de referencia]] (`-sV`); acá va eso más el stack web y el resto. Criterio de recon en [[MOC - Reconocimiento de red]].

`HOST` es el objetivo.

## SO y servicios

| Tarea | Comando |
|---|---|
| Versión de servicios | `nmap -sV HOST` |
| Sistema operativo | `nmap -O HOST` (por TCP/IP stack) |
| Banner crudo | `nc -nv HOST PORT` · `curl -sI http://HOST` |
| Pasivo (por tráfico) | `p0f -i eth0` (SO de quien te habla, sin tocar) |


## Stack web

| Tarea | Comando |
|---|---|
| Tecnologías del sitio | `whatweb http://HOST` (subir ruido con `-a 3`) |
| En masa + título/server | `httpx -u HOST -td -title -server -status-code` |
| Cabeceras reveladoras | `curl -sI http://HOST` → `Server`, `X-Powered-By`, `X-AspNet-Version` |
| Navegador | extensión Wappalyzer |
| Solo fingerprint (nikto) | `nikto -h http://HOST -Tuning b` |
| Server + vulns conocidas (nikto completo) | `nikto -h http://HOST` |

`Server` y `X-Powered-By` son el fingerprint más barato; muchos los dejan puestos.

`nikto` completo va más allá del fingerprint: marca archivos peligrosos, software viejo y misconfigs — útil como primer barrido, pero **muy ruidoso** (cientos de peticiones). Para usarlo **solo como fingerprint**, `-Tuning b` limita al módulo de identificación de software (mucho menos ruido). Otros valores de `-Tuning`: `2` misconfig, `3` info disclosure, `x` para excluir.

## CMS

| CMS | Comando |
|---|---|
| WordPress | `wpscan --url http://HOST --enumerate` |
| Genérico | `cmseek -u http://HOST` |
| Drupal | `droopescan scan drupal -u http://HOST` |
| Joomla | `joomscan -u http://HOST` |


## WAF y TLS

| Tarea | Comando |
|---|---|
| Detectar WAF | `wafw00f http://HOST` |
| Fingerprint del stack TLS | `jarm HOST` |
| Cert (CN/SAN → nombres) | `curl -vI https://HOST` · `sslscan HOST` |
| Hash del favicon (pivote) | `curl -s https://HOST/favicon.ico \| ...mmh3...` → Shodan `http.favicon.hash:<hash>` |

El hash del favicon identifica la tecnología (paneles, productos) y, en Shodan, encuentra **todos** los hosts con el mismo favicon — pivote de infraestructura.

## De la versión al exploit

Con producto y versión, buscar el fallo conocido.

| Tarea | Comando |
|---|---|
| Buscar exploit local | `searchsploit <producto> <versión>` |
| Scripts de vuln (nmap) | `nmap -sV --script vuln -p PORT HOST` |


## Errores / notas

| Punto | Detalle |
|---|---|
| Banners falsificados | `Server` se puede cambiar/ocultar — contrastar con `whatweb`, comportamiento, `jarm` |
| `-sV`/`-O` son intrusivos | mandan sondas; en sigilo, preferir pasivo (banners, `p0f`, `whatweb` liviano) |
| `-O` necesita root y un puerto abierto y uno cerrado | si no, la detección de SO falla o es imprecisa |
| Versión oculta | inferir por rutas, errores, orden de cabeceras, o `jarm` |

