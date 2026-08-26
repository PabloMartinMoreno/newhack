---
tipo: moc
dominio: web
aliases:
  - MOC GraphQL
tags:
  - dominio/web
---

# MOC - GraphQL

> [!abstract] Nota de referencia paraguas
> Encontrar el endpoint y sacar el esquema, en [[GraphQL - matriz de reconocimiento]]. Acá vive **la decisión**.

Tercer dominio del vault sin CWE propia, después de [[MOC - OAuth]] y [[MOC - SAML]]. GraphQL no es una vulnerabilidad: es una **tecnología de API** donde varias clases conocidas reaparecen con mecánicas propias, más dos que son características suyas. Como en OAuth y SAML, cada nota cuelga de su clase real.

| Fase / técnica | `clase:` | Nota |
|---|---|---|
| Descubrir el esquema | `CWE-200` | [[GraphQL - introspección del esquema]] |
| Pedir lo que no se ofrece | `CWE-862` | [[GraphQL - autorización rota en resolvers]] |
| Saltar límites por petición | `CWE-307` | [[GraphQL - lotes y alias]] |
| Agotar el servidor | `CWE-770` | [[GraphQL - denegación por complejidad]] |
| Inyección por argumento | la de cada inyección | matriz — es un vector, no una clase |

Dos clases son nuevas —`CWE-200` y `CWE-770`— porque la introspección y la denegación por complejidad no tenían dónde colgar; las otras dos reusan dominios existentes. La inyección a través de un argumento **no genera nota**: la clase es la de la inyección subyacente (SQLi, NoSQL, command), y GraphQL es solo el punto de entrada, igual que la subida de archivos es el vector y no la clase en [[File upload - XXE por archivo]].

| Eje | Valores |
|---|---|
| Fase | reconocimiento · autorización · abuso de lotes · denegación · inyección |
| Qué se ataca | el esquema · los resolvers · el control de tasa · los recursos · la capa detrás |
| Transporte | POST JSON · GET (cacheable) · lote → matriz |

**La fase es el eje**, igual que en OAuth: el trabajo se ordena en una secuencia —primero el esquema, después lo que se hace con él— y cada fase tiene su clase. El transporte va a matriz.

## Árbol de decisión — la secuencia del dominio

```
1. ¿Hay un endpoint GraphQL?  → [[GraphQL - matriz de reconocimiento]] § 1
   └─ Sí
2. SACÁ EL ESQUEMA PRIMERO  → [[GraphQL - introspección del esquema]]
   ├─ Introspección abierta → una petición y está todo
   └─ Apagada → sugerencia de campos (Clairvoyance) → el esquema igual
3. Con el esquema, ¿qué hay?
   ├─ ¿Campos sensibles o mutaciones que la UI no ofrece?
   │     → [[GraphQL - autorización rota en resolvers]]   ← EL DE MAYOR IMPACTO
   ├─ ¿Mutación de login o de OTP, con límite por petición?
   │     → [[GraphQL - lotes y alias]]   ← el que rompe el 2FA
   ├─ ¿Argumentos que llegan a una consulta o un comando?
   │     → inyección: la clase es la del sink → [[GraphQL - matriz de explotación]] § 4
   └─ ¿Relaciones circulares y sin límite de profundidad?
         → [[GraphQL - denegación por complejidad]]   ← el de menor impacto, probar con cuidado
```

Tres cosas que este orden codifica:

**El esquema va antes que todo, y es lo que hace a GraphQL más fácil que REST de atacar.** En REST hay que adivinar endpoints y parámetros; acá la introspección los entrega. Todo el resto del dominio es leer el esquema y elegir el campo. Por eso [[GraphQL - introspección del esquema]] es el paso 2 obligatorio y no una opción.

**La introspección apagada no cierra el dominio.** Es la trampa del defensor: apagarla da sensación de seguridad, pero la sugerencia de campos reconstruye el esquema igual. La recomendación real es proteger los datos en cada resolver, no esconder el mapa.

**La autorización es el de mayor impacto; la denegación el menor.** Se ordenan por lo que consiguen: la autorización rota da datos y acciones ajenas, el abuso de lotes rompe el 2FA, la inyección depende del sink, y la denegación solo tira el servicio. La denegación va última y con advertencia porque es la única que puede dañar producción como efecto principal.

## Árbol de decisión — qué consigo por fase

```
¿Qué me dio el esquema?
├─ Un campo con datos que la UI oculta → lectura no autorizada → [[MOC - Broken access control]]
├─ Una mutación administrativa sin control → escalada / acción no autorizada
├─ Una mutación de login sin límite real → fuerza bruta de credenciales o de OTP
├─ Un argumento que llega a un sink → la clase del sink:
│     SQLi, NoSQL, command, SSRF, XSS — GraphQL solo lo transporta
└─ Un ciclo sin límite → denegación de servicio
```

## Cheatsheets — entrada directa a las construcciones

- [[GraphQL - matriz de reconocimiento]] — Encontrar el endpoint, la consulta de introspección, herramientas, reconstrucción por sugerencia, mapear la superficie
- [[GraphQL - matriz de explotación]] — Autorización, alias y lotes, denegación por profundidad, inyección por argumento, sondeo de defensas

## Orden de aprendizaje

