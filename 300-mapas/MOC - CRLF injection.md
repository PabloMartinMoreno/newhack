---
tipo: moc
dominio: web
aliases:
  - MOC CRLF
tags:
  - dominio/web
---

# MOC - CRLF injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-113 - Improper Neutralization of CRLF Sequences in HTTP Headers]]. Las codificaciones, en [[CRLF inyección - matriz de referencia]]. Acá vive **la decisión**.

El dominio gira alrededor de un solo átomo: el `\r\n` que separa las cabeceras HTTP. Controlarlo dentro de un valor reflejado da control sobre la estructura de la respuesta. Es el mismo átomo que [[MOC - Request smuggling]] —allá desincroniza dónde termina una **petición**, acá controla la estructura de una **respuesta**—: las dos clases explotan que HTTP delimita con caracteres que pueden viajar en los datos.

| Eje | Valores |
|---|---|
| Alcance | una cabecera (`\r\n`) · la respuesta entera (`\r\n\r\n`) |
| Dónde cae | `Location` · `Set-Cookie` · cabecera reflejada · log |
| Codificación | `%0d%0a` · `%0a` · doble · unicode → matriz |
| Impacto | fijación · redirección · CORS · XSS · caché · falsificar logs |

**El alcance es el eje raíz**: inyectar una cabecera con un `\r\n` es una cosa, partir la respuesta entera con un `\r\n\r\n` es otra —más control, más impacto—. La codificación (cómo se cuela el salto de línea) va a matriz.

## Árbol de decisión — qué alcance tengo

```
¿La entrada se refleja en una CABECERA de respuesta?  → [[CRLF inyección - matriz de referencia]] § 1
├─ No, cae en el cuerpo → es XSS directo, no CRLF → [[MOC - Cross-site scripting]]
└─ Sí — inyectá %0d%0a con una cabecera canario
   │
   ├─ ¿Pasa un solo \r\n?
   │     → [[CRLF - inyección de cabecera]]   ← PRIMERO
   │       Set-Cookie (fijación), CORS, Location, defensas al revés
   │
   └─ ¿Pasa el doble \r\n\r\n?
         → [[CRLF - división de respuesta]]
           cuerpo controlado → XSS sin sink, o envenenamiento de caché
```

Tres cosas que este orden codifica:

**Primero confirmar que cae en una cabecera.** Si el reflejo es en el cuerpo, es XSS y no hace falta CRLF. La distinción es una petición y evita perseguir un dominio equivocado.

**La inyección de una cabecera va antes que la división.** Un solo `\r\n` alcanza para fijar una sesión o aflojar CORS, y pasa filtros que bloquean el doble. La división necesita más control y da más impacto — es el escalón, no el punto de partida.

**Qué se inyecta decide el impacto, no la técnica.** Con una cabecera: `Set-Cookie` es fijación, CORS es robo, `Location` es redirección. Con la respuesta entera: XSS o caché. El árbol de impacto lo detalla.

## Árbol de decisión — qué consigo

```
¿Qué inyecté?
├─ Set-Cookie → fijación de sesión → toma de cuenta → [[MOC - Gestión de sesión]]
├─ Access-Control-Allow-* → robo cruzado → [[MOC - CORS]]
├─ Location → redirección abierta → [[CWE-601 - URL Redirection to Untrusted Site]]
├─ Cuerpo completo → XSS reflejado sin sink → [[MOC - Cross-site scripting]]
├─ Cuerpo + caché → XSS masivo y persistente → [[MOC - Web cache]]
└─ Línea de log → falsificar/ocultar → ataca la telemetría
```

## Cheatsheets — entrada directa

| Matriz | Cubre |
|---|---|
| [[CRLF inyección - matriz de referencia]] | Codificaciones del `\r\n`, confirmar, bypass de filtros, dónde cae, ubicar el corte |
| [[CRLF impacto - matriz de referencia]] | Payloads de una cabecera, división a XSS, caché, inyección de logs, por impacto |

## Orden de aprendizaje

