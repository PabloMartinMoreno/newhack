---
tipo: tradecraft
clase: "[[T1003.006 - DCSync]]"
eje: credencial
implementacion: "Pedir al DC la replicación de los secretos de una cuenta, vía protocolo de replicación"
opsec: ruidoso
telemetria: ["[[Windows 4662 - Directory object operation]]"]
requisitos: [derechos-de-replicación]
coste: bajo
alternativas: ["[[LSASS - volcado vía comsvcs.dll MiniDump]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - dcsync
tags:
  - dominio/ad
---

# DCSync

## Cuándo lo elijo

Cuando ya tengo una cuenta con derechos de replicación —administrador de dominio, o una cuenta a la que se los delegaron— y quiero **los secretos de cualquier cuenta sin tocar ninguna máquina**. Es el camino a los hashes de todo el dominio, incluida la cuenta que firma los tickets, que es la llave para [[Golden ticket]].

Es preferible a [[LSASS - volcado vía comsvcs.dll MiniDump]] cuando se tienen los derechos: no requiere ejecutar nada en el controlador ni volcar memoria en ningún host. Es una conversación de red.

## Por qué funciona

Porque replicar es una función legítima del directorio: los controladores se sincronizan constantemente, y el permiso para pedir esa sincronización está modelado como derechos sobre el objeto raíz del dominio. Quien los tenga puede pedirla, sin ser controlador. Ver [[T1003.006 - DCSync]].

El hallazgo real casi nunca es "el atacante es administrador de dominio". Es **una cuenta de servicio, de respaldo o de sincronización a la que alguien le delegó esos derechos** y nadie los revisó. Esa delegación olvidada es lo que aparece en una revisión de permisos.

## Cómo falla

- **Sin los derechos de replicación, no funciona.** No hay bypass: es una comprobación de permisos del protocolo. La mitigación es auditar quién los tiene.
- **Solicitar replicación desde algo que no es un controlador** es en sí mismo la anomalía — no hay forma de hacerlo pareciendo legítimo, porque legítimamente solo lo hacen los controladores entre sí.
- **Segmentación** que impida hablar el protocolo de replicación con el controlador desde una máquina cualquiera.

## Coste

Bajo, una vez que se tienen los derechos. La conversación de replicación es rápida y devuelve lo pedido. Todo el costo estuvo en llegar a tener los derechos, que es el resto del dominio de AD.

## Huella esperada

Ruidoso para quien mire el lugar correcto, invisible para el resto.

- [[Windows 4662 - Directory object operation]] es el artefacto, y la señal es exacta: los **derechos extendidos de replicación** invocados por algo que **no es una cuenta de controlador de dominio**. No tiene falsos positivos — ninguna operación legítima hace eso salvo los controladores entre sí, que se excluyen por cuenta.
- Es de alta fidelidad y de forma `evento`: una sola operación de estas ya es el ataque.
- **El requisito previo es la trampa.** El evento solo existe si la auditoría de acceso al directorio está configurada **sobre el objeto raíz del dominio**, no solo habilitada por directiva. Sin ese segundo paso, DCSync no deja rastro y parece que no pasó nada. Ver [[Windows 4662 - Directory object operation]] y [[Ausencia de alertas no es ausencia de ataque]].

Es el ejemplo más claro del vault de una técnica de altísima fidelidad que **no se detecta si la fuente no está bien configurada** — y la configuración que falta es justo la que nadie hace.
