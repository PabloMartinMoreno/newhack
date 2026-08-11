---
tipo: tradecraft
clase: "[[CWE-330 - Use of Insufficiently Random Values]]"
eje: fallo
implementacion: "Reconstruir el patrón de generación y predecir identificadores ajenos"
opsec: limpio
telemetria: ["[[Log de autenticación de la aplicación]]"]
requisitos: [manejo-de-sesion-propio, muestras-de-tokens]
coste: alto
alternativas: ["[[Sesión - robo de token]]", "[[Sesión - fijación]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - predicción de sesión
  - reconstruir el generador
tags:
  - dominio/web
---

# Sesión - token predecible

## Cuándo lo elijo

Cuando el manejo de sesión **no es el del marco de trabajo**. Es la condición que decide si vale la pena mirar: los marcos grandes usan generadores criptográficos desde hace años y ahí no hay nada. Lo que hay que buscar es sesión escrita a mano — microservicios internos, APIs viejas, paneles de administración hechos aparte.

La señal es el formato del token. Uno de biblioteca conocida se reconoce a simple vista; uno corto, con estructura visible, o que decodifica a algo legible, es artesanal y merece análisis.

Es el hallazgo del dominio con **mejor relación esfuerzo/impacto** cuando sale, y el que más veces no sale. Por eso se decide rápido con una muestra chica: si veinte tokens no muestran ninguna estructura, se abandona esta vía.

## Por qué funciona

Porque impredecible es una propiedad difícil de conseguir por accidente y fácil de romper sin darse cuenta.

Las tres formas, todas frecuentes en código propio: el generador de azar de propósito general del lenguaje, que es determinista y cuyo estado interno se reconstruye observando salidas; el valor derivado de datos conocidos —marca de tiempo, identificador de usuario, contador— donde pasarlo por un hash no agrega entropía porque la entrada sigue siendo adivinable; y el valor genuinamente aleatorio pero **corto**, que simplemente se recorre entero.

Lo que distingue a esta técnica de todo el resto del dominio: **no necesita víctima**. Robar una sesión requiere un XSS, una red o un descuido; predecirla no requiere nada más que el algoritmo. Y escala sola — quien predice una, predice todas, incluidas las administrativas.

## Cómo falla

- **Generador criptográfico con 128 bits** — la mitigación, y es lo que hace cualquier marco de trabajo moderno. Cierra la vía por completo.
- **Los tokens no muestran estructura** — el caso normal. Se descarta rápido y se sigue con otra rama del árbol.
- **La entropía es alta pero el generador es débil** — teóricamente explotable, prácticamente inviable: reconstruir el estado interno de un generador exige muchas muestras consecutivas y sin huecos, y en un sistema con otros usuarios activos los huecos son inevitables.
- **No se pueden pedir tokens suficientes** — el análisis necesita decenas o cientos, y el control de ritmo lo impide.
- **Hay validación adicional** — token atado a la IP, a la huella del cliente o a un segundo valor. Predecirlo no alcanza.

## Coste

Alto, y con probabilidad baja de éxito. Es una apuesta: la mayoría de las veces el análisis termina en "es aleatorio" después de una hora. Por eso conviene el descarte temprano — una muestra chica decide si vale seguir.

## Huella esperada

Es la variante **más silenciosa de todo el vault**, y por una razón estructural: un token predicho es indistinguible de uno legítimo. No hay nada que detectar en el uso.

- La fase de **recolección** sí es visible: decenas o cientos de peticiones pidiendo sesión nueva desde un mismo origen en poco tiempo. Ningún usuario hace eso, y es la única ventana de detección que existe.
- El uso posterior no genera ninguna anomalía: el token es válido, la sesión existe, el servidor la reconoce.
- Lo único que queda del lado azul es lo contextual, igual que en [[Autenticación - credential stuffing]]: la sesión de un usuario apareciendo desde un origen que no es el suyo.

Esa asimetría —recolección ruidosa, uso invisible— es lo que hace que la detección tenga que estar en la fase de recolección o no esté en ningún lado.

El análisis concreto está en [[Sesión - matriz de referencia]] § Análisis del token.
