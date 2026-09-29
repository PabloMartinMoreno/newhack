---
tipo: moc
dominio: fase
aliases:
  - MOC pre-explotación
  - Pre-explotación
  - Weaponización
tags:
  - fase
---

# MOC - Pre-explotación

> [!abstract] Fase del engagement
> Weaponización: **fabricar el arsenal antes de disparar**. Va entre [[MOC - Reconocimiento]] y [[MOC - Explotación]]. Todavía no hay ejecución en el objetivo — acá se prepara lo que la explotación va a entregar y lo que se va a operar una vez adentro. Es una vista, no un contenedor: los MOCs que llama existen por sí solos y aparecen también en otras fases.

## Adónde enruta

| Cuándo | Va a | Qué trae |
|---|---|---|
| Preparar la sesión que voy a recibir | [[MOC - Shells]] | reverse/bind/webshell, one-liner nativo vs generado |
| Fabricar el binario/payload | [[Payload generado con msfvenom]] · [[msfvenom - matriz de referencia]] | cuándo un binario, formatos, staged/stageless, handler |

Es el mismo [[MOC - Shells]] que opera [[MOC - Post-explotación]] con la sesión viva; acá se decide **cuál preparar**. La herramienta, en [[metasploit]].

## Relación con otras fases

- **Antes:** [[MOC - Reconocimiento]] — lo que devolvió el recon decide qué arsenal preparar (arquitectura, SO, egress).
- **Después:** [[MOC - Explotación]] entrega el payload; la sesión resultante se opera en [[MOC - Post-explotación]].

## Huecos conocidos

- [x] Shells (reverse/bind/webshell) y generación de payloads con msfvenom
- [ ] **Cross-compiling de exploits** — compilar código de exploit para la arquitectura/SO del objetivo, sin dominio propio
- [ ] **Búsqueda y adaptación de exploits** — searchsploit y ajustar un PoC público antes de lanzarlo
- [ ] **Preparación anti-AV del payload** — empaquetado/ofuscación real (más allá de los encoders de msfvenom, que no evaden EDR); sin escribir
