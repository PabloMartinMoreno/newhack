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
> Information gathering: mapear antes de tocar. Es la fase que precede a [[MOC - Explotación]] y la única que no explota nada — se leen las respuestas que el protocolo está obligado a dar. Enruta **por qué se reconoce**: la red que encuentra los objetivos, la superficie de la app, o el directorio.

El nodo raíz es qué estás mapeando, y el segundo corte es pasivo vs activo — cuánto ruido metés y cuánto toca al objetivo.

## Árbol de decisión — ¿qué reconozco?
```
¿Qué estoy mapeando?
├─ La red — encontrar hosts, puertos, servicios (pre-superficie)
│  └─ [[MOC - Reconocimiento de red]]   ← lo que descubre la web y el AD antes de tener superficie
├─ Una aplicación web ya ubicada
│  └─ [[MOC - Reconocimiento web]]   ← footprinting, subdominios, fingerprint, crawling
└─ Active Directory (ya con una credencial de dominio)
   └─ [[MOC - AD enumeración]]   ← el directorio como base de datos; SIEMPRE primero con credencial
```
Recon de red y recon de superficie no son lo mismo: el de red **encuentra** el servidor web o el DC; el de superficie mapea la app o el directorio una vez ubicados. Por eso el de red es su propio dominio y los otros dos viven dentro de sus hubs.

## Adónde enruta
- **Red / infraestructura** — [[MOC - Reconocimiento de red]]: descubrimiento de hosts, sondeos TCP/UDP, identificación de servicio. La teoría de por qué cada sondeo da lo que da, en [[MOC - Red]]. Identificado el servicio, su enumeración por protocolo: [[MOC - Servicios de red]].
- **Superficie web** — [[MOC - Reconocimiento web]]: footprinting pasivo, subdominios, fingerprint del stack, crawling de rutas y parámetros.
- **Directorio (AD)** — [[MOC - AD enumeración]]: usuarios, grupos, ACLs, SPNs, la política. Es el mapa que decide toda la fase de explotación de AD.

`MOC - Explotación web` y `MOC - Active Directory` también aparecen en otras fases: son vistas de dominio, no contenedores exclusivos.

## Relación con otras fases
- **Después:** [[MOC - Explotación]] — lo que el recon devolvió decide qué se ataca y por dónde.

## Huecos conocidos

- [x] Enruta las tres caras del recon: red (pre-superficie), web y directorio.
- [ ] Reconocimiento pasivo profundo (certificate transparency, DNS histórico, OSINT) — hoy repartido en las matrices de web; sin dominio propio.
