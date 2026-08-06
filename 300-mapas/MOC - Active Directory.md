---
tipo: moc
dominio: ad
aliases:
  - MOC AD
tags:
  - dominio/ad
---

# MOC - Active Directory

Superficie: [[Active Directory]].

## Árbol de decisión — ¿qué tengo y qué quiero?

```
¿Qué credencial tengo?
├─ Ninguna (solo red)
│  ├─ ¿Hay LLMNR/NBT-NS/mDNS? → envenenamiento + relay
│  └─ ¿SMB signing off?       → relay NTLM
├─ Usuario sin privilegios
│  ├─ ¿Cuentas con SPN?          → [[T1558.003 - Kerberoasting]]
│  ├─ ¿Preauth deshabilitada?    → AS-REP roasting
│  └─ ¿ACLs abusables?           → cadenas de BloodHound
├─ Admin local en un host
│  └─ ¿Sesiones de otros?        → [[T1003.001 - LSASS Memory]]
└─ Admin de dominio
   └─ Persistencia → golden ticket · DCSync · AdminSDHolder
```

## Orden de aprendizaje

1. Modelo de autenticación: NTLM vs Kerberos — sin esto nada más se entiende
2. Estructura del directorio: objetos, atributos, ACLs, SPN
3. Enumeración autenticada y no autenticada
4. Credenciales: dónde viven en memoria y en disco
5. Movimiento lateral: qué autentica cada protocolo
6. Escalada por relaciones (ACLs, delegaciones)
7. Persistencia y dominio cruzado

## Cara azul

Cada rama del árbol debe terminar enlazando su artefacto en `550-telemetria/`: [[Sysmon EID 10 - ProcessAccess]], `4768/4769` de Kerberos, `4662` de acceso a objetos del directorio, `5145` de acceso a recursos compartidos.

## Estado

> [!note] Dominio semilla, sin desarrollar
> AD es un dominio **de infra** que arrancó como semilla para demostrar el ciclo rojo↔azul (LSASS). No es parte del sprint web ni está incompleto por descuido: está pendiente de desarrollo como esfuerzo propio, cuando se decida abrir infra.

Por desarrollar: delegaciones (constrained, unconstrained, RBCD) · ADCS (ESC1-ESC13) · telemetría de Kerberos (una nota por EID: `4768`/`4769`/`4662`/`5145`).
