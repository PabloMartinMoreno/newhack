---
tipo: tradecraft
clase: "[[CWE-639 - Authorization Bypass Through User-Controlled Key]]"
eje: direccion
implementacion: "Cambiar el identificador de un objeto para alcanzar recursos de otro usuario"
opsec: limpio
telemetria: ["[[Log de auditoría de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [dos-cuentas-o-identificador-conocido, sesion-valida]
coste: bajo
alternativas: ["[[Control de acceso - escalada vertical]]"]
probado: nunca
contexto: [api-rest]
aliases:
  - acceso horizontal
  - referencia directa a objeto
tags:
  - dominio/web
---

# Control de acceso - IDOR

## Cuándo lo elijo

Primero, en cuanto hay dos cuentas. Es el hallazgo más frecuente de toda la web y el más barato de buscar: se pide un recurso con la sesión de A usando el identificador de B, y se mira si vuelve.

La condición que lo hace eficiente es tener **dos cuentas del mismo nivel**. Con una sola hay que adivinar identificadores y no se sabe qué debería devolver el sistema; con dos, cada endpoint se prueba en un minuto y la respuesta es inequívoca. Conseguir la segunda cuenta al inicio del engagement es la decisión que más rinde en este dominio.

Si el identificador no es predecible, no se descarta: se busca dónde se filtra. Ver [[Control de acceso bypass - matriz de referencia]] § Identificadores.

## Por qué funciona

Autenticar y autorizar son capas distintas y solo la primera es transversal. La sesión se valida una vez, en un punto que cubre toda la aplicación; la propiedad del objeto hay que verificarla en **cada consulta**, escrita a mano, y basta que falte en una.

Lo que hace a este dominio distinto de todos los anteriores del vault: **no hay nada que romper**. No se evade un parser ni se escapa de un contexto. La petición es sintácticamente perfecta y semánticamente legítima; lo único fuera de lugar es quién la manda. Por eso ningún WAF lo ve y ninguna herramienta automática lo encuentra sin entender el modelo de datos.

## Cómo falla

- **El identificador no es predecible y no se filtra en ningún lado** — hay que encontrar la fuga primero, y a veces no existe.
- **El control está bien puesto en el endpoint probado** — y mal en otro. La conclusión correcta no es "no hay IDOR" sino "no hay en este endpoint": la cobertura desigual es la norma.
- **La respuesta es idéntica para autorizado y no autorizado** — algunas apps devuelven `404` tanto para "no existe" como para "no es tuyo". Correcto de su parte, y obliga a buscar oráculos por tiempo o por efecto lateral.
- **Solo se filtra en la vista** — el objeto se devuelve completo por la API y la interfaz lo recorta. Al revés de lo que parece, esto es un hallazgo, no una defensa.
- **Rate limiting** — enumerar identificadores secuenciales dispara los límites. Buscar la existencia del fallo no los necesita; extraer masivamente, sí.

## Coste

Bajísimo en esfuerzo por endpoint y **alto en cobertura**: la vulnerabilidad puede estar en cualquiera de cientos de puntos, y encontrarla exige recorrerlos con método. El trabajo no es explotar, es no saltearse nada — por eso el dominio tiene [[Control de acceso - matriz de pruebas]] en vez de una matriz de payloads.

## Un límite que no es técnico

> [!warning] Los datos son de personas reales
> Confirmar el hallazgo requiere **un** objeto ajeno. Enumerar diez mil registros de clientes no aumenta la severidad del informe y sí convierte una prueba en una fuga de datos real, con obligaciones legales de notificación para el cliente.
>
> Se demuestra con el mínimo, se documenta el alcance potencial por cálculo, y se para. Si el alcance hay que probarlo, se acuerda por escrito antes.

## Huella esperada

`opsec: limpio` no significa indetectable: significa que **no hay nada técnicamente anómalo que detectar**. La sesión es válida, la petición está bien formada, la respuesta es `200`. Ni el WAF ni el log de acceso tienen de qué agarrarse.

- [[Log de auditoría de la aplicación]] es la única fuente que lo ve, y solo si registra **el dueño del objeto además del actor**. La detección es literalmente comparar esos dos campos.
- [[Log de acceso del servidor web]] muestra, si acaso, un patrón: muchas peticiones al mismo endpoint con el identificador variando de forma secuencial. Eso detecta la **enumeración masiva**, no el acceso puntual — que es el que un atacante real haría.
- Un pico en la cantidad de objetos distintos tocados por una misma sesión, comparado contra la línea base de esa cuenta, es la señal más robusta que existe acá.

El método sistemático está en [[Control de acceso - matriz de pruebas]]; los bypass, en [[Control de acceso bypass - matriz de referencia]].
