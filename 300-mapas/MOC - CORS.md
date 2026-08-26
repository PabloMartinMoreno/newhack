---
tipo: moc
dominio: web
aliases:
  - MOC CORS
  - cross-origin resource sharing
tags:
  - dominio/web
---

# MOC - CORS

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-942 - Permissive Cross-domain Policy with Untrusted Domains]]. Los payloads, en [[CORS bypass de origen - matriz de referencia]]. Acá vive **la decisión**.

Este dominio se confunde con CSRF más que ningún otro, y la confusión es la que hay que desarmar primero porque decide qué se busca. **CSRF abusa que el navegador manda la petición; CORS mal configurado abusa que el atacante lee la respuesta.** Uno escribe a ciegas, el otro lee. Un `Access-Control-Allow-Origin` permisivo no habilita ningún CSRF —a veces lo estorba—, y al revés, una defensa de CSRF no cierra un CORS abierto.

| Eje | Valores |
|---|---|
| Validación del origen | reflejo directo · subcadena · `null` · comodín de subdominio |
| Agravante | `Allow-Credentials: true` · sin credenciales |
| Autenticación del endpoint | por cookie · por cabecera → decide si hay ataque |
| Impacto | robo de token anti-CSRF · datos personales · clave de API · escalada |

El **eje que genera notas es cómo falla la validación del origen**, y solo ese. El resto son condiciones: `Allow-Credentials` decide la severidad, la autenticación por cookie decide si el ataque es posible, el impacto sale de qué devuelve el endpoint.

## Árbol de decisión — qué validación tengo enfrente

```
¿El endpoint autentica por cookie?
├─ No (cabecera Authorization) → el navegador no la manda solo
│                                 → no hay robo por CORS, sea cual sea la config
└─ Sí — ¿hay Access-Control-Allow-Credentials: true?
   ├─ No → solo se lee lo público. Hallazgo de baja severidad, reportá y seguí
   └─ Sí — mandá un Origin inventado y mirá la respuesta:
      │
      ├─ Se refleja tal cual
      │     → [[CORS - reflejo del origen con credenciales]]   ← PRIMERO, cierra en una petición
      ├─ No refleja, pero variantes de cadena pasan
      │     → [[CORS - validación por subcadena]]
      ├─ Refleja null
      │     → [[CORS - null y comodín de subdominio]]  (rama null)
      └─ Acepta *.objetivo.com y tengo un subdominio
            → [[CORS - null y comodín de subdominio]]  (rama comodín)
```

Tres cosas que este orden codifica:

**La primera pregunta descarta el dominio.** Si el endpoint autentica por cabecera y no por cookie, no hay ataque posible por más abierto que esté CORS: el navegador no adjunta la cabecera `Authorization` sola. Una petición para saberlo, mismo filtro que abre [[MOC - CSRF]].

**La segunda pregunta fija la severidad.** Sin `Allow-Credentials`, el reflejo del origen deja leer la versión no autenticada del endpoint, que suele ser pública. Es un hallazgo de configuración real pero de severidad baja, y hay que reportarlo como tal en vez de inflarlo — el comodín `*` sobre datos públicos es correcto por diseño.

**Reflejo directo antes que las variantes de cadena.** El reflejo ciego cierra el dominio en una petición y no cuesta nada. Las variantes de cadena vienen después y pueden exigir registrar un dominio.

## Árbol de decisión — leo la respuesta, ¿qué me llevo?

```
Confirmé que puedo leer respuestas autenticadas
├─ ¿Hay un token anti-CSRF en alguna respuesta?
│     → robalo → habilita el CSRF que CORS no da → [[MOC - CSRF]]
│       es la combinación que más rinde: leer con CORS, escribir con CSRF
├─ ¿Clave de API o token de sesión?
│     → acceso reutilizable fuera del navegador
├─ ¿Datos personales en /cuenta, /perfil, /me?
│     → el hallazgo demostrable de fuga
└─ ¿La víctima es admin?
      → respuestas de endpoints administrativos → escalada
```

El primer nodo es el que eleva el dominio de "fuga de datos" a "toma de cuenta". CORS mal configurado por sí solo lee; encadenado con el token robado, escribe. Los dos dominios juntos hacen lo que ninguno solo, y por eso [[MOC - CSRF]] y este se referencian.

## Cheatsheets — entrada directa a los payloads

