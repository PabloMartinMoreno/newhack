---
tipo: moc
dominio: web
aliases:
  - MOC XPath
tags:
  - dominio/web
---

# MOC - XPath injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-643 - XPath Injection]]. La sintaxis, en [[XPath consulta - matriz de referencia]]. Acá vive **la decisión**.

Es la cuarta y última hermana de las inyecciones de consulta, con [[MOC - SQL injection]], [[MOC - NoSQL injection]] y [[MOC - LDAP injection]]. De las cuatro es la **más parecida a SQLi**: rompe comillas y balancea expresiones, no cierra paréntesis como LDAP ni cambia el tipo del dato como NoSQL. Quien conoce SQLi tiene medio dominio ganado.

| Eje | Valores |
|---|---|
| Canal | reflejado · ciego booleano |
| Objetivo | salto de autenticación · lectura del documento |
| Versión | XPath 1.0 · 2.0 (con `doc()`, lectura externa) → matriz |
| Contexto | comilla simple · doble · anidado → matriz |

**El canal es el eje raíz**, como en SQLi y LDAP —no hay bifurcación de familia como en NoSQL—: un solo mecanismo, romper la expresión, y lo que decide es si el resultado se refleja. La versión y el contexto van a matriz.

## Árbol de decisión — qué canal y qué objetivo

```
¿La entrada llega a una expresión XPath sin escapar?  → [[XPath consulta - matriz de referencia]] § 1
├─ Meté una comilla → ¿error de XPath?
│  └─ No → se escapa, no hay dominio
└─ Sí, inyecta
   │
   ├─ ¿El objetivo es entrar?
   │     → [[XPath - manipulación de la consulta]]   ← PRIMERO, salto de autenticación
   │       ' or '1'='1, BALANCEANDO las comillas (no hay comentario)
   │
   ├─ ¿Leer datos Y se reflejan?
   │     → misma nota: ampliar el conjunto de nodos con or true() o el | de unión
   │
   ├─ ¿Leer datos y NO se reflejan?
   │     → [[XPath - extracción ciega]] con substring() y string-length()
   │       OJO: XPath 1.0 no tiene canal temporal — necesita oráculo booleano
   │
   └─ ¿Es XPath 2.0? → doc('file://') o doc('http://')
         → lectura de archivos / SSRF → [[MOC - XXE]] y [[MOC - SSRF]]
```

Tres cosas que este orden codifica:

**Hay que balancear, no comentar.** Es la diferencia técnica con SQLi: XPath 1.0 no tiene `--`, así que el resto de la consulta queda y el payload debe dejarlo sintácticamente válido. `' or '1'='1' or 'a'='a` en vez del `' or '1'='1'--` de SQL.

**No hay control de acceso dentro del documento.** Una vez inyectado, todo el XML es alcanzable —no hay "otras tablas" que requieran `UNION` ni permisos por nodo—. La lectura es más directa que en SQLi, y `name()`/`count()` reconstruyen el esquema entero.

**XPath 2.0 abre lectura externa.** `doc()` y `unparsed-text()` leen archivos y URLs, cruzando el dominio con [[MOC - XXE]] y [[MOC - SSRF]]. Probar la versión es parte del reconocimiento porque cambia el techo del impacto.

## Árbol de decisión — qué consigo

```
¿Qué inyecté?
├─ Expresión siempre-verdadera en login → salto de autenticación → [[MOC - Autenticación]]
├─ Conjunto de nodos ampliado → todo el documento (sin control de acceso)
├─ substring() como oráculo → extracción carácter por carácter
└─ doc() en XPath 2.0 → lectura de archivos / SSRF
```

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[XPath consulta - matriz de referencia]] | Sintaxis, confirmar, salto de auth, balanceo, ampliar nodos, funciones, XPath 2.0, escape |
| [[XPath extracción ciega - matriz de referencia]] | Oráculo booleano, medir largo, extracción con `substring`, enumerar esquema con `name`/`count`, `xcat` |

