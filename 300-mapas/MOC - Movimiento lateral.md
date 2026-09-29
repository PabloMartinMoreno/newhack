---
tipo: moc
dominio: fase
aliases:
  - MOC movimiento lateral
tags:
  - fase
---

# MOC - Movimiento lateral

> [!abstract] Fase del engagement
> Moverse de un host a otro con el material sacado en [[MOC - Post-explotación]]. Precede a [[MOC - Persistencia]]. Enruta **por el material que tengo** para autenticarme como otro.

> [!note] Hoy es casi todo Active Directory
> El movimiento lateral con contenido en el vault vive en AD. El árbol real —*qué material tengo*, con la lógica de NTLM contra Kerberos— está en [[MOC - AD movimiento lateral]] y no se reproduce acá. Lateral no-AD (reutilización de SSH, pivoting/túneles) entra cuando exista como dominio.

## Adónde enruta

| Cuándo | Va a | Qué trae |
|---|---|---|
| Tengo hash NTLM o ticket Kerberos | [[MOC - AD movimiento lateral]] | pass-the-hash / pass-the-ticket; NTLM contra Kerberos |
| Puedo actuar en nombre de otro (delegación) | [[MOC - AD delegaciones]] | sin restricciones, restringida, RBCD |

La cadena de AD entera, en [[MOC - Active Directory]].

## Relación con otras fases

- **Antes:** [[MOC - Post-explotación]] — el volcado de credenciales entrega el material para moverse.
- **Después:** [[MOC - Persistencia]] — asegurar el acceso una vez movido.

## Huecos conocidos

- [x] Enruta el movimiento lateral de AD (hash/ticket, delegaciones).
- [ ] **Lateral no-AD sin abrir**: reutilización de credenciales SSH, pivoting y túneles (SOCKS, port-forwarding). Cuando exista, esta fase deja de ser solo un router hacia AD y gana árbol propio.
