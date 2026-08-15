---
tipo: tradecraft
clase: "[[CWE-90 - LDAP Injection]]"
eje: canal
implementacion: "Extraer atributos carácter por carácter con el comodín, leyendo un oráculo booleano sobre la respuesta"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]"]
requisitos: [inyección-de-filtro-confirmada, un-oráculo-observable]
coste: alto
alternativas: ["[[LDAP - manipulación del filtro]]", "[[NoSQL - extracción ciega]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - LDAP blind
  - blind attribute extraction
tags:
  - dominio/web
---

# LDAP - extracción ciega

## Cuándo lo elijo

Cuando [[LDAP - manipulación del filtro]] confirmó que se puede inyectar pero la respuesta **no devuelve los datos** —solo cambia entre dos estados: login sí o no, resultado presente o ausente—. Es el paralelo exacto de [[NoSQL - extracción ciega]] y [[SQLi - canal booleano ciego]], con el comodín de LDAP como herramienta de coincidencia parcial.

Se llega acá desde el salto de filtro cuando el objetivo pasa de "entrar" a "sacar datos" —un correo, un rol, un atributo `memberOf`, un hash— y esos atributos no se reflejan.

## Por qué funciona

El comodín `*` convierte cualquier atributo en un oráculo. Un filtro que devuelve un estado distinto según si un atributo **coincide con un patrón** permite preguntar por el valor carácter por carácter:

```
(&(uid=admin)(mail=a*))    → ¿el correo de admin empieza con 'a'?
(&(uid=admin)(mail=b*))    → ¿con 'b'?
```

El estado de la respuesta —login exitoso o no, contenido presente o ausente— es el oráculo booleano. Se itera el patrón: fijado el primer carácter, se prueba el segundo (`aa*`, `ab*`…), hasta reconstruir el atributo entero.

El comodín también sirve para **enumerar qué atributos existen** antes de extraerlos:

```
(&(uid=admin)(mail=*))     → ¿admin tiene atributo mail?
(&(uid=admin)(memberOf=*)) → ¿pertenece a algún grupo?
```

Y para **enumerar usuarios**:

```
(&(uid=a*)(objectClass=*)) → ¿hay algún uid que empiece con 'a'?
```

Los patrones de extracción y de enumeración están en [[LDAP extracción ciega - matriz de referencia]]. La estructura es la misma que en NoSQL con `$regex`: lo único que cambia entre las inyecciones hermanas es la sintaxis del comodín.

Cuando no hay oráculo booleano —la respuesta es idéntica siempre— LDAP no tiene un canal temporal fácil como SQLi o NoSQL con JavaScript, así que la extracción ciega depende de que exista **algún** estado observable. Si no lo hay, el dominio se corta acá.

## Cómo falla

Falla contra el escape de metacaracteres, igual que la rama de filtro: sin poder inyectar el `*`, no hay oráculo.

Falla cuando la respuesta no tiene ningún estado observable —ni contenido, ni código, ni un login que dependa del atributo—: sin oráculo, la extracción no avanza, y LDAP no ofrece la salida temporal que sí tienen las otras inyecciones.

Y se encarece hasta lo impráctico con un límite de tasa: la extracción ciega son cientos o miles de consultas, y un control efectivo la vuelve inviable.

## Coste

Alto, el más alto del dominio. Extraer un atributo de largo desconocido del alfabeto completo son cientos de peticiones, y sin canal temporal el único acelerador es bisecar el alfabeto con rangos en el comodín. Es trabajo de script —`ldap-blind` o uno propio—, no manual.

Conviene medir antes: cuánto dato hay que sacar, si hay límite de tasa, si el oráculo es fiable. Si el objetivo era solo confirmar la inyección o entrar, el salto de filtro ya lo hizo y esta rama no hace falta.

## Huella esperada

La rama más ruidosa del dominio por volumen, y la que mejor se detecta **por agregado**:

- Cientos de consultas casi idénticas, variando un patrón de comodín, desde un mismo origen en poco tiempo. Es una firma de volumen clarísima —el mismo endpoint, diferencias mínimas en el filtro—, y la ve [[Log de acceso del servidor web]] aunque no registre el cuerpo, porque el **patrón de repetición** está en la cadencia.
- [[Registro del WAF]] ve además los metacaracteres de LDAP en el cuerpo, la misma firma que la rama de filtro pero repetida cientos de veces.

Es el mismo caso que [[NoSQL - extracción ciega]]: la detección por `forma: agregado` rinde sin instrumentar el cuerpo, porque la tasa de consultas casi idénticas es anómala por sí sola. Y la misma asimetría del dominio: el salto de filtro es silencioso —acierta a la primera—, la extracción ciega es ruidosa —cientos de intentos—. La rama barata es la más difícil de detectar, la cara es la más fácil. Anotado como candidato de detección en [[MOC - LDAP injection]].
