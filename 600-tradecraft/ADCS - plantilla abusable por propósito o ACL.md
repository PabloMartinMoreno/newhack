---
tipo: tradecraft
clase: "[[T1649 - Steal or Forge Authentication Certificates]]"
eje: credencial
implementacion: "Abusar una plantilla mal configurada por su EKU, su rol de agente, o su ACL escribible, para obtener un certificado que autentica como un privilegiado"
opsec: ruidoso
telemetria: ["[[Windows 4768 - Kerberos TGT requested]]", "[[Windows 4662 - Directory object operation]]"]
requisitos: [plantilla-de-certificado-mal-configurada, permiso-de-inscripción]
coste: bajo
alternativas: ["[[ADCS - certificado con SAN arbitrario]]", "[[ADCS - abuso de la configuración de la CA]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - ESC2
  - ESC3
  - ESC4
  - enrollment agent
tags:
  - dominio/ad
---

# ADCS - plantilla abusable por propósito o ACL

## Cuándo lo elijo

Cuando `certipy find -vulnerable` marca una plantilla como `ESC2`, `ESC3`, `ESC4`, `ESC13` o `ESC15` —es decir, la plantilla está mal configurada por algo **que no es el SAN**—. Es el complemento de [[ADCS - certificado con SAN arbitrario]] (ESC1): la misma idea —una plantilla deja obtener un certificado que autentica como otro— pero por un fallo distinto de configuración.

La elijo cuando el fallo está en la **plantilla**. Si está en la CA misma —una bandera, una ACL, un endpoint relayable—, la rama es [[ADCS - abuso de la configuración de la CA]].

## Por qué funciona

Cada código es un camino distinto para que un certificado termine autenticando como un privilegiado:

- **ESC2 — cualquier propósito.** La plantilla tiene EKU "Any Purpose" o ninguno. Un certificado sin EKU restrictivo sirve para autenticar aunque la plantilla no fuera pensada para eso.
- **ESC3 — agente de inscripción.** La plantilla otorga el EKU `Certificate Request Agent`, que permite pedir certificados **en nombre de otro usuario**. Se obtiene el cert de agente y con él se pide un cert de autenticación como administrador.
- **ESC4 — ACL escribible.** No hay que encontrar una plantilla ya vulnerable: si se tiene `WriteProperty` sobre una plantilla, se la **reconfigura** para volverla ESC1, se explota, y se la restaura. Convierte un permiso de escritura en toma de dominio.
- **ESC13 — política de emisión.** La plantilla está ligada a una política de emisión que a su vez está ligada a un grupo privilegiado: el cert emitido incluye la pertenencia a ese grupo.
- **ESC15 (EKUwu).** Un fallo que permite inyectar un EKU de aplicación arbitrario en la petición, sorteando las restricciones de la plantilla.

Los comandos de cada uno están en [[ADCS - matriz de referencia]]. En todos, el paso final es el mismo: `certipy auth` con el `.pfx` obtenido devuelve el TGT y el hash NT del privilegiado.

Lo que une a la familia es que el fallo es de la **plantilla**, un objeto del directorio que un administrador de PKI configuró mal y que casi nadie audita después.

## Cómo falla

Falla cuando las plantillas están bien configuradas —EKU restrictivo, sin rol de agente indebido, ACL cerrada—, que es lo que Certipy confirma cuando no marca nada vulnerable.

Falla contra la **extensión de mapeo fuerte** (KB5014754): aunque se obtenga el certificado, el DC puede rechazar la autenticación si exige el mapeo por SID y el cert no lo tiene. Es la mitigación que Microsoft empujó y que rompe varias de estas cadenas si está en modo obligatorio.

Falla si no se tiene permiso de inscripción sobre la plantilla vulnerable: la mala configuración existe pero no se puede pedir el cert.

## Coste

Bajo. Con `certipy find` identificando el `ESCx` y permiso de inscripción, cada cadena son dos o tres comandos. ESC4 agrega el paso de reconfigurar y restaurar la plantilla, que es una escritura más.

El costo está en el reconocimiento —correr `certipy find -vulnerable` y leer qué rama está abierta— y en tener el permiso que cada una requiere, que sale de la enumeración de ACL de BloodHound.

## Huella esperada

Ruidosa en dos puntos, según la rama:

- **La inscripción del certificado** deja eventos en la CA (`4886`/`4887` en el log de la entidad certificadora), que el vault no modela como artefacto propio.
- **El uso del certificado** para autenticarse deja una [[Windows 4768 - Kerberos TGT requested]] con información de certificado en el campo correspondiente. Es la señal de que alguien se autenticó con un cert, y su anomalía es de contexto —un usuario que normalmente no usa certificados, o un cert recién emitido—.
- **ESC4 y ESC13** modifican objetos del directorio (la plantilla, la política): esa escritura deja [[Windows 4662 - Directory object operation]], la misma clase de señal de alta fidelidad que la escritura de RBCD, si la auditoría está sobre esos objetos.

El uso del certificado lo ve [[Autenticación por certificado a cuenta privilegiada]]: ancla en el `4768` con información de certificado (PKINIT) para una cuenta privilegiada. No distingue el cert forjado del legítimo —los dos son PKINIT válido—, pero un administrador autenticándose con certificado es la anomalía. Y la señal de configuración de ESC4/ESC13 —la modificación de la plantilla— deja `4662`, análoga a RBCD. Como en toda la persistencia por certificado, el problema defensivo de fondo es que el cert **sobrevive al cambio de contraseña**: la detección del uso llega tarde, la mitigación es de configuración de la PKI.
