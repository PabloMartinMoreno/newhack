---
tipo: moc
dominio: web
aliases:
  - MOC SSTI
  - inyección de plantillas
tags:
  - dominio/web
---

# MOC - SSTI

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]]. Identificar el motor, en [[SSTI - matriz de identificación]]. Acá vive **la decisión**.

Este dominio se enseña al revés. La imagen que deja cualquier tutorial es "SSTI igual a ejecución remota", y de ahí salen los dos errores caros: tirar payloads antes de saber qué motor hay, y abandonar el hallazgo cuando no se llega a ejecutar. **Lo primero que hay que pedirle a un SSTI no es una shell, es el contexto** — ahí suele estar la clave de firma, y con ella se falsifican sesiones sin tocar el sistema operativo.

| Eje | Valores |
|---|---|
| Capacidad del motor | ejecución directa · entorno restringido · sin lógica · del lado del cliente |
| Contexto de inyección | la entrada **es** la plantilla · la entrada está dentro de una expresión → matriz |
| Motor | Jinja2 · Twig · Freemarker · Velocity · ERB · Pug · Handlebars → matriz |
| Impacto | RCE · lectura de archivos · secretos del contexto · XSS (lado del cliente) |

**El motor va a matriz y no a eje**, mismo criterio que el motor de base de datos en [[MOC - SQL injection]] y la shell en [[MOC - Command injection]]. La distinción se hace acá con cuidado, porque es tentador convertirlo en eje: el motor cambia el payload por completo. Pero no cambia la **decisión** — lo que decide es qué capacidad tiene, y esa es la columna que sí es eje.

El contexto de inyección va a matriz por el mismo precedente que la ruptura del contexto en command injection: cambia el prefijo del payload, no la técnica.

## Árbol de decisión — qué capacidad tengo

```
¿{{7*7}} devuelve 49?
├─ No → probá los siete delimitadores → [[SSTI - matriz de identificación]] § 1
│       si ninguno evalúa, no hay SSTI
└─ Sí
   ├─ ¿En el cuerpo crudo, o solo en el DOM?
   │  └─ Solo en el DOM → [[SSTI - del lado del cliente]]
   │                       el resultado es XSS, no RCE
   └─ En el cuerpo → identificá el motor  → [[SSTI - matriz de identificación]] § 4
      │
      ├─ PEDÍ EL CONTEXTO PRIMERO      → [[SSTI - lectura sin ejecución]]
      │  una petición, sin ruido, y a veces termina el trabajo acá
      │
      ├─ ¿El motor expone ejecución?   (Freemarker, Velocity, ERB, Smarty, Pug)
      │  └─ Sí → [[SSTI - ejecución directa]]
      ├─ ¿Entorno restringido?         (Jinja2, Twig, Nunjucks)
      │  └─ Sí → [[SSTI - escape del entorno restringido]]   ← el caro
      └─ ¿Sin lógica?                  (Handlebars, Mustache, Django)
         └─ No hay ejecución → quedate en lectura
```

Tres cosas que este orden codifica:

**Identificar va antes que todo.** Cuatro peticiones resuelven el motor; tirar payloads a ciegas gasta veinte y llena el registro de errores del servidor con excepciones que son la señal más clara para el defensor. Es la única fase del dominio que no se puede saltear.

**Leer el contexto va antes que escalar.** Cuesta una petición, es limpia, y devuelve la clave de firma con frecuencia suficiente como para justificar hacerlo siempre. Buscar ejecución antes de mirar el contexto es el error de orden del dominio.

**El escape del entorno restringido va último porque es el más caro.** Consume más peticiones que cualquier otra técnica web del vault, y conviene entrar con un presupuesto fijado de antemano.

## Árbol de decisión — no llego a ejecutar, ¿qué queda?

```
El entorno restringido no cedió o el motor es sin lógica
├─ ¿Hay clave de firma en el contexto?
│     → falsificás sesiones y tokens → [[Sesión - falsificación de JWT]]
│       Es toma de cuenta sin tocar el sistema operativo
├─ ¿Credenciales de base de datos o de servicios?
│     → acceso directo, y suelen estar reusadas
├─ ¿Variables de entorno?
│     → en contenedor, es el depósito de secretos
├─ ¿Direcciones o cabeceras internas?
│     → insumo para [[MOC - SSRF]]
└─ ¿Nada de valor?
      → reportalo igual: evaluación de expresiones del lado del servidor,
        severidad según lo que se pudo leer
```

