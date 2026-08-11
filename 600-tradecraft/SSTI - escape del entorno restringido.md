---
tipo: tradecraft
clase: "[[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]]"
eje: capacidad-del-motor
implementacion: "Trepar el grafo de objetos del lenguaje desde un objeto expuesto hasta una primitiva peligrosa"
opsec: ruidoso
telemetria: ["[[Proceso hijo del servidor web]]", "[[Log de errores del servidor web]]", "[[Conexión saliente del servidor de aplicación]]"]
requisitos: [motor-con-entorno-restringido, acceso-a-atributos-de-objeto]
coste: alto
alternativas: ["[[SSTI - ejecución directa]]", "[[SSTI - lectura sin ejecución]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - sandbox escape
  - Jinja2 SSTI
tags:
  - dominio/web
---

# SSTI - escape del entorno restringido

## Cuándo lo elijo

Cuando el motor evalúa expresiones pero no expone ejecución directa: Jinja2 estándar, Twig sin extensiones peligrosas, Handlebars con ayudantes, Nunjucks. La señal es que `{{7*7}}` devuelve `49` y el payload documentado de ejecución devuelve un error de atributo prohibido o de indefinido.

Es la rama cara del dominio, y conviene entrar sabiéndolo: si la aplicación no vale una escalada a ejecución, [[SSTI - lectura sin ejecución]] resuelve más rápido con menos ruido.

## Por qué funciona

El entorno restringido bloquea nombres, no **caminos**. Prohíbe escribir `os` o `import`, y a la vez deja acceder a los atributos de los objetos que sí expone. Como en estos lenguajes todo objeto lleva referencias a su clase, y toda clase a su jerarquía, desde cualquier objeto se llega al resto del intérprete.

El recorrido es siempre el mismo, y entenderlo una vez sirve para todos los motores del mismo lenguaje:

1. Partir de un objeto cualquiera que la plantilla exponga — una cadena vacía, un diccionario, la configuración.
2. Subir a su clase, y de ahí a la raíz de la jerarquía de tipos.
3. Enumerar las subclases de esa raíz: son **todas** las clases cargadas en el proceso.
4. Elegir una que envuelva algo peligroso —lectura de archivos, ejecución de subprocesos, importación— e invocarla.

Ese es todo el método. Los payloads que circulan son ese recorrido escrito para un motor y una versión, y por eso se rompen tan seguido: el índice de la subclase útil cambia con las dependencias instaladas.

**Conviene enumerar en vez de copiar el índice.** Pedir la lista de subclases y buscar por nombre cuesta una petición más y sobrevive a cualquier cambio de versión; un payload con un número fijo adentro funciona en el laboratorio y falla en producción.

La otra vía, más corta cuando está disponible, es abusar de un objeto que el propio marco de trabajo expone —la configuración de la aplicación, un objeto de petición, un ayudante de la plantilla— porque suelen traer métodos que leen archivos o evalúan cadenas sin necesidad de trepar nada.

## Cómo falla

Falla cuando el motor filtra el acceso a atributos que empiezan con guion bajo, que es el bloqueo estándar contra este recorrido. Hay vueltas —acceso por corchetes, por concatenación de cadenas, por atributos alternativos— y están en la matriz, pero cada capa de filtro agrega peticiones y algunas configuraciones cierran la rama de verdad.

Falla cuando el largo del campo no alcanza. Estos payloads son largos y hay campos que truncan; a veces se resuelve encadenando dos inyecciones o usando el objeto de configuración, que es mucho más corto.

Y falla cuando el entorno restringido está bien construido y la aplicación no expone nada útil. Es un resultado legítimo: se documenta el SSTI con la lectura que sí se consiguió y se cierra.

## Coste

Alto, y es el que más peticiones consume de todo el dominio web del vault. Enumerar subclases devuelve respuestas enormes que hay que filtrar, y cada capa de filtro del motor obliga a reescribir el payload entero.

Conviene fijar un presupuesto antes de empezar —quince o veinte peticiones— y si no salió, bajar a lectura de archivos. La escalada a ejecución es tentadora y es donde se va la tarde.

## Huella esperada

Es la variante más ruidosa del dominio por volumen, no por firma. La enumeración de subclases genera respuestas gigantes y muchos errores intermedios: [[Log de errores del servidor web]] se llena de excepciones de atributo indefinido, cada una con el nombre de la plantilla.

Cuando el escape funciona, la huella pasa a ser la de la ejecución: proceso hijo del servidor web, o una conexión saliente si el payload elegido descarga la segunda etapa en vez de ejecutar en línea. Las dos ya tienen detección propia.

Hay un caso sin huella y conviene tenerlo presente: si el escape se usa solo para **leer** —archivos de configuración, variables de entorno— no nace ningún proceso ni sale ninguna conexión. Queda únicamente el ruido del reconocimiento previo, que es exactamente el patrón de [[Ráfaga de errores del servidor desde un mismo origen]] y la única ventana de detección real.
