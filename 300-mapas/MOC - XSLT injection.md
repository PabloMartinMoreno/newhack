---
tipo: moc
dominio: web
aliases:
  - MOC XSLT
tags:
  - dominio/web
---

# MOC - XSLT injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-94 - Improper Control of Generation of Code]]. Identificar el procesador, en [[XSLT - matriz de identificación]]. Acá vive **la decisión**.

Es el primo de [[MOC - SSTI]] sobre XML: los dos son inyección en un lenguaje de plantilla/transformación evaluado del lado del servidor, y los dos se modelan por **capacidad del motor**, no por el motor. En XSLT esa capacidad la fija el **procesador** —libxslt, Xalan, Saxon, .NET— y sobre todo qué tiene habilitado: recursos externos y funciones de extensión.

| Eje | Valores |
|---|---|
| Capacidad del procesador | lectura/SSRF (`document`) · ejecución (extensiones) |
| Procesador | libxslt/PHP · Xalan/Java · .NET · Saxon → matriz |
| Impacto | divulgación · lectura de archivos · SSRF · RCE · escritura |

**La capacidad es el eje raíz**, igual que en SSTI. El procesador va a matriz —cambia la sintaxis del payload, no la decisión—, mismo criterio que el motor de plantillas en SSTI y el de base de datos en SQLi.

## Árbol de decisión — qué capacidad tiene el procesador

```
¿1+1 evalúa en la transformación?  → [[XSLT - matriz de identificación]] § 1
├─ No → no se inyecta en la hoja; revisar dónde cae la entrada
└─ Sí — identificá el procesador con system-property('xsl:vendor')
   │
   ├─ ¿document() / unparsed-text() habilitados?
   │     → [[XSLT - lectura y SSRF]]   ← PROBAR PRIMERO, menor requisito
   │       lectura de archivos, SSRF a interno/metadatos, divulgación
   │
   └─ ¿Funciones de extensión habilitadas? (php:function, Java, .NET)
         → [[XSLT - ejecución por funciones de extensión]]   ← el techo: RCE
           depende del procesador y de que estén activas
```

Tres cosas que este orden codifica:

**Identificar el procesador va antes que todo.** El `vendor` decide qué sintaxis de extensión probar y por lo tanto si hay RCE; tirar payloads sin identificar gasta peticiones y llena el registro de errores. Es la fase obligatoria, como en SSTI.

**La lectura va antes que la ejecución, porque necesita menos.** `document()` está activo por defecto más seguido que las extensiones, así que la lectura de archivos y el SSRF se consiguen sin que las extensiones estén habilitadas. Son impacto alto sin llegar a RCE, y el escalón barato.

**La ejecución depende de una configuración específica.** `registerPHPFunctions`, las extensiones de Xalan, el scripting de .NET — están apagadas más seguido que en las plantillas de SSTI. Un XSLT sin extensiones tiene la lectura como techo, y tratarlo como RCE es perder el tiempo.

## Árbol de decisión — qué consigo por capacidad

```
¿Qué permite el procesador?
├─ Solo document() → lectura de archivos → [[MOC - XXE]] (mismo abuso de parser)
│               → SSRF a interno / metadatos → [[MOC - SSRF]]
├─ unparsed-text() (2.0) → lectura de texto plano, más limpia
├─ Funciones de extensión → RCE → efecto de [[MOC - Command injection]]
└─ exsl:document (escritura) → webshell → [[Escritura de archivo en la raíz web]]
```

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[XSLT - matriz de identificación]] | Confirmar, `system-property`, firmas por procesador, versión, qué capacidades hay, canal ciego |
| [[XSLT payloads - matriz de referencia]] | Divulgación, lectura, SSRF, RCE por procesador (PHP/Java/.NET), escritura, canal ciego |

## Orden de aprendizaje

1. [[CWE-94 - Improper Control of Generation of Code]] — la transformación como código, y por qué depende del procesador
2. [[XSLT - matriz de identificación]] — el procesador antes que cualquier payload
3. [[XSLT - lectura y SSRF]] — el escalón barato, sin extensiones
4. [[XSLT - ejecución por funciones de extensión]] — el techo, cuando las extensiones están activas

## Relación con otros dominios

- [[MOC - SSTI]] — el primo directo: los dos son inyección en un motor de plantilla/transformación, modelados por capacidad. [[XSLT - ejecución por funciones de extensión]] es a XSLT lo que [[SSTI - ejecución directa]] a las plantillas; el canal ciego y el orden de lectura son idénticos.
- [[MOC - XXE]] — la lectura por `document()` abusa que un parser de XML lea recursos locales, el mismo fondo que XXE. Los dos viven sobre XML; XXE ataca la resolución de entidades, XSLT la transformación. El XXE local sin telemetría y la lectura local de XSLT comparten hueco de fuente.
- [[MOC - SSRF]] — `document('http://...')` es un vector de SSRF; entra en aquel MOC con su economía de destinos.
- [[MOC - Command injection]] — la ejecución por extensión converge en el mismo efecto —proceso hijo del servidor web— y la misma detección lo cubre.
- [[MOC - File upload]] — `exsl:document` que escribe en la raíz web es webshell, cruza con [[Webshell]].

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Identificación / reconocimiento | [[Log de errores del servidor web]] | Ráfaga de excepciones de XSLT con el nombre del procesador |
| Lectura local (`file://`) | — | **Nada** — no cruza ninguna frontera |
| SSRF (`document http`) | [[Conexión saliente del servidor de aplicación]] · [[Consulta DNS saliente]] | Conexión saliente del proceso |
| Ejecución por extensión | [[Proceso hijo del servidor web]] | Intérprete hijo del servidor de aplicación |
| Escritura (`exsl:document`) | [[Escritura de archivo en la raíz web]] | Archivo ejecutable nuevo en la raíz |

La observación es la misma que en SSTI y refuerza el patrón acumulado:

**Ninguna detección propia hizo falta: el dominio se cierra reutilizando SSRF, XXE, command injection y escritura de archivo.** La ejecución la ve [[Intérprete de comandos como hijo del servidor web]], el SSRF las reglas de conexión saliente, la escritura [[Archivo ejecutable nuevo en la raíz web]], y el reconocimiento ruidoso [[Ráfaga de errores del servidor desde un mismo origen]]. Es la mejor evidencia acumulada de que detectar **efecto** en vez de firma paga: un dominio que no existía cuando se escribieron esas reglas queda cubierto por ellas, porque converge en los mismos efectos —conexión saliente, proceso hijo, archivo nuevo—.

El único caso sin telemetría es la **lectura local con `file://`**, que no emite nada —mismo hueco de fuente que el XXE local—: sin conexión, sin proceso, ninguna fuente lo ve. Es límite de fuente, no de contenido.

Vigésimo primer dominio cerrado sin detección nueva.

## Huecos conocidos

- [x] Las dos capacidades — lectura/SSRF y ejecución
- [x] Identificación por procesador y payloads por lenguaje — dos matrices
- [x] Cara azul — cubierta por SSRF, XXE, command injection y escritura de archivo existentes
- [ ] **Lectura local con `file://` sin telemetría**, mismo hueco de fuente que el XXE local: no cruza ninguna frontera vigilada
- [ ] XProc y otras tuberías de procesamiento XML como superficie vecina
- [ ] XSLT del lado del cliente (en el navegador) — otra superficie, sin acceso al servidor
