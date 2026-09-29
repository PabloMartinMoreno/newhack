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

Con el objetivo ya mapeado, la pregunta es qué munición dejar lista: qué shell vas a recibir, con qué payload, y qué exploit vas a lanzar.

## Adónde enruta

```
¿Qué estoy preparando?
├─ La sesión que voy a recibir
│  └─ [[MOC - Shells]]   ← reverse / bind / webshell, y el origen del payload (nativo vs generado)
└─ El binario/payload a entregar
   └─ [[msfvenom - matriz de referencia]]   ← formatos, staged/stageless, encoders, handler
```

- **Shells** — [[MOC - Shells]]: la dirección de la conexión (reverse/bind/webshell), la estabilización a TTY y el criterio one-liner nativo vs binario generado. Es el mismo MOC que opera [[MOC - Post-explotación]] una vez que la sesión está viva; acá se decide **cuál preparar**.
- **Payloads generados** — [[Payload generado con msfvenom]] y [[msfvenom - matriz de referencia]], con [[metasploit]] como entidad: cuándo un binario en vez de un one-liner, y cómo se fabrica.

## Relación con otras fases

- **Antes:** [[MOC - Reconocimiento]] — lo que devolvió el recon decide qué arsenal preparar (arquitectura, SO, egress).
- **Después:** [[MOC - Explotación]] entrega el payload; la sesión resultante se opera en [[MOC - Post-explotación]].

## Huecos conocidos

- [x] Shells (reverse/bind/webshell) y generación de payloads con msfvenom
- [ ] **Cross-compiling de exploits** — compilar código de exploit para la arquitectura/SO del objetivo, sin dominio propio
- [ ] **Búsqueda y adaptación de exploits** — searchsploit y ajustar un PoC público antes de lanzarlo
- [ ] **Preparación anti-AV del payload** — empaquetado/ofuscación real (más allá de los encoders de msfvenom, que no evaden EDR); sin escribir
