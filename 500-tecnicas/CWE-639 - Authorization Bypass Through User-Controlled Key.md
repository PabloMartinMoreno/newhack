---
tipo: tecnica
taxonomia: cwe
identificador: CWE-639
wstg: WSTG-ATHZ-04
tacticas: []
aliases:
  - CWE-639
  - IDOR
  - Insecure direct object reference
  - Referencia directa insegura a objetos
tags:
  - dominio/web
---

# CWE-639 - Authorization Bypass Through User-Controlled Key

> [!note] Nota paraguas
> Sin contenido operativo. La decisión vive en [[MOC - Broken access control]]; la variante en [[Control de acceso - IDOR]]; el método de prueba en [[Control de acceso - matriz de pruebas]].

## Qué es

La aplicación usa un identificador provisto por el cliente para localizar un objeto, y **no verifica que quien lo pide tenga derecho a ese objeto en particular**. Cambiar el identificador devuelve el recurso de otro.

## Por qué existe

Porque autenticar y autorizar son cosas distintas y la primera es mucho más visible que la segunda. Un `middleware` que exige sesión válida se escribe una vez y protege toda la aplicación; verificar que *este* usuario es dueño de *este* objeto hay que escribirlo en **cada consulta**, y basta olvidarlo una vez.

El resultado es una asimetría característica: la aplicación está perfectamente autenticada y no autorizada. La sesión es legítima, el usuario es quien dice ser, y aun así lee datos ajenos.

## Por qué es el hallazgo más frecuente

Tres razones que se refuerzan:

- **No deja rastro de error.** Toda petición es válida, autenticada y devuelve `200`. No hay excepción, ni error de sintaxis, ni nada anómalo que un desarrollador note al probar.
- **Los tests no lo ven.** Las pruebas automatizadas se escriben desde la perspectiva de un usuario que accede a lo suyo. Nadie escribe el test de "el usuario A no puede ver lo de B" salvo que ya haya pensado en el problema.
- **Escala con el código.** Cada endpoint nuevo es una oportunidad nueva. Una aplicación grande tiene cientos de puntos donde el control puede faltar, y basta uno.

## Lo que no es una mitigación

**Identificadores no predecibles.** Cambiar un entero secuencial por un UUID no arregla nada: **oculta**. El control de acceso sigue ausente, y el identificador se filtra igual por listados, respuestas de otros endpoints, exportaciones, mensajes compartidos o el historial del propio usuario. Es defensa en profundidad razonable y solución cero.

Es la confusión más común del dominio y conviene ser explícito en un informe: si el hallazgo se cierra cambiando el formato del identificador, no se cerró.

## La mitigación real

Verificar la propiedad o el permiso **en la consulta misma**, no antes ni después: pedir el objeto por identificador *y* por dueño a la vez, de modo que un objeto ajeno simplemente no exista para esa consulta. Que sea imposible escribir la consulta insegura es mejor que recordar el chequeo.

## Ejes que la descomponen

Ver [[MOC - Broken access control]]. Resumen: dirección × dónde falla el control × vector × obstáculo × impacto.

## Referencias canónicas

- [CWE-639](https://cwe.mitre.org/data/definitions/639.html)
- WSTG-ATHZ-04
- OWASP Top 10 — A01 Broken Access Control
