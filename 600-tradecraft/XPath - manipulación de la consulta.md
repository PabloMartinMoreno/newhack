---
tipo: tradecraft
clase: "[[CWE-643 - XPath Injection]]"
eje: canal
implementacion: "Cerrar la comilla y balancear la expresión para volverla siempre-verdadera o ampliar el conjunto de nodos"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Registro del WAF]]"]
requisitos: [entrada-en-una-expresión-xpath-sin-escapar]
coste: bajo
alternativas: ["[[XPath - extracción ciega]]", "[[SQLi - canal UNION]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - XPath auth bypass
  - XPath always true
tags:
  - dominio/web
---

# XPath - manipulación de la consulta

## Cuándo lo elijo

Es el caso base del dominio y el primero a probar. Se reconoce cuando la aplicación consulta datos guardados en XML —un login contra un archivo de usuarios, una búsqueda en un catálogo XML, una configuración— y la entrada llega a una expresión XPath sin escapar. Se confirma metiendo una comilla simple y viendo si la expresión se rompe.

El objetivo natural es el **salto de autenticación**, idéntico al de SQLi: volver la condición siempre-verdadera. Cuando el resultado se refleja, la misma manipulación amplía el conjunto de nodos para devolver más datos. Si no se refleja y hay que inferir, la rama es [[XPath - extracción ciega]].

## Por qué funciona

La consulta es una cadena con comillas, como en SQL, y la entrada cae dentro de un valor entre comillas. Romperla es cerrar la comilla y agregar lógica booleana:

```
//usuario[nombre='INPUT' and clave='INPUT']
```

**Salto de autenticación:**
```
nombre = ' or '1'='1
→ //usuario[nombre='' or '1'='1' and clave='...']
```

`' or '1'='1` vuelve la condición verdadera. La diferencia con SQLi es que **no hay comentario** para descartar el resto: hay que **balancear** las comillas para que la expresión quede válida hasta el final. Por eso el payload cierra el `clave='...'` también, dejando todo sintácticamente correcto:

```
nombre = ' or '1'='1' or 'a'='a
→ //usuario[nombre='' or '1'='1' or 'a'='a' and clave='...']
```

**Devolver el primer usuario sin conocerlo:**
```
' or position()=1 or '
```

**Ampliar el conjunto de nodos** cuando se refleja, para leer de más:
```
' or true() or '
→ devuelve todos los nodos usuario
```

Los payloads por contexto —dónde cae la entrada, cómo balancear— están en [[XPath consulta - matriz de referencia]]. Como en LDAP, la forma exacta de la consulta casi nunca se ve y se infiere probando qué balanceo la deja válida.

Una ventaja sobre SQLi: **no hay control de acceso dentro del documento**. Una vez que se amplía el conjunto de nodos, se llega a todo el XML —no hay "otras tablas" que requieran `UNION`—, así que la divulgación es más directa.

## Cómo falla

Falla cuando la aplicación **escapa las comillas** de la entrada o usa consultas XPath parametrizadas: sin poder cerrar la cadena, no hay inyección. Es la mitigación directa.

Falla cuando hay un segundo control —si la aplicación verifica la contraseña por separado después de la búsqueda—, igual que en LDAP: el salto en la búsqueda no basta si hay una comprobación real de la clave después.

Y falla, en el sentido de que se complica, cuando el balanceo de comillas es difícil porque la consulta tiene una estructura anidada: ahí hay que razonar la expresión, pero sigue siendo trabajo de minutos con el catálogo de payloads.

## Coste

Bajo. El salto de autenticación son unas pocas peticiones probando cierres y balanceos —`' or '1'='1`, `' or true() or '`—. El catálogo cubre la mayoría de las estructuras, y quien conoce SQLi reconoce el patrón de inmediato.

El único costo que sube es acertar el balanceo cuando la consulta es compleja, pero no hay motor pesado detrás: es razonar comillas.

## Huella esperada

Firma clara y un efecto anómalo, idénticos a los de las hermanas de inyección:

- La entrada lleva **sintaxis de XPath** —`' or `, `true()`, `position()`, `count(`— en un campo que normalmente es un nombre o una búsqueda. Esa sintaxis no aparece en tráfico legítimo, así que es una firma de buena fidelidad sobre el cuerpo, que ve [[Registro del WAF]]. Es la misma clase de firma que la comilla de [[SQLi contextos - matriz de referencia]] y el `*)(` de [[LDAP - manipulación del filtro]].
- El salto de autenticación deja **un login exitoso sin la contraseña correcta** en [[Log de autenticación de la aplicación]], y como en SQLi, NoSQL y LDAP, **acierta a la primera sin ráfaga de fallos**, así que la detección por volumen no lo ve: solo la firma lo delata.

Es la cuarta hermana con la misma cara azul: firma de sintaxis de consulta sobre el cuerpo, más el salto silencioso. Refuerza la conclusión de [[MOC - LDAP injection]] —una sola detección de firma de inyección cubriría a las cuatro—, anotada en [[MOC - XPath injection]].
