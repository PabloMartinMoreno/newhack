---
tipo: moc
dominio: transversal
aliases:
  - MOC ataques de contraseña
  - Ataques de contraseña
  - password attacks
tags:
  - dominio/post-explotacion
---

# MOC - Ataques de contraseña

> [!abstract] Dominio transversal
> Conseguir una contraseña por dos caminos opuestos: **adivinar contra un servicio vivo** (online) o **romper un hash capturado** (offline). No es una fase: el online vive en reconocimiento/explotación (acceso inicial) y el offline en post-explotación (tras un volcado). Es una vista que une lo que ya está disperso. Red puro.

## Árbol de decisión — ¿servicio o hash?

```
¿Qué tengo delante?
├─ Un servicio vivo que pide credencial  → ONLINE (ruidoso, con lockout y rate limit)
│  ├─ muchos usuarios, 1-2 contraseñas comunes → [[Autenticación - password spraying]]  ← evita lockout
│  ├─ credenciales filtradas de otra brecha     → [[Autenticación - credential stuffing]]
│  └─ 1 usuario, muchas contraseñas (brute)      → por servicio en [[MOC - Servicios de red]] · web en [[MOC - Autenticación]]
└─ Un hash o ticket capturado            → OFFLINE (sin límite, pero necesitás el hash y cómputo)
   └─ [[Cracking offline - matriz de referencia]]  ([[hashcat]] / [[john]])
```

**Online primero spraying, no brute.** Una contraseña contra muchos usuarios casi no dispara bloqueos; muchas contraseñas contra un usuario lo bloquea en minutos. El brute de un solo usuario es para cuando el lockout no existe o no importa.

## De dónde salen los hashes (offline)

El offline casi nunca empieza en esta nota: el hash llega de otro dominio. El mapa fuente → qué sale → cómo se rompe:

| Fuente | Qué sale | Modo | Dominio |
|---|---|---|---|
| Kerberoasting | TGS-REP (RC4) | `-m 13100` | [[MOC - AD roasting]] |
| AS-REP roasting | AS-REP | `-m 18200` | [[MOC - AD roasting]] |
| SAM / LSASS / NTDS | NTLM | `-m 1000` | [[MOC - AD volcado de credenciales]] |
| Responder / relay | NetNTLMv2 | `-m 5600` | [[Envenenamiento de resolución de nombres]] |
| `/etc/shadow` | sha512crypt `$6$` | `-m 1800` | [[Enumeración de privesc Linux - matriz de referencia]] |
| Secreto de JWT | HMAC | `-m 16500` | [[JWT - matriz de referencia]] |
| Archivos (ZIP/SSH/KeePass/Office) | según `*2john` | varios | loot local |

El detalle de cada modo y ataque, en [[Cracking offline - matriz de referencia]].

## Online vs offline — el criterio

- **Online** no necesita hash pero es **ruidoso y limitado**: lockout, rate limit, y cada intento es un log de autenticación fallida. Se elige spraying para no bloquear, y se cuida el ritmo.
- **Offline** no tiene límite de intentos —corrés hasta agotar la wordlist— pero exige **tener el hash** (un paso previo en otro dominio) y **poder de cómputo**. Un bcrypt o sha512crypt resiste fuerza bruta pura; ahí ganan wordlist curada + reglas.

## Cara roja

- **Online** (distribuido, no se duplica acá): [[Autenticación - password spraying]], [[Autenticación - credential stuffing]], [[Autenticación - enumeración de usuarios]]; brute por servicio en las matrices de [[MOC - Servicios de red]].
- **Offline**: [[Cracking offline - matriz de referencia]], con [[hashcat]] (GPU) y [[john]] (CPU, formatos raros y `*2john`).

## Relación con otras fases

- **Explotación / acceso inicial:** el online consigue la primera credencial contra un servicio expuesto.
- **Post-explotación:** el offline rompe lo que el volcado de credenciales ([[MOC - Post-explotación]]) y el roasting sacaron.

## Huecos conocidos

- [x] Offline (hashcat/john) con el mapa de fuentes; online enrutado a lo existente
- [ ] Fuerza bruta online **consolidada** (hydra/nxc/medusa/patator por protocolo) — hoy repartida en las matrices de servicio; decisión de dejarla así
- [ ] Generación de wordlists a medida (cewl, crunch, mutación por OSINT) sin nota propia
