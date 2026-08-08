---
tipo: zettel
relacionadas: ["[[Esquema de frontmatter]]", "[[Consultas del vault]]"]
aliases:
  - la bisagra de telemetría
tags: []
---

# El atacante y el defensor miran artefactos distintos del mismo hecho

## Idea

Una acción deja **muchos rastros a la vez**, en capas distintas. El atacante piensa en la acción; el defensor solo ve los rastros. Y como cada uno nombra la cosa por su lado —"volqué LSASS" contra "hubo un `OpenProcess` con esa máscara de acceso"— parecen dos temas y son uno.

El punto de contacto no es la técnica ni la herramienta: es el **artefacto**. Ese es el único objeto que ambos lados tienen que nombrar igual.

## Por qué importa

Es la razón por la que este vault es uno solo y no dos.

Si la nota roja dice "esta técnica emite X" y la azul dice "esta regla consume X", entonces se puede preguntar **qué emito que nadie mira** — que es la pregunta que ninguno de los dos lados puede responder solo. Ver [[Consultas del vault]].

Y si cada lado usa su propio vocabulario —`huella:` en rojo, `fuentes-log:` en azul— la pregunta no se puede escribir. Por eso el campo se llama `telemetria:` en los dos, y es la decisión de la que cuelga todo lo demás.

## Consecuencias

- **Aprender una cara enseña la otra.** Entender por qué una técnica es ruidosa **es** entender qué la detecta. No son dos estudios, es uno mirado desde dos lados.
- **El artefacto es más estable que la técnica.** Las técnicas caducan; `Sysmon EID 1` sigue siendo creación de proceso. Organizar por artefacto envejece mejor.
- **Un lado sin el otro miente por omisión.** Tradecraft sin telemetría declarada parece más sigiloso de lo que es. Detección sin tradecraft que la dispare parece más efectiva de lo que es.
- **El desacuerdo es información.** Si una variante marcada `opsec: limpio` resulta que dispara una regla propia, uno de los dos está mal — y averiguar cuál enseña algo. Es lo que busca `consultas.py contradicciones`.

## Fuente

Destilado de la construcción de este vault, no de una fuente única.
