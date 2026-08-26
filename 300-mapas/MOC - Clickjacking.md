---
tipo: moc
dominio: web
aliases:
  - MOC clickjacking
tags:
  - dominio/web
---

# MOC - Clickjacking

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-1021 - Improper Restriction of Rendered UI Layers or Frames]]. ¿Se puede encuadrar?, en [[Clickjacking - encuadre - matriz de referencia]]. Acá vive **la decisión**.

Es el dominio más del lado del cliente del vault: no ataca el servidor sino la **percepción de la víctima**. El objetivo recibe un clic autenticado perfectamente legítimo; lo que se manipula es qué cree la víctima que está clickeando. Eso cambia todo —no hay payload, la víctima es el objetivo, y la defensa es prevención pura—.

| Eje | Valores |
|---|---|
| Interacción | un clic · arrastrar / multipaso |
| Encuadre | sin defensa · frame-buster JS · comodín de subdominio → matriz |
| Impacto | acción de un clic · relleno · entrega de XSS · consentimiento de OAuth |

**La interacción es el eje raíz**: un clic sobre un botón sensible es una cosa, orquestar una secuencia de gestos es otra —más control, más frágil—. La factibilidad del encuadre (¿se puede meter en un marco?) es el paso previo obligatorio y va a matriz.

## Árbol de decisión — encuadre e interacción

```
¿El objetivo se puede encuadrar?  → [[Clickjacking - encuadre - matriz de referencia]]
├─ No (frame-ancestors / X-Frame-Options) → probar bypass; si no, no hay dominio
│  ├─ frame-buster JS → sandbox lo neutraliza
│  └─ comodín de subdominio → encuadrar desde un subdominio propio
└─ Sí — ¿cómo se completa la acción objetivo?
   │
   ├─ Con UN clic (borrar cuenta, cambiar correo, autorizar)
   │     → [[Clickjacking - un clic sobre acción sensible]]   ← PRIMERO
   │       marco invisible + señuelo alineado con el botón
   │
   └─ Con varios pasos o entrada
         → [[Clickjacking - relleno por arrastre y multipaso]]
           arrastre, precarga por URL, o combinado con XSS/OAuth
```

Tres cosas que este orden codifica:

**El encuadre es la pregunta que abre o cierra el dominio.** Sin poder meter el objetivo en un marco, no hay clickjacking. Es una petición para saberlo, y la mayoría de los sitios bien configurados cierran acá con `frame-ancestors`.

**El clic único va antes que el multipaso porque es más fiable.** Cada gesto extra es una chance de que la víctima note algo raro. Una acción de un clic sin confirmación es el caso limpio; el multipaso es el escalón para cuando la acción pide más.

**Clickjacking sortea las defensas de CSRF.** El clic genera la petición real del objetivo, con su token anti-CSRF válido incluido. Un formulario protegido contra CSRF sigue cayendo, porque lo que se abusa es el clic, no la petición. Es la relación clave con [[MOC - CSRF]] y hay que tenerla presente: proteger contra CSRF no protege contra clickjacking.

## Árbol de decisión — qué consigo

```
¿Qué acción encuadré?
├─ Borrar cuenta / cambiar correo sin confirmación → toma de cuenta
├─ Autorizar consentimiento de OAuth → acceso a la app del atacante → [[MOC - OAuth]]
├─ Campo reflejado precargado → entrega de XSS → [[XSS - reflejado]]
├─ Transferencia / pago de un clic → fraude
└─ Like / compartir → likejacking, informativo
```

La severidad va de informativa a crítica con el mismo fallo, igual que en CSRF: se reporta el impacto real de la acción, no "el sitio es encuadrable".

## Cheatsheets — entrada directa

- [[Clickjacking - encuadre - matriz de referencia]] — Probar el encuadre, leer las defensas, grietas, bypass de frame-buster con sandbox, Clickbandit
- [[Clickjacking - superposición - matriz de referencia]] — El CSS del marco invisible, calibrar, recortar, arrastre, precarga, entrega de XSS, plantilla

