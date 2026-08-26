---
tipo: moc
dominio: web
aliases:
  - MOC tabnabbing
tags:
  - dominio/web
---

# MOC - Tabnabbing

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-1022 - Use of Web Link to Untrusted Target with window.opener Access]]. La mecánica y los sinks, en [[Tabnabbing - matriz de referencia]]. Acá vive **la decisión**.

Dominio compacto del lado del cliente, hermano de [[MOC - Clickjacking]]: los dos abusan cómo el navegador maneja ventanas, terminan en engaño de la víctima, y tienen la misma cara azul —**prevención, no detección**—. Acá el abuso es que un enlace `target="_blank"` sin `rel="noopener"` deja a la página abierta **navegar la pestaña que la abrió** a una copia de phishing.

| Eje | Valores |
|---|---|
| Entrega | el sitio enlaza a un tercero · el atacante planta el enlace en contenido de usuario |
| Sink | `target="_blank"` · `window.open` · `form target` → matriz |
| Impacto | phishing de la pestaña original · fuga de `Referer` |

**La entrega es el eje raíz**: quién pone el enlace vulnerable decide el escenario. Si el sitio ya enlaza a algo influenciable, el atacante lo aprovecha; si el sitio renderiza enlaces de usuario, el atacante los planta. El sink —qué construcción abre la pestaña— va a matriz.

## Árbol de decisión — quién pone el enlace

```
¿Hay un enlace target="_blank" sin rel="noopener"?  → [[Tabnabbing - matriz de referencia]] § 3
├─ No, o el navegador aplica noopener por defecto → no explotable
└─ Sí — ¿quién controla el destino del enlace?
   │
   ├─ El sitio ya enlaza a un tercero influenciable
   │     → [[Tabnabbing - secuestro por enlace saliente]]
   │       comprometer/controlar ese destino, redirigir la abridora
   │
   └─ El sitio renderiza enlaces de contenido de usuario
         → [[Tabnabbing - enlace plantado en contenido de usuario]]   ← el más fácil
           publicar el enlace propio, las víctimas llegan solas
```

Dos cosas que este orden codifica:

**El enlace plantado en contenido de usuario es el más explotable.** No depende de que el sitio ya enlace a algo controlable: el atacante crea el enlace, y es la variante "almacenada" —se planta una vez, las víctimas llegan solas—, análoga a [[XSS - almacenado]]. Además pasa los filtros de XSS, porque no inyecta script, solo un enlace legítimo.

**La condición que abre o cierra el dominio es un atributo faltante.** `rel="noopener"` en el enlace, o `noopener` por defecto del navegador, cierra todo. Comprobarlo es leer el HTML renderizado. La mayoría de los navegadores y renderizadores modernos ya lo aplican, así que el dominio vive en lo viejo y en las integraciones a mano.

## Árbol de decisión — qué consigo

```
Redirigí la pestaña original
├─ A una copia de phishing del sitio → robo de credenciales al "reautenticarse"
├─ A una página que pide un pago / dato → fraude
└─ Con noopener pero sin noreferrer → fuga del Referer (menor)
```

El impacto es phishing, y su credibilidad viene de que la víctima **ya estaba** en el sitio de confianza cuando clickeó —más creíble que un phishing por correo, porque la pestaña no la abrió el atacante—.

## Cheatsheets — entrada directa

- [[Tabnabbing - matriz de referencia]] — La prueba de concepto, los sinks, detectar enlaces vulnerables, el estado del navegador, la fuga de `Referer`, las mitigaciones

## Orden de aprendizaje

1. [[CWE-1022 - Use of Web Link to Untrusted Target with window.opener Access]] — por qué `window.opener` deja navegar la pestaña abridora
2. [[Tabnabbing - matriz de referencia]] — la mecánica y cómo encontrar enlaces vulnerables
3. [[Tabnabbing - enlace plantado en contenido de usuario]] — la variante más explotable
4. [[Tabnabbing - secuestro por enlace saliente]] — cuando el sitio ya enlaza a algo controlable

## Relación con otros dominios

- [[MOC - Clickjacking]] — el hermano del lado del cliente. Los dos abusan el manejo de ventanas/marcos del navegador, terminan en engaño de la víctima, y tienen cara azul **preventiva**. Clickjacking se defiende con `frame-ancestors`, tabnabbing con `noopener`/COOP; en los dos la telemetría no sirve y la prevención lo es todo.
- [[XSS - almacenado]] — [[Tabnabbing - enlace plantado en contenido de usuario]] es la variante almacenada, y pasa filtros de XSS porque no inyecta script. Si hay XSS almacenado, no hace falta tabnabbing —se roba directo—; tabnabbing es la vía cuando el HTML se sanea pero los enlaces quedan.
- [[CWE-601 - URL Redirection to Untrusted Site]] — una redirección abierta en el objetivo puede hacer que la pestaña secuestrada aterrice en un dominio que parece el legítimo, subiendo la credibilidad del phishing.
- [[MOC - Gestión de sesión]] — el objetivo del phishing es robar credenciales o una sesión, que es aquel dominio.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Enlace saliente | [[Log de acceso del servidor web]] | Ninguna fiable — ocurre en el navegador |
| Enlace plantado | [[Log de auditoría de la aplicación]] | El enlace queda almacenado en el contenido |

La observación que comparte con clickjacking, y que consolida un patrón:

**Segundo dominio de cara azul puramente preventiva.** Con [[MOC - Clickjacking]], son los dos dominios donde no hay detección fiable posible —el ataque vive en el navegador de la víctima— y la defensa es una cabecera o un atributo: `noopener`, `Cross-Origin-Opener-Policy`. La telemetría del servidor no ve el secuestro. La única diferencia con clickjacking es que la variante de enlace plantado **deja el enlace almacenado** como evidencia de que alguien lo intentó, lo que da una detección de tipo distinto: no del ataque en vivo sino de su preparación, y solo si se audita el contenido.

Es el patrón de los ataques del lado del cliente puros que el vault ya venía nombrando —[[XSS - DOM-based]], clickjacking, y ahora tabnabbing—: **el servidor es ciego a lo que pasa en el navegador**, y la defensa se corre a las cabeceras y atributos que el navegador respeta. Refuerza [[Ausencia de alertas no es ausencia de ataque]]: la ausencia de alertas es estructural, no un hueco.

Vigésimo tercer dominio cerrado sin detección nueva, el segundo de defensa puramente preventiva.

## Huecos conocidos

- [x] Las dos entregas — enlace saliente y plantado en contenido de usuario
- [x] Mecánica, sinks, reconocimiento y mitigaciones — una matriz (dominio compacto)
- [x] Cara azul preventiva — `noopener`/COOP, no detección
- [ ] **La detección en vivo no existe**, como en clickjacking: el secuestro ocurre en el navegador. La defensa es `noopener`/COOP; la única señal es el enlace plantado en el contenido, y solo si se audita
- [ ] Fugas por `window.name` y otras vías de comunicación entre ventanas como superficie vecina
- [ ] Interacción con `Cross-Origin-Opener-Policy` y aislamiento de sitios en detalle, para pentests de aplicaciones que ya usan COOP parcialmente
