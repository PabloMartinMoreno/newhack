---
tipo: tecnica
taxonomia: cwe
identificador: CWE-89
wstg: WSTG-INPV-05
tacticas: []
visibilidad: publica
creado: 2026-08-05
aliases:
  - CWE-89
  - SQLi
  - Inyección SQL
tags:
  - dominio/web
---

# CWE-89 - SQL Injection

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - SQL injection]]; las variantes en `600-tradecraft/`; la sintaxis en [[Dialectos SQL - matriz de referencia]].

## Qué es

Construcción de una consulta SQL concatenando entrada no confiable, de modo que el atacante puede alterar la **estructura** de la consulta y no solo sus datos.

## Por qué existe

Porque el motor recibe un único string donde código y datos están mezclados. Toda mitigación real separa esos dos canales (consultas parametrizadas); todo lo demás — escapado, listas negras, WAF — es filtrado sobre un canal que sigue mezclado.

## Ejes que la descomponen

Ver [[MOC - SQL injection]] para la tabla completa y el árbol de decisión. Resumen: canal de extracción × contexto de inyección × motor × obstáculo × impacto.

## Por qué no se usa ATT&CK acá

Todo SQLi cae en `T1190 - Exploit Public-Facing Application`, que no discrimina nada. El identificador canónico para web es **CWE + WSTG**.

## Referencias canónicas

- [CWE-89](https://cwe.mitre.org/data/definitions/89.html)
- WSTG-INPV-05
- [[@portswigger-sqli-labs]]