## Orden de aprendizaje

1. [[CWE-1021 - Improper Restriction of Rendered UI Layers or Frames]] — por qué es engaño de interfaz y primo de CSRF
2. [[Clickjacking - encuadre - matriz de referencia]] — la pregunta que abre el dominio va primero
3. [[Clickjacking - un clic sobre acción sensible]] — el caso base
4. [[Clickjacking - relleno por arrastre y multipaso]] — el escalón, y los combos con XSS y OAuth

## Relación con otros dominios

- [[MOC - CSRF]] — el primo directo: los dos hacen que la víctima ejecute una acción que no quiso. CSRF falsifica la petición, clickjacking engaña el clic. Clickjacking **sortea** las defensas de CSRF porque el token viaja en la petición real. Comparten `clase:` de familia (`CWE-352` → `CWE-1021`) y el techo de severidad de necesitar una víctima que interactúe.
- [[MOC - Cross-site scripting]] — clickjacking entrega un XSS reflejado que necesita interacción, precargando el campo. El clic dispara el payload.
- [[MOC - OAuth]] — encuadrar la pantalla de consentimiento hace que la víctima autorice sin saberlo, una vía distinta al desvío de `redirect_uri`.
- [[MOC - CORS]] y [[OAuth - redirect_uri mal validado]] — el comodín de subdominio en `frame-ancestors` es la misma superficie que aquellos: una lista blanca que confía en todo lo que cuelga del dominio.
- [[XSS - CSP]] — `frame-ancestors` es una directiva de CSP; la defensa de clickjacking y la de XSS comparten la misma cabecera.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Un clic | [[Log de auditoría de la aplicación]] | La acción es legítima — indistinguible |
| Carga del marco | [[Log de acceso del servidor web]] | `Sec-Fetch-Dest: iframe` + `Referer` externo — ruidoso |
| Entrega de XSS | [[Informe de violación de CSP]] | El XSS se dispara en la víctima |

La observación que define la cara azul del dominio, y es única en el vault:

**Es el primer dominio cuya cara azul es puramente preventiva: no se puede detectar de forma fiable, solo prevenir.** El ataque vive en la página del atacante y en el navegador de la víctima; el objetivo solo recibe un clic autenticado que es, por definición, indistinguible de uno real. La carga del marco deja un `Sec-Fetch-Dest: iframe` con `Referer` externo, pero encuadrar un sitio también es legítimo —un widget, una vista previa—, así que la firma tiene fidelidad demasiado baja para alertar. No hay un efecto anómalo aguas abajo como en las inyecciones: el efecto **es** la acción legítima.

La recomendación defensiva no es una regla de detección sino **la cabecera `frame-ancestors`** que impide el encuadre. Es el caso más puro de [[Ausencia de alertas no es ausencia de ataque]] del vault: acá la ausencia de alertas es estructural —no hay nada fiable que alertar—, y la única defensa es cerrar la puerta antes. Un dominio donde la telemetría no sirve y la prevención lo es todo.

Vigésimo segundo dominio cerrado sin detección nueva, y el primero donde eso **no** es un hueco a llenar sino la naturaleza del dominio: no hay detección posible, hay prevención.

## Huecos conocidos

- [x] Las dos interacciones — un clic y multipaso
- [x] Encuadre, bypass de defensas y superposición — dos matrices
- [x] Cara azul preventiva — `frame-ancestors`, no detección
- [ ] **La detección fiable no existe, y es estructural.** El clic es indistinguible de uno legítimo. La defensa es `frame-ancestors`, no una regla — a diferencia de los otros huecos azules, este no se llena escribiendo una detección
- [ ] Tabnabbing y `window.opener` —`target=_blank` sin `noopener`— como dominio vecino del lado del cliente
- [ ] Clickjacking asistido por CSS avanzado (cursorjacking, ocultar el cursor real) — variantes más frágiles
