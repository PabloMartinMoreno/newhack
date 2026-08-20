---
tipo: tradecraft
clase: "[[T1558 - Steal or Forge Kerberos Tickets]]"
eje: credencial
implementacion: "Usar S4U2Self y S4U2Proxy desde una cuenta con delegación restringida para impersonar a cualquier usuario contra los SPNs permitidos"
opsec: limpio
telemetria: ["[[Windows 4769 - Kerberos service ticket requested]]"]
requisitos: [control-de-una-cuenta-con-delegación-restringida]
coste: bajo
alternativas: ["[[Delegación basada en recursos]]", "[[Delegación sin restricciones]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - constrained delegation
  - S4U2Proxy
  - delegación restringida
tags:
  - dominio/ad
---

# Delegación restringida

## Cuándo lo elijo

Cuando controlo una cuenta —de servicio o de máquina— que tiene **delegación restringida** configurada: el atributo `msDS-AllowedToDelegateTo` con una lista de SPNs. Se encuentra en la enumeración. La cuenta puede delegar hacia esos servicios, y yo controlo la cuenta, así que puedo impersonar a cualquiera contra ellos.

Es más sigilosa que la delegación sin restricciones porque no necesita coacción ni captura de memoria: se piden tickets legítimos. La elijo cuando ya tengo esa cuenta; si el permiso lo controla el destino, la rama es [[Delegación basada en recursos]].

## Por qué funciona

La delegación restringida viene con dos extensiones de Kerberos que son la clave del abuso:

- **`S4U2Self`** deja que la cuenta pida un ticket de servicio **para sí misma, en nombre de cualquier usuario** —sin que ese usuario haga nada—. Produce un ticket que dice "este usuario se autenticó a mí".
- **`S4U2Proxy`** toma ese ticket y pide, con él, un ticket hacia uno de los SPNs permitidos, **en nombre del usuario impersonado**.

La cadena impersona a un administrador de dominio contra el servicio permitido sin conocer su contraseña:

```
S4U2Self(admin) → ticket "admin→micuenta"
S4U2Proxy(ese ticket, SPN permitido) → ticket "admin→SPN"
```

El detalle que amplía el impacto: **el SPN se puede cambiar**. `S4U2Proxy` valida el nombre del servicio pero no la parte del servicio del SPN, así que un permiso para `TIME/dc` se puede reescribir a `CIFS/dc` o `LDAP/dc` —acceso a archivos o a DCSync— sobre el mismo host. Un solo SPN permitido abre todos los servicios de esa máquina.

Los comandos —Rubeus `s4u`, impacket `getST`— están en [[AD delegaciones - matriz de referencia]].

## Cómo falla

Falla cuando el usuario a impersonar está en *Protected Users* o marcado como "sensible, no puede delegarse": `S4U2Self` no devuelve un ticket reenviable para él, y `S4U2Proxy` lo rechaza.

Falla contra la variante de delegación restringida **sin transición de protocolo** (`msDS-AllowedToDelegateTo` sin `TRUSTED_TO_AUTH_FOR_DELEGATION`): ahí `S4U2Self` no produce un ticket reenviable a menos que el usuario se haya autenticado de verdad, lo que limita la impersonación arbitraria.

Y falla si no se controla una cuenta con delegación restringida: es el prerrequisito, y conseguirla puede ser el trabajo entero.

## Coste

Bajo, una vez que se tiene la cuenta. La cadena `S4U2Self`/`S4U2Proxy` son uno o dos comandos, y el resultado es un ticket de servicio usable de inmediato.

El costo está en conseguir la cuenta con delegación —su contraseña o su hash—, que suele venir de otra técnica: kerberoasting de la cuenta de servicio, volcado de credenciales, o control de una cuenta de máquina.

## Huella esperada

Limpia, y de ahí el `opsec: limpio`: son peticiones legítimas de Kerberos, no tickets forjados.

- La cadena deja tickets `S4U` en [[Windows 4769 - Kerberos service ticket requested]]. La firma específica es un `4769` donde el campo `Transited Services` no está vacío —señal de que hubo `S4U2Proxy`— y donde el usuario impersonado difiere de la cuenta que pide. No es un ticket anómalo por su cifrado como en kerberoasting; es anómalo por la **relación** entre quién pide y a nombre de quién.

Esa firma es de buena fidelidad si se instrumenta el campo de servicios de tránsito, y la implementa [[Impersonación por delegación S4U]]: ancla en el `4769` con `Transited Services` no vacío —la marca de S4U2Proxy— e impersonación de una cuenta privilegiada. Es distinta de [[Tickets de servicio con cifrado débil en volumen]], que consume el mismo `4769` pero busca cifrado débil. La delegación restringida cierra así su ciclo rojo↔azul; la sin restricciones sigue con detección declarada como hueco en [[MOC - Active Directory]].
