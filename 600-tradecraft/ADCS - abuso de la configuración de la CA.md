---
tipo: tradecraft
clase: "[[T1649 - Steal or Forge Authentication Certificates]]"
eje: credencial
implementacion: "Abusar la configuración de la CA misma —una bandera, una ACL, o un endpoint que acepta NTLM— para emitir un certificado privilegiado"
opsec: ruidoso
telemetria: ["[[Windows 4768 - Kerberos TGT requested]]", "[[Windows 4624 - Successful logon]]", "[[Windows 4887 - Certificate Services issued]]"]
requisitos: [configuración-de-la-CA-abusable]
coste: medio
alternativas: ["[[ADCS - plantilla abusable por propósito o ACL]]", "[[Relay de NTLM]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - ESC6
  - ESC7
  - ESC8
  - ESC11
  - EDITF_ATTRIBUTESUBJECTALTNAME2
tags:
  - dominio/ad
---

# ADCS - abuso de la configuración de la CA

## Cuándo lo elijo

Cuando el fallo está en la **CA misma**, no en una plantilla: `certipy find` marca `ESC6`, `ESC7`, `ESC8` o `ESC11`. Es la rama más potente del catálogo de ADCS porque una CA mal configurada afecta a **todas** las plantillas a la vez, no a una.

La elijo cuando la mala configuración es de la entidad certificadora. Si es de una plantilla concreta, la rama es [[ADCS - certificado con SAN arbitrario]] (ESC1) o [[ADCS - plantilla abusable por propósito o ACL]] (el resto).

## Por qué funciona

Cada código es un abuso de la CA como objeto o como servicio:

- **ESC6 — SAN en cualquier plantilla.** La CA tiene la bandera `EDITF_ATTRIBUTESUBJECTALTNAME2`, que le hace aceptar un SAN arbitrario en la petición **aunque la plantilla no lo permita**. Convierte cualquier plantilla de autenticación en un ESC1. Es una sola bandera que abre toda la PKI.
- **ESC7 — ACL de la CA.** Con `ManageCA` se puede **encender la bandera de ESC6** —escalar de administrador de la CA a emisor de certificados arbitrarios— o, con `ManageCertificates`, aprobar peticiones pendientes que la CA rechazó. Un permiso administrativo sobre la CA se vuelve toma de dominio.
- **ESC8 — relay al endpoint web.** El endpoint de inscripción web (`certsrv`) acepta NTLM y no exige binding. Se coacciona a un objetivo valioso —un DC— a autenticarse, y se **relaya** esa autenticación al endpoint para pedir un certificado a su nombre. Con el cert del DC se hace DCSync.
- **ESC11 — relay al endpoint RPC.** Lo mismo que ESC8 pero contra el endpoint RPC de inscripción, cuando el web no está.

Los comandos están en [[ADCS - matriz de referencia]]. ESC8 y ESC11 son casos de [[Relay de NTLM]] con la CA como objetivo, y por eso este dominio y el de relay se referencian: el relay a la inscripción es la cadena que convierte una autenticación de máquina capturada en un certificado de DC.

## Cómo falla

Falla contra una CA endurecida: `EDITF_ATTRIBUTESUBJECTALTNAME2` deshabilitado (ESC6), ACL de la CA cerrada (ESC7), y **Extended Protection for Authentication** o HTTPS con binding en los endpoints de inscripción (ESC8/11), que anula el relay.

Falla contra la extensión de mapeo fuerte (KB5014754) en modo obligatorio, igual que las ramas de plantilla: el cert se emite pero el DC rechaza la autenticación sin el mapeo por SID.

Y ESC8/11 fallan si no se puede coaccionar al objetivo a autenticarse: las mismas mitigaciones de coacción de [[Relay de NTLM]] cierran esa vía.

## Coste

Medio. ESC6 con la bandera puesta es una petición, como ESC1. ESC7 requiere el permiso administrativo sobre la CA, que es el prerrequisito caro. ESC8/11 heredan el costo del relay —montar `certipy relay` y disparar la coacción—, pero la recompensa es un certificado de DC, que es DCSync.

El reconocimiento con `certipy find` es lo que decide qué rama está abierta y su costo; ESC8 contra una CA sin binding y un DC coaccionable es de las escaladas más directas a admin de dominio de todo AD.

## Huella esperada

Ruidosa, y con la particularidad de que ESC8/11 convergen con las detecciones de relay que ya existen:

- La **emisión** deja el `4887` en la CA —[[Windows 4887 - Certificate Services issued]]—; para ESC6 (SAN en cualquier plantilla) la discrepancia entre el SAN y el solicitante la ve [[Certificado emitido con sujeto ajeno al solicitante]].
- El **uso** del certificado deja [[Windows 4768 - Kerberos TGT requested]] con información de certificado, la misma señal que el resto de ADCS.
- **ESC8/11**, al ser relay, producen una [[Windows 4624 - Successful logon]] NTLM de la víctima coaccionada desde un origen ajeno —lo que cubre [[Autenticación NTLM donde el dominio usa Kerberos]]— y, si la coacción fue de un DC, la anomalía de que un DC se autentique a un host cualquiera.
- **ESC7**, al modificar la configuración de la CA, deja un cambio en el objeto de la CA en el directorio, visible en [[Windows 4662 - Directory object operation]] si la auditoría lo cubre.

La cara azul del abuso de la CA cubre las tres fases: la **emisión** la ve [[Certificado emitido con sujeto ajeno al solicitante]] sobre el `4887` (con la auditoría de la CA encendida), el **uso** del cert [[Autenticación por certificado a cuenta privilegiada]] sobre el `4768`, las ramas de **relay** las detecciones de relay existentes, y la **modificación de configuración** la firma de escritura de `4662`. El único requisito duro es que la auditoría de AD CS esté activa —sin ella el `4887` no existe—, el mismo punto ciego de configuración que el `4662` de DCSync.
