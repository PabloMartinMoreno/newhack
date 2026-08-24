---
tipo: moc
dominio: ad
aliases:
  - MOC ADCS
tags:
  - dominio/ad
---

# MOC - ADCS

> [!abstract] Fase de la kill chain de AD
> Active Directory Certificate Services: si la PKI está mal configurada, emite identidad. Hub: [[MOC - Active Directory]]. Cheatsheet: [[ADCS - matriz de referencia]]. Clase: [[T1649 - Steal or Forge Authentication Certificates]].

Un certificado autentica como su sujeto y **sobrevive al cambio de contraseña**. Por eso ADCS es a la vez vía de escalada y la peor persistencia. El abuso se clasifica por **dónde** está el fallo: la plantilla, la propia CA, o el objeto de plantilla.

## Árbol de decisión

```
certipy find → ¿dónde está el fallo?
├─ La plantilla deja poner el SAN (ESC1)
│  └─ pido un cert con el UPN de un admin  → [[ADCS - certificado con SAN arbitrario]]
├─ La plantilla está mal por EKU, agente o ACL (ESC2/3/4/13/15)
│  └─ [[ADCS - plantilla abusable por propósito o ACL]]
└─ La CA misma: bandera, ACL o relay (ESC6/7/8/11)
   └─ [[ADCS - abuso de la configuración de la CA]]
      └─ ESC8/11 son relay → parte de [[MOC - AD envenenamiento y relay]]
```

La decisión de fondo: **el certificado es el que sobrevive a la respuesta a incidentes** que rota credenciales y cierra el caso. Vale por años. Frente a un golden ticket (que muere al rotar `krbtgt` dos veces), el certificado es la persistencia más difícil de expulsar.

## Orden de aprendizaje

1. [[ADCS - certificado con SAN arbitrario]] — ESC1, el caso canónico: SAN arbitrario
2. [[ADCS - plantilla abusable por propósito o ACL]] — cuando el fallo está en la plantilla, no en el SAN
3. [[ADCS - abuso de la configuración de la CA]] — cuando el fallo está en la CA

## Cara roja

- [[ADCS - certificado con SAN arbitrario]] · [[ADCS - plantilla abusable por propósito o ACL]] · [[ADCS - abuso de la configuración de la CA]]
- Comandos: [[ADCS - matriz de referencia]] — el catálogo `ESC1`–`ESC15` con el comando de cada uno, THEFT, Shadow Credentials, `certipy`.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[ADCS - certificado con SAN arbitrario]] · emisión | [[Windows 4887 - Certificate Services issued\|4887]] | [[Certificado emitido con sujeto ajeno al solicitante]] |
| [[ADCS - certificado con SAN arbitrario]] · uso | [[Windows 4768 - Kerberos TGT requested\|4768]] | [[Autenticación por certificado a cuenta privilegiada]] |
| [[ADCS - plantilla abusable por propósito o ACL]] | [[Windows 4662 - Directory object operation\|4662]] | el uso — [[Autenticación por certificado a cuenta privilegiada]] |
| [[ADCS - abuso de la configuración de la CA]] | [[Windows 4624 - Successful logon\|4624]] | ESC8/11 — [[Autenticación NTLM donde el dominio usa Kerberos]] |

Detección en **dos fases**: la emisión (SAN ≠ solicitante, alta fidelidad, llega a tiempo) y el uso (PKINIT a cuenta privilegiada). Ambas necesitan la auditoría de AD CS encendida — el mismo punto ciego que el `4662` de DCSync.

## Huecos conocidos

- [x] Las tres familias de abuso (plantilla, plantilla-por-propósito, CA), con el catálogo `ESC1`–`ESC15` en la matriz
- [x] Detección de emisión y de uso
- [ ] La modificación de plantilla (ESC4/13) deja escritura en `4662` pero **sin detección dedicada** — el uso del cert lo ve la de PKINIT
