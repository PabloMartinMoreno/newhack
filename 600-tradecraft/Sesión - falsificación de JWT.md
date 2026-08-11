---
tipo: tradecraft
clase: "[[CWE-347 - Improper Verification of Cryptographic Signature]]"
eje: mecanismo
implementacion: "Alterar las afirmaciones de un JWT y lograr que el servidor acepte la firma"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [jwt-como-sesion, verificacion-defectuosa]
coste: medio
alternativas: ["[[Sesión - robo de token]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - JWT forjado
  - JWT attacks
tags:
  - dominio/web
---

# Sesión - falsificación de JWT

## Cuándo lo elijo

Cuando la sesión es un JWT y se quiere **cambiar quién dice ser el token**, no robar uno ajeno. La diferencia importa: robar da la cuenta de alguien; falsificar da cualquier cuenta, incluidas las administrativas, sin tocar a ningún usuario.

Lo primero es leer el token, que es gratis: es base64 y se decodifica sin ninguna clave. Las afirmaciones dicen qué hay para cambiar —un identificador de usuario, un rol, un inquilino— y la cabecera dice qué ataques valen la pena.

Antes de intentar romper la firma conviene la pregunta barata: **¿se verifica siquiera?** Modificar una afirmación sin tocar la firma y ver si el servidor lo acepta cuesta una petición y a veces termina ahí.

## Por qué funciona

Por el defecto de diseño del formato: **el token declara cómo debe verificarse a sí mismo**. La cabecera lleva el algoritmo, y a veces la clave o la URL de la clave. Una implementación ingenua obedece esas instrucciones, que vienen del atacante.

De ahí las tres familias, en orden de lo que todavía funciona:

**Confusión de algoritmo.** El token declara `HS256` donde el servidor esperaba `RS256`. Si la implementación elige el algoritmo según el token y usa "la clave" sin distinguir su tipo, verifica un HMAC usando como secreto la **clave pública** — que es pública. Es la más viable hoy y la que más sobrevive en bibliotecas viejas.

**Clave controlada por el atacante.** Las cabeceras que apuntan a la clave permiten que el token indique con qué verificarse. Si el servidor la busca donde el token dice, el atacante firma con la suya. `kid` además suele terminar en una consulta o en una ruta de archivo, lo que lo convierte en punto de inyección hacia [[MOC - SQL injection]] o [[MOC - File inclusion]].

**Secreto débil.** Con `HS256` y un secreto corto o de diccionario, se recupera fuera de línea y a partir de ahí se firma cualquier cosa. No es un fallo del formato sino de la clave, y es sorprendentemente frecuente en implementaciones internas.

El algoritmo `none` está casi extinto en bibliotecas mantenidas. Se prueba igual porque cuesta una petición.

## Cómo falla

- **Algoritmo fijado en el servidor** — se rechaza todo token que declare otro. La mitigación, y cierra las dos primeras familias.
- **Lista blanca de identificadores de clave, resuelta localmente** — cierra la tercera familia de cabeceras.
- **Secreto largo y aleatorio** — la fuerza bruta fuera de línea deja de ser viable.
- **La biblioteca es moderna y estricta** — el caso normal hoy. Las bibliotecas mantenidas cerraron `none` y la confusión de algoritmo hace años.
- **Se validan las afirmaciones** — vencimiento, emisor y destinatario. Es donde falla la mitad de las implementaciones que sí verifican bien la firma, y es un hallazgo propio aunque la firma sea impecable.

## Coste

Medio, y con descarte rápido: las pruebas baratas —firma no verificada, `none`, confusión de algoritmo— son tres peticiones y cubren la mayor parte de lo explotable. La fuerza bruta del secreto es cara y solo vale con un objetivo claro.

## Huella esperada

Es de las variantes más silenciosas, y tiene una consecuencia que conviene señalar en un informe: **un JWT sin estado no se puede revocar**. Cuando se descubre un token falsificado, no hay dónde invalidarlo salvo rotando la clave de firma, lo que cierra la sesión de todos los usuarios a la vez. Ver [[CWE-613 - Insufficient Session Expiration]].

- [[Log de autenticación de la aplicación]] registra actividad de una cuenta **sin ningún evento de acceso previo** para ella. Es la firma exacta: hay sesión y nadie se autenticó nunca. Solo se ve correlacionando el uso de sesión con los accesos, y depende de que el registro incluya el identificador de la sesión.
- Los intentos fallidos —tokens con firma inválida— sí quedan si la aplicación los registra, y son un indicador de alta fidelidad: nadie manda un JWT mal firmado por accidente.
- La fuerza bruta del secreto es **fuera de línea**: no genera ni una petición. Solo se ve el uso del token resultante, que es indistinguible de uno legítimo.

Los ataques concretos, con el orden de descarte, están en [[JWT - matriz de referencia]].
