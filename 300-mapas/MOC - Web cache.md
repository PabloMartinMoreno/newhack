---
tipo: moc
dominio: web
aliases:
  - MOC web cache
  - cache poisoning
  - cache deception
tags:
  - dominio/web
---

# MOC - Web cache

> [!abstract] Nota de referencia paraguas
> Envenenamiento en [[CWE-349 - Acceptance of Extraneous Untrusted Data With Trusted Data]], engaño en [[CWE-524 - Use of Cache Containing Sensitive Information]]. Sondear, en [[Web cache - matriz de sondeo]]. Acá vive **la decisión**.

Como [[MOC - Request smuggling]], este dominio no ataca la aplicación sino una **capa de infraestructura**: la caché compartida que hay entre el usuario y el servidor. Y como el par [[MOC - CSRF]] / [[MOC - CORS]], tiene dos técnicas que van en direcciones opuestas y hay que separar antes de nada.

| | Envenenamiento (empujar) | Engaño (robar) |
|---|---|---|
| Dirección | Mete contenido malo en una entrada pública | Guarda la respuesta privada de la víctima |
| `clase:` | `CWE-349` | `CWE-524` |
| Quién sufre | Todos los usuarios | La víctima concreta |
| El fallo | Entrada sin clave influye en la respuesta | La caché guarda algo que era privado |
| Alcance | Masivo y persistente | Un robo dirigido |

| Eje | Valores |
|---|---|
| Dirección | envenenar · engañar |
| Primitiva (envenenar) | entrada sin clave · manipulación de la clave |
| Payload (envenenar) | XSS · redirección · importación de script · DoS → matriz |
| Confusión (engañar) | extensión · delimitador · recorrido → matriz |

**La dirección es el eje raíz.** Envenenar y engañar comparten la capa —la caché— y casi nada más: distinto fallo, distinta víctima, distinto sentido del flujo. Confundirlos lleva a buscar entradas sin clave cuando lo que se quería era robar una página privada. El payload de envenenar y la confusión de ruta de engañar van a matriz, porque son catálogos de sintaxis, no decisiones.

## Árbol de decisión — qué quiero de la caché

```
¿Empujar contenido a todos, o robarle a una víctima?
│
├─ EMPUJAR (envenenar)
│  ├─ Encontrá una entrada sin clave que se refleje  → [[Web cache - matriz de sondeo]] § 3
│  │  └─ ¿Se refleja y NO está en la clave?
│  │        → [[Web cache - envenenamiento por entrada sin clave]]   ← PRIMERO
│  ├─ ¿La entrada que influye SÍ está en la clave?
│  │        → sacála: cloaking, fat GET, discrepancia
│  │        → [[Web cache - manipulación de la clave]]
│  └─ ¿Nada se refleja útil pero sí rompe la respuesta?
│           → DoS por caché: guardá un error para todos
│
└─ ROBAR (engañar)
   └─ ¿La caché decide por la extensión de la URL y el server ignora el sufijo?
         → [[Web cache - engaño de caché]]
           necesita una víctima autenticada que abra la URL
```

Tres cosas que este orden codifica:

**La entrada sin clave va primero en la rama de envenenar.** Es el caso base: si una cabecera se refleja y no está en la clave, el envenenamiento es directo. La manipulación de la clave es la rama fina, para cuando el payload queda dentro de la clave.

**El envenenamiento es un multiplicador, no una vulnerabilidad sola.** Lo que se cachea casi siempre es otra clase —un XSS, una redirección— que sin la caché afectaría solo al atacante. Por eso la severidad se decide cruzando la entrada sin clave con lo que refleja, y por eso el dominio referencia a XSS y a open redirect en vez de reimplementarlos.

**El engaño necesita víctima; el envenenamiento no.** Envenenar afecta a quien pida el recurso, sin que nadie tenga que hacer nada. Engañar exige que la víctima abra la URL preparada. Es la misma asimetría de requisito que ordenó [[MOC - OAuth]], y pone un techo de severidad a la rama de engaño.

## Árbol de decisión — envenené algo, ¿hasta dónde llega?

```
La respuesta envenenada se sirve a todos los que piden el recurso
├─ ¿Refleja en un <script src> o import?
│     → ejecución de JS en el origen, para todas las víctimas → [[MOC - Cross-site scripting]]
├─ ¿Refleja en una redirección?
│     → redirección abierta masiva → [[CWE-601 - URL Redirection to Untrusted Site]]
├─ ¿Refleja en HTML sin escapar?
│     → XSS almacenado por caché
├─ ¿Solo rompe la respuesta?
│     → DoS del recurso, persistente hasta que expira
└─ ¿Hay más cachés encadenadas (CDN + navegador)?
      → el alcance se multiplica; la del navegador es por-víctima y más difícil de purgar
```

## Cheatsheets — entrada directa a las construcciones

- [[Web cache - matriz de sondeo]] — Cache buster, detectar la caché, mapear la clave, buscar entradas sin clave, medir la ventana, sondeo del engaño
- [[Web cache entradas sin clave - matriz de referencia]] — Catálogo de cabeceras, de reflejo a impacto, DoS, cloaking, fat GET, discrepancias, confusión de ruta

