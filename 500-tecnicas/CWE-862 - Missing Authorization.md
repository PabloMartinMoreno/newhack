---
tipo: tecnica
taxonomia: cwe
identificador: CWE-862
wstg: [WSTG-ATHZ-02, WSTG-ATHZ-03]
tacticas: []
aliases:
  - CWE-862
  - Missing authorization
  - Falta de autorización
tags:
  - dominio/web
---

# CWE-862 - Missing Authorization

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Broken access control]]; las variantes en [[Control de acceso - escalada vertical]] y [[Control de acceso - salto de contexto]].

## Qué es

La aplicación **no comprueba en absoluto** si quien pide una acción tiene permiso para ejecutarla. No es que compruebe mal: es que no comprueba.

Se distingue de [[CWE-639 - Authorization Bypass Through User-Controlled Key]] en qué falta. En IDOR el control de rol existe y falta el de propiedad; acá falta el control entero, y por eso el impacto típico es **vertical**: un usuario común ejecuta funciones de administrador.

## Por qué existe

Casi siempre por una de estas tres, y las tres se ven en el mismo informe:

- **El control vive en la interfaz.** El botón de administración no se muestra a quien no es administrador, y ahí termina la protección. La ruta responde igual a quien la pida directamente. Es el caso de `forced browsing`: no hay que romper nada, hay que **conocer la URL**.
- **El control se aplica por ruta, no por función.** Un filtro protege `/admin/*` y la función administrativa vive además en `/api/v2/users/delete`, que nadie agregó al filtro. La inconsistencia entre rutas equivalentes es donde vive este bug.
- **El control cubre unos verbos y no otros.** `GET /admin/users` exige rol; `POST` al mismo recurso, no. Frecuentísimo en APIs que crecieron por partes.

## El caso que más se olvida

Los **saltos de contexto** en flujos de varios pasos: pagar sin haber validado el carrito, confirmar sin haber verificado el correo, llegar al paso cuatro con una petición directa. Formalmente es lo mismo —falta la comprobación de que el paso anterior ocurrió— pero se busca distinto, porque no hay ninguna ruta que "parezca" administrativa. Ver [[Control de acceso - salto de contexto]].

## La mitigación real

**Denegar por defecto.** Que el marco de trabajo exija una declaración explícita de permiso en cada punto de entrada y rechace lo que no la tenga. Mientras el modelo sea "permitir salvo que alguien se acuerde de proteger", la pregunta no es si hay un endpoint sin control sino cuántos.

Complemento necesario: que el control viva en una capa que **toda** ruta atraviese, no replicado en cada controlador, donde la copia número cuarenta se escribe distinta.

## Ejes que la descomponen

Ver [[MOC - Broken access control]]. Resumen: dirección × dónde falla el control × vector × obstáculo × impacto.

## Referencias canónicas

- [CWE-862](https://cwe.mitre.org/data/definitions/862.html)
- [CWE-425](https://cwe.mitre.org/data/definitions/425.html) — Direct Request, el caso de `forced browsing`
- WSTG-ATHZ-02, WSTG-ATHZ-03
- OWASP Top 10 — A01 Broken Access Control
