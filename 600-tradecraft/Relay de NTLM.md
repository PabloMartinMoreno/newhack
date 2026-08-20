---
tipo: tradecraft
clase: "[[T1557.001 - LLMNR NBT-NS Poisoning and SMB Relay]]"
eje: lateral
implementacion: "Reenviar la autenticación NTLM capturada a otro servidor en tiempo real, autenticándose como la víctima sin conocer su contraseña"
opsec: ruidoso
telemetria: ["[[Windows 4624 - Successful logon]]", "[[Windows 4662 - Directory object operation]]"]
requisitos: [autenticación-ntlm-capturable, objetivo-sin-firma-obligatoria]
coste: bajo
alternativas: ["[[Envenenamiento de resolución de nombres]]", "[[Delegación basada en recursos]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - NTLM relay
  - ntlmrelayx
  - relay a LDAP
tags:
  - dominio/ad
---

# Relay de NTLM

## Cuándo lo elijo

Cuando hay una autenticación NTLM que se puede interceptar —por envenenamiento o coacción— y **al menos un objetivo no exige firma** de la comunicación. En vez de capturar el hash para romperlo, se reenvía la autenticación tal cual a ese objetivo, autenticándose ahí como la víctima.

Es la rama que **no depende de romper una contraseña**, así que la elijo cuando la captura de [[Envenenamiento de resolución de nombres]] dio un hash que no se rompe, o directamente cuando el objetivo es escalar y no solo conseguir una credencial. El requisito es que el destino tenga la firma deshabilitada, que se comprueba antes.

## Por qué funciona

NTLM es un desafío-respuesta que **no está atado al canal**: el servidor manda un desafío, el cliente responde, y nada garantiza que el que responde sea el que abrió la conexión. El atacante se pone en el medio —abre una conexión al objetivo real, y le pasa a la víctima el desafío del objetivo—:

1. La víctima se autentica al atacante (por envenenamiento o coacción).
2. El atacante, en tiempo real, abre una conexión al **objetivo real** y reenvía la autenticación de la víctima.
3. El objetivo autentica al atacante **como la víctima**, sin que este conozca la contraseña.

Lo que se consigue depende de a dónde se reenvíe, y ahí está la escalada:

| Relay a | Da |
|---|---|
| SMB (sin firma) | Ejecución en ese host, como la víctima |
| LDAP (sin firma/binding) | Configurar RBCD sobre una máquina → [[Delegación basada en recursos]] |
| LDAP con la víctima privilegiada | DCSync directo |
| Endpoint web de una CA (ESC8) | Un certificado a nombre de la víctima → [[ADCS - certificado con SAN arbitrario]] |
| HTTP interno | Acción como la víctima |

`ntlmrelayx` es la herramienta, y los objetivos y la coacción están en [[AD envenenamiento y relay - matriz de referencia]]. El relay a LDAP para configurar RBCD es la cadena moderna más potente: convierte una autenticación de máquina capturada en control de esa máquina.

## Cómo falla

Falla contra la **firma obligatoria**: SMB signing, LDAP signing y channel binding hacen que el objetivo rechace una autenticación reenviada, porque la firma sí ata la autenticación al canal. Es la mitigación correcta, y comprobar qué objetivos la exigen es el reconocimiento clave —`nxc smb 10.0.0.0/24` muestra la columna de firma—.

Falla cuando no hay ningún objetivo sin firma alcanzable: si todo el dominio exige firma, el relay no tiene a dónde ir y solo queda romper el hash.

Y falla contra **relay reflexivo** —reenviar la autenticación de un host a sí mismo—, que Microsoft mitigó hace años; el relay tiene que ir a un host **distinto** del que originó la autenticación.

## Coste

Bajo. `ntlmrelayx` apuntado a los objetivos sin firma, más el envenenamiento o la coacción que dispara la autenticación, es la cadena entera. La coacción hace que una máquina se autentique a demanda, así que no hay que esperar.

El reconocimiento —qué objetivos no firman, qué víctima tiene privilegio— es lo que decide el impacto: relay a un LDAP sin firma con una cuenta de máquina capturada es RBCD y escalada; relay a un SMB cualquiera es solo ese host.

## Huella esperada

Ruidosa y, a diferencia del envenenamiento, con el efecto **en la telemetría del objetivo**, no solo en la red:

- El relay produce una [[Windows 4624 - Successful logon]] en el objetivo, tipo 3 (red) y **NTLM**, con la identidad de la víctima desde un origen que no es el suyo. Eso lo cubre [[Autenticación NTLM donde el dominio usa Kerberos]]: NTLM donde el dominio usa Kerberos es la anomalía, y un relay es exactamente eso.
- Si el relay va a LDAP y configura RBCD, la escritura del atributo deja [[Windows 4662 - Directory object operation]], que cubre [[Escritura del atributo de delegación RBCD]] — la misma detección que la delegación, sin saber que el vector fue un relay.

Es la rama del par con mejor cobertura azul, porque su efecto aterriza en hosts monitoreados: un logon NTLM anómalo, o una escritura de RBCD. El envenenamiento que lo alimenta es más difícil de ver —vive en la red—, pero el relay en sí converge en detecciones que ya existen. Anotado en [[MOC - Active Directory]].
