---
tipo: tradecraft
clase: "[[CWE-643 - XPath Injection]]"
eje: canal
implementacion: "Extraer el documento carácter por carácter con substring() y string-length(), leyendo un oráculo booleano"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]"]
requisitos: [inyección-xpath-confirmada, un-oráculo-observable]
coste: alto
alternativas: ["[[XPath - manipulación de la consulta]]", "[[SQLi - canal booleano ciego]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - XPath blind
  - substring extraction
tags:
  - dominio/web
---

# XPath - extracción ciega

## Cuándo lo elijo

Cuando [[XPath - manipulación de la consulta]] confirmó la inyección pero la respuesta **no devuelve los datos** —solo cambia entre dos estados—. Es el paralelo exacto de [[SQLi - canal booleano ciego]], [[NoSQL - extracción ciega]] y [[LDAP - extracción ciega]], y de las cuatro es la que **más se parece a la de SQLi**, porque XPath tiene funciones equivalentes a las de SQL.

Se llega acá desde el salto de consulta cuando el objetivo pasa de "entrar" a "leer el documento" y el contenido no se refleja.

## Por qué funciona

XPath tiene funciones de cadena que convierten cualquier nodo en un oráculo, casi idénticas a las de SQL:

- `string-length(X)` — el largo de un valor, para medir antes de extraer.
- `substring(X, pos, 1)` — un carácter en una posición.
- `count(X)` — cuántos nodos, para enumerar estructura.
- `name(X)` — el nombre de un nodo, para descubrir el esquema sin conocerlo.

El oráculo booleano se arma comparando:

```
' or substring(//usuario[1]/clave, 1, 1)='a' or '   → ¿el primer carácter es 'a'?
' or substring(//usuario[1]/clave, 1, 1)='b' or '
```

El estado de la respuesta —login sí/no, contenido presente/ausente— es el oráculo. Se itera la posición y el carácter, igual que en las hermanas.

**Medir el largo primero**, para no probar de más:
```
' or string-length(//usuario[1]/clave)=8 or '
```

**Enumerar la estructura del documento** —la gran ventaja de XPath, porque no hay control de acceso por nodo—:
```
' or count(/*)=1 or '                    → ¿cuántos nodos raíz?
' or name(/*[1])='usuarios' or '         → ¿cómo se llama la raíz?
' or count(//usuario)=5 or '             → ¿cuántos usuarios hay?
```

Con `name()` y `count()` se reconstruye el esquema entero del XML sin conocerlo, y después se extrae cada valor. Los patrones están en [[XPath extracción ciega - matriz de referencia]].

XPath 1.0 **no tiene canal temporal** —como LDAP, sin `sleep`—, así que la extracción ciega depende de un oráculo booleano. XPath 2.0 agrega funciones que a veces permiten otros canales, pero es menos común.

## Cómo falla

Falla contra el escape de comillas y las consultas parametrizadas, igual que la rama de manipulación.

Falla cuando no hay ningún estado observable en la respuesta: sin oráculo booleano y sin canal temporal (en XPath 1.0), la extracción no avanza.

Y se encarece con límite de tasa: extraer un documento entero son miles de consultas.

## Coste

Alto, el más alto del dominio. Extraer carácter por carácter sin canal temporal son cientos de peticiones por valor, y un documento entero son miles. El acelerador es la comparación con `>` para bisecar, y `string-length()` para no probar posiciones vacías. Es trabajo de herramienta —`xcat` automatiza la extracción ciega de XPath— o de script propio.

Conviene medir antes: cuánto documento hay que sacar, si hay oráculo fiable, si hay límite de tasa. Si el objetivo era entrar o confirmar, el salto de consulta ya lo hizo.

## Huella esperada

La rama más ruidosa del dominio por volumen, y la que mejor se detecta **por agregado** —idéntico a las tres hermanas—:

- Cientos o miles de consultas casi idénticas, variando la posición y el carácter de un `substring()`, desde un mismo origen. Es una firma de volumen clarísima que ve [[Log de acceso del servidor web]] por la cadencia, aunque no registre el cuerpo.
- [[Registro del WAF]] ve además las funciones XPath —`substring(`, `string-length(`, `count(`— repetidas en el cuerpo.

Es el mismo caso que las otras extracciones ciegas: `forma: agregado` sobre la repetición con variación mínima, detectable por volumen sin instrumentar el cuerpo. Y la misma asimetría del dominio: el salto de consulta es silencioso, la extracción ciega es ruidosa. Con esto son **cuatro dominios de inyección con la cara azul idéntica**, lo que cierra el argumento de [[MOC - LDAP injection]]: una detección de firma de inyección sobre el cuerpo y una de agregado de consultas casi idénticas cubrirían a las cuatro hermanas a la vez. Anotado en [[MOC - XPath injection]].
