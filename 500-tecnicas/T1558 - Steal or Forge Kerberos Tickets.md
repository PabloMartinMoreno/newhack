---
tipo: tecnica
taxonomia: attack
identificador: T1558
tacticas: [credential-access, privilege-escalation, lateral-movement]
aliases:
  - T1558
  - Kerberos delegation abuse
  - abuso de delegación
tags:
  - dominio/ad
---

# T1558 - Steal or Forge Kerberos Tickets

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Active Directory]]; las variantes de delegación en [[Delegación sin restricciones]], [[Delegación restringida]] y [[Delegación basada en recursos]]; los comandos en [[AD delegaciones - matriz de referencia]].

## Qué es

La técnica padre de la que cuelgan las sub-técnicas ya modeladas —[[T1558.001 - Golden Ticket]], [[T1558.003 - Kerberoasting]], [[T1558.004 - AS-REP Roasting]]— y el eje que faltaba: **el abuso de la delegación de Kerberos**. La delegación es una función legítima —un servicio actúa en nombre del usuario contra otro servicio— y su abuso produce tickets de impersonación sin robar ninguna contraseña.

## Por qué la delegación es un eje de escalada propio

Kerberos permite que un servicio, al que un usuario se autenticó, **reutilice esa identidad** para acceder a un tercer servicio en su nombre. Es lo que hace que un servidor web pueda consultar una base de datos como el usuario final. El problema es que quien controla un servicio con delegación —o quien puede configurarla— puede **impersonar a cualquiera**, incluido un administrador de dominio.

Las tres variantes son tres formas de conseguir esa impersonación, ordenadas por lo que hace falta:

- **Sin restricciones (unconstrained).** El servicio guarda el TGT completo de todo el que se autentica a él. Comprometerlo y forzar a un objetivo valioso a autenticarse captura su TGT.
- **Restringida (constrained).** El servicio puede delegar hacia SPNs específicos. Con `S4U2Self` y `S4U2Proxy` se impersona a cualquier usuario contra esos servicios.
- **Basada en recursos (RBCD).** El permiso lo controla el objeto de **destino**, no el de origen. Si se puede escribir un atributo en la máquina objetivo, se agrega una cuenta propia y se impersona a cualquiera contra ella.

## Por qué es distinto de forjar un ticket

Golden y silver ticket **forjan** un ticket con un secreto robado. La delegación no forja nada: **pide tickets legítimos** por los canales normales de Kerberos, abusando una configuración. Por eso deja una huella distinta —tickets `S4U` reales, no forjados— y por eso la detección es de configuración y de anomalía, no de firma criptográfica.

## Por qué importa más de lo que parece

La delegación se configura por comodidad y se olvida. Un servidor con delegación sin restricciones, o una cuenta con RBCD escribible por cualquiera, es una escalada a administrador de dominio que no depende de romper ninguna contraseña ni de una vulnerabilidad de software: es el diseño de Kerberos usado como estaba pensado, por quien no debía.

## Referencias canónicas

- [T1558](https://attack.mitre.org/techniques/T1558/)
- [T1134.001](https://attack.mitre.org/techniques/T1134/001/) — Token Impersonation, el efecto en Windows
- [T1098](https://attack.mitre.org/techniques/T1098/) — Account Manipulation, la escritura de RBCD
