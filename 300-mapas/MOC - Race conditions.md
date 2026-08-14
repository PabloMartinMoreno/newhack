---
tipo: moc
dominio: web
aliases:
  - MOC race conditions
  - condiciones de carrera
tags:
  - dominio/web
---

# MOC - Race conditions

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-362 - Concurrent Execution using Shared Resource with Improper Synchronization]]. Disparar la colisión, en [[Race - matriz de disparo]]. Acá vive **la decisión**.

Este dominio es sobre **cuándo**, no sobre qué. En casi todo el resto del vault el ataque está en el contenido de la petición —un payload, un operador—; acá la petición es perfectamente válida y lo único anómalo es que llegan varias en la misma ventana de milisegundos. No hay nada que filtrar en la entrada porque la entrada no tiene nada de malo.

| Eje | Valores |
|---|---|
| Tipo de ventana | superación de límite · colisión entre endpoints · subestado oculto |
| Técnica de disparo | ataque de un solo paquete (HTTP/2) · último byte (HTTP/1.1) → matriz |
| Impacto | dinero/saldo · cuentas · permisos · límites de negocio |

**El tipo de ventana es el eje raíz.** Es lo que decide todo el enfoque de reconocimiento: buscar un contador, buscar dos operaciones que se cruzan, o buscar una operación no atómica. La técnica de disparo —cómo se hace que las peticiones colisionen— es ortogonal: la misma para las tres ramas, y va a matriz.

## Árbol de decisión — qué ventana estoy atacando

```
¿Qué tipo de ventana hay?
│
├─ ¿Una operación con un LÍMITE verificado antes de aplicarse?
│  (saldo, cupo, uso único, "una vez por cuenta")
│     → [[Race - superación de límite]]   ← PRIMERO, el caso base
│       repetir la MISMA operación N veces en la ventana
│
├─ ¿DOS operaciones distintas que comparten estado?
│  (aplicar cupón + confirmar pago, cambiar correo + verificar)
│     → [[Race - colisión entre endpoints]]
│       cruzarlas para pegar en el estado intermedio
│
└─ ¿UNA operación que parece atómica pero no lo es?
   (registro que valida-luego-crea, token que actúa-luego-marca)
      → [[Race - subestado oculto]]
        colisionar contra sí misma para partir sus pasos internos
```

Tres cosas que este orden codifica:

**La superación de límite va primero porque es la más común y la más fácil de reconocer.** Cualquier "solo N veces" es candidato, y el ataque es repetir la misma petición. Las otras dos requieren entender el flujo de negocio y son más caras.

**La dificultad crece con la sutileza del estado.** Superar un límite se ve en el contador; cruzar dos operaciones requiere saber qué estado intermedio existe; partir una operación no atómica requiere **sospechar** un subestado que ninguna interfaz muestra. El reconocimiento pasa de leer un número a inferir una costura.

**La técnica de disparo es la misma para las tres.** El ataque de un solo paquete sobre HTTP/2 es lo que volvió el dominio explotable de forma fiable, eliminando el jitter de la red. Sin esa técnica, las tres ramas son teóricas; con ella, productivas. Por eso [[Race - matriz de disparo]] se lee antes que las técnicas.

## Árbol de decisión — colisioné, ¿qué conseguí?

```
El límite se superó / el estado quedó inconsistente
├─ ¿Saldo, dinero, créditos duplicados? → crítica
├─ ¿Cuenta administrativa por doble registro? → crítica
├─ ¿Objeto sin permisos, accesible? → alta → [[MOC - Broken access control]]
├─ ¿Token de un solo uso con varios efectos? → según qué habilita
└─ ¿Voto / like / acción trivial duplicada? → informativa, no la infles
```

La severidad va de trivial a crítica con el mismo fallo, igual que en [[MOC - CSRF]]: se reporta el impacto real, no "hay una condición de carrera". Vaciar una cuenta y duplicar un like son la misma vulnerabilidad con severidades incomparables.

## Cheatsheets — entrada directa

| Matriz | Cubre |
|---|---|
| [[Race - matriz de disparo]] | Ataque de un solo paquete, último byte, Turbo Intruder, calentar conexión, calibrar, detectar la ventana |
| [[Race - superficies y sub-estados]] | Dónde viven las ventanas por tipo, ataques sensibles al tiempo, elegir el endpoint más lento, severidad |

