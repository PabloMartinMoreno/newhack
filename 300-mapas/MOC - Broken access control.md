---
tipo: moc
dominio: web
aliases:
  - MOC control de acceso
  - Control de acceso
  - Broken access control
tags:
  - dominio/web
---

# MOC - Broken access control

> [!abstract] Nota de referencia paraguas
> Las definiciones viven en [[CWE-639 - Authorization Bypass Through User-Controlled Key]], [[CWE-862 - Missing Authorization]] y [[CWE-915 - Improperly Controlled Modification of Dynamically-Determined Object Attributes]]. El método de prueba, en [[Control de acceso - matriz de pruebas]]. Acá vive **la decisión**.

Tres CWE en un MOC. Comparten lo único que importa a efectos operativos: **el mismo método de prueba**. La matriz actor × objeto × operación las encuentra a las tres, y separarlas obligaría a repetir ese método en tres mapas.

> [!important] Este dominio no tiene payloads
> Es la diferencia estructural con los seis dominios anteriores del vault, y cambia cómo se trabaja. No hay sintaxis que memorizar ni parser que engañar: la petición es válida, la sesión es legítima, la respuesta es `200`. Lo único fuera de lugar es **quién** la manda.
>
> Consecuencias prácticas: ningún WAF lo detecta, ninguna herramienta automática lo encuentra sin entender el modelo de datos, y el trabajo no es explotar sino **no saltearse ningún endpoint**. Por eso la matriz principal del dominio es de método y no de payloads.

| Eje | Valores |
|---|---|
| Dirección | horizontal · vertical · de contexto |
| Dónde falla el control | ausente · confía en dato del cliente · solo en la interfaz · inconsistente entre rutas o verbos |
| Vector | identificador · ruta directa · campo de más · orden de peticiones |
| Obstáculo | identificador no predecible · control por ruta · validación de campos |
| Impacto | lectura ajena · modificación ajena · escalada a admin · toma de cuenta |

## Árbol de decisión — qué estoy buscando

```
¿Qué quiero alcanzar?
├─ Datos de otro usuario del mismo nivel  → [[Control de acceso - IDOR]]
├─ Una función de mayor privilegio
│  ├─ ¿Conozco la ruta?     → [[Control de acceso - escalada vertical]]
│  └─ ¿Hay endpoint de escritura con asignación automática?
│                           → [[Control de acceso - mass assignment]]
└─ El resultado de un proceso sin cumplir sus pasos
                            → [[Control de acceso - salto de contexto]]
```

Las dos ramas de escalada vertical son alternativas reales, no un orden: `mass assignment` llega al mismo lugar **sin necesitar descubrir ninguna ruta administrativa**, y por eso conviene probarla primero cuando la aplicación es una API que devuelve objetos completos.

## Árbol de decisión — el endpoint responde 403

```
¿Qué probaste?
├─ Otro verbo                → GET/POST/PUT/PATCH/DELETE, override → § Verbos
├─ Cabeceras de reescritura  → X-Original-URL, X-Forwarded-For     → § Cabeceras
├─ Normalizar la ruta        → /Admin, //admin, /..;/admin         → § Normalización
├─ Otra versión de la API    → v1 en vez de v2                     → § Normalización
└─ Todo lo anterior → el control está bien puesto EN ESTE ENDPOINT
```

La última línea es la conclusión que hay que escribir con cuidado. **La cobertura desigual es la norma**: que un endpoint esté protegido no dice nada del siguiente. En este dominio, a diferencia de los otros, un "no se pudo" nunca es una conclusión sobre la aplicación.

## Árbol de decisión — el identificador no es predecible

```
¿Dónde se filtra?
├─ Listados, buscadores, exportaciones
├─ Notificaciones y correos
├─ Contenido compartido con vos
├─ Respuestas de otros endpoints
└─ En ningún lado → mirar el TIPO: UUIDv1 y derivados de tiempo son predecibles
```

Cambiar un entero por un UUID **no es una mitigación**: oculta el identificador sin agregar el control que falta. Es la confusión más común del dominio y conviene decirlo explícito en el informe, o el hallazgo se cierra cambiando el formato del identificador y el problema queda intacto.

