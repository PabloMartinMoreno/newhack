---
tipo: tradecraft
clase: "[[T1558.004 - AS-REP Roasting]]"
eje: credencial
implementacion: "Pedir el TGT de cuentas sin preautenticación y romper la respuesta fuera de línea"
opsec: ruidoso
telemetria: ["[[Windows 4768 - Kerberos TGT requested]]"]
requisitos: [cuentas-sin-preautenticación]
coste: medio
alternativas: ["[[Kerberoasting]]"]
probado: nunca
contexto: [lab-ad]
aliases:
  - asrep roast
tags:
  - dominio/ad
---

# AS-REP roasting

## Cuándo lo elijo

Cuando la enumeración muestra cuentas con la **preautenticación deshabilitada**. Es hermano de [[Kerberoasting]] con una ventaja decisiva: **no requiere ninguna credencial válida**, solo conocer el nombre de la cuenta.

Eso lo mueve más temprano en la cadena — se puede intentar con una lista de nombres, sin haber comprometido nada. Si además ya se está autenticado, es una consulta más de la misma pasada de enumeración.

## Por qué funciona

La preautenticación es lo que obliga a probar que se conoce la contraseña antes de que el controlador emita nada. Sin ella, el controlador responde a cualquiera, y parte de la respuesta viene cifrada con la contraseña de la cuenta. Ver [[T1558.004 - AS-REP Roasting]].

De ahí, igual que kerberoasting: se ataca fuera de línea, sin bloqueo ni límite.

La condición completa es un atributo por cuenta, así que la superficie es exactamente la lista de cuentas que lo tienen puesto. En un dominio sano es vacía; en la práctica hay alguna, casi siempre por compatibilidad con algo viejo.

## Cómo falla

- **Todas las cuentas exigen preautenticación** — no hay superficie. Es la mitigación, y es un clic por cuenta.
- **Contraseña fuerte** en la cuenta vulnerable — se pide la respuesta y no se rompe.
- **Solo AES** — encarece el crackeo.
- **No se conocen nombres de cuenta válidos** — si se intenta sin credencial, hay que adivinar nombres primero.

## Coste

Medio, mismo perfil que kerberoasting: pedir es instantáneo, romper depende de la contraseña. La diferencia es el requisito de entrada más bajo — puede no hacer falta ninguna credencial.

## Huella esperada

- [[Windows 4768 - Kerberos TGT requested]] es el artefacto: una petición de ticket inicial con **preautenticación en cero** es la firma exacta, y es de alta fidelidad porque casi ninguna cuenta legítima está configurada así.
- Igual que su hermano, el **tipo de cifrado RC4** en la respuesta indica degradación deliberada.
- A diferencia de kerberoasting, acá una sola petición ya es sospechosa: no hace falta agregación, porque la condición —preautenticación ausente— casi no ocurre de forma legítima. Es más cerca de forma `evento` que de `agregado`.
- **El crackeo es fuera de línea e invisible.** La ventana de detección es la petición.

Del lado azul, la mejor jugada no es solo detectar: es **listar las cuentas sin preautenticación y arreglarlas**, porque la superficie es finita y conocida.
