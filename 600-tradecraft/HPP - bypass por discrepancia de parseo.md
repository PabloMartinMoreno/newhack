---
tipo: tradecraft
clase: "[[CWE-235 - Improper Handling of Extra Parameters]]"
eje: uso-de-la-discrepancia
implementacion: "Duplicar un parámetro para que el filtro valide un valor inocente y la aplicación use el malicioso"
opsec: ruidoso
telemetria: ["[[Registro del WAF]]", "[[Log de acceso del servidor web]]"]
requisitos: [dos-capas-que-resuelven-el-duplicado-distinto]
coste: bajo
alternativas: ["[[HPP - inyección de parámetros]]", "[[Command injection evasión - matriz de referencia]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - HPP WAF bypass
  - bypass por parámetro duplicado
tags:
  - dominio/web
---

# HPP - bypass por discrepancia de parseo

## Cuándo lo elijo

Cuando hay un filtro, un WAF o un control de autorización que valida un parámetro, y se sospecha que la validación y el uso resuelven un duplicado distinto. Se reconoce probando `?x=1&x=2` y viendo qué valor usa la aplicación —el primero, el último, concatenado—, y comparándolo con qué valida el filtro.

El objetivo es **colar un valor que el filtro bloquearía**: se pone el inocente donde el filtro mira y el malicioso donde la aplicación mira. Es sobre todo una técnica de evasión al servicio de otra inyección. Si el objetivo es agregar parámetros nuevos a una petición que la aplicación construye, la rama es [[HPP - inyección de parámetros]].

## Por qué funciona

La cadena de componentes —WAF, marco de trabajo, backend— resuelve un parámetro duplicado de formas distintas, y la tabla de [[HPP - matriz de referencia]] dice cuál hace qué. El caso clásico:

```
?buscar=inocuo&buscar=' OR '1'='1
```

Si el WAF toma el **primer** valor (`inocuo`) para validar y la aplicación toma el **último** (`' OR '1'='1`) para ejecutar, el payload de SQLi pasa el WAF sin que este lo vea. El WAF valida una cosa, la base ejecuta otra.

Los usos:

- **Evadir un WAF** para cualquier inyección: SQLi, XSS, command. HPP es el sobre que mete el payload donde el WAF no mira. Se combina con las evasiones de cada dominio.
- **Saltar validación de lógica**: `precio=100&precio=1` si la validación mira el primero y el cobro el último.
- **Bypass de autorización**: `rol=usuario&rol=admin` cuando la comprobación y el uso discrepan.

La resolución también cambia con la **codificación del separador**: un `&` literal contra `%26` contra `;` los tratan distinto según el componente, lo que da más combinaciones para encontrar la discrepancia. Está en la matriz.

## Cómo falla

Falla cuando la cadena resuelve los duplicados **igual en todas las capas** —el WAF y la aplicación toman el mismo valor—, así que no hay dónde esconder el payload. Es la mitigación correcta.

Falla cuando el borde **normaliza** los parámetros duplicados —rechaza la petición o se queda con uno— antes de que lleguen a la aplicación.

Y falla cuando el WAF valida **después** de resolver el duplicado, mirando el mismo valor que usará la aplicación.

## Coste

Bajo. Descubrir la resolución de cada capa son pocas peticiones con `?x=1&x=2` y variantes de codificación. Una vez conocida la discrepancia, colar el payload es mecánico.

El costo depende de qué inyección se quiera colar detrás: HPP es el vehículo, y el payload sale del dominio correspondiente. Si no hay discrepancia entre capas, la técnica no aporta y hay que evadir el WAF por otro lado.

## Huella esperada

Firma clara y un punto ciego irónico:

- La petición lleva **el mismo parámetro dos veces**, visible en [[Log de acceso del servidor web]] si registra la query completa y en [[Registro del WAF]]. Un parámetro duplicado con un valor inocente y otro con un payload es la firma —aunque algunos usos legítimos duplican parámetros, un duplicado donde uno es un payload de inyección no es normal—.
- **El punto ciego es el propio WAF.** Si el WAF valida el primer valor y la aplicación usa el segundo, el WAF **no ve el ataque** —por construcción registra el valor inocente que validó—. Es la ironía del dominio: la herramienta que debería detectar la inyección es la que la deja pasar, porque mira el valor equivocado. La detección tiene que estar en un componente que vea **todos** los valores del parámetro y valide cada uno, no solo el que su resolución elige.

Es una firma escribible —alertar parámetros duplicados con valores discrepantes— pero con la vuelta de que el WAF, la fuente natural, es justo el que la técnica ciega. Refuerza el patrón de discrepancia de parseo de [[MOC - Request smuggling]]: la defensa falla cuando dos componentes ven cosas distintas. Anotado en [[MOC - HTTP parameter pollution]].