## Cheatsheets

- [[Control de acceso - matriz de pruebas]] — El método: preparación, la matriz actor × objeto × operación, cómo leer cada respuesta, priorización, qué documentar
- [[Control de acceso bypass - matriz de referencia]] — Verbos, cabeceras, normalización de rutas, descubrimiento, dónde se filtran los identificadores, campos de mass assignment

## Orden de aprendizaje

1. [[CWE-639 - Authorization Bypass Through User-Controlled Key]] — autenticar no es autorizar
2. [[Control de acceso - matriz de pruebas]] — el método, que acá es el contenido central
3. [[Control de acceso - IDOR]] — el caso base, horizontal
4. [[CWE-862 - Missing Authorization]] → [[Control de acceso - escalada vertical]] — de horizontal a vertical
5. [[Control de acceso - mass assignment]] — escalada vertical sin ruta administrativa
6. [[Control de acceso - salto de contexto]] — el que no se busca porque ninguna ruta parece sospechosa

El punto 2 va antes que cualquier técnica, al revés que en los demás dominios. Sin dos cuentas y sin recorrido sistemático, este dominio no se prueba: se tropieza con él.

## Relación con otros dominios

- [[MOC - SSRF]] — cuando la función administrativa existe pero está segmentada en la red interna, el camino deja de ser de autorización y pasa a ser de alcance.
- [[MOC - XXE]] — cambiar el formato del cuerpo para esquivar validación desemboca ahí si el endpoint acepta XML.
- [[MOC - SQL injection]] — un identificador controlado que llega a una consulta es a la vez este dominio y aquel. Vale probar los dos sobre el mismo parámetro.
- [[Inyección SQL en parámetro de búsqueda]] — modelo de hallazgo; los de este dominio siguen la misma estructura, con la particularidad de que la evidencia incluye **dos** sesiones.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| IDOR | [[Log de auditoría de la aplicación]] | Actor distinto del dueño del objeto — comparar los dos campos |
| Escalada vertical | [[Log de auditoría de la aplicación]] | Acción administrativa con rol efectivo insuficiente |
| Escalada vertical | [[Log de acceso del servidor web]] | Ráfaga de `403`/`404` seguida de un `200` en ruta administrativa |
| Mass assignment | [[Log de auditoría de la aplicación]] | Cambio de un campo sensible fuera del flujo administrativo |
| Salto de contexto | [[Log de auditoría de la aplicación]] | Secuencia de pasos **incompleta**; tiempos imposibles |

Cuatro de las cinco filas dependen del mismo artefacto, y es el que **no existe salvo que alguien lo programe**. Ninguna configuración lo enciende: [[Log de auditoría de la aplicación]] hay que construirlo.

Peor: la mayoría de las implementaciones registran el actor y la acción, y **no el dueño del objeto ni los campos modificados** — que son exactamente los dos campos de los que depende toda la tabla de arriba. Sin ellos queda un historial, no una detección.

Esa es la recomendación defensiva de mayor retorno de todo el dominio web, y no es una regla de detección: es un requisito de instrumentación.

## Huecos conocidos

- [x] Dirección — horizontal, vertical y de contexto
- [x] Vector — identificador, ruta, campo de más, orden de peticiones
- [x] Método de prueba — en [[Control de acceso - matriz de pruebas]]
- [x] Bypass de `403` — en [[Control de acceso bypass - matriz de referencia]]
- [x] Cara azul — [[Acceso a un objeto de otro usuario]] (`correlacion`) y [[Cambio de privilegio fuera del flujo administrativo]] (`invariante`), las dos sobre [[Log de auditoría de la aplicación]]
- [x] Detección sobre secuencias — resuelto con `forma: invariante` en el esquema de `deteccion`
- [ ] **El artefacto sigue habiendo que instrumentarlo.** Las dos reglas dependen de campos que la mayoría de las aplicaciones no registra: el dueño del objeto y los campos modificados. Sin ellos no son difíciles de escribir, son imposibles
- [ ] Autorización en GraphQL y en arquitecturas de microservicios — mismo dominio, superficie distinta
