---
tipo: tradecraft
clase: "[[CWE-862 - Missing Authorization]]"
eje: direccion
implementacion: "Ejecutar funciones de mayor privilegio sin tener el rol"
opsec: limpio
telemetria: ["[[Log de auditoría de la aplicación]]", "[[Log de acceso del servidor web]]"]
requisitos: [sesion-valida, ruta-o-funcion-conocida]
coste: medio
alternativas: ["[[Control de acceso - mass assignment]]", "[[Control de acceso - IDOR]]"]
probado: nunca
contexto: [api-rest]
aliases:
  - escalada vertical
  - privilege escalation
  - forced browsing
tags:
  - dominio/web
---

# Control de acceso - escalada vertical

## Cuándo lo elijo

Cuando el objetivo no es ver lo de otro usuario sino **hacer lo que solo un administrador puede hacer**. Es el hallazgo de mayor severidad del dominio, porque el impacto no depende de cuántos objetos se alcancen: alcanza con una función.

El trabajo previo es de reconocimiento y determina todo lo demás: hay que **conocer la ruta**. Nadie rompe nada acá; se pide algo que existe y que no debería responder. Las fuentes están en [[Control de acceso bypass - matriz de referencia]] § Descubrir rutas.

Antes de asumir que la ruta está protegida, hay tres pruebas baratas que fallan muchísimas veces: otro verbo HTTP, otra versión de la API, y la ruta equivalente en otro prefijo. Ninguna es un truco: son inconsistencias reales de aplicaciones que crecieron por partes.

## Por qué funciona

Porque el control de acceso vertical suele estar puesto **donde se ve** y no donde se ejecuta.

El caso clásico es la interfaz: el botón de administración no se le muestra a quien no es administrador, y ahí terminó la protección. La ruta responde igual a cualquiera que la conozca. Es `forced browsing`, y sigue vivo décadas después porque ocultar y proteger se sienten igual desde el lado del desarrollador.

Los otros dos casos son de cobertura: un filtro protege un prefijo de rutas y la misma función vive además en otro; o el control se aplica a un verbo y no a los demás. En ambos, el control existe y no cubre todo. Por eso probar `POST` donde `GET` fue rechazado no es una casualidad afortunada: es el patrón.

## Cómo falla

- **El control está en el servidor y bien puesto** — devuelve `403` con cualquier verbo, ruta y cabecera. Es la mitigación correcta.
- **La ruta existe pero requiere parámetros que no se conocen** — responde `400` en vez de `403`, lo que confirma que no hay control y no alcanza para explotar. Sigue siendo un hallazgo reportable.
- **La función es administrativa pero está segmentada** — vive en otro host, solo accesible desde la red interna. Ahí el camino pasa por [[MOC - SSRF]].
- **El rol se valida contra el servidor en cada operación** — las manipulaciones de rol del lado del cliente no hacen nada.
- **La acción queda registrada con nombre y apellido.** A diferencia de [[Control de acceso - IDOR]], acá el impacto suele ser una escritura, y el registro de auditoría —cuando existe— la atribuye a la cuenta usada.

## Coste

Medio, y casi todo en reconocimiento. Explotar es una petición; encontrar la ruta puede llevar horas de leer JavaScript, comparar versiones de API y probar convenciones de nombres. La relación esfuerzo/impacto es la mejor del dominio.

## Un límite operativo

> [!danger] Confirmar sin ejecutar
> Una función administrativa **hace cosas**: borra usuarios, cambia permisos, mueve dinero. Confirmar que el control de acceso falta no requiere ejecutar la acción destructiva.
>
> Se busca la variante de solo lectura de la misma función administrativa, o se ejecuta sobre un objeto propio creado para eso. Si no hay forma no destructiva de demostrarlo, se documenta el razonamiento y se pide autorización explícita antes.

## Huella esperada

- [[Log de auditoría de la aplicación]] con una acción administrativa atribuida a una cuenta sin ese rol. Es de los indicadores más limpios que existen: **la anomalía está en el campo de rol, no en la petición**.
- [[Log de acceso del servidor web]] con peticiones a rutas administrativas desde sesiones que nunca las visitan. Si además hay una ráfaga de `404` y `403` previa, eso es el reconocimiento y precede al acceso exitoso por minutos.
- Un `200` en una ruta administrativa después de una serie de `403` en rutas parecidas es la firma completa: se ve el barrido y se ve dónde encontró el hueco.

El método está en [[Control de acceso - matriz de pruebas]]; el descubrimiento de rutas y los bypass, en [[Control de acceso bypass - matriz de referencia]].
