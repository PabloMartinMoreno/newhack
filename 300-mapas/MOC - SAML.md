---
tipo: moc
dominio: web
aliases:
  - MOC SAML
  - federación SAML
tags:
  - dominio/web
---

# MOC - SAML

> [!abstract] Nota de referencia paraguas
> Decodificar la aserción y elegir la rama, en [[SAML - matriz de identificación]]. Acá vive **la decisión**.

Segundo dominio del vault sin CWE propia, igual que [[MOC - OAuth]]. SAML no es una vulnerabilidad: es un protocolo de federación, y lo que se rompe en él ya tiene clase. Ocupa el mismo lugar que OAuth en la arquitectura —autenticar delegando en un tercero— con ejes distintos, y por eso es dominio aparte y no una rama de aquel.

| Fase rota | `clase:` | Nota |
|---|---|---|
| La verificación de la firma | `CWE-347` | [[SAML - firma no verificada o eliminada]] |
| El desacople verificar/leer, moviendo elementos | `CWE-347` | [[SAML - envoltura de firma XML]] |
| El desacople verificar/leer, partiendo el texto | `CWE-287` | [[SAML - inyección de comentarios en NameID]] |
| El parser de XML, antes de la firma | `CWE-611` | [[SAML - XXE en el parser de la aserción]] |

Las cuatro clases ya existían. Como en OAuth, **no hizo falta escribir ninguna técnica nueva**: SAML es una superficie sobre vulnerabilidades conocidas, y la regla 7 del `CLAUDE.md` —la `clase:` es la vulnerabilidad, no el vector— lo coloca solo.

| Eje | Valores |
|---|---|
| Fase rota | firma no verificada · envoltura · comentario en NameID · XXE en el parser |
| Objetivo | la sesión (entrar como la víctima) · el servidor (XXE) |
| Binding | POST · Redirect (DEFLATE) → matriz |
| Impacto | suplantación · escalada de rol · lectura de archivos · SSRF |

El **binding va a matriz**, mismo criterio que el flujo en OAuth: cambia cómo se decodifica la aserción —base64 directo o base64 + DEFLATE crudo—, no cambia qué se decide.

## Árbol de decisión — qué rompo

```
¿Cuál es el objetivo?
├─ El servidor (leer archivos, red interna)
│  └─ ¿El parser resuelve entidades?
│     └─ Sí → [[SAML - XXE en el parser de la aserción]] → [[MOC - XXE]]
│            ocurre ANTES de validar la firma: no hace falta una firma válida
└─ La sesión (entrar como la víctima)
   │
   ├─ Quitá <Signature>, editá NameID, reenviá
   │  └─ ¿Pasa? → [[SAML - firma no verificada o eliminada]]   ← PRIMERO, cinco minutos
   │
   ├─ ¿La firma se valida? Duplicá la aserción, una firmada + una falsa
   │  └─ ¿El SP lee la falsa? → [[SAML - envoltura de firma XML]]
   │
   └─ ¿La firma cubre el NameID y puedo elegir mi identificador en el IdP?
      └─ NameID con <!----> partido → [[SAML - inyección de comentarios en NameID]]
```

Tres cosas que este orden codifica:

**La firma no verificada va primero porque cuesta cinco minutos.** Editar un campo y reenviar, sin criptografía ni construcción de XML. Cuando funciona, todo lo demás sobra.

**La envoltura y el comentario son el mismo fallo por dos mecanismos.** Los dos explotan que el proveedor de servicio **verifica un dato y usa otro**: la envoltura mueve elementos, el comentario parte el texto. Es el patrón de [[Control de acceso - salto de contexto]] —dos operaciones que deberían mirar lo mismo miran cosas distintas— trasladado a la firma XML.

**El XXE ocurre aguas arriba de todo.** El parseo pasa antes de validar la firma, así que la rama del servidor ni siquiera necesita una firma válida. Cambia el objetivo del dominio entero: de la cuenta al servidor.

## Árbol de decisión — conseguí algo, ¿hasta dónde llega?

```
¿Qué obtuve?
├─ Sesión como la víctima
│  └─ ¿La víctima es admin del SP? → toma de la aplicación entera
├─ Escalada con mi cuenta (role → admin en AttributeStatement)
│  └─ solo si la firma no cubre los atributos
├─ Una aserción que el SP acepta sin validar Audience/NotOnOrAfter
│  └─ reusable en OTRO proveedor de servicio, o más tarde → persistencia
└─ XXE en el parser
   └─ [[MOC - XXE]]: file:// primero, después red interna y metadatos de instancia
```

La aserción reutilizable es la que se subestima: un proveedor de servicio que no valida `Audience` acepta una aserción emitida para otro, así que comprometer un SP débil de la federación puede abrir los demás.

