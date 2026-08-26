---
tipo: moc
dominio: web
aliases:
  - MOC prototype pollution
tags:
  - dominio/web
---

# MOC - Prototype pollution

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-1321 - Prototype Pollution]]. Confirmar la contaminación, en [[Prototype pollution - matriz de identificación]]. Acá vive **la decisión**.

Este dominio se pasa por alto porque su mitad barata no parece nada. Contaminar un prototipo, mirado solo, es escribir una propiedad de más en un objeto que a nadie le importa. Lo que lo vuelve serio es que el efecto es **global al proceso** y que un gadget lo convierte en cualquier cosa —escalada, ejecución, XSS—. El error de leerlo como un problema de JavaScript menor es el mismo que leer [[MOC - Deserialización]] como un problema de RCE: se descarta lo explotable.

| Eje | Valores |
|---|---|
| Lado | servidor · cliente |
| Gadget | propiedad que gobierna · ejecución (servidor) · XSS (cliente) · ninguno |
| Vector | cuerpo JSON · query string · fragmento · documento almacenado → matriz |
| Clave | `__proto__` · `constructor.prototype` · `prototype` → matriz |

El **lado es el eje raíz**, no el gadget, y es la decisión de taxonomía del dominio. Servidor y cliente comparten el mecanismo de contaminación pero divergen en todo lo demás: qué gadget existe, qué impacto se alcanza, qué telemetría lo ve. Un XSS por contaminación del lado del cliente no tiene nada que ver operativamente con un `NODE_OPTIONS` del lado del servidor, aunque la primera petición se parezca.

El vector y la clave van a matriz por el mismo criterio de siempre: cambian la sintaxis del payload, no la decisión.

## Árbol de decisión — qué puedo hacer con la contaminación

```
¿Confirmaste que contamina?    → [[Prototype pollution - matriz de identificación]]
├─ No → no hay dominio. Probá las tres claves antes de descartar
└─ Sí — ¿de qué lado?
   │
   ├─ SERVIDOR
   │  ├─ 1. Lote de propiedades genéricas (esAdmin, role, skipValidation…)
   │  │     → [[Prototype pollution - propiedad que gobierna una decisión]]   ← PRIMERO
   │  │       una petición, sin gadget, sin conocer la pila
   │  └─ 2. ¿Hay gadget en las bibliotecas cargadas?
   │        → [[Prototype pollution - gadget del lado del servidor]]
   │          child_process, motor de plantillas, resolución de módulos
   │
   └─ CLIENTE
      ├─ ¿Hay un sink de DOM directo?
      │  └─ Sí → [[XSS - DOM-based]] es más barato. Usá aquello
      └─ ¿No, pero hay biblioteca con gadget?
         → [[Prototype pollution - gadget del lado del cliente]]
           construcción de HTML, config del sanitizador, carga de recursos
```

Tres cosas que este orden codifica:

**La propiedad genérica va antes que el gadget.** No necesita conocer la pila ni encontrar una cadena: contamina un lote de nombres plausibles y mira qué cambia. Resuelve seguido y cuesta una petición, mientras que el gadget de ejecución puede no existir.

**Del lado del cliente, comparar con DOM-based antes de invertir.** Si hay un sink directo, [[XSS - DOM-based]] llega al mismo lugar con mucho menos trabajo. La contaminación del lado del cliente se justifica cuando **no** hay sink pero sí hay gadget, o cuando hace falta evadir un sanitizador que un XSS clásico no evade.

**Sin gadget sigue siendo un hallazgo.** Una contaminación confirmada sin impacto máximo demostrado es un hallazgo real —el fondo es una función que copia mal—, y se reporta con lo que se pudo mostrar. Abandonarla por no llegar a RCE es el error del dominio.

## Árbol de decisión — no encontré gadget, ¿qué queda?

```
Contamina pero no hay cadena de ejecución
├─ ¿Alguna bandera de autorización sin definir?
│     → escalada → [[Prototype pollution - propiedad que gobierna una decisión]]
├─ ¿Alguna opción que relaje una validación?
│     → saltear controles de entrada aguas abajo
├─ ¿root o rutas de servido de archivos?
│     → [[Path traversal]] por contaminación
└─ ¿Nada?
      → reportá la contaminación: función de mezcla insegura,
        con el efecto global como agravante
```

El agravante que hay que escribir siempre en el informe es el **alcance**: a diferencia de [[Control de acceso - mass assignment]], que toca un objeto, esto toca todos los del proceso, incluidos los de otros usuarios. Una contaminación de baja severidad aparente puede estar afectando peticiones ajenas sin que nadie lo note.

## Cheatsheets — entrada directa a los payloads

