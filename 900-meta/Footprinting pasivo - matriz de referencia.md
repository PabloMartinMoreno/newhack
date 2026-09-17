---
tipo: meta
aliases:
  - Footprinting pasivo - matriz
  - OSINT infra - matriz
  - passive footprinting
tags:
  - meta/referencia
  - dominio/red
---

# Footprinting pasivo - matriz de referencia

> [!info] Referencia pura, no un zettel
> Recon **externo de una organización sin tocarla**: quién es dueño del dominio y de las IPs, qué rangos tiene, qué servicios expone y qué dejó público. Distinto de descubrir nombres, que es [[Enumeración pasiva de subdominios - matriz de referencia]] — se encadenan (subdominios → resolver → estas IPs). Criterio de recon en [[MOC - Reconocimiento de red]].

`dominio` y `<ip>` son marcadores.

## WHOIS

| Tarea | Comando |
|---|---|
| Registrante y NS del dominio | `whois dominio` |
| Dueño y netblock de una IP | `whois <ip>` (mirar `OrgName`, `NetRange`, `CIDR`) |
| Contra un servidor puntual | `whois -h <whois-server> <consulta>` |

`whois <ip>` da el rango que pertenece a la org — la base para saber qué más es suyo.

## ASN y rangos de la org

De la org a todos sus prefijos IP.

| Tarea | Comando |
|---|---|
| ASN a partir de una IP | `whois -h whois.cymru.com " -v <ip>"` |
| Rangos de un ASN | `amass intel -asn <ASN>` |
| ASNs de una organización | `amass intel -org "Nombre Empresa"` |
| Web | `bgp.he.net` (ASN, prefijos, peers) |

## Servicios expuestos (sin escanear)

Shodan y Censys ya tienen escaneada internet — se consulta, no se escanea.

| Tarea | Comando |
|---|---|
| Servicios/puertos de una IP | `shodan host <ip>` |
| Todo lo de una org | `shodan search 'org:"Nombre Empresa"'` |
| Por certificado | `shodan search 'ssl:"empresa.com"'` |
| Pivote desde subdominios | resolvés los subs a IPs y `for ip in $(cat ips.txt); do shodan host $ip; done` |

## Intel de dominio (web)

| Sitio | Qué da |
|---|---|
| `domain.glass` | Infra, tecnologías, relaciones del dominio |
| `virustotal.com/gui/domain/dominio` | Subdominios vistos, resoluciones, detecciones |
| `dnsdumpster.com` | Mapa DNS y hosts |

## Almacenamiento cloud expuesto

| Sitio | Qué da |
|---|---|
| `buckets.grayhatwarfare.com/files` | Buckets S3/Azure/GCS **públicos** por palabra clave (nombre de la org) |

Un bucket abierto es data expuesta directa — de los hallazgos de mayor retorno del recon externo.

## Errores / notas

| Punto | Detalle |
|---|---|
| WHOIS con privacidad | muchos dominios ocultan el registrante (GDPR/privacy) — el netblock de la IP sigue siendo útil |
| Shodan desactualizado | los datos son del último escaneo, no en vivo — puede haber cambios |
| Alcance | confirmá que los rangos/hosts encontrados están en scope antes de tocarlos |
