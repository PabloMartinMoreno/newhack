---
tipo: moc
dominio: web
aliases:
  - MOC NoSQL
tags:
  - dominio/web
---

# MOC - NoSQL injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-943 - Improper Neutralization of Special Elements in Data Query Logic]]. Los operadores, en [[NoSQL operadores - matriz de referencia]]. Acá vive **la decisión**.

Es la hermana de [[MOC - SQL injection]], y conviene leerla con aquel al lado porque muchos conceptos se trasladan —canal reflejado contra ciego, extracción carácter por carácter, salto de autenticación— y otros no. La diferencia estructural que ordena el dominio es que en NoSQL la consulta suele ser un **objeto**, no una cadena, y eso abre una vía que en SQL no existe: cambiar el tipo del dato en vez de romper una cadena.

| Eje | Valores |
|---|---|
| Familia de inyección | operador (manipular la estructura) · JavaScript (evaluar código) |
| Canal de extracción | reflejado · ciego booleano · ciego temporal |
| Contexto de entrada | cuerpo JSON · query string parseada · cadena forzada → matriz |
| Motor | Mongo · Couch · Elasticsearch → matriz |

**La familia de inyección es el eje raíz**, y es la divergencia respecto de SQLi. Allá el eje fue el canal de extracción, porque todos los motores rompen una cadena igual. Acá lo primero que decide es **manipular la estructura o evaluar código**: son dos mundos con payloads, impacto y mitigación distintos. El canal de extracción es el segundo eje, heredado de SQLi. El motor y el contexto de entrada van a matriz, mismo criterio que en aquel dominio.

## Árbol de decisión — qué familia y qué canal

```
¿Cómo llega la entrada?  → [[NoSQL operadores - matriz de referencia]] § 0
├─ Se fuerza a cadena → no hay inyección de operador
│  └─ ¿Llega a un $where que evalúa JS? → [[NoSQL - inyección de JavaScript]]
│     Si no, no hay dominio
└─ Llega a un objeto (JSON, o query con corchetes)
   │
   ├─ Meté un operador: {"$ne":null} en el campo
   │  └─ ¿Cambia la respuesta? → hay inyección de operador
   │
   ├─ ¿El objetivo es entrar?
   │     → [[NoSQL - inyección de operador]]   ← PRIMERO, salto de login
   │
   ├─ ¿El objetivo es sacar datos y NO se reflejan?
   │  ├─ ¿Hay oráculo booleano? → [[NoSQL - extracción ciega]] con $regex
   │  └─ ¿Solo tiempo? → canal temporal, necesita $where → [[NoSQL - inyección de JavaScript]]
   │
   └─ ¿La entrada llega a un $where?
         → [[NoSQL - inyección de JavaScript]]  ← la única que evalúa código
```

Tres cosas que este orden codifica:

**El contexto de entrada va antes que el operador.** Si la entrada se fuerza a cadena, la inyección de operador está muerta de entrada y solo queda el `$where`. Confirmarlo con una prueba de operador es el paso cero, y evita gastar payloads contra un campo que nunca los va a aceptar.

**El salto de operador va primero porque cierra el caso más común barato.** Un `{"$ne":null}` en el campo de contraseña es dos peticiones y da login administrativo. La extracción ciega es la rama cara, para cuando el dato importa y no se refleja.

**La inyección de JavaScript es la grave y la rara.** Es la única que llega a evaluar código —acotado al motor, sin acceso al sistema operativo, y eso hay que decirlo para no sobrevender—. También es el canal temporal cuando no hay oráculo booleano, así que la extracción ciega la referencia.

## Árbol de decisión — qué consigo por familia

```
¿Qué inyecté?
├─ Operador de comparación ($ne, $gt)
│  ├─ en login → salto de autenticación → [[MOC - Autenticación]]
│  └─ en búsqueda → devolver todo, enumerar
├─ $regex
│  └─ extracción carácter por carácter de campos ocultos → [[NoSQL - extracción ciega]]
├─ $where / mapReduce (JavaScript)
│  ├─ || true → devolver todo
│  ├─ sleep condicional → extracción por tiempo
│  ├─ bucle → denegación de servicio
│  └─ this.campo → leer campos que la consulta no expone
└─ el dato es un ObjectId / número
      → búsqueda binaria con $gt/$lt, más rápida que $regex
```

## Cheatsheets — entrada directa a los payloads

- [[NoSQL operadores - matriz de referencia]] — Contexto de entrada, salto de auth, comparación, `$regex`, `$where`, contrabando por query string
- [[NoSQL extracción ciega - matriz de referencia]] — Oráculo booleano y temporal, extracción por `$regex`, búsqueda binaria, `$exists`, automatización

