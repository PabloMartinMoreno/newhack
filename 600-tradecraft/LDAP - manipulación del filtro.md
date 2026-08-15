---
tipo: tradecraft
clase: "[[CWE-90 - LDAP Injection]]"
eje: canal
implementacion: "Cerrar el filtro y reescribir su lógica booleana con paréntesis, operadores y comodín para saltar la autenticación o ampliar el resultado"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Registro del WAF]]"]
requisitos: [entrada-en-un-filtro-ldap-sin-escapar]
coste: bajo
alternativas: ["[[LDAP - extracción ciega]]", "[[NoSQL - inyección de operador]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - LDAP auth bypass
  - filter injection
tags:
  - dominio/web
---

# LDAP - manipulación del filtro

## Cuándo lo elijo

Es el caso base del dominio y el primero a probar. Se reconoce cuando la aplicación autentica o busca contra un directorio —login corporativo, búsqueda de usuarios, listas de contactos— y la entrada llega a un filtro LDAP sin escapar. Se confirma metiendo un `*` o un `)` y viendo si la respuesta cambia o el filtro se rompe.

El objetivo natural es el **salto de autenticación**: reescribir el filtro para que sea siempre-verdadero. Cuando el resultado sí se refleja, la misma manipulación amplía la búsqueda para devolver más objetos o atributos de los previstos. Si el resultado no se refleja y hay que inferir, la rama es [[LDAP - extracción ciega]].

## Por qué funciona

El filtro está en notación prefija con paréntesis, y la entrada cae dentro de un término. Manipularla es **cerrar el término, cerrar el filtro, y agregar la lógica propia**. Los dos patrones centrales:

**Comodín en la contraseña.** Si el filtro es `(&(uid=INPUT)(userPassword=INPUT))`, poner `*` en la contraseña la vuelve "cualquiera":

```
uid=admin, pass=*   →  (&(uid=admin)(userPassword=*))   → entra si admin existe
```

**Cerrar y anular.** Inyectar en el `uid` para cerrar la comprobación de contraseña antes de que aparezca:

```
uid = admin)(&))   →  (&(uid=admin)(&))(userPassword=...))
```

El `(&)` es un filtro siempre-verdadero, y lo que sigue queda fuera de la evaluación. El resultado es login como `admin` sin su contraseña.

**Siempre-verdadero sin usuario:**

```
uid = *)(uid=*   →  (&(uid=*)(uid=*)...)   → devuelve el primer usuario
```

Los patrones por contexto —dónde cae la entrada, qué hay que cerrar— están en [[LDAP filtro - matriz de referencia]]. El trabajo es identificar la forma del filtro original, que casi nunca se ve, probando qué cierres hacen que la inyección funcione.

Cuando el resultado se refleja, cambiar `&` por `|` o inyectar términos con `*` amplía la búsqueda: `(|(uid=INPUT)(uid=*))` devuelve todos los usuarios en vez de uno, que es divulgación de directorio.

## Cómo falla

Falla cuando la aplicación **escapa los metacaracteres** de LDAP —`(`, `)`, `*`, `\`— en la entrada: sin poder meter un paréntesis ni un asterisco, no hay forma de reescribir el filtro. Es la mitigación directa.

Falla contra consultas parametrizadas o APIs que separan la entrada de la estructura del filtro.

Y falla cuando hay un segundo control —un bind real contra el directorio con la contraseña, no solo una búsqueda—: si la aplicación busca el usuario y **después** intenta autenticar con la contraseña provista, el comodín en la búsqueda no basta porque el bind con la contraseña falsa falla igual. Distinguir "busca y compara" de "busca y luego hace bind" es parte del reconocimiento.

## Coste

Bajo. El salto de autenticación son unas pocas peticiones probando cierres —`*`, `admin)(&))`, `*)(uid=*`—. La forma exacta del filtro se infiere por prueba y error, y hay un catálogo acotado de payloads que cubre la mayoría de los casos.

El único costo que sube es cuando el filtro es complejo o hay varias comprobaciones anidadas: ahí hay que razonar la estructura, pero sigue siendo trabajo de minutos, no de herramienta pesada.

## Huella esperada

Firma clara y un efecto anómalo:

- La entrada lleva **metacaracteres de filtro LDAP** —`*`, `)(`, `)(&`, `)(|`— en un campo que normalmente es un nombre de usuario o una búsqueda. Esos caracteres en un `uid` no aparecen en tráfico legítimo, así que es una firma de buena fidelidad sobre el cuerpo o el parámetro, que ve [[Registro del WAF]]. Es la misma clase de firma que la clave `$` de [[NoSQL - inyección de operador]] y el `__proto__` de [[MOC - Prototype pollution]]: la anomalía no tiene forma legítima.
- El salto de autenticación deja **un login exitoso sin la contraseña correcta** —un bind o una autorización que no debería haber pasado—, en [[Log de autenticación de la aplicación]]. Como en NoSQL, el salto acierta a la primera y **no deja ráfaga de fallos**, así que la detección por volumen no lo ve: solo la firma del metacarácter lo delata.

Cuarto dominio de inyección donde la firma sobre el cuerpo es la señal real y depende de instrumentarlo. Anotado en [[MOC - LDAP injection]] como candidato, junto con la firma hermana de NoSQL.
