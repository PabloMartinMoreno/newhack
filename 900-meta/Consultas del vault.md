---
tipo: meta
aliases:
  - Consultas
  - consultas.py
tags:
  - meta/consultas
---

# Consultas del vault

Las consultas que **solo existen porque los dos lados están en el mismo vault**. Son la única razón válida para fusionar.

> [!important] Sin estas consultas, la fusión es nominal
> Son la única razón válida para tener rojo y azul en el mismo vault. Se corren con `consultas.py`, no se leen: en nvim no hay Dataview.

## Implementación CLI

`900-meta/consultas.py` — sin dependencias más que `pyyaml`. Lee el frontmatter de todas las notas, resuelve los wikilinks contra nombres **y aliases**, arma el índice invertido y responde:

```sh
900-meta/consultas.py todo
900-meta/consultas.py revalidacion --meses 3
900-meta/consultas.py huecos
900-meta/consultas.py contradicciones
900-meta/consultas.py higiene
```

Funciona desde cualquier directorio (resuelve el vault relativo al propio script) y acepta `--vault`. Desde nvim: `:!%:h/consultas.py todo` o `:!900-meta/consultas.py huecos`.

**Diferencias con Dataview, a propósito:**

- Indexa **solo enlaces del frontmatter**, no del cuerpo. Una mención de paso en una prosa no es una relación afirmada; `telemetria:` sí lo es. Evita el ruido que en Dataview mete `file.inlinks`.
- Los enlaces rotos del frontmatter se **reportan** en `higiene` en vez de hacer desaparecer notas del resultado. Los `alternativas:` que apuntan a notas todavía no escritas aparecen ahí: es roadmap, no error.
- `revalidacion` incluye el tradecraft **sin** `probado:`, que en Dataview se caía del filtro por comparación con `null`. Ese es el caso peor y era invisible.
- `higiene` valida los enums de [[Esquema de frontmatter]] y exige `opsec`/`probado`/`contexto` en todo tradecraft.

Cortes rápidos sin script:

```sh
rg -l '^opsec: quemado' 600-tradecraft/
rg --no-heading '^probado: 202[45]' 600-tradecraft/
rg -l 'Sysmon EID 10' 600-tradecraft/ 650-detecciones/   # los dos lados de una bisagra
```

## Relacionadas

[[Esquema de frontmatter]] · [[Estructura del vault]] · [[Validación de tradecraft en laboratorio]]

## Apéndice: las mismas preguntas en Dataview

> [!note] No se ejecutan acá
> Quedan como especificación legible de qué pregunta cada consulta. Solo sirven si algún día el vault se abre en Obsidian con el plugin Dataview instalado.

### 1. Backlog de revalidación — la que compensa la caducidad

Tradecraft no probado en más de seis meses. Este es el backlog de laboratorio, no una lista de lectura.

````
```dataview
TABLE opsec, contexto, probado
FROM "600-tradecraft"
WHERE probado < date(today) - dur(6 months)
SORT probado ASC
```
````

### 2. Huecos defensivos propios

Artefactos que **tu tradecraft emite** y que **ninguna detección tuya consume**. Es un backlog azul generado por experiencia roja propia, no por una lista genérica.

````
```dataview
TABLE
  length(filter(file.inlinks, (i) => i.tipo = "tradecraft")) AS "Variantes que lo emiten"
FROM "550-telemetria"
WHERE length(filter(file.inlinks, (i) => i.tipo = "tradecraft")) > 0
  AND length(filter(file.inlinks, (i) => i.tipo = "deteccion")) = 0
SORT length(filter(file.inlinks, (i) => i.tipo = "tradecraft")) DESC
```
````

### 3. Detecciones nunca puestas a prueba

Reglas cuya telemetría no tiene ninguna variante de tradecraft enlazada. Sobre el papel funcionan; nadie las atacó.

````
```dataview
TABLE estado, fidelidad, telemetria
FROM "650-detecciones"
WHERE !any(map(telemetria, (t) => any(map(t.file.inlinks, (i) => i.tipo = "tradecraft"))))
SORT estado ASC
```
````

### 4. Contradicciones — la query que encuentra mentiras propias

Tradecraft marcado `opsec: limpio` cuya telemetría coincide con una detección propia **en producción**. O está mal la etiqueta o está mal la regla.

````
```dataview
TABLE clase, telemetria, probado
FROM "600-tradecraft"
WHERE opsec = "limpio"
  AND any(map(telemetria, (t) => any(map(t.file.inlinks,
      (i) => i.tipo = "deteccion" AND i.estado = "produccion"))))
```
````

### 5. Puntos únicos de fallo

Artefactos que sostienen muchas detecciones. Si el cliente no recolecta Sysmon, sabés exactamente qué se apaga — y del lado rojo, qué se te habilita.

````
```dataview
TABLE
  length(filter(file.inlinks, (i) => i.tipo = "deteccion")) AS "Detecciones que dependen",
  por-defecto AS "Activado por defecto",
  coste
FROM "550-telemetria"
SORT length(filter(file.inlinks, (i) => i.tipo = "deteccion")) DESC
```
````

### 6. Técnicas sin ninguna de las dos caras

Cobertura del grafo: dónde hay taxonomía sin contenido.

````
```dataview
TABLE
  length(filter(file.inlinks, (i) => i.tipo = "tradecraft")) AS "Tradecraft",
  length(filter(file.inlinks, (i) => i.tipo = "deteccion")) AS "Detecciones"
FROM "500-tecnicas"
SORT length(file.inlinks) ASC
```
````

### 7. Higiene

Frontmatter inválido y enlaces rotos: lo resuelve `consultas.py higiene`.

Inbox estancado:

````
```dataview
LIST file.cday
FROM "000-inbox"
WHERE file.cday < date(today) - dur(14 days)
SORT file.cday ASC
```
````

### Nota sobre el desreferenciado de enlaces

Las consultas 3 y 4 dependen de que Dataview resuelva `t.file.inlinks` sobre un enlace del frontmatter. Funciona si el valor está escrito como `"[[Nota]]"` (comillas incluidas) y el destino existe. Si el enlace está roto, la nota se cae silenciosamente del resultado — otra razón para no tener links a notas inexistentes fuera de los MOCs.

