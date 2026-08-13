---
tipo: tecnica
taxonomia: cwe
identificador: CWE-943
wstg: WSTG-INPV-05
tacticas: []
aliases:
  - CWE-943
  - NoSQL injection
  - inyección NoSQL
tags:
  - dominio/web
---

# CWE-943 - Improper Neutralization of Special Elements in Data Query Logic

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - NoSQL injection]]; los operadores en [[NoSQL operadores - matriz de referencia]]; la extracción ciega en [[NoSQL extracción ciega - matriz de referencia]].

## Qué es

La aplicación construye una consulta a una base de datos NoSQL —Mongo, Couch, Redis, Elasticsearch— mezclando entrada del usuario con la estructura de la consulta, sin separarlas. El atacante aporta elementos que el motor interpreta como **parte de la lógica de la consulta** en vez de como dato: operadores, expresiones, código.

Es la hermana de [[CWE-89 - SQL Injection]] en el mundo sin SQL. La clase padre es la misma —neutralización impropia en la lógica de una consulta— y muchos conceptos se trasladan: canal reflejado contra ciego, extracción carácter por carácter, salto de autenticación. Lo que cambia es la sintaxis y una diferencia estructural que ordena el dominio.

## Por qué no es SQLi con otra sintaxis

En SQL la consulta es una cadena, y la inyección es siempre romper esa cadena. En NoSQL —Mongo sobre todo— la consulta es a menudo un **objeto estructurado**, no una cadena, y eso abre una vía que en SQL no existe:

- **Inyección de operador.** Si la entrada se coloca en un objeto de consulta, el atacante no rompe una cadena: **cambia el tipo del dato**. Donde la aplicación espera `{"user": "admin"}` con una cadena, el atacante manda `{"user": {"$ne": null}}` con un objeto operador. No hay comilla que escapar; se contrabandea una estructura.
- **Inyección de JavaScript.** Algunos operadores —`$where`, `mapReduce`— evalúan JavaScript del lado del servidor. Ahí la entrada llega a un intérprete, y el dominio se acerca a la ejecución de código dentro del motor de la base.

La primera no tiene equivalente en SQLi y es la más común; la segunda es más rara y más grave. Esa bifurcación —manipular la estructura contra evaluar código— es el eje raíz del dominio.

## Por qué el contexto de entrada decide tanto

Que se pueda inyectar un operador depende de **cómo llega la entrada**:

- Un **cuerpo JSON** permite anidar objetos: `{"user": {"$ne": null}}` pasa tal cual. Es el caso fácil.
- Una **query string** llega como cadena, pero muchos frameworks la parsean a objetos —`user[$ne]=` se convierte en `{"user": {"$ne": ""}}`—, así que el operador se contrabandea igual.
- Una entrada que el código fuerza a cadena antes de la consulta cierra la inyección de operador y deja solo la de sintaxis.

Por eso el reconocimiento empieza por cómo se parsea la entrada, no por el motor.

## Por qué la mitigación no es escapar comillas

Escapar caracteres no sirve contra la inyección de operador, porque no hay caracteres que escapar: el ataque es un objeto bien formado. La mitigación es de tipo y de estructura:

- **Forzar el tipo** de la entrada a cadena antes de usarla en la consulta — un operador deja de poder colarse si el campo solo acepta texto.
- **Validar el esquema** de la entrada, rechazando claves que empiecen con `$` o que contengan `.`.
- **No usar** `$where` ni evaluación de JavaScript con entrada del usuario.
- Consultas parametrizadas donde el motor las ofrezca.

## Referencias canónicas

- [CWE-943](https://cwe.mitre.org/data/definitions/943.html)
- [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — SQL Injection, la hermana
- WSTG-INPV-05
- OWASP Top 10 — A03 Injection
