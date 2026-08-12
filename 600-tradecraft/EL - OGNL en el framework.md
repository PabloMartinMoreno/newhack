---
tipo: tradecraft
clase: "[[CWE-917 - Expression Language Injection]]"
eje: superficie
implementacion: "Abusar de que el framework evalúa como OGNL un parámetro, nombre de parámetro o cabecera que el desarrollador no marcó"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Conexión saliente del servidor de aplicación]]", "[[Log de errores del servidor web]]", "[[Registro del WAF]]"]
requisitos: [framework-que-evalua-entrada-como-el-por-diseño]
coste: bajo
alternativas: ["[[EL - reflejo directo en expresión]]", "[[EL - evaluación indirecta y ciega]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - Struts OGNL
  - framework EL injection
tags:
  - dominio/web
---

# EL - OGNL en el framework

## Cuándo lo elijo

Cuando la aplicación corre sobre un framework que **evalúa entrada como EL por diseño**, y la vulnerabilidad no está en el código de la aplicación sino en el framework mismo. El caso emblemático es Struts 2 con OGNL, pero el patrón reaparece en otros componentes que usan OGNL o SpEL para procesar la petición.

Se reconoce por la pila, no por un reflejo: si el reconocimiento identifica Struts 2, un componente de Spring que enruta con expresiones, o cualquier cosa que documente OGNL en su procesamiento de peticiones, esta rama es la primera a probar, y muchas veces hay un CVE con número asignado para la versión exacta.

Si la expresión la construye el código de la aplicación —no el framework—, la rama es [[EL - reflejo directo en expresión]] o [[EL - evaluación indirecta y ciega]] según se refleje o no.

## Por qué funciona

Struts 2 hizo célebre este patrón: el framework tomaba valores de la petición —parámetros, nombres de parámetros, la cabecera `Content-Type`, mensajes— y en ciertos flujos los evaluaba como OGNL. El desarrollador de la aplicación nunca escribió una expresión; el framework la evaluaba por él, sobre datos que venían del atacante.

De ahí una cadena de CVE críticos, cada uno un lugar distinto donde la entrada llegaba al evaluador:

- Un parámetro con un prefijo especial que forzaba la evaluación.
- El **nombre** de un parámetro, no su valor.
- La cabecera `Content-Type` en la subida de archivos.
- Mensajes de error que se reevaluaban.

El detalle que hace peligrosa esta rama es que el punto de entrada **no parece un campo de datos**: nadie audita el nombre de un parámetro o una cabecera esperando una expresión. Por eso los payloads son largos y específicos por CVE, y viven en [[EL injection payloads - matriz de referencia]] con la versión afectada.

Como OGNL da acceso directo a `Runtime`, cada uno de esos CVE es ejecución de comandos sin autenticación. Los de Struts estuvieron entre los más explotados en masa de la historia web, y siguen apareciendo en aplicaciones que no se parchearon.

## Cómo falla

Falla contra un framework parcheado a la versión donde ese punto de entrada se cerró. La explotación depende de la versión exacta, así que el reconocimiento de versión es lo que decide si la rama existe: un Struts al día no tiene estos agujeros.

Falla contra las mitigaciones que el framework agregó con el tiempo —listas blancas de clases en OGNL, restricción del contexto de evaluación—, que fueron endureciéndose CVE tras CVE.

Y falla, como toda la familia, si el sandbox del motor está activo y el payload no lo escapa.

## Coste

Bajo, cuando hay CVE. El reconocimiento de versión es una petición o dos —una traza de error, una ruta característica—, y si la versión es vulnerable el payload es público y probado. Es de las ramas de mayor retorno del vault: sin autenticación, ejecución directa, payload conocido.

El coste sube solo si hay que adaptar un payload público a una mitigación parcial de una versión intermedia, que es trabajo de precisión sobre la lista blanca de OGNL.

## Huella esperada

Ruidosa y bien cubierta, porque termina en ejecución y a menudo en salida a la red.

- El proceso hijo del servidor web lo ve [[Intérprete de comandos como hijo del servidor web]].
- Si el payload descarga una segunda etapa, la conexión saliente la ven las reglas de SSRF sobre [[Conexión saliente del servidor de aplicación]].
- Los payloads de estos CVE son **cadenas OGNL largas y muy características** —`(#_memberAccess=...)`, `@java.lang.Runtime@`— que aparecen en la URL, en una cabecera o en el cuerpo. Es de los pocos casos donde una firma rinde: esas cadenas no existen en tráfico legítimo, y las reglas de WAF las conocen. Lo cubre [[Payload de inyección en parámetros de la URL]] y sobre todo [[Registro del WAF]], que ve el cuerpo y las cabeceras que el log de acceso no registra.

La contracara es la de siempre con las firmas: el payload por el cuerpo de un `POST` o en una cabecera solo lo ve el WAF, no [[Log de acceso del servidor web]]. Y estos CVE precisamente entraban por cabeceras y cuerpos, así que la fuente de firma tiene que ser la que mira ahí.
