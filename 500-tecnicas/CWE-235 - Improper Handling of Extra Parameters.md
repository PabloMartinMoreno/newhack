---
tipo: tecnica
taxonomia: cwe
identificador: CWE-235
wstg: WSTG-INPV-04
tacticas: []
aliases:
  - CWE-235
  - HTTP parameter pollution
  - HPP
  - contaminación de parámetros
tags:
  - dominio/web
---

# CWE-235 - Improper Handling of Extra Parameters

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - HTTP parameter pollution]]; la resolución por marco de trabajo y los payloads, en [[HPP - matriz de referencia]].

## Qué es

Una petición HTTP puede llevar el **mismo parámetro varias veces** —`?rol=usuario&rol=admin`—. La especificación no dice qué hacer con eso, así que cada componente decide: unos toman el primero, otros el último, otros los concatenan, otros arman una lista. El ataque explota que **dos componentes de la cadena resuelvan el duplicado distinto**.

Es primo de [[CWE-444 - Inconsistent Interpretation of HTTP Requests]] (request smuggling) y de la discrepancia de caché de [[MOC - Web cache]]: los tres abusan que dos parsers de lo mismo no coincidan. En smuggling la discrepancia es sobre dónde termina la petición; en HPP es sobre qué valor tiene un parámetro repetido.

## Cómo resuelve cada tecnología

La resolución del duplicado depende del marco de trabajo, y esa tabla **es** el dominio. Ejemplos:

| Tecnología | `?x=1&x=2` da |
|---|---|
| PHP / Apache | `2` (el último) |
| ASP.NET / IIS | `1,2` (concatenado) |
| JSP / Tomcat | `1` (el primero) |
| Python (según el marco) | `1` o `[1,2]` |
| Node / Express | `[1,2]` (lista) |

Cuando un WAF valida con una resolución y la aplicación usa otra, el atacante mete un valor inocente donde el WAF mira y el malicioso donde la aplicación mira.

## Qué se consigue

- **Bypass de un filtro o WAF.** El WAF valida el primer valor (inocente), la aplicación usa el último (malicioso). Es una forma de colar cualquier otra inyección —SQLi, XSS— por un WAF que la bloquearía.
- **Bypass de lógica o de autorización.** Duplicar un parámetro de control —`admin=false&admin=true`— si la validación y el uso discrepan.
- **Inyección de parámetros en una petición al backend.** Si la aplicación reenvía la entrada a otro servicio construyendo una URL, meter un `&` inyecta parámetros nuevos en esa petición —segundo orden—.
- **Inyección de parámetros en URLs generadas** del lado del cliente —un enlace, un formulario—.

## Por qué la mitigación es de consistencia

No se filtra un carácter: la petición es válida. La mitigación es que la cadena resuelva los duplicados **igual en todas las capas**, o que se rechacen las peticiones con parámetros repetidos.

- **Normalizar** los parámetros duplicados en el borde —rechazar o quedarse con uno— antes de que lleguen a la aplicación.
- Que el WAF y la aplicación usen la **misma** resolución.
- Validar la entrada después de resolver el duplicado, no antes.

## Referencias canónicas

- [CWE-235](https://cwe.mitre.org/data/definitions/235.html)
- [CWE-444](https://cwe.mitre.org/data/definitions/444.html) — request smuggling, el primo por discrepancia de parseo
- WSTG-INPV-04
- OWASP — Testing for HTTP Parameter Pollution
