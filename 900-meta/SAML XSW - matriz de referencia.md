---
tipo: meta
aliases:
  - XSW patterns
  - patrones de envoltura de firma
tags:
  - meta/referencia
  - dominio/web
---

# SAML XSW - matriz de referencia

> [!info] Referencia pura, no un zettel
> Los ocho patrones de envoltura de firma XML, en orden de prueba. El criterio está en [[SAML - envoltura de firma XML]]; decodificar la aserción, en [[SAML - matriz de identificación]].

La envoltura funciona cuando **el verificador y el lector miran elementos distintos**. Cada patrón coloca la aserción firmada donde el verificador la encuentra y una aserción falsa donde el lector busca los datos. Cuál funciona depende de cómo la biblioteca resuelve la referencia de la firma, y por eso se prueban en orden.

## Los dos ingredientes

- **Aserción firmada original** — intacta, con su `ID` y su firma válida. Se conserva sin tocar.
- **Aserción falsa** — copia con el `NameID` cambiado a la víctima, **sin** firma. Se le da un `ID` distinto o el mismo, según el patrón.

La diferencia entre los ocho patrones es **dónde** va cada una y qué `ID` llevan.

## Orden de prueba

Del más simple al más raro. SAML Raider los aplica todos; a mano se prueban en este orden.

### XSW1 — firma envuelve una Response falsa

Sobre la firma de la **Response**. Se agrega una Response falsa como hermana, con `ID` nuevo, y la original firmada queda dentro de la falsa.

### XSW2 — como XSW1, firma con referencia distinta

Igual pero la firma referencia por un `ID` que ahora resuelve a la copia. El verificador valida la original; el lector toma la falsa.

### XSW3 — aserción falsa antes de la firmada

Sobre la firma de la **Assertion**. Aserción falsa como hermana **antes** de la original, las dos hijas de la Response. Muchos lectores toman la primera aserción; el verificador valida la segunda, que sigue firmada.

### XSW4 — falsa envuelve a la original

Como XSW3 pero la aserción original queda **dentro** de la falsa.

### XSW5 — la firma dentro de la falsa apunta afuera

La firma de la aserción original se copia dentro de la falsa, con su referencia apuntando a la original. El lector ve la falsa completa; el verificador sigue el `ID` a la original.

### XSW6 — original dentro de la firma de la falsa

Anida la original dentro del elemento `<Signature>` de la aserción falsa.

### XSW7 — `Extensions` como contenedor

La aserción firmada se mete en un elemento `<Extensions>`, que tiene un esquema laxo y admite contenido arbitrario. La falsa queda en la posición normal.

### XSW8 — `Object` como contenedor (para SAML sin `ID` en la firma)

Para firmas que no usan referencia por `ID`. La original va dentro de un `<Object>` de la firma; la falsa toma su lugar.

## Tabla de decisión

| Firma cubre | Patrones a probar |
|---|---|
| La Response | XSW1, XSW2 |
| La Assertion | XSW3, XSW4, XSW5, XSW6 |
| Cualquiera, con contenedor laxo | XSW7, XSW8 |

Si no se sabe qué firma cubre, se prueban todos en orden. El de la matriz de identificación —mirar dónde está el `<Signature>` y qué `ID` referencia— acota cuáles tienen sentido.

## Qué cambiar en la aserción falsa

En todos los patrones, la falsa lleva:

```xml
<saml:NameID>administrador@objetivo.com</saml:NameID>
```

Y si el objetivo es escalar en vez de suplantar:

```xml
<saml:Attribute Name="role">
  <saml:AttributeValue>admin</saml:AttributeValue>
</saml:Attribute>
```

Recordar que la falsa **no se firma**: toda la gracia es que su validez la presta la original firmada.

## Manejo de `ID`

El `ID` es la pieza que hace o rompe cada patrón:

| Situación | Qué hacer con los `ID` |
|---|---|
| El verificador resuelve por `ID` referenciado en la firma | La original mantiene su `ID`; la falsa lleva otro |
| El lector toma "la primera aserción" | El `ID` no importa, importa la posición |
| La biblioteca rechaza `ID` duplicados | Dar `ID` distintos, o el patrón no aplica |
| El verificador toma "el primer elemento con este `ID`" | `ID` duplicado, con la original primero |

Los `ID` duplicados son el corazón de la mitad de los patrones y la razón por la que las bibliotecas corregidas los rechazan de plano.

## Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El SP rechaza por XML mal formado | Un cierre de etiqueta quedó mal. `xmllint` antes de reenviar |
| Firma inválida en todos los patrones | El verificador y el lector miran el mismo nodo. Rama cerrada |
| Acepta pero con la identidad original | La falsa está en el lugar equivocado para ese lector. Otro patrón |
| `Duplicate ID` | La biblioteca los rechaza. Probar los patrones con `ID` distintos |
| Funciona en XSW3 y no en XSW1 | La firma cubre la Assertion, no la Response. Esperable |
| Ninguno funciona | Biblioteca moderna que valida y lee el mismo nodo. Reportar que la firma se valida bien |

## Relacionadas

[[MOC - SAML]] · [[SAML - envoltura de firma XML]] · [[SAML - matriz de identificación]]
