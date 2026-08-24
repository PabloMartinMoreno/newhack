---
tipo: moc
dominio: ad
aliases:
  - MOC AD volcado de credenciales
tags:
  - dominio/ad
---

# MOC - AD volcado de credenciales

> [!abstract] Fase de la kill chain de AD
> Sacar credenciales de donde estén: memoria, disco, o el propio directorio. Hub: [[MOC - Active Directory]]. Cheatsheet: [[AD volcado de credenciales - matriz de referencia]]. Clases: [[T1003.001 - LSASS Memory]] · [[T1003.006 - DCSync]].

Dónde viven las credenciales decide cómo se sacan y qué privilegio hace falta. La distinción grande: **en un host** (admin local) contra **en el dominio** (derechos de replicación).

## Árbol de decisión

```
¿Qué acceso tengo, y qué credenciales quiero?
├─ Admin local en un host
│  ├─ sesiones de otros en memoria  → [[LSASS - volcado vía comsvcs.dll MiniDump]]
│  │   ├─ sale hash NTLM  → [[MOC - AD movimiento lateral]] (pass-the-hash)
│  │   └─ sale ticket     → [[MOC - AD movimiento lateral]] (pass-the-ticket)
│  ├─ hashes locales en disco       → SAM + LSA Secrets (matriz)
│  └─ secretos DPAPI del usuario    → matriz
└─ Admin de dominio (o derechos de replicación delegados)
   └─ los secretos de TODO el dominio, sin tocar un endpoint  → [[DCSync]]
      ├─ el hash de krbtgt   → [[MOC - AD persistencia]] (golden)
      └─ NTDS completo offline → matriz
```

La decisión clave: **DCSync no necesita ejecutar nada en un DC** —pide la replicación por protocolo—, así que evita el volcado de LSASS en el controlador. Pero requiere el privilegio de replicación, que ya es admin de dominio o una ACL abusable hacia él.

## Orden de aprendizaje

1. [[LSASS - volcado vía comsvcs.dll MiniDump]] — dónde viven las credenciales en memoria
2. [[DCSync]] — los secretos del dominio por protocolo, sin tocar el DC

## Cara roja

- [[LSASS - volcado vía comsvcs.dll MiniDump]] · [[DCSync]]
- Comandos: [[AD volcado de credenciales - matriz de referencia]] — LSASS, SAM, LSA Secrets, NTDS, DPAPI, y qué permite cada formato.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[LSASS - volcado vía comsvcs.dll MiniDump]] | [[Sysmon EID 10 - ProcessAccess\|Sysmon 10]] | [[Acceso a LSASS desde proceso no firmado]] |
| [[DCSync]] | [[Windows 4662 - Directory object operation\|4662]] | [[Replicación de directorio desde un origen no autorizado]] |

**La fidelidad más alta no deja rastro si la fuente no está bien configurada.** [[DCSync]] es de altísima fidelidad y **no emite nada** si la auditoría no está sobre el objeto raíz del dominio — el segundo paso que nadie hace. Ver [[Ausencia de alertas no es ausencia de ataque]].

## Huecos conocidos

- [x] LSASS en memoria y DCSync por replicación, ambos con detección
- [ ] SAM/LSA/NTDS/DPAPI viven en la matriz, sin nota de criterio propia
- [ ] El acceso a LSASS por otras vías (`nanodump`, direct syscalls) esquiva la firma de `Sysmon 10` — límite conocido de la detección