1. [[GraphQL - matriz de reconocimiento]] — el endpoint y el esquema van primero, como en OAuth y SAML la matriz abre
2. [[GraphQL - introspección del esquema]] — por qué el esquema barato lo cambia todo, y que apagarlo no alcanza
3. [[GraphQL - autorización rota en resolvers]] — el impacto directo, un control por resolver en vez de por endpoint
4. [[GraphQL - lotes y alias]] — cómo una comodidad del protocolo rompe el control de tasa
5. [[GraphQL - denegación por complejidad]] — el cliente controla cuánto trabaja el servidor

Es el tercer MOC del vault donde la matriz va primera en el orden de lectura, y por la misma razón que en los otros dos dominios de capa: sin el esquema, las técnicas no tienen dónde apuntar.

## Relación con otros dominios

- [[MOC - Broken access control]] — [[GraphQL - autorización rota en resolvers]] es su misma clase, `CWE-862`, con la superficie que GraphQL agranda: un control por resolver en vez de por endpoint, y el grafo que lleva al mismo dato por muchos caminos. El método de prueba es [[Control de acceso - matriz de pruebas]] aplicado al esquema.
- [[MOC - Autenticación]] — [[GraphQL - lotes y alias]] es fuerza bruta —`CWE-307`— con un multiplicador propio: mil intentos por petición. Rompe el control de tasa que [[Autenticación - password spraying]] tiene que respetar.
- [[MOC - SQL injection]], [[MOC - Command injection]], [[MOC - SSRF]] — GraphQL es un **vector** hacia todas: un argumento sin sanear llega al sink. La clase es la del sink; el dominio solo aporta el punto de entrada, que la introspección lista.
- [[MOC - Web cache]] — GraphQL por GET es cacheable, y ahí los dos dominios se cruzan.
- [[File upload - XXE por archivo]] — el mismo principio de "el vector no es la clase": la subida es a XXE lo que el argumento GraphQL es a la inyección.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Introspección | [[Registro del WAF]] | La consulta contiene `__schema` / `__type` — no aparece en tráfico normal |
| Reconstrucción por sugerencia | [[Log de auditoría de la aplicación]] | Ráfaga de consultas con campos inexistentes |
| Autorización rota | [[Log de auditoría de la aplicación]] | Acceso a objeto o acción fuera del rol — si el log registra a nivel de resolver |
| Lotes y alias | [[Log de autenticación de la aplicación]] | Cientos de intentos — **si el log cuenta operaciones, no peticiones** |
| Denegación | [[Log de acceso del servidor web]] · [[Log de errores del servidor web]] | Pico de latencia y `5xx` — detección por efecto |

Tres observaciones que este dominio deja, y son sobre la unidad de medida:

**GraphQL rompe la correspondencia una-petición-una-operación, y con ella media telemetría.** Toda la instrumentación web asume que una petición HTTP es una acción: un login, una lectura, una consulta. GraphQL mete N operaciones en una petición, y eso desincroniza las fuentes. [[Log de acceso del servidor web]] ve una petición a `/graphql`; qué hizo esa petición —mil logins, una lectura administrativa, una consulta que tira el servidor— es invisible ahí. Es la misma clase de problema que el desajuste de conteo de [[MOC - Request smuggling]], en otra capa.

**Por eso las firmas útiles están en el cuerpo o a nivel de operación, no en el log de acceso.** La firma de `__schema` la ve el WAF; el volumen de intentos de [[GraphQL - lotes y alias]] solo se ve si el log de autenticación cuenta operaciones. El log de acceso, que es lo que casi todos miran, es ciego para GraphQL por construcción — ve siempre la misma URL.

**La única cara azul bien cubierta es la denegación, y es por efecto.** Un pico de latencia y `5xx` correlacionado con una petición grande a `/graphql` lo ve cualquier monitoreo de disponibilidad, sin instrumentar nada. Es la excepción: el resto del dominio necesita registro a nivel de resolver y de operación, que casi nunca está.

Décimo segundo dominio cerrado sin detección nueva. La recomendación defensiva transversal —y va en el informe— no es una regla: es **instrumentar el registro por operación y por resolver**, sin lo cual GraphQL es un punto ciego uniforme. Es [[Un log sin identidad es un historial, no una detección]] llevado a su conclusión: acá falta no un campo sino la unidad de conteo entera.

## Huecos conocidos

- [x] Las cuatro fases con clase propia, más la inyección como vector
- [x] Reconocimiento y explotación — dos matrices
- [x] Cara azul de denegación — por efecto, con el monitoreo existente
- [ ] **La telemetría por operación no existe.** El log de acceso ve una URL; lo que hizo la petición es invisible sin registro a nivel de resolver y de operación. No es una detección faltante sino la unidad de medida equivocada, como el conteo de peticiones en [[MOC - Request smuggling]]
- [ ] **La firma de introspección es escribible ya**, sobre el WAF: alertar consultas con `__schema` en producción detecta el reconocimiento. Candidato a detección propia, hueco de trabajo
- [x] NoSQL injection como dominio propio — [[MOC - NoSQL injection]], `CWE-943`. Aparece como sink de argumentos GraphQL; GraphQL es el vector, aquella es la clase
- [ ] Suscripciones de GraphQL (WebSocket) con su superficie propia
- [ ] CSRF sobre GraphQL cuando acepta `application/x-www-form-urlencoded` — se cruza con [[CSRF - endpoint que espera JSON]]