- [[Prototype pollution - matriz de identificación]] — Las tres claves, confirmación en cliente y servidor, funciones vulnerables, evasión de filtros, herramienta
- [[Prototype pollution gadgets - matriz de referencia]] — Propiedades genéricas, `NODE_OPTIONS`, plantillas, Express, HTML del cliente, config del sanitizador, carga de recursos

## Orden de aprendizaje

1. [[CWE-1321 - Prototype Pollution]] — por qué escribir en `__proto__` escribe en todos los objetos
2. [[Prototype pollution - matriz de identificación]] — confirmar antes de nada, y con qué canal
3. [[Prototype pollution - propiedad que gobierna una decisión]] — la mitad que no necesita gadget, y la que más rinde
4. [[Prototype pollution - gadget del lado del servidor]] — de contaminación a ejecución, cuando la pila lo permite
5. [[Prototype pollution - gadget del lado del cliente]] — el mismo mecanismo terminando en XSS

El punto 3 va antes que los gadget a propósito. La imagen del dominio es "contaminación a RCE", y esa imagen hace saltearse la escalada de autorización, que no necesita cadena y funciona más veces.

## Relación con otros dominios

- [[MOC - Broken access control]] — [[Prototype pollution - propiedad que gobierna una decisión]] **es** [[Control de acceso - mass assignment]] por otro camino, con la misma lista de campos y la misma detección. La diferencia es el alcance: mass assignment escribe en un objeto, la contaminación en todos. Su clase vecina es [[CWE-915 - Improperly Controlled Modification of Dynamically-Determined Object Attributes]].
- [[MOC - Deserialización]] — mismo reparto entre la primitiva barata (contaminar / tener el blob) y la cadena cara (gadget). Los dos dominios se enseñan al revés por la misma razón: la fama del caso caro tapa el caso frecuente.
- [[MOC - Cross-site scripting]] — el gadget del lado del cliente termina en XSS, y evade los filtros que detienen un XSS clásico porque el payload no lleva etiquetas.
- [[MOC - SSTI]] — el gadget de motor de plantillas del lado del servidor llega al mismo efecto que [[SSTI - ejecución directa]] por otro camino. Conviene revisar los dos cuando la pila es Node con plantillas.
- [[MOC - File inclusion]] — contaminar `root` o rutas de servido convierte el dominio en [[Path traversal]].

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Contaminación (cualquiera) | [[Log de acceso del servidor web]] · [[Registro del WAF]] | `__proto__` o `constructor[prototype]` en la petición — firma que sí funciona |
| Propiedad que gobierna | [[Log de auditoría de la aplicación]] | Privilegio ejercido sin el cambio de estado que lo concede |
| Gadget del servidor | [[Proceso hijo del servidor web]] | Intérprete hijo del servidor de aplicación |
| Gadget del servidor | [[Log de errores del servidor web]] | Excepciones dispersas sin relación con la petición que las causa |
| Gadget del cliente | [[Informe de violación de CSP]] | Solo si el gadget viola la política — el de carga de recursos no |

Una observación que este dominio deja y que corrige una regla del vault:

**Acá la firma sí funciona, y es la excepción.** Todo el vault insiste en detectar efecto y no firma, porque las firmas se evaden. Prototype pollution es el caso donde la firma rinde: las cadenas `__proto__` y `constructor[prototype]` **no aparecen en tráfico legítimo casi nunca**, así que una regla de firma sobre ellas tiene pocos falsos positivos. Lo cubre [[Payload de inyección en parámetros de la URL]], la única detección de firma del vault, y este es el dominio donde mejor rinde.

La letra chica que la limita es la misma de siempre: el payload por el cuerpo de un `POST` no lo ve [[Log de acceso del servidor web]] —solo [[Registro del WAF]]—, y el que viaja en el fragmento no lo ve nadie del lado del servidor.

Ninguna detección propia hizo falta: sexto dominio consecutivo cerrado reutilizando reglas. [[Cambio de privilegio fuera del flujo administrativo]] cubre la escalada, [[Intérprete de comandos como hijo del servidor web]] la ejecución.

## Huecos conocidos

- [x] Los dos lados, con su gadget propio
- [x] La mitad sin gadget — escalada por propiedad
- [x] Identificación y gadgets — dos matrices
- [x] Cara azul — cubierta por detecciones existentes, y el caso donde la firma sí rinde
- [ ] **Contaminación almacenada.** Si el objeto contaminado se guarda en una base NoSQL y se recarga, la contaminación sobrevive al reinicio del proceso. No está modelada como variante propia porque el vector cambia y el impacto no; anotado por si aparece un caso que lo justifique
- [ ] Contaminación en otros lenguajes: Python (`__class__`), Ruby, PHP con `__wakeup`. Son mecanismos distintos con el mismo nombre prestado — dominios aparte si se escriben
