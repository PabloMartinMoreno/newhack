---
tipo: tradecraft
clase: "[[CWE-347 - Improper Verification of Cryptographic Signature]]"
eje: fase-del-flujo
implementacion: "Modificar la aserción cuando la firma no se comprueba, se puede quitar, o se acepta alg none"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [sp-que-no-valida-la-firma-de-la-asercion]
coste: bajo
alternativas: ["[[SAML - envoltura de firma XML]]", "[[SAML - inyección de comentarios en NameID]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - SAML signature stripping
  - SAML sin firma
tags:
  - dominio/web
---

# SAML - firma no verificada o eliminada

## Cuándo lo elijo

Primero, siempre. Es la prueba más barata del dominio: se decodifica la aserción, se cambia el `NameID` —el campo que identifica al usuario— por el de la víctima, y se reenvía. Si el proveedor de servicio la acepta, no valida la firma en absoluto.

Se prueba antes que [[SAML - envoltura de firma XML]] porque cuando funciona no hace falta ninguna manipulación del XML: es cambiar un campo y mandar. Solo se pasa a la envoltura cuando la firma **sí** se valida y hay que engañarla.

## Por qué funciona

SAML transporta una aserción firmada por el proveedor de identidad, y la seguridad entera del protocolo descansa en que el proveedor de servicio verifique esa firma. Esa verificación se omite o se degrada de tres maneras, todas de implementación:

- **No se verifica.** La biblioteca parsea la aserción y lee el `NameID` sin comprobar la firma. Es más común de lo que parece porque muchas integraciones de SAML se escriben a mano y "andaban" en las pruebas, donde el proveedor era de confianza.
- **Se puede quitar.** El proveedor de servicio verifica la firma **si está**, pero acepta la aserción sin ella. Se borra el elemento `<Signature>` entero y pasa.
- **Se acepta un algoritmo nulo.** El atributo del método de firma admite un valor que equivale a "sin firma", o la biblioteca acepta que se lo cambie. Es el `alg: none` de [[OAuth - validación del id_token]] trasladado a XML.

En los tres casos, una vez que la firma no protege, se edita el `NameID` a `administrador@objetivo.com` y la sesión se abre como esa persona. La mecánica de decodificar y recodificar la aserción está en [[SAML - matriz de identificación]].

Este dominio es primo del `id_token` de OAuth, y por eso comparten `clase:`: los dos son un token firmado por un tercero que el consumidor tiene que verificar bien, y los dos fallan en las mismas cinco comprobaciones. Lo que cambia es el formato —XML firmado en vez de JWT—, y el formato trae una superficie que el JWT no tiene: la envoltura de firma.

## Cómo falla

Falla contra una biblioteca de SAML mantenida, que verifica la firma, rechaza la aserción sin ella y no acepta algoritmos nulos. Ahí hay que pasar a atacar la firma en vez de evitarla — [[SAML - envoltura de firma XML]].

Falla cuando la firma cubre **toda** la respuesta y el proveedor exige que exista, porque entonces quitarla invalida el mensaje entero.

Y falla, en el sentido de que no aplica, cuando el proveedor de servicio compara la aserción recibida contra una copia esperada o valida el certificado con precisión. Es la implementación correcta y la que hay que recomendar.

## Coste

Bajo, el más bajo del dominio. Decodificar la aserción, editar un campo, recodificar y reenviar son cinco minutos con la extensión de SAML de un proxy. No hace falta criptografía ni construir nada.

El único trabajo previo es capturar una aserción válida, que se consigue autenticándose una vez con una cuenta propia. A partir de ahí se edita el `NameID` de esa aserción propia hacia la víctima.

## Huella esperada

Casi nula, y de ahí el `opsec: limpio`. Una aserción modificada que el proveedor de servicio acepta produce un inicio de sesión indistinguible de uno legítimo: desde su punto de vista, la persona se autenticó por SAML.

La única señal aprovechable es un desajuste que exige registrar más de lo que se registra: **una aserción sin firma válida que resultó en una sesión**, o un `NameID` que no corresponde al proveedor de identidad que la emitió. Vale lo mismo que en [[OAuth - validación del id_token]] — si la aplicación distinguiera esos campos, probablemente los estaría validando, y no sería vulnerable.

Queda en [[Log de autenticación de la aplicación]] como un inicio de sesión federado normal. Ninguna detección del vault lo ve, por el mismo motivo que el resto de la familia de tokens: la señal depende de un campo que las implementaciones vulnerables, por serlo, no capturan. Anotado en [[MOC - SAML]].
