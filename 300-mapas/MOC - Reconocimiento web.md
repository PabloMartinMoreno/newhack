---
tipo: moc
dominio: web
aliases:
  - Reconocimiento web
  - recon web
tags:
  - dominio/web
---

# MOC - Reconocimiento web

> [!abstract] Mapear la superficie web antes de atacarla
> El reconocimiento **de la aplicación**, no de la red: qué activos hay, qué stack corre, qué rutas y parámetros expone. Es el paso previo a elegir familia de ataque en [[MOC - Explotación web]]. Lo que **encuentra** el servidor web en primer lugar —hosts, puertos— es pre-superficie y vive en [[MOC - Reconocimiento de red]].

Recon de red y recon de superficie no son lo mismo: el de red ubica el servidor; éste mapea la app una vez ubicada. El orden interno va de menos a más ruido: primero lo que no toca el objetivo, después lo que sí.

## Árbol de decisión — ¿qué tan ruidoso puedo ser?
```
¿Cuánto puedo tocar el objetivo?
├─ Nada (pasivo, sin un paquete al objetivo)
│  ├─ La organización y su huella  → [[Footprinting pasivo - matriz de referencia]]
│  └─ Activos por fuentes de terceros → [[Enumeración pasiva de subdominios - matriz de referencia]]
└─ Activo (mando peticiones)
   ├─ Descubrir más nombres         → [[Fuzzing de subdominios y vhosts - matriz de referencia]]
   ├─ Identificar el stack           → [[Fingerprinting - matriz de referencia]]
   └─ Mapear rutas y parámetros      → [[Crawling web - matriz de referencia]]
```
## Matrices

| Fase | Qué se saca | Matriz |
|---|---|---|
| Pasivo — organización | whois, ASN/netblocks, `shodan host`, buckets | [[Footprinting pasivo - matriz de referencia]] |
| Pasivo — activos | subdominios por certificate transparency, DNS histórico, archivos web | [[Enumeración pasiva de subdominios - matriz de referencia]] |
| Activo — más nombres | brute de subdominios (capa DNS) y vhosts (capa HTTP) con ffuf/gobuster | [[Fuzzing de subdominios y vhosts - matriz de referencia]] |
| Activo — stack | SO, servidor web, framework, CMS, WAF (versión → CVE) | [[Fingerprinting - matriz de referencia]] |
| Activo — mapeo | URLs, endpoints, JS, parámetros siguiendo enlaces | [[Crawling web - matriz de referencia]] |
| Activo — rutas a mano | checklist: robots, `.git`, `.env`, actuator, swagger, paneles | [[Rutas web sensibles - matriz de referencia]] |


## Relación con otras fases y dominios

- **Después:** [[MOC - Explotación web]] — con la app mapeada, elegir la familia por *dónde falla*.
- **Antes / al lado:** [[MOC - Reconocimiento de red]] encuentra el servidor; esto mapea la app. Ambas se llegan desde la fase [[MOC - Reconocimiento]].

## Huecos conocidos

- [x] Recon pasivo (organización y activos) y activo (subdominios/vhosts, fingerprint, crawling, rutas sensibles)
- [ ] Reconocimiento de APIs (esquema OpenAPI/GraphQL, versionado) sin matriz propia — hoy repartido entre crawling y las notas de GraphQL
