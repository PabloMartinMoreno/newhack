---
tipo: tecnica
taxonomia: cwe
identificador: CWE-1336
wstg: WSTG-INPV-18
tacticas: []
aliases:
  - CWE-1336
  - SSTI
  - server-side template injection
  - inyección de plantilla
tags:
  - dominio/web
---

# CWE-1336 - Improper Neutralization of Special Elements Used in a Template Engine

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - SSTI]]; identificar el motor, en [[SSTI - matriz de identificación]]; los payloads, en [[SSTI payloads - matriz de referencia]].

## Qué es

La aplicación construye la **plantilla** con entrada del usuario, en vez de pasarle esa entrada como dato. El motor recibe entonces expresiones que el atacante escribió y las evalúa con los privilegios del proceso.

La diferencia cabe en dos líneas:

```python
render_template_string("Hola " + nombre)   # la entrada ES la plantilla
render_template("saludo.html", nombre=nombre)   # la entrada es un dato
```

La primera es la vulnerabilidad entera. No hace falta ningún otro fallo.

## Por qué no es XSS

Se confunden porque el síntoma inicial es el mismo —entrada reflejada en la respuesta— y porque la primera prueba de las dos se parece. La diferencia es **dónde se evalúa**:

| | XSS | SSTI |
|---|---|---|
| Dónde ejecuta | Navegador de la víctima | Servidor |
| Qué consigue | La sesión de quien visita | El proceso de la aplicación |
| Qué se prueba | `<script>` o el contexto de salida | Una operación aritmética: `{{7*7}}` |

Si `{{7*7}}` vuelve como `49`, la evaluación pasó del lado del servidor y el dominio es este. Si vuelve literal, no hay SSTI aunque el reflejo exista.

Esa prueba es también lo que separa este dominio de su primo del lado del cliente: cuando el motor corre en el navegador —AngularJS, Vue— la misma inyección da ejecución de JavaScript en el origen, o sea XSS por otro camino. Ver [[SSTI - del lado del cliente]].

## Por qué el motor decide tanto

A diferencia de SQLi, donde todos los motores hacen lo mismo con sintaxis distinta, acá el motor decide **qué es alcanzable**:

- Algunos exponen ejecución directa: hay una construcción documentada para invocar al sistema operativo.
- Otros corren en un entorno restringido y hay que trepar el grafo de objetos del lenguaje hasta encontrar algo peligroso.
- Otros son deliberadamente sin lógica y no llegan a ejecución nunca — lo que se obtiene ahí es lectura de datos, que no es poco.

Por eso identificar el motor va antes que cualquier payload, y por eso es el único paso del dominio que no se puede saltear.

## Por qué la mitigación no es filtrar

Filtrar los delimitadores no alcanza: cada motor tiene varios, y algunos aceptan sintaxis alternativa. Poner el motor en modo restringido ayuda y no cierra el problema, porque los entornos restringidos de plantilla se rompen con regularidad — no fueron diseñados como frontera de seguridad.

La mitigación real es **no construir plantillas con entrada del usuario**. Si el usuario tiene que aportar formato, se usa un motor sin lógica y se lo trata como frontera de confianza, no como comodidad.

## Referencias canónicas

- [CWE-1336](https://cwe.mitre.org/data/definitions/1336.html)
- [CWE-94](https://cwe.mitre.org/data/definitions/94.html) — Code Injection, la clase padre
- WSTG-INPV-18
- OWASP Top 10 — A03 Injection