## Orden de aprendizaje

1. [[CWE-349 - Acceptance of Extraneous Untrusted Data With Trusted Data]] — qué es una clave de caché y qué queda fuera
2. [[Web cache - matriz de sondeo]] — detectar sin envenenar a nadie, que acá también es regla de seguridad
3. [[Web cache - envenenamiento por entrada sin clave]] — el caso base, donde se entiende el hueco
4. [[Web cache - manipulación de la clave]] — cuando el payload queda en la clave y hay que sacarlo
5. [[CWE-524 - Use of Cache Containing Sensitive Information]] — el reverso: la caché guardando lo privado
6. [[Web cache - engaño de caché]] — robar la respuesta de la víctima

El punto 2 va antes que las técnicas y por la misma razón que en [[MOC - Request smuggling]]: sondear mal envenena a usuarios reales. La matriz de sondeo con su cache buster se lee antes de tocar nada.

## Relación con otros dominios

- [[MOC - Request smuggling]] — el otro dominio de capa de infraestructura, y el vecino directo. El smuggling es **una** forma de envenenar la caché —entrega el payload al back y la caché lo guarda—; el envenenamiento por entrada sin clave es otra que no necesita desincronizar nada. La discrepancia de normalización de [[Web cache - manipulación de la clave]] y la de [[Web cache - engaño de caché]] son el mismo patrón de dos parsers que no coinciden.
- [[MOC - Cross-site scripting]] — el payload más común que se cachea. La caché convierte un XSS reflejado en almacenado y masivo; las defensas de XSS no ven que vino de la caché, pero [[Violación de CSP por script inline]] sí ve el efecto en la víctima.
- [[CWE-601 - URL Redirection to Untrusted Site]] — una redirección que refleja `X-Forwarded-Host` se vuelve open redirect para todos al cachearse.
- [[MOC - Broken access control]] — el engaño de caché roba datos de la víctima, mismo resultado que [[Control de acceso - IDOR]] por otra vía. Y [[Acceso a un objeto de otro usuario]] tiene el perfil defensivo más parecido.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Envenenamiento por cabecera | [[Registro del WAF]] | Cabecera `X-Forwarded-*` con host externo sobre respuesta cacheable |
| Envenenamiento a XSS | [[Informe de violación de CSP]] | El script cacheado se dispara en las víctimas |
| Manipulación de la clave (fat GET) | [[Registro del WAF]] | Un `GET` con cuerpo — anomalía sin forma legítima |
| Engaño de caché | [[Log de acceso del servidor web]] | Respuesta con `Set-Cookie`/`private` **que se cacheó** |
| Engaño de caché | [[Log de auditoría de la aplicación]] | Lectura de datos de la víctima desde otra sesión |

Dos observaciones que este dominio deja:

**El envenenamiento se delata aguas abajo, no en el momento.** El instante del envenenamiento —una cabecera rara sobre una respuesta cacheable— solo lo ve bien el WAF, y detectar que la respuesta cacheada no corresponde a la petición exige comparar contenido, que ninguna fuente modela. Pero el **efecto** sí se ve: si lo cacheado es un XSS, [[Violación de CSP por script inline]] se dispara en cada víctima. Es el mismo principio de detectar efecto en vez de firma que sostiene medio lado azul del vault, y acá salva la cara azul del envenenamiento.

**El engaño tiene la cara azul más escribible del dominio, y es de fuente disponible.** Una respuesta con `Set-Cookie` o `Cache-Control: private` que aun así se cacheó es una firma de alta fidelidad —no ocurre por accidente— y vive en las **cabeceras de respuesta**, que se registran más seguido que los cuerpos. A diferencia de casi todos los huecos recientes, este no es de instrumentación imposible: es un candidato real a detección propia cuando se abra esa fase. Queda anotado abajo.

Décimo primer dominio cerrado sin detección nueva. La racha sigue, pero el engaño de caché es el primer caso en varios dominios donde la detección propia **sería escribible con la fuente que ya existe** — no un hueco de fuente, un pendiente de trabajo.

## Huecos conocidos

- [x] Las dos direcciones, cada una con su `clase:` real
- [x] Envenenamiento por entrada sin clave y por manipulación de clave
- [x] Sondeo seguro con cache buster y confusión de ruta — dos matrices
- [x] Cara azul del envenenamiento a XSS — cubierta por [[Violación de CSP por script inline]] aguas abajo
- [ ] **Detección del engaño de caché — escribible, no imposible.** Una respuesta `private`/`Set-Cookie` cacheada es firma de alta fidelidad sobre las cabeceras de respuesta, que sí se registran. Es candidato a detección propia; el hueco es de trabajo, no de fuente
- [ ] La correlación "respuesta cacheada que no corresponde a la petición" sigue sin fuente, igual que el desajuste de conteo de [[MOC - Request smuggling]]
- [ ] Caché del lado del cliente (navegador) y `Vary` mal usado como superficie propia
