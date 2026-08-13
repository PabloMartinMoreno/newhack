---
tipo: tecnica
taxonomia: cwe
identificador: CWE-770
wstg: WSTG-BUSL-09
tacticas: []
aliases:
  - CWE-770
  - resource exhaustion
  - denegación por complejidad
tags:
  - dominio/web
---

# CWE-770 - Allocation of Resources Without Limits or Throttling

> [!note] Nota paraguas
> Sin contenido operativo. Su uso en GraphQL vive en [[GraphQL - denegación por complejidad]]; los payloads, en [[GraphQL - matriz de explotación]].

## Qué es

La aplicación reserva recursos —memoria, CPU, conexiones a la base, tiempo— en proporción a lo que el usuario pide, sin un límite superior. Una sola petición cuidadosamente armada consume lo que debería costar miles, y con pocas peticiones se agota el servidor.

## Por qué es una clase propia de GraphQL

REST acota el trabajo por endpoint: cada URL hace una cosa de tamaño conocido. GraphQL le da al **cliente** el control de la forma de la consulta, y esa libertad es la superficie. El cliente decide qué campos pedir, cuántas relaciones seguir, y a qué profundidad — y si el servidor no pone límites, decide también cuánto trabajo se hace.

Dos formas, las dos en [[GraphQL - denegación por complejidad]]:

- **Profundidad.** Si el tipo A referencia a B y B referencia a A, una consulta puede pedir `A.B.A.B.A.B…` decenas de niveles. Cada nivel multiplica el trabajo, y unas pocas líneas generan una explosión combinatoria.
- **Amplitud y alias.** Pedir el mismo campo caro cientos de veces con alias distintos, o expandir listas anidadas, multiplica la carga en una sola petición.

## Por qué también amplifica otros ataques

`CWE-770` en GraphQL no es solo denegación de servicio. La misma falta de límite sobre **cuántas operaciones** entran en una petición es lo que habilita el abuso de lotes: mil intentos de login en un solo mensaje HTTP. Ahí la clase se cruza con [[CWE-307 - Improper Restriction of Excessive Authentication Attempts]] — ver [[GraphQL - lotes y alias]]. La falta de límite es la misma; cambia si el recurso agotado es el servidor o el control de tasa.

## Por qué la mitigación es de límites, no de validación

No hay entrada maliciosa que filtrar: la consulta es válida, solo es cara. La mitigación es poner techos:

- **Límite de profundidad** de la consulta.
- **Análisis de costo/complejidad** antes de ejecutar, rechazando lo que supere un presupuesto.
- **Límite de cantidad** de operaciones por petición, contra los lotes y los alias.
- Tiempo máximo y paginación obligatoria en las listas.

## Referencias canónicas

- [CWE-770](https://cwe.mitre.org/data/definitions/770.html)
- WSTG-BUSL-09
- OWASP API Security — API4 Unrestricted Resource Consumption
