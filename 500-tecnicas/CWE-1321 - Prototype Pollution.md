---
tipo: tecnica
taxonomia: cwe
identificador: CWE-1321
wstg: 
tacticas: []
aliases:
  - CWE-1321
  - prototype pollution
  - contaminación de prototipos
tags:
  - dominio/web
---

# CWE-1321 - Prototype Pollution

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Prototype pollution]]; confirmar la contaminación, en [[Prototype pollution - matriz de identificación]]; los gadgets, en [[Prototype pollution gadgets - matriz de referencia]].

## Qué es

En JavaScript, cada objeto hereda de un prototipo, y casi todos heredan del mismo: `Object.prototype`. Si una función que copia datos del usuario a un objeto permite escribir la propiedad `__proto__`, no escribe en el objeto: escribe **en el prototipo compartido**.

A partir de ese momento, **todos los objetos del proceso** que no definan esa propiedad la ven aparecer con el valor que puso el atacante.

```js
const o = {};
merge(o, JSON.parse('{"__proto__": {"esAdmin": true}}'));
({}).esAdmin        // true
```

El objeto `o` no cambió. Cambió el idioma que hablan todos los objetos.

## Por qué es distinta del resto de las inyecciones

No hay intérprete que se confunda ni parser que se rompa. La operación es legítima: copiar propiedades de un objeto a otro es lo que hacen `merge`, `extend`, `clone`, `defaultsDeep` y el parseo de una query string. El fallo es que ninguna de esas funciones distingue una clave de datos de una clave estructural.

De ahí dos consecuencias que ordenan todo el dominio:

**La contaminación y el impacto están separados.** Contaminar es la mitad barata; convertirlo en algo requiere un **gadget**: un lugar del código que lea una propiedad que normalmente no existe y haga algo con ella. Es el mismo reparto que en [[MOC - Deserialización]] entre tener el blob y tener la cadena.

**El efecto es global y persistente.** No queda acotado a la petición: el prototipo contaminado afecta a todas las peticiones que atienda ese proceso hasta que se reinicie. Del lado del servidor eso significa que un ataque puede alterar el comportamiento de otros usuarios, y que una prueba mal hecha deja la aplicación en un estado raro sin que nadie entienda por qué.

## Las tres claves que hay que bloquear

| Clave | Qué hace |
|---|---|
| `__proto__` | Acceso directo al prototipo. La que todos filtran |
| `constructor.prototype` | El mismo destino por otro camino. La que se olvidan |
| `prototype` | Cuando lo que se contamina es una función |

Filtrar solo la primera es el error de mitigación más común, y por eso la segunda es la que hay que probar siempre.

## Por qué la mitigación no es filtrar

Se puede filtrar, y hay que hacerlo, pero no es la solución de fondo porque depende de acertar todas las variantes y todas las codificaciones. Lo que cierra el problema es estructural:

- `Object.freeze(Object.prototype)` — el prototipo deja de admitir escrituras.
- `Object.create(null)` para los objetos que reciben datos del usuario: nacen sin prototipo, así que no hay nada que contaminar.
- `Map` en vez de objetos planos cuando lo que se necesita es un diccionario.
- La bandera `--disable-proto=delete` de Node.

La tercera es la que más rinde en código nuevo: la mitad de los objetos que se contaminan son diccionarios disfrazados de objetos.

## Referencias canónicas

- [CWE-1321](https://cwe.mitre.org/data/definitions/1321.html)
- [CWE-915](https://cwe.mitre.org/data/definitions/915.html) — la clase vecina: modificar atributos que no correspondían
- OWASP Top 10 — A08 Software and Data Integrity Failures