Este segundo árbol es el que rescata los hallazgos que se abandonan. Un SSTI sin ejecución **no es un hallazgo menor**: es lectura arbitraria del estado del proceso, y la clave de firma sola vale más que muchas shells.

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[SSTI - matriz de identificación]] | Los siete delimitadores, el polyglot, el árbol de identificación, firmas por motor, caso ciego |
| [[SSTI payloads - matriz de referencia]] | Ejecución por motor, el recorrido de Jinja2, evasión de filtros, volcado de contexto, canal ciego |

## Orden de aprendizaje

1. [[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]] — la entrada como plantilla contra la entrada como dato
2. [[SSTI - matriz de identificación]] — antes que cualquier payload, siempre
3. [[SSTI - lectura sin ejecución]] — la rama barata, y la que más veces alcanza
4. [[SSTI - ejecución directa]] — cuando el motor lo regala
5. [[SSTI - escape del entorno restringido]] — el método de trepar el grafo de objetos, que sirve para todos los motores del mismo lenguaje
6. [[SSTI - del lado del cliente]] — por qué sobrevive a los filtros de XSS

El punto 3 va antes que el 4 a propósito, al revés de como suele enseñarse. Empezar por el payload de ejecución deja la impresión de que sin RCE no hay hallazgo, que es falso y hace tirar accesos de lectura al proceso.

## Relación con otros dominios

- [[MOC - Command injection]] — convergen en el mismo efecto y por eso comparten detección: [[Intérprete de comandos como hijo del servidor web]] ve las dos sin saber cuál fue. La diferencia operativa es que SSTI llega a ejecución **sin** que la aplicación invoque una shell.
- [[MOC - Cross-site scripting]] — el diagnóstico se cruza al principio y hay que separarlos con la prueba aritmética. [[SSTI - del lado del cliente]] termina en XSS pero evade los filtros que detienen un XSS clásico.
- [[MOC - Deserialización]] — el mismo patrón: la aplicación interpreta como código algo que debía ser dato, y en los dos casos lo fallido es más visible que lo exitoso.
- [[MOC - Gestión de sesión]] — la salida más rentable de un SSTI sin ejecución es la clave de firma, y con ella se entra a ese dominio.
- [[MOC - SSRF]] — el contexto de la plantilla suele exponer direcciones internas.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Identificación | [[Log de errores del servidor web]] | Ráfaga de excepciones de plantilla desde un mismo origen |
| Ejecución directa | [[Proceso hijo del servidor web]] | Intérprete hijo del servidor de aplicación |
| Escape del entorno restringido | [[Log de errores del servidor web]] | Excepciones de atributo indefinido, en volumen |
| Escape → segunda etapa | [[Conexión saliente del servidor de aplicación]] | Descarga desde el proceso de la aplicación |
| Canal ciego | [[Consulta DNS saliente]] | Subdominio con identificador de motor |
| Lectura sin ejecución | — | **Nada.** No cruza ninguna frontera vigilada |
| Del lado del cliente | [[Informe de violación de CSP]] | Solo si hay política y el payload la viola |

Dos observaciones que este dominio deja claras:

**Ninguna detección propia hizo falta.** Es el cuarto dominio que se cierra reutilizando reglas existentes. [[Intérprete de comandos como hijo del servidor web]] cubre la ejecución y [[Ráfaga de errores del servidor desde un mismo origen]] cubre la fase de identificación, que en este dominio es obligatoria y ruidosa. Ninguna de las dos sabe qué es SSTI.

**La fase obligatoria es la ruidosa, y eso es una ventaja defensiva rara.** En casi todos los dominios el atacante puede saltear el reconocimiento si sabe lo que busca. Acá no: identificar el motor exige provocar errores, y cada payload de motor equivocado deja una excepción con el nombre de la plantilla. La ventana de detección es anterior al ataque exitoso, no simultánea.

## Huecos conocidos

- [x] Las cuatro capacidades del motor
- [x] Identificación — en [[SSTI - matriz de identificación]]
- [x] Payloads por motor y evasión de filtros — en [[SSTI payloads - matriz de referencia]]
- [x] Cara azul — cubierta por detecciones existentes, sin reglas nuevas
- [ ] **[[SSTI - lectura sin ejecución]] no se detecta.** No es hueco de contenido sino de fuente: no nace proceso, no sale conexión, no hay excepción. Haría falta inspección del cuerpo de las respuestas, que es prevención de fuga y no detección. Mismo límite que el XXE local en [[MOC - XXE]]
- [ ] Inyección en plantillas de correo y de generación de documentos, donde el renderizado es asíncrono y siempre ciego
- [ ] Expression Language de Java como dominio aparte: comparte método con SSTI pero la superficie es otra —Spring, OGNL, formularios de validación— y merece sus propios ejes
