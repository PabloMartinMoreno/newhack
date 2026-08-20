---
tipo: tradecraft
clase: "[[T1558 - Steal or Forge Kerberos Tickets]]"
eje: credencial
implementacion: "Escribir msDS-AllowedToActOnBehalfOfOtherIdentity en la máquina objetivo con una cuenta propia y usar S4U para impersonar a cualquiera contra ella"
opsec: ruidoso
telemetria: ["[[Windows 4662 - Directory object operation]]", "[[Windows 4769 - Kerberos service ticket requested]]"]
requisitos: [permiso-de-escritura-sobre-el-objeto-de-la-máquina-objetivo]
coste: bajo
alternativas: ["[[Delegación restringida]]", "[[Delegación sin restricciones]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - RBCD
  - resource-based constrained delegation
  - delegación basada en recursos
tags:
  - dominio/ad
---

# Delegación basada en recursos

## Cuándo lo elijo

Cuando tengo **permiso de escritura sobre el objeto de una máquina** —`GenericWrite`, `GenericAll`, `WriteProperty` sobre `msDS-AllowedToActOnBehalfOfOtherIdentity`, o soy dueño del objeto—. Es la delegación que más rinde en pentests modernos, porque el permiso lo controla el **destino** y esos permisos de escritura aparecen por todos lados en BloodHound.

La elijo cuando la enumeración muestra que puedo escribir sobre una máquina objetivo. A diferencia de las otras dos, no necesito una cuenta con delegación ya configurada: **la configuro yo**.

## Por qué funciona

RBCD invierte quién decide la delegación: en vez de un atributo en la cuenta de origen, es un atributo en la máquina de **destino** —`msDS-AllowedToActOnBehalfOfOtherIdentity`— que dice "estas cuentas pueden impersonar usuarios contra mí". Si puedo escribir ese atributo, agrego una cuenta que controlo, y desde ella hago la cadena `S4U` para impersonar a cualquiera contra esa máquina.

La cadena completa:

1. **Consigo una cuenta con SPN.** Cualquier usuario de dominio puede crear una cuenta de máquina —`ms-DS-MachineAccountQuota` es 10 por defecto—, y una cuenta de máquina tiene SPN. Si el cupo es cero, sirve una cuenta de servicio propia.
2. **Escribo el atributo** `msDS-AllowedToActOnBehalfOfOtherIdentity` de la máquina objetivo, poniendo el SID de mi cuenta.
3. **`S4U2Self` + `S4U2Proxy`** desde mi cuenta, impersonando a un administrador contra el objetivo —igual que [[Delegación restringida]], pero el permiso lo acabo de poner yo—.

El resultado es acceso como administrador a la máquina objetivo: `CIFS` para archivos, `HOST` para ejecución, `LDAP` si el objetivo es un DC. Los comandos —`addcomputer.py`, `rbcd.py`, Rubeus `s4u`, PowerView `Set-ADComputer`— están en [[AD delegaciones - matriz de referencia]].

Es el ataque que convierte un `GenericWrite` sobre una máquina —un permiso que parece menor— en control total de esa máquina.

## Cómo falla

Falla cuando no tengo permiso de escritura sobre el atributo de ninguna máquina objetivo. Es el prerrequisito, y BloodHound es lo que dice si existe y por qué camino.

Falla cuando `ms-DS-MachineAccountQuota` es cero **y** no controlo ninguna cuenta con SPN: sin una cuenta que ponga en el atributo, la cadena no arranca. Es una mitigación cada vez más común, y la salida es conseguir una cuenta de servicio existente.

Falla si el usuario a impersonar está en *Protected Users* o es sensible, igual que en la delegación restringida.

## Coste

Bajo. Con el permiso de escritura y una cuenta de máquina, la cadena entera son tres o cuatro comandos y termina en acceso administrativo al objetivo. Es de las escaladas de mejor relación coste/impacto de AD.

El costo está en conseguir el permiso de escritura, que sale de otra técnica —una ACL mal puesta que BloodHound encuentra, o el control previo de una cuenta con ese permiso—.

## Huella esperada

Ruidosa en un punto muy específico y detectable, que es lo que la hace la más "azul-amigable" de las tres:

- La **escritura del atributo** `msDS-AllowedToActOnBehalfOfOtherIdentity` es una modificación de un objeto del directorio, que deja [[Windows 4662 - Directory object operation]]. Es una firma de altísima fidelidad: ese atributo casi nunca se escribe legítimamente, y una escritura fuera del flujo de administración de una máquina es el ataque casi con certeza.
- La creación de la cuenta de máquina (`addcomputer`) deja un `4741` (creación de cuenta de equipo), y la cadena `S4U` posterior deja los mismos tickets `S4U` que [[Delegación restringida]] en [[Windows 4769 - Kerberos service ticket requested]].

A diferencia de las otras dos ramas, RBCD **tiene dos señales escribibles**: la escritura del atributo —[[Escritura del atributo de delegación RBCD]], sobre `4662`, análoga a la de DCSync— y el uso posterior de la cadena S4U —[[Impersonación por delegación S4U]], sobre el `4769`—. RBCD queda doblemente cubierta, la configuración y el uso; la delegación restringida comparte la segunda; la sin restricciones queda como hueco declarado en [[MOC - Active Directory]].
