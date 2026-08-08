---
tipo: tecnica
taxonomia: cwe
identificador: CWE-915
wstg: WSTG-BUSL-01
tacticas: []
aliases:
  - CWE-915
  - Mass assignment
  - Autobinding
  - Object injection
tags:
  - dominio/web
---

# CWE-915 - Mass Assignment

> [!note] Nota paraguas
> Nombre oficial completo: *Improperly Controlled Modification of Dynamically-Determined Object Attributes*. Sin contenido operativo: la decisión vive en [[MOC - Broken access control]]; la variante, en [[Control de acceso - mass assignment]].

## Qué es

El marco de trabajo asigna automáticamente los campos recibidos a las propiedades de un objeto, y el atacante **agrega campos que el formulario no tenía**. Si uno de esos campos gobierna privilegios, precio o estado, se escribe algo que ningún control de acceso previó porque nadie previó que ese campo fuera escribible.

## Por qué existe

Es una comodidad del marco de trabajo convertida en superficie. Escribir la asignación campo por campo es tedioso y propenso a olvidos, así que todos los marcos modernos ofrecen hacerlo de una. Esa función no distingue entre un campo que el usuario debía poder editar y uno que no: **la única diferencia está en la intención del programador**, que no está escrita en ningún lado.

## Por qué está en este dominio y no en otro

Porque es escalada de privilegios por escritura. El resultado es idéntico al de [[CWE-862 - Missing Authorization]] —un usuario común obtiene capacidades de administrador— y lo que falla es lo mismo: nadie verificó que este usuario pudiera modificar este atributo. Cambia el mecanismo, no la clase.

La diferencia práctica está en cómo se busca: no manipulando identificadores ni rutas, sino **agregando campos** a peticiones que ya funcionan.

## Dónde se encuentra

El indicio más fiable no está en la petición: está en la **respuesta**. Si un endpoint devuelve un objeto con campos que el formulario de edición no muestra, esos campos son los candidatos. Enviarlos de vuelta en la petición de actualización es toda la técnica.

Por eso las APIs REST que devuelven el objeto completo son el terreno natural del problema: documentan sus propios campos internos.

## La mitigación real

Lista **blanca** de campos asignables por endpoint y por rol. Las listas negras fallan por la razón de siempre: hay que acordarse de agregar cada campo nuevo, y el campo que se olvida es el que importa.

Complemento: separar el objeto que se recibe del que se persiste, de modo que los campos sensibles no existan siquiera en el que llega del cliente.

## Ejes que la descomponen

Ver [[MOC - Broken access control]]. Resumen: dirección × dónde falla el control × vector × obstáculo × impacto.

## Referencias canónicas

- [CWE-915](https://cwe.mitre.org/data/definitions/915.html)
- WSTG-BUSL-01
- OWASP API Security — API3 Broken Object Property Level Authorization