1. [[CWE-113 - Improper Neutralization of CRLF Sequences in HTTP Headers]] — por qué el `\r\n` es el átomo de la estructura HTTP
2. [[CRLF - inyección de cabecera]] — el caso base, una cabecera propia
3. [[CRLF - división de respuesta]] — el escalón: la respuesta entera controlada

## Relación con otros dominios

- [[MOC - Request smuggling]] — el hermano por átomo: el `\r\n` controla la estructura HTTP en las dos, la petición allá y la respuesta acá. Sobre HTTP/1.1 los dos viven; HTTP/2 los mitiga y la degradación los reintroduce.
- [[MOC - Cross-site scripting]] — la división de respuesta es XSS sin sink de HTML: el cuerpo entero es del atacante, así que evade filtros que buscan el payload en el contenido de la página.
- [[MOC - Web cache]] — una respuesta partida y cacheada es XSS masivo, la misma convergencia que el smuggling: los tres dominios entregan una respuesta envenenada a la caché.
- [[MOC - Gestión de sesión]] — el `Set-Cookie` inyectado es [[CWE-384 - Session Fixation]] por otro vector.
- [[MOC - CORS]] y [[CWE-601 - URL Redirection to Untrusted Site]] — las cabeceras inyectadas habilitan esos ataques directamente.
- [[MOC - Host header]] — la otra clase de manipulación de cabeceras; el Host es un valor confiado, el CRLF es un carácter inyectado, pero las dos abusan la estructura de las cabeceras.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Inyección de cabecera | [[Log de acceso del servidor web]] · [[Registro del WAF]] | `%0d%0a` en un parámetro, a menudo en la URL |
| División de respuesta | [[Registro del WAF]] | `%0d%0a` repetido + fragmentos de respuesta HTTP en la entrada |
| División a XSS | [[Informe de violación de CSP]] | El XSS se dispara en la víctima |
| Inyección de logs | — | **Corrompe la propia telemetría** |

Dos observaciones que este dominio deja:

**Es de las inyecciones más detectables por firma, y a favor del defensor.** El `%0d%0a` es inconfundible y —a diferencia de las otras inyecciones— suele viajar en la **URL** de una redirección, no en el cuerpo, así que lo ve [[Log de acceso del servidor web]] sin instrumentar cuerpos. Sumado a las firmas de las cuatro hermanas de inyección y del Host, consolida el candidato transversal: una regla de firma de metacaracteres de estructura en la entrada cubriría todo el grupo de inyección. El CRLF es el caso más fácil de ese grupo porque el salto de línea codificado no tiene ningún uso legítimo en un parámetro.

**La inyección de logs ataca la capa defensiva directamente, y es único en el vault.** Todas las demás técnicas dejan rastro en la telemetría; esta puede **falsificar** ese rastro, insertando líneas de log que ocultan el ataque real o incriminan. Es el único caso del vault donde el rojo ataca al azul en su propio terreno, y vale como recordatorio de que la telemetría también es una superficie: un log que acepta `\r\n` sin escapar no es una fuente confiable. Refuerza [[Un log sin identidad es un historial, no una detección]] desde el otro lado —no solo puede faltar un campo, puede estar envenenado—.

Décimo noveno dominio cerrado sin detección nueva, con la firma más limpia del grupo de inyección.

## Huecos conocidos

- [x] Los dos alcances — una cabecera y la respuesta entera
- [x] Codificaciones, bypass y payloads de impacto — dos matrices
- [x] Cara azul de firma — la más limpia del grupo de inyección
- [ ] **La firma de metacaracteres de estructura es transversal a todo el grupo de inyección** (4 hermanas + Host + CRLF). El `%0d%0a` es el caso más limpio. Candidato de detección de mayor retorno del vault, hueco de trabajo
- [ ] **La inyección de logs exige tratar la telemetría como superficie**: escapar `\r\n` en lo que se registra. No es una detección sino un endurecimiento de la fuente
- [ ] Inyección en cabeceras de correo (`CWE-93`, SMTP) como dominio vecino: mismo `\r\n` en otro protocolo
