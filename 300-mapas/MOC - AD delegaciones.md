---
tipo: moc
dominio: ad
aliases:
  - MOC AD delegaciones
tags:
  - dominio/ad
---

# MOC - AD delegaciones

> [!abstract] Fase de la kill chain de AD
> Kerberos permite que un servicio actúe en nombre de otro. Mal configurado, es escalada. Hub: [[MOC - Active Directory]]. Cheatsheet: [[AD delegaciones - matriz de referencia]]. Clase: [[T1558 - Steal or Forge Kerberos Tickets]].

Las tres variantes piden tickets **legítimos** —no forjan nada—, así que no hay firma criptográfica que las delate. Se distinguen por qué controla el atacante.

## Árbol de decisión

```
¿Qué controlo?
├─ Un host con delegación SIN restricciones (TRUSTED_FOR_DELEGATION)
│  └─ coacciono a un DC a autenticarse ahí, capturo su TGT  → [[Delegación sin restricciones]]
├─ Una cuenta con msDS-AllowedToDelegateTo (restringida)
│  └─ pido un ticket S4U a los servicios listados, impersonando a quien quiera  → [[Delegación restringida]]
└─ Escritura sobre el objeto de una máquina
   └─ escribo msDS-AllowedToActOnBehalfOfOtherIdentity + S4U  → [[Delegación basada en recursos]]   ← la que más rinde hoy
```

La decisión práctica: **RBCD es la más accesible** porque solo necesita escritura sobre una máquina —muy común en ACLs mal puestas—, mientras que sin restricciones necesita comprometer ya un host con esa bandera, y restringida una cuenta ya configurada para delegar.

## Orden de aprendizaje

1. [[Delegación sin restricciones]] — la más antigua: coacción + captura de TGT
2. [[Delegación restringida]] — S4U y la impersonación en el propio protocolo
3. [[Delegación basada en recursos]] — la escritura de atributo que la habilita

## Cara roja

- [[Delegación sin restricciones]] · [[Delegación restringida]] · [[Delegación basada en recursos]]
- Comandos: [[AD delegaciones - matriz de referencia]] — sin restricciones (coacción + captura de TGT), restringida (`S4U`), RBCD (escribir el atributo + `S4U`).

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[Delegación sin restricciones]] | [[Windows 4624 - Successful logon\|4624]] · [[Windows 4768 - Kerberos TGT requested\|4768]] | [[Cuenta de alto valor autenticándose a host con delegación]] |
| [[Delegación restringida]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | [[Impersonación por delegación S4U]] |
| [[Delegación basada en recursos]] | [[Windows 4662 - Directory object operation\|4662]] | [[Escritura del atributo de delegación RBCD]] |

**La delegación se detecta por configuración, no por firma, y solo una tiene señal escribible.** RBCD deja una escritura de atributo de altísima fidelidad —análoga a la de DCSync—. Las otras dos no escriben nada: su señal es la anomalía de relación (cuenta de alto valor a host con delegación, S4U con impersonación privilegiada), que necesita línea base.

## Huecos conocidos

- [x] Las tres variantes, cada una con su artefacto
- [x] RBCD cierra su ciclo rojo↔azul (escritura de `4662`)
- [ ] Sin restricciones y restringida quedan con detección declarada pero **dependiente de inventario** (listas de hosts con delegación × cuentas de alto valor), no de un campo del evento
