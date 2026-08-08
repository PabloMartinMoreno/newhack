---
tipo: tecnica
taxonomia: cwe
identificador: CWE-78
wstg: WSTG-INPV-12
tacticas: []
aliases:
  - CWE-78
  - OS command injection
  - Inyección de comandos
  - shell injection
tags:
  - dominio/web
---

# CWE-78 - OS Command Injection

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Command injection]]; las variantes en `600-tradecraft/`; la sintaxis en [[Command injection shells - matriz de referencia]].

## Qué es

La aplicación construye un comando de sistema operativo concatenando entrada no confiable y lo entrega a un **intérprete de shell**. El atacante altera la estructura del comando, no solo sus argumentos.

## Por qué existe

Por la misma razón que [[CWE-89 - SQL Injection]]: un único string donde código y datos van mezclados, interpretado por algo que no distingue quién escribió cada parte. La diferencia es el intérprete — `/bin/sh` en vez del motor SQL — y que el resultado es ejecución directa en el host, sin pasar por una base de datos.

El culpable concreto casi siempre es una API que **invoca shell por conveniencia**: `system()`, `popen()`, `exec()` con string, `shell_exec()`, `os.system()`, `subprocess` con `shell=True`, `Runtime.exec(String)`, backticks de Perl o Ruby.

## La mitigación real

Pasar el comando y sus argumentos como **array**, sin shell de por medio (`execve`, `subprocess.run([...])` sin `shell=True`). Eso elimina la clase entera: sin shell no hay metacaracteres que interpretar.

Lo que **no** la elimina: escapar caracteres, listas negras, `escapeshellcmd`. Filtran sobre un canal que sigue mezclado. Y `escapeshellarg` — que sí es correcto para su propósito — no protege contra [[CWE-88 - Argument Injection]], porque un argumento perfectamente escapado sigue siendo un argumento válido.

## Ejes que la descomponen

Ver [[MOC - Command injection]] para la tabla completa y los árboles. Resumen: canal de extracción × ruptura del contexto × shell × obstáculo × impacto.

## Por qué no se usa ATT&CK acá

Mismo argumento que en SQLi: la entrada cae en `T1190` y la ejecución en `T1059`, y ninguno de los dos discrimina nada. El identificador canónico para web es **CWE + WSTG**.

## Referencias canónicas

- [CWE-78](https://cwe.mitre.org/data/definitions/78.html)
- WSTG-INPV-12
