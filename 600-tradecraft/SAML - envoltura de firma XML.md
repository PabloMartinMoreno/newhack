---
tipo: tradecraft
clase: "[[CWE-347 - Improper Verification of Cryptographic Signature]]"
eje: fase-del-flujo
implementacion: "Colocar una aserción falsa donde la lee la aplicación y la firmada donde la valida el verificador"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [firma-valida-pero-verificador-y-lector-desacoplados]
coste: alto
alternativas: ["[[SAML - firma no verificada o eliminada]]", "[[SAML - inyección de comentarios en NameID]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - XSW
  - XML signature wrapping
  - envoltura de firma
tags:
  - dominio/web
---

# SAML - envoltura de firma XML

## Cuándo lo elijo

Cuando la firma **sí** se valida —así que [[SAML - firma no verificada o eliminada]] no pasó— pero el proveedor de servicio usa una biblioteca o una integración propia que separa dos pasos que deberían ser uno: verificar la firma, y leer los datos.

Es la rama cara y la más específica del dominio. No tiene equivalente en OAuth ni en JWT: es propia del XML firmado, y es la razón por la que SAML merece dominio aparte en vez de ser una fila en la matriz de tokens.

## Por qué funciona

Una firma XML no firma "el documento": firma un **elemento identificado por su `ID`**, referenciado desde dentro de la propia firma. El verificador comprueba que ese elemento no cambió. El problema aparece cuando **el elemento que se verifica no es el mismo que la aplicación lee**.

El ataque mete dos aserciones en la respuesta:

- La **original firmada**, intacta, en un lugar donde el verificador la encuentra por su `ID` y confirma que su firma es válida.
- Una **falsa, sin firmar**, con el `NameID` de la víctima, colocada donde el código de la aplicación va a buscar los datos del usuario.

El verificador dice "la firma es válida" —porque validó la original—, y el lector toma el `NameID` de la falsa. Las dos afirmaciones son ciertas por separado; el fallo es que se refieren a elementos distintos.

Dónde se esconde la aserción firmada y dónde se pone la falsa depende de cómo la biblioteca resuelve las referencias, y hay una decena de patrones —envolver la firma, mover la original a un elemento hermano, anidar, jugar con `ID` duplicados—. El catálogo está en [[SAML XSW - matriz de referencia]]; probarlos en orden es el trabajo.

La causa de fondo es la misma en todos: **el desacople entre qué se valida y qué se usa**, que es exactamente el patrón de [[SAML - inyección de comentarios en NameID]] y, más lejos, de [[Control de acceso - salto de contexto]]. Dos operaciones que deberían mirar el mismo dato miran datos distintos.

## Cómo falla

Falla cuando la biblioteca valida y lee el **mismo** nodo, resolviendo la referencia una sola vez y rechazando documentos con `ID` duplicados o con más de una aserción. Es lo que hacen las bibliotecas modernas después de que esta clase de fallo se documentara en masa alrededor de 2012.

Falla cuando el esquema se valida de forma estricta y no admite elementos de más en posiciones inesperadas.

Y falla, prácticamente, cuando ninguno de los patrones de la matriz coincide con cómo esa biblioteca resuelve las referencias. Es una rama de prueba y error, y puede agotarse sin resultado — se reporta entonces que la firma se valida correctamente.

## Coste

Alto. Cada patrón de envoltura es una edición distinta del XML y hay que probarlos uno por uno, observando si el proveedor de servicio acepta la aserción y con qué identidad. Son diez o quince intentos bien construidos, y construir cada uno a mano es delicado porque un XML mal formado se rechaza por otra razón y confunde el diagnóstico.

Herramienta ayuda —la extensión SAML Raider de Burp aplica los patrones automáticamente—, y sin ella el coste sube bastante. Conviene fijarla antes de empezar.

## Huella esperada

Casi nula del lado observable, como toda la familia. Una envoltura exitosa produce un inicio de sesión que el proveedor de servicio considera legítimo, porque la firma que verificó era genuina.

La diferencia con [[SAML - firma no verificada o eliminada]] es que acá **la respuesta contiene dos aserciones**, o una estructura anómala con `ID` repetidos. Eso sí es una firma detectable, y de buena fidelidad: una respuesta SAML bien formada tiene exactamente una aserción, así que dos —o un `<Signature>` en una posición rara— no ocurre en tráfico legítimo. La detección exige inspeccionar la estructura del XML, no solo el resultado del inicio de sesión.

No existe en el vault porque ninguna fuente parsea el cuerpo de la respuesta SAML a ese nivel, y queda anotado como el hueco de instrumentación del dominio en [[MOC - SAML]]. Es el mismo tipo de límite que el reconocimiento de payloads en el cuerpo de un POST: la señal está, la fuente no la mira.
