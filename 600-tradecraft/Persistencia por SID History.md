---
tipo: tradecraft
clase: "[[T1134.005 - SID-History Injection]]"
eje: persistencia
implementacion: "Escribir el atributo SIDHistory de una cuenta controlada con el SID de un grupo privilegiado, para que sea miembro silencioso de ese grupo"
opsec: requiere-bypass
telemetria: ["[[Windows 4765 - SID History added]]"]
requisitos: [admin-de-dominio, acceso-a-la-base-del-directorio]
coste: bajo
alternativas: ["[[Escalada intra-bosque por SID History]]", "[[Golden ticket]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - SID history persistence
  - sIDHistory injection
tags:
  - dominio/ad
---

# Persistencia por SID History

## Cuándo lo elijo

Cuando ya tengo administrador de dominio y quiero **persistencia sigilosa**: una cuenta común que sea, a efectos de autorización, miembro de un grupo privilegiado, sin aparecer en ninguna lista de membresías. Se escribe el atributo `SIDHistory` de una cuenta que controlo con el SID de *Domain Admins* o *Enterprise Admins*.

Es la variante de **persistencia** de la inyección de SID History, distinta de la de **escalada** ([[Escalada intra-bosque por SID History]], que inyecta el SID en un ticket forjado y no toca el atributo). La elijo cuando quiero que el acceso sobreviva sin depender de forjar un ticket cada vez; si el objetivo es escalar del hijo a la raíz del bosque de una, aquella es más directa.

## Por qué funciona

Windows trata los SID del atributo `SIDHistory` **como propios a efectos de autorización** —para eso existe, para que una cuenta migrada conserve el acceso de sus grupos viejos—. Escribir ahí el SID de un grupo administrativo hace que la cuenta tenga ese acceso sin ser miembro nominal:

1. Con admin de dominio, escribir `SIDHistory` de una cuenta controlada con el SID de *Domain Admins* (`-512`) o *Enterprise Admins* (`-519`).
2. La cuenta ahora tiene los privilegios del grupo, pero **no aparece** al listar los miembros del grupo —`Get-ADGroupMember` no la muestra—.
3. El acceso persiste hasta que alguien audite el atributo `SIDHistory`, que casi nadie hace.

Es más sigilosa que agregar la cuenta al grupo —que sí sale en la lista de membresías y en la primera revisión— y que el golden ticket —que hay que forjar cada vez—. La escritura se hace con `mimikatz sid::add`, `DSInternals Add-ADDBSidHistory`, o directamente sobre la base del directorio. Los comandos están en [[AD confianzas - matriz de referencia]].

Requiere admin de dominio para escribir el atributo, así que —como el golden ticket— es persistencia **después** del compromiso, no una vía de acceso. Su valor es sobrevivir a la respuesta: una cuenta con SID History privilegiado reabre el dominio después de que se rotaron credenciales y se cerró el incidente.

## Cómo falla

Falla contra la auditoría del atributo `SIDHistory`: una revisión que busque cuentas con `SIDHistory` poblado fuera de una migración lo encuentra —es la mitigación de fondo, y la que hay que recomendar—.

Falla cuando el filtrado de SID en las confianzas descarta el SID inyectado en el contexto donde se lo usa, aunque dentro del propio dominio no aplica.

Y presupone el compromiso del dominio: es persistencia, no escalada. Sin admin de dominio no se puede escribir el atributo.

## Coste

Bajo. La escritura es un comando. El valor no es el costo sino la **sigilosidad y la duración**: sobrevive a la rotación de contraseñas, no aparece en las membresías, y no hay que hacer nada recurrente. Es de las persistencias más limpias de AD, comparable al certificado de ADCS pero sin depender de la PKI.

El costo real es el prerrequisito —admin de dominio— y la disciplina de no dejarla en una cuenta obvia.

## Huella esperada

Requiere-bypass, con una señal de escritura de alta fidelidad y una de uso más difusa:

- La **escritura del atributo** deja [[Windows 4765 - SID History added]] —el evento de "SID History agregado"—, con el SID agregado en el campo `SourceSid`. Un SID de un grupo administrativo agregado al historial de una cuenta común, sin una migración de por medio, es la firma casi inequívoca. Lo ve [[SID History agregado a una cuenta]], de alta fidelidad porque la escritura de `SIDHistory` es rarísima fuera de migraciones.
- El **uso** —la cuenta autenticándose y ejerciendo el privilegio— deja un [[Windows 4624 - Successful logon]] cuyo token incluye el grupo privilegiado, pero eso es más difícil de distinguir de una membresía legítima.

A diferencia de la variante de escalada por ticket forjado —que inyecta el SID en el PAC y no deja rastro de escritura—, esta **sí tiene una firma de alta fidelidad en el momento de la escritura**. Es la que cierra el ciclo rojo↔azul del SID History: [[SID History agregado a una cuenta]] la cubre en la escritura, mientras la variante de ticket forjado sigue dependiendo parcialmente de la detección de golden. La señal en reposo de mayor retorno es la misma que la mitigación: **auditar el atributo `SIDHistory`** en todo el directorio.
