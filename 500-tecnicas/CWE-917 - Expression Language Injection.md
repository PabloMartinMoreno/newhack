---
tipo: tecnica
taxonomia: cwe
identificador: CWE-917
wstg: WSTG-INPV-18
tacticas: []
aliases:
  - CWE-917
  - EL injection
  - inyección de Expression Language
  - OGNL injection
  - SpEL injection
tags:
  - dominio/web
---

# CWE-917 - Expression Language Injection

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - EL injection]]; identificar el motor, en [[EL injection - matriz de identificación]]; los payloads, en [[EL injection payloads - matriz de referencia]].

## Qué es

Los frameworks de Java usan lenguajes de expresión —SpEL, OGNL, MVEL, JUEL— para evaluar cadenas cortas en tiempo de ejecución: `${usuario.nombre}` en una plantilla, una regla de validación, una condición de ruteo. Cuando una de esas cadenas se construye con entrada del usuario, el atacante escribe la expresión, y el evaluador la ejecuta con los privilegios de la aplicación.

Como esos lenguajes pueden instanciar clases y llamar métodos arbitrarios de Java, una expresión controlada llega a ejecución de comandos casi siempre.

## Por qué es un dominio aparte de SSTI

Comparte el mecanismo con [[MOC - SSTI]] —entrada que termina evaluada como código en un motor— pero la **superficie es otra**, y eso cambia todo el trabajo de encontrarlo:

| | SSTI | EL injection |
|---|---|---|
| Dónde aparece | Plantillas de presentación | Validación, ruteo, mensajes de error, cabeceras |
| Qué se ve primero | Entrada reflejada en la página | A menudo **nada** — la evaluación es indirecta |
| Motor | Jinja2, Twig, Freemarker… | SpEL, OGNL, MVEL, JUEL |
| Framework | Cualquiera | Java: Spring, Struts, servlets |

La diferencia que importa es la segunda: en SSTI la entrada se refleja y `{{7*7}}` vuelve como `49`. En EL injection la expresión se evalúa en un lugar que **no devuelve el resultado** —un mensaje de validación, una decisión de ruteo, un registro—, así que se descubre a ciegas y se confirma por canal fuera de banda. Es lo que lo hace más difícil de encontrar y la razón de modelarlo por dónde entra, no por qué motor es.

## Por qué es tan grave en Java

Los lenguajes de expresión de Java tienen acceso al `Runtime`, a la reflexión y a la instanciación de clases por diseño, porque su público es el desarrollador del framework. OGNL en particular fue la causa de algunos de los CVE más explotados de la historia web —los de Struts 2—, precisamente porque el framework evaluaba como OGNL entradas que el desarrollador no sabía que llegaban al evaluador.

Ese es el patrón que se repite: **el framework evalúa como EL algo que el programador de la aplicación nunca marcó como expresión**. Una cabecera, un parámetro, un nombre de parámetro, un mensaje de error.

## Por qué la mitigación no es filtrar

Filtrar la sintaxis de EL no alcanza: cada motor tiene varias formas de escribir lo mismo y varios delimitadores. Los sandbox de SpEL y OGNL existen pero se rompen con regularidad, igual que los entornos restringidos de las plantillas.

La mitigación real es **no construir expresiones con entrada del usuario** y mantener el framework parcheado —los arreglos de Struts fueron precisamente cerrar los lugares donde OGNL evaluaba entrada por accidente—. Donde haga falta que el usuario aporte una fórmula, se usa un evaluador sin acceso al sistema, tratado como frontera de confianza.

## Referencias canónicas

- [CWE-917](https://cwe.mitre.org/data/definitions/917.html)
- [CWE-1336](https://cwe.mitre.org/data/definitions/1336.html) — SSTI, la clase vecina por mecanismo
- WSTG-INPV-18
- OWASP Top 10 — A03 Injection
