---
tipo: moc
dominio: fase
aliases:
  - Reconocimiento
  - Information gathering
tags:
  - fase
---

# MOC - Reconocimiento

> [!abstract] Fase del engagement
> Information gathering: mapear antes de tocar. Precede a [[MOC - Explotación]] y es la única fase que no explota nada — se leen las respuestas que el protocolo está obligado a dar. Enruta **por qué se reconoce**: la red, la superficie de la app, o el directorio.

## Adónde enruta

| Cuándo | Va a | Qué trae |
|---|---|---|
| Mapear la red (hosts, puertos, servicio) | [[MOC - Reconocimiento de red]] | descubrimiento, sondeos TCP/UDP, identificación de servicio |
| Ya con un servicio identificado | [[MOC - Servicios de red]] | puerto → protocolo → matriz de enumeración |
| Mapear una app web | [[MOC - Reconocimiento web]] | footprinting, subdominios, fingerprint, crawling, dorking |
| Enumerar el directorio (con credencial de dominio) | [[MOC - AD enumeración]] | usuarios, grupos, ACLs, SPNs, política |

Recon de red **encuentra** el servidor/DC (pre-superficie); recon web y AD **mapean** una vez ubicados. La teoría de por qué cada sondeo da lo que da, en [[MOC - Red]].

## Relación con otras fases
- **Después:** [[MOC - Explotación]] — lo que el recon devolvió decide qué se ataca y por dónde.

## Huecos conocidos

- [x] Enruta las tres caras del recon: red (pre-superficie), web y directorio.
- [ ] Reconocimiento pasivo profundo (certificate transparency, DNS histórico, OSINT) — hoy repartido en las matrices de web; sin dominio propio.