## Cheatsheets — entrada directa a los payloads

- [[SAML - matriz de identificación]] — Reconocer el flujo, decodificar los dos bindings, anatomía de la aserción, las cinco pruebas de apertura, herramienta
- [[SAML XSW - matriz de referencia]] — Los ocho patrones de envoltura en orden, manejo de `ID`, qué cambiar en la aserción falsa

## Orden de aprendizaje

1. [[SAML - matriz de identificación]] — decodificar y reconocer va primero, como en OAuth
2. [[SAML - firma no verificada o eliminada]] — el caso barato y de mayor probabilidad
3. [[SAML - envoltura de firma XML]] — el ataque propio del XML firmado, el que da nombre al dominio
4. [[SAML - inyección de comentarios en NameID]] — el mismo desacople por otro mecanismo
5. [[SAML - XXE en el parser de la aserción]] — el dominio dado vuelta: el servidor como objetivo

Es el segundo MOC del vault donde la matriz va **primera** en el orden de lectura, por la misma razón que en OAuth: sin decodificar la aserción, las cuatro ramas son indistinguibles.

## Relación con otros dominios

- [[MOC - OAuth]] — el otro protocolo de federación, mismo lugar en la arquitectura. [[SAML - firma no verificada o eliminada]] es primo de [[OAuth - validación del id_token]]: los dos son un token firmado por un tercero mal verificado, comparten `clase:` y comparten las cinco comprobaciones. La diferencia es el formato —XML firmado en vez de JWT—, y ese formato trae la envoltura, que el JWT no tiene.
- [[MOC - XXE]] — [[SAML - XXE en el parser de la aserción]] entra ahí, con la misma `clase:` y las mismas ramas. El orden de destinos es el de aquel MOC.
- [[MOC - Broken access control]] — la envoltura y el comentario son [[Control de acceso - salto de contexto]] en la capa de firma: verificar una cosa y usar otra.
- [[MOC - Autenticación]] — SAML es el mecanismo de autenticación cuando se delega en un IdP. Todo lo de contraseñas y segundo factor de allá **se saltea** cuando una de estas ramas funciona.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Firma no verificada | [[Log de autenticación de la aplicación]] | Aserción sin firma válida que abrió sesión — **si se registra** |
| Envoltura de firma | [[Log de autenticación de la aplicación]] | Respuesta con **dos aserciones** o `ID` duplicados |
| Comentario en NameID | [[Log de autenticación de la aplicación]] | `NameID` que contiene un comentario XML |
| XXE en el parser | [[Conexión saliente del servidor de aplicación]] | Conexión saliente durante el parseo — **la única con huella de red** |

La observación que este dominio deja, y parte en dos su cara azul:

**Las tres ramas de firma son silenciosas; la de XXE es ruidosa.** Es la división limpia del dominio. Las de firma producen un inicio de sesión que el proveedor de servicio considera legítimo —la firma que verificó era genuina o la aserción parecía sin firma por diseño—, así que solo se detectan inspeccionando el XML de la aserción, que ninguna fuente del vault parsea. La de XXE, en cambio, hace que el servidor abra una conexión, y eso lo ven las reglas de SSRF que ya existen.

Las firmas de las tres ramas de firma son de **buena fidelidad si se instrumenta**: dos aserciones en una respuesta, un `ID` duplicado o un comentario en el `NameID` no ocurren en tráfico legítimo. No es un hueco de contenido sino de fuente —la recomendación de mayor retorno es registrar la estructura cruda de la aserción, no escribir una regla—, el mismo patrón que [[CORS - reflejo del origen con credenciales]] con la cabecera `Origin` y que [[Un log sin identidad es un historial, no una detección]].

Ninguna detección propia hizo falta: octavo dominio consecutivo cerrado reutilizando reglas. La cara azul aprovechable —la de XXE— la cubren [[Barrido de puertos internos desde el servidor de aplicación]] y [[Petición al servicio de metadatos de instancia]].

## Huecos conocidos

- [x] Las cuatro fases rotas, cada una con su `clase:` real
- [x] Decodificación de los dos bindings y los ocho patrones de XSW — dos matrices
- [x] Cara azul de XXE — cubierta por las reglas de SSRF existentes
- [ ] **Las tres ramas de firma no se detectan, por falta de instrumentación del XML.** La recomendación de mayor retorno es registrar la estructura cruda de la aserción. Mismo hueco de fuente que CORS con `Origin`
- [ ] Metadatos del proveedor de identidad manipulables: si el SP descarga la configuración del IdP de una URL, es SSRF y confusión de proveedor a la vez
- [ ] SAML Single Logout, con su propia superficie de repetición y falsificación
- [ ] Cifrado de la aserción (no solo firma): relleno y confusión de algoritmo en `EncryptedAssertion`
