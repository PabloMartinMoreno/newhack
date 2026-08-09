---
tipo: tecnica
taxonomia: attack
identificador: T1649
tacticas: [credential-access, persistence]
aliases:
  - T1649
  - ADCS
  - abuso de certificados
tags:
  - dominio/ad
---

# T1649 - Steal or Forge Authentication Certificates

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Active Directory]]; la variante, en [[ADCS - certificado con SAN arbitrario]].

## Qué es

Obtener un certificado que sirve para autenticarse como otra cuenta, aprovechando cómo está configurada la autoridad de certificación del dominio.

## Por qué es tan grave

Por una propiedad que lo separa de todo lo demás: **un certificado no se invalida cambiando la contraseña**.

Todas las otras técnicas de credenciales de AD pierden efecto cuando la cuenta rota su contraseña. Un certificado de autenticación vale hasta su fecha de vencimiento —que suele ser de años— y solo se corta revocándolo explícitamente, cosa que hay que saber que hay que hacer.

Es la mejor persistencia del dominio: silenciosa, de larga duración, y sobrevive a la respuesta a incidentes que rota credenciales y da el caso por cerrado.

## Por qué funciona

Porque la autoridad de certificación emite lo que sus plantillas permiten, y las plantillas se configuran mal con facilidad.

El caso central: una plantilla que **permite al solicitante elegir a nombre de quién se emite el certificado**, y que además sirve para autenticarse. Cualquiera que pueda solicitarla pide un certificado a nombre de un administrador y se autentica con él. No hay nada roto: la plantilla dice que se puede.

Las demás variantes son parientes del mismo problema: permisos de inscripción demasiado abiertos, permisos de escritura sobre las plantillas, o sobre la autoridad misma.

Y en su forma más grave, robar la clave privada de la autoridad permite **firmar certificados propios** — el equivalente en certificados de [[T1558.001 - Golden Ticket]], con la misma consecuencia y la misma dificultad de recuperación.

## Por qué se descubre tarde

Porque la autoridad de certificación suele estar fuera del inventario mental de AD. Se instaló para el wifi o para la VPN, la administra otro equipo, y sus plantillas no se revisan nunca. Mientras tanto, es parte del sistema de autenticación del dominio.

## La mitigación real

Auditar las plantillas: cuáles permiten elegir el nombre del sujeto, cuáles sirven para autenticación, y quién puede solicitarlas. Exigir aprobación del administrador donde haga falta. Y tratar la autoridad de certificación con el mismo nivel de protección que un controlador de dominio, porque tiene el mismo poder.

## Referencias canónicas

- [T1649](https://attack.mitre.org/techniques/T1649/)
