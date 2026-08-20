---
tipo: tradecraft
clase: "[[T1649 - Steal or Forge Authentication Certificates]]"
eje: persistencia
implementacion: "Solicitar un certificado a nombre de otra cuenta desde una plantilla mal configurada"
opsec: requiere-bypass
telemetria: ["[[Windows 4768 - Kerberos TGT requested]]", "[[Windows 4887 - Certificate Services issued]]"]
requisitos: [plantilla-que-permite-elegir-el-sujeto, derecho-de-inscripción]
coste: medio
alternativas: ["[[DCSync]]", "[[Golden ticket]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - ESC1
  - abuso de plantilla de certificado
tags:
  - dominio/ad
---

# ADCS - certificado con SAN arbitrario

## Cuándo lo elijo

Cuando la enumeración encuentra una autoridad de certificación con una plantilla que **permite al solicitante elegir a nombre de quién se emite** y que además sirve para autenticación. Es escalada y persistencia a la vez, y muchas veces la vía más limpia a administrador de dominio.

Se busca temprano precisamente porque la autoridad de certificación suele estar fuera del inventario mental de AD — se instaló para otra cosa y nadie revisa sus plantillas.

## Por qué funciona

Porque la autoridad emite lo que sus plantillas permiten. Si una plantilla deja que el solicitante fije el nombre del sujeto, se pide un certificado a nombre de un administrador y se usa para autenticarse como él. Nada está roto: la plantilla dice que se puede. Ver [[T1649 - Steal or Forge Authentication Certificates]].

La propiedad que lo hace tan valioso: **un certificado no se invalida cambiando la contraseña**. Vale hasta su vencimiento —años— y solo se corta revocándolo, cosa que hay que saber hacer. Es la mejor persistencia del dominio: sobrevive a la respuesta a incidentes que rota credenciales y da el caso por cerrado.

## Cómo falla

- **Plantillas bien configuradas** — que no dejen elegir el sujeto, o que exijan aprobación del administrador. Es la mitigación, y es auditar plantillas.
- **Derecho de inscripción restringido** — si no se puede solicitar la plantilla, no hay ataque.
- **La autoridad no se usa para autenticación** — algunas emiten certificados para otros fines y no sirven para esto.
- **Monitoreo de emisiones** — una autoridad que revisa a nombre de quién se emite cada certificado detecta la anomalía en el momento.

## Coste

Medio. Encontrar la plantilla vulnerable es reconocimiento; solicitarla y usar el certificado es rápido. La incertidumbre está en si existe una plantilla abusable, no en la explotación.

## Huella esperada

Sigilosa, y ese es el problema.

- **La emisión del certificado** queda en el `4887` de la autoridad de certificación —[[Windows 4887 - Certificate Services issued]]—, y ahí está la señal más fuerte de ESC1: un certificado con el UPN de un administrador en el SAN pedido por una cuenta cualquiera. La discrepancia entre el SAN y el solicitante la ve [[Certificado emitido con sujeto ajeno al solicitante]] **en el momento de emitir**, antes del uso. El requisito es que la auditoría de AD CS esté encendida, que casi nunca lo está.
- **El uso del certificado** para autenticarse deja [[Windows 4768 - Kerberos TGT requested]], porque el certificado se canjea por un ticket inicial. Lo ve [[Autenticación por certificado a cuenta privilegiada]]; distinguirlo de una autenticación con tarjeta inteligente legítima requiere contexto, y llega más tarde que la señal de emisión.
- **La persistencia es lo peor de detectar**, porque no hay evento recurrente: el certificado ya emitido se usa cuando el atacante quiere, y sobrevive a toda rotación de credenciales.

Del lado azul, la jugada de mayor retorno es preventiva: **auditar las plantillas** antes de que alguien las use. La autoridad de certificación tiene el mismo poder que un controlador de dominio y casi nunca la misma vigilancia.
