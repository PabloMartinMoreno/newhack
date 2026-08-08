---
tipo: tecnica
taxonomia: cwe
identificador: CWE-330
wstg: WSTG-SESS-01
tacticas: []
aliases:
  - CWE-330
  - Token predecible
  - Aleatoriedad insuficiente
tags:
  - dominio/web
---

# CWE-330 - Use of Insufficiently Random Values

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Gestión de sesión]]; la variante, en [[Sesión - token predecible]].

## Qué es

Un valor que debía ser impredecible se puede predecir. En web, los tres que importan son el identificador de sesión, el token de recuperación de contraseña y el token anti-CSRF.

## Por qué sigue apareciendo

No en los marcos de trabajo grandes, que hace años usan generadores criptográficos. Aparece en **manejo de sesión escrito a mano**, que es más común de lo que parece: microservicios internos, APIs viejas, paneles de administración hechos aparte, y cualquier lugar donde alguien decidió que la sesión del marco de trabajo no le servía.

Las tres formas concretas:

- **Generador no criptográfico.** La función de azar de propósito general de casi todos los lenguajes es predecible: observando suficientes salidas se reconstruye el estado interno y se predicen las siguientes.
- **Valor derivado de datos conocidos.** Marca de tiempo, identificador de usuario, contador, o alguna combinación con hash. El hash no agrega entropía: si la entrada es adivinable, la salida también.
- **Entropía insuficiente.** Aleatorio de verdad pero corto. Treinta y dos bits se recorren enteros.

## Cómo se reconoce

Pidiendo muchos tokens seguidos y mirándolos juntos. Un token bien generado no tiene estructura: no comparte prefijos, no crece, no se decodifica a nada legible, y sus bits pasan cualquier prueba estadística simple.

Los indicios de lo contrario son groseros cuando se los busca: valores que cambian de a uno, prefijos largos compartidos entre tokens emitidos en el mismo segundo, base64 que decodifica a texto con el nombre del usuario adentro.

## Por qué es más grave que otros hallazgos del dominio

Porque no requiere víctima. Robar una sesión necesita un XSS, una red o un descuido; predecirla no necesita nada más que el algoritmo. Y escala: si se predice una, se predicen todas, incluidas las de administradores, sin interactuar con ningún usuario.

Es el hallazgo del dominio con mejor relación entre esfuerzo de explotación e impacto, y el más difícil de detectar del lado azul — un token predicho es indistinguible de uno legítimo.

## La mitigación real

Usar el generador criptográfico del sistema, con al menos 128 bits de entropía, y no derivar el valor de nada. En la práctica: usar el manejo de sesión del marco de trabajo y no escribir uno propio.

## Referencias canónicas

- [CWE-330](https://cwe.mitre.org/data/definitions/330.html)
- [CWE-338](https://cwe.mitre.org/data/definitions/338.html) — generador no criptográfico
- WSTG-SESS-01