## Orden de aprendizaje

1. [[CWE-643 - XPath Injection]] — por qué es la más parecida a SQLi, y las dos diferencias (sin comentarios, sin control de acceso)
2. [[XPath - manipulación de la consulta]] — el caso base, el salto de autenticación con balanceo
3. [[XPath - extracción ciega]] — el paralelo de las hermanas, con `substring()` como oráculo

El punto 1 va primero y conviene leerlo con SQLi al lado: la mecánica se traslada casi entera, y lo eficiente es aprender solo lo que cambia —el balanceo y la ausencia de control de acceso—.

## Relación con otros dominios

- [[MOC - SQL injection]] — la hermana más cercana. El salto de autenticación, la extracción por `substring`, el oráculo booleano son casi idénticos; cambia que XPath no tiene comentarios (hay que balancear) ni control de acceso (todo el documento es alcanzable sin `UNION`).
- [[MOC - NoSQL injection]] y [[MOC - LDAP injection]] — las otras dos hermanas. Las cuatro comparten [[SQLi ciego - matriz de referencia]] como modelo de extracción ciega; XPath, NoSQL y LDAP reusan su estructura.
- [[MOC - XXE]] — el documento consultado es XML, y XPath 2.0 con `doc('file://')` llega a lectura de archivos como un XXE. Los dos viven sobre XML; XXE ataca el parser, XPath ataca la consulta.
- [[MOC - SSRF]] — `doc('http://')` de XPath 2.0 es un vector de SSRF.
- [[MOC - Autenticación]] — el salto de consulta es bypass de autenticación por otra vía, `CWE-643` en vez de `CWE-287`, como el salto de las otras hermanas.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Manipulación de consulta | [[Registro del WAF]] | Sintaxis XPath `' or `, `true()`, `position()` en un campo de usuario |
| Salto de autenticación | [[Log de autenticación de la aplicación]] | Login exitoso sin contraseña, sin ráfaga de fallos previa |
| Extracción ciega | [[Log de acceso del servidor web]] | Cientos de consultas con `substring()` variando posición |

Con este dominio se cierran las **cuatro hermanas de inyección**, y la cara azul es la misma en las cuatro — eso es la conclusión, no una repetición:

**Una detección de firma y una de agregado cubrirían SQLi, NoSQL, LDAP y XPath juntas.** Los metacaracteres difieren —`'` en SQL y XPath, `$` en NoSQL, `*)(` en LDAP— pero el patrón es idéntico: **caracteres de estructura de consulta en un campo de datos**. Y las cuatro comparten la asimetría: el salto de autenticación acierta a la primera sin ráfaga de fallos (solo la firma lo ve), la extracción ciega es cientos de consultas casi idénticas (`forma: agregado`). Escribir una regla de firma de inyección sobre el cuerpo y una de agregado de consultas casi idénticas es el trabajo azul de mayor retorno del vault, porque una sola de cada una cubre cuatro dominios. Es el argumento más fuerte a favor de detectar por **clase de patrón** en vez de por dominio.

Décimo séptimo dominio cerrado sin detección nueva, y el que consolida el candidato transversal.

## Huecos conocidos

- [x] Los dos canales — reflejado y ciego
- [x] Salto de autenticación y lectura del documento
- [x] Sintaxis, balanceo, funciones y extracción ciega — dos matrices
- [x] XPath 2.0 con `doc()` como cruce a XXE y SSRF
- [x] Cara azul — la misma de las cuatro hermanas, con el candidato transversal consolidado
- [ ] **La detección de firma de inyección transversal (SQLi+NoSQL+LDAP+XPath) es escribible ya.** Una regla sobre el cuerpo que marque metacaracteres de consulta en campos de datos cubriría las cuatro. El mayor retorno azul del vault, hueco de trabajo
- [ ] XQuery completo (más allá de XPath) como superficie propia, con FLWOR y funciones de módulo
