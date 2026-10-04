---
tipo: moc
dominio: fase
aliases:
  - MOC post-explotación
  - Post-explotación
tags:
  - fase
---

# MOC - Post-explotación

> [!abstract] Fase del engagement
> Ya hay ejecución en un host — ¿qué hago una vez adentro? Viene después de [[MOC - Explotación]] y precede a [[MOC - Movimiento lateral]]. La sesión en sí se prepara en [[MOC - Pre-explotación]] ([[MOC - Shells]]); esta fase es **operar el foothold**: estabilizar, enumerar, escalar privilegios, sacar credenciales y mover archivos.

El nodo raíz es una necesidad, no una técnica: afianzar el acceso y extraer del host lo que sirve para seguir. Antes de nada, preguntarse si el objetivo se cumple sin abrir sesión —enumerar y leer config se hace por el canal directo del RCE—.

## Adónde enruta

| Cuándo | Va a | Qué trae |
|---|---|---|
| Estabilizar y operar la sesión | [[MOC - Shells]] | TTY y operación (el cuál se decidió en [[MOC - Pre-explotación]]) |
| Enumerar y escalar privilegios | [[Enumeración de privesc Linux - matriz de referencia]] · Windows *(hueco)* | SUID, sudo, capabilities, cron, escribibles; en Windows tokens/servicios |
| Sacar credenciales del host | [[MOC - AD volcado de credenciales]] | LSASS, SAM, NTDS, DCSync |
| Romper lo capturado (hashes/tickets) | [[MOC - Ataques de contraseña]] | offline con hashcat/john; online spray/brute |
| Traer herramientas / sacar datos | [[MOC - Transferencia de archivos]] | ingress y exfiltración |

## Relación con otras fases

- **Antes:** [[MOC - Explotación]] da la ejecución; [[MOC - Pre-explotación]] preparó la sesión.
- **Después:** [[MOC - Movimiento lateral]] con las credenciales en mano; y [[MOC - Persistencia]].

## Huecos conocidos

- [x] Credenciales locales ([[MOC - AD volcado de credenciales]]) y transferencia ([[MOC - Transferencia de archivos]])
- [ ] **Escalada de privilegios local — el hueco más grande.** Linux (SUID/SGID, sudo, capabilities, cron, PATH hijacking, grupos privilegiados) y Windows (SeImpersonate/SeBackup y otros privilegios de token, servicios mal permisados, unquoted paths, DLL hijacking). Sin dominio propio todavía.
- [ ] **Enumeración local** (Linux/Windows) previa a la escalada — sin nota propia.
- [ ] **Evasión** (AMSI/CLM/UAC bypass, AV) — sin abrir; es lo que el ejemplo pone en la post-explotación de Windows.
