---
tipo: moc
dominio: ad
aliases:
  - MOC AD roasting
tags:
  - dominio/ad
---

# MOC - AD roasting

> [!abstract] Fase de la kill chain de AD
> Credenciales que se rompen **fuera de línea**, sin tocar la cuenta. Hub: [[MOC - Active Directory]]. Cheatsheet: [[AD roasting - matriz de referencia]]. Clases: [[T1558.004 - AS-REP Roasting]] · [[T1558.003 - Kerberoasting]].

Kerberos entrega material cifrado con la contraseña de una cuenta a quien lo pida. Si esa contraseña es débil, se rompe sin conexión y sin bloqueo.

## Árbol de decisión

```
¿Qué material puedo pedir?
├─ ¿Tengo credencial de dominio?
│  ├─ No  → ¿cuentas con preautenticación deshabilitada?
│  │        └─ Sí  → [[AS-REP roasting]]   ← no necesita credencial
│  └─ Sí  → ¿cuentas de servicio con SPN?
│           └─ Sí  → [[Kerberoasting]]
└─ Ya tengo el hash de una cuenta de servicio con SPN
   └─ falsificar su ticket directo  → silver ticket (matriz) → [[MOC - AD persistencia]]
```

Las dos rompen offline: **no hay nada que ver mientras se rompe**, la única ventana azul es el momento de pedir. AS-REP no necesita credencial; Kerberoast sí, pero devuelve cuentas de servicio, que suelen tener contraseñas viejas y privilegios altos.

## Orden de aprendizaje

1. [[AS-REP roasting]] — el caso sin credencial; preautenticación en cero
2. [[Kerberoasting]] — el caso con credencial; SPN y cifrado RC4

## Cara roja

- [[AS-REP roasting]] · [[Kerberoasting]]
- Comandos: [[AD roasting - matriz de referencia]] — pedir, formatos de hash, modos de hashcat, silver ticket como atajo.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[AS-REP roasting]] | [[Windows 4768 - Kerberos TGT requested\|4768]] | [[Solicitud de TGT sin preautenticación]] |
| [[Kerberoasting]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | [[Tickets de servicio con cifrado débil en volumen]] |

**Cuando el ataque es fuera de línea, se detecta la petición, no el ataque.** Ambas señales anclan en el pedido: preautenticación en cero (AS-REP) o cifrado RC4 y volumen anormal (Kerberoast).

## Huecos conocidos

- [x] Las dos variantes, con detección sobre el pedido
- [ ] Targeted Kerberoasting (escribir un SPN sobre una cuenta que se controla) — matriz, sin nota propia