## Orden de aprendizaje

1. [[CWE-943 - Improper Neutralization of Special Elements in Data Query Logic]] — por qué cambiar el tipo del dato es distinto de romper una cadena
2. [[NoSQL - inyección de operador]] — el caso base, el salto de login, y el que no existe en SQLi
3. [[NoSQL - extracción ciega]] — el paralelo de SQLi ciego, carácter por carácter con `$regex`
4. [[NoSQL - inyección de JavaScript]] — la grave y la rara, la que evalúa código en el motor

El punto 2 va primero porque es lo que hace a NoSQL distinto de SQLi: la inyección de operador no tiene equivalente en el mundo SQL, y entenderla es entender el dominio.

## Relación con otros dominios

- [[MOC - SQL injection]] — la hermana. El canal ciego, la extracción por carácter y la búsqueda binaria se trasladan casi tal cual; [[NoSQL - extracción ciega]] y [[SQLi ciego - matriz de referencia]] tienen la misma estructura. Lo que no se traslada es la inyección de operador, propia de NoSQL.
- [[MOC - GraphQL]] — NoSQL es uno de los sinks de los argumentos de GraphQL: un `filter` o un `where` sin sanear llega acá. Era el hueco declarado en aquel MOC. GraphQL es el vector, esta es la clase.
- [[MOC - Autenticación]] — el salto de operador es un bypass de autenticación por otra vía, `CWE-943` en lugar de `CWE-287`. El impacto es el mismo que atacar las credenciales, sin tocarlas.
- [[MOC - Command injection]] y [[MOC - SSTI]] — la inyección de JavaScript comparte con ellos la ruptura de contexto, aunque acota la ejecución al motor de la base.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Inyección de operador | [[Registro del WAF]] | Clave que empieza con `$` en el cuerpo o `campo[$op]` en la query |
| Salto de login | [[Log de autenticación de la aplicación]] | Login exitoso **sin** ráfaga de fallos previa |
| Extracción ciega | [[Log de acceso del servidor web]] | Cientos de consultas casi idénticas con variación mínima |
| Inyección de JavaScript | [[Registro del WAF]] | `$where`, `sleep(`, `this.` en el cuerpo |
| Denegación por JS | [[Log de errores del servidor web]] | Base colgada, tiempos disparados — efecto |

Dos observaciones que este dominio deja:

**La firma de la clave `$` rinde, como en prototype pollution y OGNL.** Una clave que empieza con `$` en la entrada —`$ne`, `$where`, `$regex`— no aparece en tráfico legítimo casi nunca. Es una firma de alta fidelidad sobre el cuerpo, y la ve [[Registro del WAF]] si lo inspecciona. Cuarto dominio donde detectar por firma paga, por la misma razón de siempre: la anomalía no tiene forma legítima. La letra chica también: el payload en el cuerpo solo lo ve el WAF, no [[Log de acceso del servidor web]].

**El salto de operador escapa a la detección por volumen, y la extracción ciega no.** El salto acierta a la primera y no deja ráfaga de fallos, así que las reglas de fuerza bruta como [[Fallos de acceso contra cuentas inexistentes]] no lo ven — solo la firma del `$` lo delata. La extracción ciega, en cambio, es cientos de consultas casi idénticas: eso es `forma: agregado` sobre la **repetición con variación mínima**, y se detecta por volumen sin instrumentar el cuerpo, como candidato escribible. Es la asimetría defensiva del dominio: la rama barata es la más silenciosa, la cara es la más ruidosa.

Décimo tercer dominio cerrado sin detección nueva. Dos candidatos escribibles quedan anotados: la firma del `$` sobre el WAF, y el agregado de consultas casi idénticas para la extracción ciega.

## Huecos conocidos

- [x] Las dos familias — operador y JavaScript
- [x] Los tres canales — reflejado, booleano, temporal
- [x] Contexto de entrada y contrabando por query string — en la matriz de operadores
- [x] Cara azul de firma — cubierta por el WAF, con dos candidatos escribibles
- [ ] **Motores más allá de Mongo.** Couch, Elasticsearch, Redis tienen inyecciones propias con otra sintaxis. Van a la matriz cuando se escriban; el eje —familia y canal— es el mismo
- [ ] Inyección en el marco de agregación (`$lookup`, `$graphLookup`) como superficie más nueva
- [ ] La detección por agregado de la extracción ciega es escribible ya; queda como candidato, hueco de trabajo
