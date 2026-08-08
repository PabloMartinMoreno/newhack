---
tipo: moc
dominio: web
aliases:
  - MOC SSRF
  - Server-side request forgery
tags:
  - dominio/web
---

# MOC - SSRF

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-918 - Server-Side Request Forgery]]. Los destinos y payloads, en las matrices de `900-meta/`. Acá vive **la decisión**.

SSRF no vale por la petición: vale por **desde dónde sale**. El servidor está adentro del perímetro y tiene alcance de red, identidad y confianza implícita que el atacante no tiene. Todo el árbol de decisión ordena por lo mismo: qué se alcanza desde esa posición.

| Eje | Valores |
|---|---|
| Retorno | directo · semiciego (estado, tamaño, tiempo) · ciego |
| Destino | loopback · red interna · metadatos de nube · el propio servicio |
| Esquema | `http`/`https` · `file` · `gopher` · `dict` · específicos del lenguaje |
| Bypass del filtro | lista negra de IP · lista blanca de dominio · validación previa · codificación |
| Impacto | lectura interna · escaneo · credenciales de nube · RCE · exfiltración |

## Árbol de decisión — elegir destino

Este árbol va **antes** que el de canal, al revés que en los demás dominios. El motivo es de rentabilidad: el destino decide el impacto, y hay un destino que cuesta una petición y termina el trabajo.

```
¿Corre en la nube?
├─ Sí → [[SSRF - metadatos de instancia cloud]]     ← una petición, credenciales
│  └─ ¿IMDSv2 o cabecera obligatoria? → sigue abajo
└─ No / cerrado
   ├─ ¿Esquema no-http disponible?
   │  ├─ file://   → lectura local, sin red
   │  └─ gopher:// → [[SSRF - gopher a servicio interno]]   ← la vía a RCE
   └─ Solo http
      ├─ ¿Hay retorno? → [[SSRF - canal directo]] contra servicios internos
      └─ No            → [[SSRF - escaneo de la red interna]]
```

Invertirlo —barrer la red interna antes de probar `169.254.169.254`— es el error más caro del dominio: cientos de peticiones para llegar a algo que estaba a una.

## Árbol de decisión — elegir canal

```
¿La respuesta del destino vuelve en la respuesta HTTP?
├─ Sí, entera        → [[SSRF - canal directo]]
├─ Sí, un fragmento  → [[SSRF - canal directo]], pocos bytes por petición
└─ No
   ├─ ¿Difiere el estado, el tamaño o el error? → semiciego: oráculo de un bit
   ├─ ¿Difiere el tiempo?                       → semiciego, más ruidoso
   └─ Nada difiere                              → [[SSRF - canal ciego]] puro
```

Dos cosas que cambian la práctica respecto de los demás dominios:

**Ciego no quiere decir inútil.** Con `gopher`, un SSRF ciego llega a RCE sin ver una sola respuesta: escribir en Redis o mandar un correo no necesita contestación. La severidad no depende del retorno.

**El renderizador de PDF convierte ciego en directo.** Si la superficie es un exportador que acepta HTML, el JavaScript del lado del servidor lee la respuesta interna y la escribe en el documento. Ver [[SSRF superficies - matriz de referencia]] § 2.

## Árbol de decisión — bypass del filtro

Las primitivas se combinan; todas viven en [[SSRF evasión - matriz de referencia]], una sección por filtro.

```
¿Qué te está bloqueando?
├─ Lista negra de IP        → decimal / octal / IPv6 / 0 / nip.io → § Lista negra
├─ Lista blanca de dominio  → @ / # / sufijo / barra invertida    → § Lista blanca
├─ Valida y después pide    → redirección 302 / DNS rebinding     → § Validación previa
└─ Filtro de cadena         → codificar una o dos veces           → § Codificación
```

La tercera rama es la que más paga y la que menos se prueba: **la mayoría de las validaciones miran la URL, no la conexión**. Una redirección las salta enteras.

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[SSRF superficies - matriz de referencia]] | Dónde nace: parámetros, webhooks, renderizadores de PDF, cabeceras, descubrimiento de OAuth |
| [[SSRF destinos - matriz de referencia]] | Rutas de IMDS por proveedor, rangos internos, los puertos que pagan, cómo leer el oráculo |
| [[SSRF esquemas - matriz de referencia]] | Qué esquema soporta cada cliente, `file`, `dict`, payloads de `gopher` |
| [[SSRF evasión - matriz de referencia]] | Representaciones de IP, confusión de parsers, redirección, DNS rebinding |

## Orden de aprendizaje

1. [[CWE-918 - Server-Side Request Forgery]] — qué es, y por qué no es CSRF
2. [[SSRF superficies - matriz de referencia]] — encontrarlo, que es la mitad del trabajo
3. [[SSRF - canal directo]] — el caso feliz, fija el modelo mental
4. [[SSRF - metadatos de instancia cloud]] — el impacto que justifica todo el dominio
5. [[SSRF evasión - matriz de referencia]] — los filtros y por qué casi todos fallan
6. [[SSRF - canal ciego]] → [[SSRF - escaneo de la red interna]]
7. [[SSRF - gopher a servicio interno]] — de lectura a ejecución

El punto 4 va temprano a propósito: sin entender qué se gana llegando a `169.254.169.254`, el resto del dominio parece un ejercicio de curiosidad.

## Relación con otros dominios

- [[RFI - inclusión remota]] **es un SSRF** cuyo resultado, además de traerse, se ejecuta. La diferencia está en qué hace la app con la respuesta, no en la petición.
- [[File upload - XXE por archivo]] — un parser XML con entidades externas es una máquina de SSRF. Cuando exista el dominio de XXE, este es el nodo que los une.
- [[MOC - Command injection]] — [[Command injection - canal fuera de banda]] también genera peticiones salientes, y comparte [[Conexión saliente del servidor de aplicación]]. Distinguirlos del lado azul exige mirar el proceso de origen.
- [[Webshell]] — destino compartido cuando `gopher` a Redis escribe en la raíz web.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Canal directo | [[Conexión saliente del servidor de aplicación]] | Destino fuera de la lista de lo habitual |
| Canal ciego | [[Consulta DNS saliente]] | Subdominio único por prueba, dominio sin historial |
| Escaneo interno | [[Conexión saliente del servidor de aplicación]] | Cientos de conexiones fallidas en progresión ordenada |
| Metadatos de nube | [[Conexión saliente del servidor de aplicación]] | Conexión a `169.254.169.254` desde el proceso de la app |
| `gopher` a interno | [[Conexión saliente del servidor de aplicación]] | Puerto de servicio interno desde un proceso que no lo usa |

La fila de metadatos es la de mayor fidelidad de todo el vault del lado web: una aplicación pide metadatos al arrancar, no en medio de una petición de usuario. La contracara es que **el tráfico a loopback no cruza la red** y no aparece en telemetría de flujo: para eso hace falta telemetría de host.

## Huecos conocidos

- [x] Retorno — directo y ciego completos
- [x] Destino — metadatos de nube y red interna
- [x] Esquema — [[SSRF - gopher a servicio interno]] y su matriz
- [x] Bypass del filtro — en [[SSRF evasión - matriz de referencia]]
- [ ] **Cara azul sin escribir.** [[Conexión saliente del servidor de aplicación]] existe y ninguna detección lo consume
- [ ] `CWE-611 - XML External Entity` no existe todavía: [[File upload - XXE por archivo]] sigue colgando de `CWE-434`
- [ ] Explotación posterior de credenciales de nube — es otro dominio, no de web
