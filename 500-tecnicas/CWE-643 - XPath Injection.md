---
tipo: tecnica
taxonomia: cwe
identificador: CWE-643
wstg: WSTG-INPV-09
tacticas: []
aliases:
  - CWE-643
  - XPath injection
  - inyección XPath
  - XQuery injection
tags:
  - dominio/web
---

# CWE-643 - XPath Injection

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - XPath injection]]; la sintaxis en [[XPath consulta - matriz de referencia]]; la extracción ciega en [[XPath extracción ciega - matriz de referencia]].

## Qué es

La aplicación consulta un documento XML con una expresión XPath construida mezclando entrada del usuario con la estructura de la consulta, sin separarlas. El atacante aporta caracteres que el motor XPath interpreta como **parte de la expresión** en vez de como dato.

Es la cuarta hermana de las inyecciones de consulta, con [[CWE-89 - SQL Injection]], [[CWE-943 - Improper Neutralization of Special Elements in Data Query Logic]] (NoSQL) y [[CWE-90 - LDAP Injection]]. De las cuatro, es la **más parecida a SQLi**: la sintaxis rompe comillas y balancea expresiones, no cierra paréntesis como LDAP ni cambia el tipo del dato como NoSQL.

## Por qué es la más parecida a SQLi

Una consulta XPath típica de autenticación se ve casi como SQL:

```
//usuario[nombre/text()='INPUT' and clave/text()='INPUT']
```

Inyectar es lo mismo que en SQL: cerrar la comilla y agregar lógica.

```
nombre = ' or '1'='1
→ //usuario[nombre/text()='' or '1'='1' and ...]
```

`' or '1'='1` vuelve la condición siempre-verdadera, exactamente como el salto de autenticación de SQLi. Por eso quien conoce SQLi tiene medio dominio ganado — cambia el motor y las funciones, no la mecánica de romper una cadena.

## Dos diferencias que sí importan

**No hay comentarios.** XPath 1.0 no tiene una sintaxis de comentario como el `--` de SQL, así que no se puede "comentar el resto" de la consulta: hay que **balancear** las comillas para que la expresión quede sintácticamente válida hasta el final. Es el detalle técnico que más cambia respecto de SQLi.

**No hay control de acceso dentro del documento.** En SQL, alcanzar otra tabla requiere `UNION` y permisos; en XPath, una vez que se inyecta, **todo el documento es alcanzable**. No hay "tablas" separadas ni autorización por nodo: la raíz `/` lleva a todo. Extraer el documento entero es cuestión de recorrerlo, no de saltar barreras. Eso hace la extracción más directa que en SQLi.

## Por qué la mitigación es de separación y escape

- **Consultas XPath parametrizadas** —variables enlazadas—, donde la biblioteca las ofrezca. Es la defensa correcta, como las consultas preparadas en SQL.
- **Escapar** las comillas simples y dobles de la entrada, y validar el formato.
- No construir la expresión concatenando entrada del usuario.

## Referencias canónicas

- [CWE-643](https://cwe.mitre.org/data/definitions/643.html)
- [CWE-89](https://cwe.mitre.org/data/definitions/89.html) — SQL Injection, la hermana más cercana
- WSTG-INPV-09
- OWASP Top 10 — A03 Injection
