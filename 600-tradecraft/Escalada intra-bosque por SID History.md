---
tipo: tradecraft
clase: "[[T1134.005 - SID-History Injection]]"
eje: persistencia
implementacion: "Forjar un ticket en un dominio comprometido con el SID de Enterprise Admins de la raíz inyectado, para controlar el bosque entero"
opsec: requiere-bypass
telemetria: ["[[Windows 4769 - Kerberos service ticket requested]]", "[[Windows 4624 - Successful logon]]"]
requisitos: [hash-de-krbtgt-de-cualquier-dominio-del-bosque]
coste: bajo
alternativas: ["[[Golden ticket]]", "[[Movimiento entre bosques por la clave de confianza]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - child to forest root
  - escalada al bosque
tags:
  - dominio/ad
---

# Escalada intra-bosque por SID History

## Cuándo lo elijo

Cuando ya tengo administrador de un dominio del bosque —concretamente su hash de `krbtgt`, por [[DCSync]]— y ese dominio **no es la raíz del bosque**. La escalada de un dominio hijo (o cualquier dominio) a la raíz es casi automática, y es el paso que convierte "administro un dominio" en "administro el bosque".

Se reconoce con la enumeración de confianzas: si hay una relación de bosque hacia una raíz, esta es la vía. Es la alternativa a [[Golden ticket]] cuando el golden es de un dominio no-raíz y se quiere alcanzar la raíz.

## Por qué funciona

Dentro de un bosque, el filtrado de SID está deshabilitado por defecto, así que un SID de otro dominio del bosque inyectado en un ticket se acepta como propio. La cadena:

1. Tengo el hash de `krbtgt` del dominio hijo (por [[DCSync]] en ese dominio).
2. Forjo un [[Golden ticket]] para ese dominio, pero le **inyecto en el SID History** el SID del grupo *Enterprise Admins* de la **raíz del bosque** —`S-1-5-21-<raíz>-519`—.
3. El ticket dice: usuario del hijo, pero miembro de Enterprise Admins de la raíz. Windows lo acepta por transitividad y sin filtrado.
4. Con ese ticket, DCSync contra la **raíz del bosque**, o acceso a cualquier recurso del bosque.

El SID `-519` es *Enterprise Admins*, el grupo con control del bosque entero. Inyectarlo es la escalada. El comando —`ticketer.py` con `-extra-sid`, o mimikatz `/sids:`— está en [[AD confianzas - matriz de referencia]].

Es la razón por la que **el límite de seguridad es el bosque, no el dominio**: no hace falta comprometer la raíz, alcanza con el dominio más débil y este salto. Un bosque con un dominio de laboratorio mal protegido es un bosque comprometido.

## Cómo falla

Falla cuando el **filtrado de SID está habilitado** en la confianza intra-bosque —posible en algunos modelos, aunque no es el defecto—: el SID inyectado de la raíz se descarta y la escalada no cruza.

Falla si no se tiene el hash de `krbtgt` del dominio de partida: sin él no hay golden ticket que forjar, y conseguirlo es [[DCSync]], que ya requiere admin de dominio. O sea, esta técnica **presupone** el compromiso de un dominio; es el paso de escalada, no de acceso inicial.

Y no aplica entre bosques distintos, donde el filtrado sí está activo por defecto — ahí la vía es [[Movimiento entre bosques por la clave de confianza]].

## Coste

Bajo. Con el hash de `krbtgt` del hijo y el SID de la raíz —que sale de la enumeración—, forjar el ticket con el SID extra es un comando, y el DCSync contra la raíz otro. Es de las escaladas de mejor relación coste/impacto de AD: de un dominio al bosque entero en dos pasos.

El costo está aguas arriba —comprometer el primer dominio— y en la enumeración de confianzas para saber que existe la relación y cuál es el SID de la raíz.

## Huella esperada

Requiere-bypass, porque hereda las señales del golden ticket más una propia:

- El ticket forjado deja las señales de [[Golden ticket]] en [[Windows 4769 - Kerberos service ticket requested]] —un ticket de servicio sin ticket inicial previo—, que cubre [[Ticket de servicio sin ticket inicial previo]].
- La señal propia es el **SID inyectado**: un ticket cuya cuenta lleva en el PAC un SID de *Enterprise Admins* de la raíz que no corresponde a su pertenencia real. Detectarlo exige inspeccionar el `SIDHistory`/PAC del ticket, o auditar el atributo `SIDHistory` de las cuentas —casi ninguna legítima lo tiene fuera de una migración—.

Ninguna detección ancla en el SID inyectado en el **ticket** —esta variante mete el SID en el PAC de un ticket forjado, no en el atributo, así que no toca el directorio y no deja firma de escritura—: la de golden ticket lo ve como un golden cualquiera. Es un límite de la técnica, no un hueco de contenido. La variante **de persistencia** —[[Persistencia por SID History]], que escribe el atributo— sí deja el evento `4765` y la cubre [[SID History agregado a una cuenta]]. Contra la escalada por ticket, la señal de mayor retorno sigue siendo auditar el atributo `SIDHistory` en reposo, que es lo que detecta la persistencia, no la escalada momentánea.
