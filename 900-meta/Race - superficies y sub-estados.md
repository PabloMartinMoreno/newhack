---
tipo: meta
aliases:
  - superficies de race
  - dónde hay condiciones de carrera
tags:
  - meta/referencia
  - dominio/web
---

# Race - superficies y sub-estados

> [!info] Referencia pura, no un zettel
> Dónde viven las ventanas y qué se saca de cada una. Cómo disparar la colisión está en [[Race - matriz de disparo]]; el criterio, en las tres notas de `600-tradecraft/`.

El dominio no se busca con un payload sino reconociendo **patrones de lógica** que dejan ventana. Este es el catálogo de dónde mirar.

## 1. Superación de límite — el patrón contador

Ver [[Race - superación de límite]]. Cualquier "solo N veces" verificado antes de aplicarse.

| Superficie | Qué se saca |
|---|---|
| Tarjeta de regalo / cupón / crédito | Canjear el mismo saldo varias veces |
| Retiro / transferencia | Sacar más de lo que hay; saldo negativo |
| "Un voto / reseña / like por cuenta" | Multiplicar |
| Código de invitación de un solo uso | Reutilizar |
| Descuento de un solo uso | Aplicar varias veces |
| Límite de tasa de la aplicación | Superar el número permitido |
| Stock / reserva de asiento | Comprar el mismo ítem dos veces |
| Puntos / recompensas | Duplicar el canje |

Pista de reconocimiento: cualquier número que "no debería bajar de cero" o "no debería pasar de N".

## 2. Colisión entre endpoints — el patrón dos-operaciones

Ver [[Race - colisión entre endpoints]]. Dos operaciones que comparten estado y no deben cruzarse.

| Par de operaciones | Estado que se cruza |
|---|---|
| Aplicar cupón + confirmar pago | Precio calculado vs precio cobrado |
| Cambiar correo + enviar verificación | Token válido para el correo viejo |
| Agregar al carrito + cobrar | Contenido del carrito al momento del cobro |
| Cambiar permiso + realizar acción | Permiso viejo o nuevo según el cruce |
| Aceptar invitación + cambiar rol | Rol al momento de aceptar |

Pista: flujos de dos pasos donde el estado intermedio, si se lo alcanza, es aprovechable.

## 3. Subestado oculto — el patrón operación-no-atómica

Ver [[Race - subestado oculto]]. Una operación que parece atómica pero tiene pasos internos.

| Operación | Subestado alcanzable |
|---|---|
| Registro (validar + crear) | Dos cuentas con el mismo identificador |
| Registro multipaso | Cuenta sin el paso de seguridad posterior |
| Crear objeto + asignar permisos por defecto | Objeto sin permisos, accesible |
| Aplicar token + marcarlo usado | Token de un solo uso con varios efectos |
| Reservar + confirmar | Recurso reservado y confirmado dos veces |

Pista: "construcción parcial" — un objeto o cuenta que queda a medio crear y es usable en ese estado.

## 4. Ataques sensibles al tiempo — el vecino que no es carrera

No son condiciones de carrera pero se prueban con las mismas herramientas y aparecen en el mismo reconocimiento, así que van acá para no perderlos:

- **Tokens predecibles por tiempo.** Si un token de restablecimiento se genera con la marca de tiempo como semilla, dos peticiones en el mismo instante producen el mismo token. Se cruza con [[Sesión - token predecible]].
- **Comparación con fuga temporal.** Un `==` que corta al primer byte distinto filtra el largo de la coincidencia por tiempo. Se cruza con [[La latencia como canal de datos]].

Estos no necesitan colisión, necesitan **coincidencia temporal** o **medición**, pero el instrumental de disparo simultáneo de [[Race - matriz de disparo]] sirve para forzar el mismo instante.

## 5. Qué endpoint elegir cuando hay varios

Si el mismo efecto se puede disparar desde endpoints distintos, elegir el **más lento**: una operación que tarda más tiene una ventana más ancha, y colisiona más fácil. Un endpoint que hace mucho trabajo antes de escribir el estado es mejor objetivo que uno optimizado.

## 6. Confirmar el impacto sin exagerar

La severidad de una carrera va de trivial a crítica según qué límite se supera:

| Resultado | Severidad |
|---|---|
| Saldo negativo / dinero duplicado | Crítica |
| Cuenta administrativa por doble registro | Crítica |
| Objeto sin permisos accesible | Alta |
| Voto o like duplicado | Baja / informativa |

Reportar el impacto real, no "hay una condición de carrera": duplicar un like y vaciar una cuenta son el mismo fallo con severidades incomparables, igual que en [[MOC - CSRF]].

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| No encuentro ningún límite obvio | Buscar subestados, § 3, o pares de operaciones, § 2 |
| La ráfaga no supera el límite | Puede haber atomicidad; probar un endpoint más lento, § 5 |
| El doble efecto no sirve de nada | El límite superado no tiene impacto. Buscar otro |
| Parece carrera pero es token predecible | Es § 4, no una carrera. Otra técnica |
| Colisiona pero la base rechaza | Hay restricción de datos. Buena mitigación; no hay hallazgo |

## Relacionadas

[[MOC - Race conditions]] · [[Race - matriz de disparo]] · [[Sesión - token predecible]] · [[La latencia como canal de datos]]
