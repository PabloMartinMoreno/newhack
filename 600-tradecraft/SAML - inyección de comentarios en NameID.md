---
tipo: tradecraft
clase: "[[CWE-287 - Improper Authentication]]"
eje: fase-del-flujo
implementacion: "Partir el NameID con un comentario XML para que el verificador y el lector obtengan textos distintos"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [cuenta-propia-con-prefijo-del-correo-de-la-victima]
coste: medio
alternativas: ["[[SAML - envoltura de firma XML]]", "[[SAML - firma no verificada o eliminada]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - SAML comment injection
  - XML canonicalization bypass
tags:
  - dominio/web
---

# SAML - inyección de comentarios en NameID

## Cuándo lo elijo

Cuando la firma se valida bien y cubre el `NameID` —así que ni quitarla ni envolverla funciona— pero el proveedor de servicio extrae el texto del `NameID` de una forma que un comentario XML puede partir.

Es una rama estrecha y específica: solo aplica si se puede **registrar una cuenta propia** cuyo identificador contenga el prefijo del correo de la víctima. Sin esa condición no hay ataque, y por eso va después de las otras dos aunque su firma sea la misma que la de firma-no-verificada.

## Por qué funciona

El truco explota una diferencia entre dos operaciones que deberían dar el mismo resultado: **cómo se canonicaliza el XML para verificar la firma**, y **cómo se lee el texto de un elemento para usarlo**.

Se registra una cuenta con un `NameID` como `victima@objetivo.com<!---->.atacante.com` — el correo de la víctima, un comentario XML vacío, y el resto del dominio propio para que la cuenta sea legítimamente del atacante. El proveedor de identidad firma esa aserción sin problema, porque es una cuenta real.

Al llegar al proveedor de servicio pasan dos cosas distintas con el mismo campo:

- **La verificación de la firma** canonicaliza el XML tratando el comentario como parte del contenido, así que valida sobre el texto completo. La firma es correcta.
- **La lectura del `NameID`** usa una función que, ante un comentario, **devuelve solo el primer fragmento de texto** — `victima@objetivo.com` — y descarta el resto.

El verificador aprueba una cosa y el lector toma otra. La sesión se abre como la víctima, con una aserción genuinamente firmada.

Es exactamente el mismo patrón que [[SAML - envoltura de firma XML]] —desacople entre lo que se valida y lo que se usa— pero por otro mecanismo: acá no se mueven elementos, se abusa de cómo una biblioteca de XML colapsa el texto alrededor de un comentario. Fue un fallo real y masivo en 2018, en varias bibliotecas a la vez, precisamente porque la función de lectura de texto era una utilidad compartida.

## Cómo falla

Falla contra bibliotecas que leen el `NameID` con una función que concatena **todos** los nodos de texto, ignorando los comentarios de forma consistente con la canonicalización. Es la corrección que se aplicó cuando el fallo se hizo público.

Falla cuando no se puede registrar una cuenta con el `NameID` deseado: si el proveedor de identidad no permite elegir el identificador, o valida que el dominio del correo sea propio, no hay forma de construir el valor partido.

Y falla cuando el `NameID` es opaco —un identificador aleatorio en vez de un correo—, porque entonces no hay un prefijo de la víctima que replicar.

## Coste

Medio. La técnica en sí es una petición, pero el prerrequisito es un trabajo aparte: conseguir que el proveedor de identidad emita una aserción con el `NameID` partido. Eso puede exigir registrar una cuenta, controlar un dominio, y a veces pasar por una verificación de correo que no se puede completar.

Cuando el registro es abierto y el `NameID` es el correo, es barato. Cuando el proveedor de identidad es corporativo y cerrado, la rama no es viable y conviene descartarla temprano.

## Huella esperada

Casi nula, igual que el resto del dominio, y por la misma razón: la aserción está genuinamente firmada, así que el inicio de sesión parece legítimo.

Hay una señal específica y de buena fidelidad si se mira el lugar correcto: **el `NameID` de la aserción contiene un comentario XML**. Un `NameID` legítimo no tiene comentarios; uno partido con `<!---->` en medio es el ataque, y no ocurre por accidente. Detectarlo exige inspeccionar el XML de la aserción antes de que la función de lectura lo colapse — que es justo lo que la implementación vulnerable no hace.

Como en toda la familia, no hay detección en el vault porque ninguna fuente parsea la aserción a ese nivel. Queda en el mismo hueco de instrumentación que [[SAML - envoltura de firma XML]], anotado en [[MOC - SAML]]. La recomendación defensiva de mayor retorno no es una regla sino registrar el `NameID` crudo, con sus comentarios, junto al usuario que autenticó.