## Orden de aprendizaje

1. [[CWE-362 - Concurrent Execution using Shared Resource with Improper Synchronization]] — comprobar-luego-actuar y la ventana
2. [[Race - matriz de disparo]] — el ataque de un solo paquete va antes que las técnicas, sin él son teóricas
3. [[Race - superación de límite]] — el caso base, el patrón contador
4. [[Race - colisión entre endpoints]] — dos operaciones que se cruzan
5. [[Race - subestado oculto]] — la operación no atómica, la más sutil

El punto 2 va antes que las técnicas y es la particularidad del dominio: acá el "cómo se dispara" es más difícil que el "qué se ataca", al revés de casi todos los demás. La técnica de sincronización es el conocimiento que hace la diferencia.

## Relación con otros dominios

- [[MOC - Request smuggling]] — el otro dominio donde la **temporización y el nivel de paquete** son la técnica, no el payload. El ataque de un solo paquete de las carreras y la desincronización del smuggling comparten el instrumental de HTTP/2 crudo y Turbo Intruder, y las dos matrices de disparo se referencian.
- [[MOC - Broken access control]] — muchas carreras terminan en un objeto sin permisos o una cuenta con rol de más; el subestado oculto es una vía a la escalada que [[Control de acceso - matriz de pruebas]] no cubre porque no es un problema de quién pide sino de cuándo.
- [[MOC - Autenticación]] — el doble registro y el bypass de límite de intentos por carrera se cruzan con aquel dominio.
- [[Sesión - token predecible]] y [[La latencia como canal de datos]] — los ataques sensibles al tiempo de [[Race - superficies y sub-estados]] § 4 no son carreras pero comparten instrumental y reconocimiento.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Superación de límite | [[Log de acceso del servidor web]] | Ráfaga de peticiones idénticas casi simultáneas |
| Superación de límite | [[Log de auditoría de la aplicación]] | **Invariante roto**: saldo negativo, uso único duplicado |
| Colisión entre endpoints | [[Log de acceso del servidor web]] | Dos flujos secuenciales llegando solapados |
| Subestado oculto | [[Log de auditoría de la aplicación]] | Estado imposible: dos cuentas mismo id, objeto sin permisos |

Una sola observación, pero es la más limpia del vault sobre `forma:`:

**Es el dominio que pide detección por invariante y prohíbe la de firma.** Cada petición es individualmente válida —canjear la tarjeta una vez es legítimo—, así que **no hay ninguna firma que distinga el ataque**: la única señal es que el resultado es imposible. El saldo no debería quedar negativo; un token de un solo uso no debería tener dos efectos; no debería haber dos cuentas con el mismo identificador único. Eso es exactamente `forma: invariante` —una condición que nunca debería violarse sobre una secuencia—, la misma que [[Actividad de sesión posterior a su cierre]] y [[Ticket de servicio sin ticket inicial previo]].

El agregado ayuda como señal temprana —la ráfaga de peticiones idénticas y simultáneas es anómala—, pero es débil en la colisión entre endpoints, donde no hay ráfaga idéntica. El invariante, en cambio, confirma las tres ramas por igual. Es el argumento más fuerte del vault a favor de que `forma: invariante` sea un tipo de detección de primera clase y no una regla sobre un evento.

Décimo cuarto dominio cerrado sin detección nueva. Los dos candidatos —el agregado de la ráfaga simultánea y el invariante sobre el resultado— son escribibles con [[Log de auditoría de la aplicación]], que ya se modela; quedan anotados abajo.

## Huecos conocidos

- [x] Los tres tipos de ventana
- [x] La técnica de disparo — ataque de un solo paquete y último byte
- [x] Dónde buscar y los ataques sensibles al tiempo vecinos — dos matrices
- [x] Cara azul de invariante — identificada, con dos candidatos escribibles sobre el log de auditoría
- [ ] **La detección por invariante es escribible ya.** "Ningún saldo negativo", "ningún uso único duplicado" son invariantes sobre el log de auditoría, `forma: invariante`. Candidatos de detección propia, hueco de trabajo
- [ ] Carreras a nivel de sistema de archivos y de sistema operativo (TOCTOU clásico) — otro contexto, fuera del alcance web de este MOC
- [ ] Carreras en sistemas distribuidos: el mismo fallo cuando el estado compartido está en varios nodos sin bloqueo global
