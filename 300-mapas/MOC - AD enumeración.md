---
tipo: moc
dominio: ad
aliases:
  - MOC AD enumeración
tags:
  - dominio/ad
---

# MOC - AD enumeración

> [!abstract] Fase de la kill chain de AD
> El directorio es una base de datos legible. Hub: [[MOC - Active Directory]]. Cheatsheet: [[AD enumeración - matriz de referencia]]. Clase: [[T1087.002 - Domain Account Discovery]].

**Enumerar antes que explotar, siempre.** Todo lo demás se elige mirando lo que el directorio devolvió. La enumeración no es una fase que se hace y termina: se vuelve a ella después de cada credencial nueva.

## Árbol de decisión

```
¿Tengo credencial de dominio?
├─ No, solo red
│  ├─ usuarios por fuerza de Kerberos (sin bloqueo)  → kerbrute (matriz)
│  └─ null session / RID cycling en SMB              → enum4linux, rpcclient (matriz)
└─ Sí, una credencial cualquiera  → [[Enumeración LDAP del directorio]]   ← SIEMPRE PRIMERO
   ├─ ¿qué quiero encontrar?
   │  ├─ cuentas con SPN            → objetivo de [[MOC - AD roasting]] (Kerberoast)
   │  ├─ cuentas sin preautenticación → objetivo de [[MOC - AD roasting]] (AS-REP)
   │  ├─ máquinas con delegación    → objetivo de [[MOC - AD delegaciones]]
   │  ├─ PKI / plantillas           → certipy find → [[MOC - ADCS]]
   │  └─ confianzas del bosque      → [[MOC - AD confianzas]]
   └─ el grafo completo de permisos → BloodHound (matriz)
```

La enumeración **decide el resto del dominio**: cada rama de arriba es una consulta LDAP, y su resultado apunta a la fase siguiente. Por eso este MOC es el que más se relee.

## Orden de aprendizaje

1. [[Enumeración LDAP del directorio]] — el directorio como base de datos; la máscara de `userAccountControl`

## Cara roja

- [[Enumeración LDAP del directorio]]
- Comandos: [[AD enumeración - matriz de referencia]] — sin y con credencial, consultas LDAP puntuales, BloodHound, la máscara de bits de `userAccountControl`.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[Enumeración LDAP del directorio]] | [[Windows 4624 - Successful logon\|4624]] | punto ciego — tráfico legítimo (a propósito) |

La enumeración LDAP es el **punto ciego del dominio**: es indistinguible del uso legítimo. Se declara, no se esconde. Ver [[Ausencia de alertas no es ausencia de ataque]].

## Huecos conocidos

- [x] La consulta con credencial y la máscara de `userAccountControl`
- [ ] **Sin detección a propósito** — tráfico legítimo; el único ángulo azul es volumen anómalo de consultas, que necesita línea base y no tiene nota
- [ ] Enumeración sin credencial (kerbrute, RID cycling) vive en la matriz, sin nota de criterio propia