- [[CORS bypass de origen - matriz de referencia]] — Las tres cabeceras, reflejo, sufijo, prefijo, subcadena, `null` con `iframe` sandbox, cómo leer la respuesta y qué robar

## Orden de aprendizaje

1. [[CWE-942 - Permissive Cross-domain Policy with Untrusted Domains]] — qué relaja CORS y por qué no es CSRF
2. [[CORS - reflejo del origen con credenciales]] — el caso directo y de mayor impacto
3. [[CORS - validación por subcadena]] — cuando valida pero valida mal
4. [[CORS - null y comodín de subdominio]] — los dos casos de "la lista está bien salvo una entrada"

El punto 1 va primero y es más importante que en otros dominios: sin separar CORS de CSRF, las tres técnicas parecen resolver un problema que no es el suyo.

## Relación con otros dominios

- [[MOC - CSRF]] — el par que más se confunde y el que mejor se encadena. CSRF escribe sin ver; CORS lee. Robar el token anti-CSRF con CORS habilita el CSRF que de otro modo estaba cerrado. Son opuestos que se complementan.
- [[CWE-601 - URL Redirection to Untrusted Site]] y [[OAuth - redirect_uri mal validado]] — la validación del origen falla igual que la de la dirección de redirección: reflejo, prefijo, sufijo, subcadena. El catálogo de bypass de [[CORS bypass de origen - matriz de referencia]] y el de [[OAuth redirect_uri - matriz de referencia]] son el mismo problema en dos cabeceras distintas.
- [[CORS - null y comodín de subdominio]] comparte la superficie de subdominios con [[CSRF - double submit y cookie inyectada]] y con el comodín de [[OAuth - redirect_uri mal validado]]. Enumerar los subdominios una vez sirve para los tres.
- [[MOC - Gestión de sesión]] — lo que se roba suele ser un token, y qué se hace con él es aquel dominio.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Reflejo del origen | [[Log de acceso del servidor web]] | `Origin` externo sobre endpoint de datos — **si se registra `Origin`** |
| Validación por subcadena | [[Log de acceso del servidor web]] | `Origin` parecido al dominio pero no en la lista blanca |
| `null` | [[Log de acceso del servidor web]] | `Origin: null` sobre endpoint autenticado — sin explicación legítima |
| Comodín de subdominio | — | El `Origin` es un subdominio real. No hay anomalía en el flujo de CORS |

La observación que este dominio deja, y es incómoda:

**Todo el dominio comparte un mismo hueco, y es de fuente, no de contenido.** La señal de las cuatro variantes es la cabecera `Origin`, y [[Log de acceso del servidor web]] **no la registra por defecto**. La detección no es difícil de escribir —comparar el `Origin` recibido contra la lista blanca real y alertar cuando un origen reflejado no está en ella tendría alta fidelidad—: es imposible sin instrumentar el campo. Es el mismo patrón que [[Un log sin identidad es un historial, no una detección]], acá aplicado a `Origin`.

Dos de las variantes serían de altísima fidelidad si el campo estuviera: `Origin: null` sobre un endpoint autenticado no pasa por accidente —análogo a [[Petición al servicio de metadatos de instancia]]—, y un origen reflejado que no está en la lista blanca real es, por definición, el ataque. La recomendación defensiva de mayor retorno del dominio no es una regla: es **registrar la cabecera `Origin` en las peticiones a endpoints con credenciales**.

El comodín de subdominio es el único que no se detecta ni con el campo instrumentado, porque el `Origin` es legítimo. Ese solo se ve desde el subdominio comprometido, no desde acá.

## Huecos conocidos

- [x] Las cuatro formas de fallar la validación del origen
- [x] Payloads y lectura de la respuesta — en [[CORS bypass de origen - matriz de referencia]]
- [ ] **Sin detección, por falta de instrumentación de `Origin`.** No es hueco de contenido: la fuente no captura el campo. La recomendación de mayor retorno es instrumentarlo, no escribir una regla. Primer dominio del vault cuya cara azul entera depende de un campo ausente
- [ ] `Timing-Allow-Origin` y otras cabeceras de origen cruzado con superficie propia
- [ ] CORS en preflight: abusar de `Access-Control-Allow-Headers` y `-Methods` demasiado amplios para habilitar peticiones que no serían simples
- [ ] Configuraciones de dominio cruzado heredadas —`crossdomain.xml` de Flash, `clientaccesspolicy.xml`— que sobreviven en aplicaciones viejas
