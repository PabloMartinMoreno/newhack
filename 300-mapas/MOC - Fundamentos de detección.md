---
tipo: moc
dominio: azul
aliases:
  - MOC fundamentos azules
  - Fundamentos de detección
tags: []
---

# MOC - Fundamentos de detección

> [!abstract] Nota de referencia paraguas
> Los conceptos transversales del lado azul. No son de ninguna tecnología: valen igual en un log de Apache, en Sysmon o en un SIEM. Las técnicas concretas viven en los MOC de cada dominio.

Este mapa existe porque **un curso te enseña las herramientas y estos conceptos aparecen sueltos, de a uno, sin que nadie los junte**. Junto son el criterio con el que se decide qué regla escribir, dónde ponerla y si sirve.

## Orden de lectura

Es una secuencia, no una lista. Cada una supone la anterior.

1. [[El atacante y el defensor miran artefactos distintos del mismo hecho]] — por qué las dos caras son un solo estudio
2. [[Detectar el efecto sobrevive a la evasión]] — dónde anclar una regla, y cuánto va a durar
3. [[La detección vive en el agregado, no en el evento]] — las cuatro formas que puede tener una regla
4. [[Sin línea base no hay anomalía]] — por qué un umbral inventado no detecta nada
5. [[La fidelidad se paga en volumen]] — el compromiso que no se puede evitar, solo mover
6. [[Un log sin identidad es un historial, no una detección]] — cuando falta un campo, no una regla
7. [[Ausencia de alertas no es ausencia de ataque]] — cómo se lee un panel en cero
8. [[Toda detección es una hipótesis con fecha de vencimiento]] — el ciclo de vida, y por qué existe `estado:`

Los dos primeros dan el marco. Del 3 al 5 son sobre escribir la regla. El 6 y el 7 son sobre sus límites. El 8 cierra: nada de esto es permanente.

## Árbol de decisión — quiero detectar algo, ¿por dónde empiezo?

```
¿Qué produce ese ataque que una operación normal no produzca?
├─ Nada observable → no hay detección: hay que ENCENDER TELEMETRÍA
│                    ver [[Ausencia de alertas no es ausencia de ataque]]
├─ Un evento único e inconfundible
│                  → forma: evento — la más barata y la más fácil de validar
├─ Una relación entre dos registros
│                  → forma: correlacion — ¿comparten una clave que se pueda unir?
├─ Una cantidad, proporción o tasa
│                  → forma: agregado — necesitás línea base ANTES de escribirla
└─ Algo que nunca debería pasar en una secuencia
                   → forma: invariante — ¿están registrados los dos extremos?
```

Las dos preguntas del final son las que tumban reglas antes de escribirlas, y conviene hacerlas primero: **¿existe la clave para unir?** y **¿están los dos extremos registrados?** Si la respuesta es no, el trabajo no es escribir la regla: es instrumentar. Ver [[Un log sin identidad es un historial, no una detección]].

## Árbol de decisión — la regla ya existe y no sirve

```
¿Qué está fallando?
├─ Alerta demasiado      → ¿bajás el umbral o cambiás la fuente?
│                          cambiar la fuente casi siempre gana → § La fidelidad se paga en volumen
├─ No alerta nunca       → ¿no hay ataques, o está ciega?
│                          → [[Ausencia de alertas no es ausencia de ataque]]
├─ Se evade fácil        → está anclada en firma, no en efecto
│                          → [[Detectar el efecto sobrevive a la evasión]]
└─ Funcionaba y dejó     → cambió el sistema
                           → [[Toda detección es una hipótesis con fecha de vencimiento]]
```

## Dónde aplicar esto en el vault

- Las 23 detecciones de `650-detecciones/` están todas en `estado: idea` menos una. Leerlas con estos conceptos en la mano es el ejercicio: cada una declara su `forma:`, su `fidelidad:`, sus falsos positivos y sus evasiones, y se puede discutir si acertó.
- Los 27 artefactos de `550-telemetria/` declaran cada uno sus **limitaciones**. Esa sección es la lista de puntos ciegos, que es de donde sale la cobertura real.
- [[Validación de tradecraft en laboratorio]] es el ciclo del lado rojo. El equivalente azul —validar detecciones— todavía no está escrito.

## Cheatsheets — entrada directa a la sintaxis

Cuando ya sabés qué querés detectar y solo falta escribirlo:

| Matriz | Cubre |
|---|---|
| [[Detección por forma - matriz de referencia]] | Cada valor de `forma:` traducido a consulta concreta. **Empezar por acá** — es el campo propio del vault |
| [[KQL - matriz de referencia]] | Tablas de Defender y Sentinel, operadores, `join`, agregación por ventana, línea base |
| [[Sigma - matriz de referencia]] | Esqueleto, `logsource`, modificadores, correlaciones, y qué no expresa |
| [[Sysmon - matriz de configuración]] | Instalación, filtros de inclusión y exclusión, `GrantedAccess`, verificar que el evento llega |

## Huecos conocidos

- [ ] Procedimiento de **triaje de una alerta**: qué preguntarse, en qué orden, cuándo escalar
- [ ] Procedimiento de **validación de detecciones en laboratorio**, el par del ciclo rojo
- [ ] Notas sobre **normalización y parseo**: por qué el mismo evento se ve distinto en cada fuente
- [ ] Nada sobre **respuesta a incidentes**: contención, erradicación, cadena de custodia. Es otro oficio y el vault no lo modela
