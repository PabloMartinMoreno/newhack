---
tipo: meta
aliases:
  - reconocimiento GraphQL
  - detectar GraphQL
  - graphw00f
tags:
  - meta/referencia
  - dominio/web
---

# GraphQL - matriz de reconocimiento

> [!info] Referencia pura, no un zettel
> Encontrar el endpoint, sacar el esquema, y reconstruirlo cuando la introspección está apagada. La explotación está en [[GraphQL - matriz de explotación]]; el criterio, en [[MOC - GraphQL]].

## 1. Encontrar el endpoint

Rutas comunes:

`/graphql` · `/graphiql` · `/graphql/console` · `/api/graphql` · `/v1/graphql` · `/query` · `/gql` · `/graphql.php` · `/index.php?graphql`

Detectar que un endpoint es GraphQL:

```sh
curl -s https://objetivo/graphql -H 'Content-Type: application/json' -d '{"query":"{__typename}"}'
```

Respuesta con `{"data":{"__typename":"Query"}}` → es GraphQL. Un error que mencione `query` o `must provide query string` también confirma.

`?query={__typename}` por GET, si acepta GET.

## 2. La consulta de introspección

La completa —la que traen las herramientas— es larga; esta versión reducida saca lo esencial:

```graphql
{
  __schema {
    types {
      name
      fields { name args { name type { name } } }
    }
    queryType { name }
    mutationType { name }
  }
}
```

Sacar solo las mutaciones —la lista de acciones que cambian estado:

```graphql
{ __schema { mutationType { fields { name args { name } } } } }
```

Interrogar un tipo concreto:

```graphql
{ __type(name:"User") { fields { name type { name kind } } } }
```

## 3. Herramientas

| Herramienta | Para qué |
|---|---|
| **GraphiQL** / **GraphQL Playground** | Si están expuestas, dan el esquema y autocompletado en el navegador |
| **InQL** (extensión de Burp) | Introspección, genera plantillas de consulta y mutación |
| **graphql-voyager** | Dibuja el esquema como grafo, útil para ver relaciones circulares |
| **Clairvoyance** | Reconstruye el esquema por sugerencia de campos cuando la introspección está apagada |
| **graphw00f** | Identifica qué motor GraphQL es (Apollo, Hasura, graphql-ruby…) |

Identificar el motor con graphw00f vale la pena: cada implementación tiene defensas y comportamientos por defecto distintos —cuál permite lotes, cuál sugiere campos, cuál trae límite de profundidad.

## 4. Cuando la introspección está apagada

La respuesta a `__schema` viene con un error tipo `introspection is disabled`. El esquema se reconstruye igual — ver [[GraphQL - introspección del esquema]].

**Sugerencia de campos.** Mandar un campo mal escrito y leer la corrección:

```graphql
{ user { usrname } }
```

Respuesta: `Cannot query field "usrname" on type "User". Did you mean "username"?` — cada sugerencia confirma nombres válidos. Clairvoyance lo automatiza contra un diccionario.

**Detectar si la sugerencia está activa** antes de invertir: un campo obviamente inexistente que devuelva "did you mean" significa que sirve.

**Fuerza bruta de nombres**, cuando ni la sugerencia está: probar nombres de campo comunes y ver cuáles no dan error de "campo desconocido".

## 5. Mapear la superficie de ataque

Con el esquema, clasificar antes de explotar:

| Buscar en el esquema | Para la rama |
|---|---|
| Campos sensibles no expuestos en la UI (`passwordHash`, `isAdmin`, `email`) | [[GraphQL - autorización rota en resolvers]] |
| Mutaciones no listadas (`deleteUser`, `setRole`, `updateAny`) | misma |
| Relaciones circulares (`User.posts.author.posts…`) | [[GraphQL - denegación por complejidad]] |
| Mutaciones de login / verificación de OTP | [[GraphQL - lotes y alias]] |
| Argumentos que parecen llegar a una consulta (`filter`, `where`, `orderBy`, `id`) | inyección — ver [[GraphQL - matriz de explotación]] § inyección |

## 6. Método de transporte

| Forma | Cómo |
|---|---|
| POST JSON | `{"query":"...","variables":{}}` — lo normal |
| POST con `operationName` | Cuando hay varias operaciones en el documento |
| GET | `?query=...` — a veces habilitado, y **cacheable**, se cruza con [[MOC - Web cache]] |
| Lote | `[{"query":"..."},{"query":"..."}]` — array, si el servidor lo acepta → [[GraphQL - lotes y alias]] |

Probar si acepta GET y si acepta lotes es parte del reconocimiento: los dos habilitan ramas enteras.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `must provide query string` | Es GraphQL, mandá un `query` válido |
| `introspection is disabled` | Reconstruir por sugerencia, § 4 |
| `Did you mean "..."` | La sugerencia está activa: Clairvoyance |
| Sin sugerencias y sin introspección | Solo fuerza bruta de nombres |
| `{"data":{"__typename":"Query"}}` | Confirmado GraphQL |
| El lote devuelve un solo resultado | No soporta lotes; probar alias en su lugar |
| GET rechazado | Solo POST; no hay cruce con caché |

## Relacionadas

[[MOC - GraphQL]] · [[GraphQL - matriz de explotación]] · [[GraphQL - introspección del esquema]] · [[Control de acceso - matriz de pruebas]]
