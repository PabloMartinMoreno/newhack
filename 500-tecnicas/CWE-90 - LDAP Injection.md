---
tipo: tecnica
taxonomia: cwe
identificador: CWE-90
wstg: WSTG-INPV-06
tacticas: []
aliases:
  - CWE-90
  - LDAP injection
  - inyección LDAP
tags:
  - dominio/web
---

# CWE-90 - LDAP Injection

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - LDAP injection]]; la sintaxis del filtro en [[LDAP filtro - matriz de referencia]]; la extracción ciega en [[LDAP extracción ciega - matriz de referencia]].

## Qué es

La aplicación construye una consulta a un directorio LDAP —típicamente para autenticar contra un Active Directory o un directorio corporativo— mezclando entrada del usuario con la estructura del filtro de búsqueda, sin separarlas. El atacante aporta caracteres que el directorio interpreta como **parte de la lógica del filtro** en vez de como dato.

Es la tercera hermana de las inyecciones de consulta, con [[CWE-89 - SQL Injection]] y [[CWE-943 - Improper Neutralization of Special Elements in Data Query Logic]]. Comparten la clase padre y varios conceptos —canal reflejado contra ciego, extracción carácter por carácter, salto de autenticación— pero LDAP tiene una sintaxis distinta que cambia toda la mecánica.

## Por qué la sintaxis lo hace distinto

Un filtro LDAP se escribe en **notación prefija** (polaca), con los operadores adelante y los términos entre paréntesis:

```
(&(uid=juan)(userPassword=1234))     → uid=juan Y password=1234
(|(uid=juan)(uid=admin))             → uid=juan O uid=admin
```

- `&` es Y, `|` es O, `!` es NO — y van **antes** de sus operandos.
- `*` es el comodín: coincide con cualquier cosa.
- Cada término va entre paréntesis, y el anidamiento define la lógica.

Romper un filtro no es cerrar una comilla como en SQL: es **cerrar paréntesis y agregar cláusulas** que cambian la lógica booleana. Un `*` en el lugar correcto convierte una comprobación exacta en un "cualquiera", y un paréntesis bien puesto anula la comprobación de contraseña. Por eso el trabajo del dominio es entender dónde cae la entrada dentro del filtro y qué hay que cerrar para reescribir la lógica.

## Por qué el impacto suele ser autenticación

LDAP se usa sobre todo para **autenticar y autorizar**: "¿existe un usuario con este `uid` y esta contraseña?". Una inyección que vuelve ese filtro siempre-verdadero es un salto de autenticación directo, y por eso el objetivo típico no es extraer datos sino **entrar**. La extracción de atributos —correos, roles, hashes— es el segundo premio, y se hace carácter por carácter con comodines cuando el resultado no se refleja.

## Por qué la mitigación es de escape y de estructura

No hay comilla que escapar, pero sí caracteres especiales del filtro:

- **Escapar** los metacaracteres de LDAP en la entrada: `(`, `)`, `*`, `\`, `/` y el nulo, con su secuencia `\XX`. Es la defensa directa.
- **Consultas parametrizadas** o APIs que separan la entrada de la estructura del filtro, donde el marco de trabajo las ofrezca.
- **Validar** la entrada contra un formato estricto —un `uid` no debería contener paréntesis ni asteriscos.
- No construir el DN de bind con entrada sin escapar.

## Referencias canónicas

- [CWE-90](https://cwe.mitre.org/data/definitions/90.html)
- [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — SQL Injection, la hermana
- WSTG-INPV-06
- OWASP Top 10 — A03 Injection
