---
tipo: moc
dominio: web
aliases:
  - MOC EL injection
  - OGNL
tags:
  - dominio/web
---

# MOC - EL injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-917 - Expression Language Injection]]. Identificar el motor, en [[EL injection - matriz de identificación]]. Acá vive **la decisión**.

Este dominio es el primo de Java de [[MOC - SSTI]], y separarlos es la decisión que lo define. Comparten el mecanismo —entrada evaluada como código en un motor de expresiones— pero la **superficie es otra**, y ahí está todo el trabajo: SSTI vive en las plantillas y se ve reflejado; EL injection vive en la validación, el ruteo, los mensajes de error y las cabeceras, y **casi nunca se ve**. Modelarlo por dónde entra, no por qué motor es, es lo que lo hace encontrable.

| Eje | Valores |
|---|---|
| Superficie | reflejo directo · evaluación indirecta/ciega · el framework evalúa por diseño |
| Motor | SpEL · OGNL · MVEL · JUEL → matriz |
| Capacidad | RCE · lectura de archivos · lectura de contexto (JUEL) |
| Canal | reflejado · fuera de banda |

**La superficie es el eje raíz**, y es la divergencia deliberada respecto de SSTI. Allá el eje fue la capacidad del motor y la superficie de origen se mandó a matriz. Acá se invierte: los motores de Java (SpEL, OGNL, MVEL) ejecutan todos directo, así que la capacidad casi no discrimina; lo que decide el trabajo es **cómo llega la entrada al evaluador**, porque de eso depende si se ve el resultado y dónde hay que buscar. El motor va a matriz, mismo criterio que el motor de plantillas en SSTI.

## Árbol de decisión — cómo llega la entrada al evaluador

```
¿La pila es Java? (Tomcat, Spring, Struts, JBoss)
├─ No → esto no es EL. Mirá [[MOC - SSTI]]
└─ Sí — ¿${7*7} vuelve como 49 en la respuesta?
   │
   ├─ Sí, reflejado → [[EL - reflejo directo en expresión]]
   │                   el caso fácil: identificar motor y tirar el payload
   │
   ├─ No vuelve, pero la pila usa OGNL/SpEL por diseño (Struts, ruteo Spring)
   │     → [[EL - OGNL en el framework]]
   │       buscá el CVE de la versión: nombre de parámetro, Content-Type, cabecera
   │
   └─ No vuelve, y la entrada se evalúa en validación/error/log
         → [[EL - evaluación indirecta y ciega]]
           confirmá por canal fuera de banda: DNS o HTTP a un host propio
```

Tres cosas que este orden codifica:

**La primera pregunta descarta el dominio.** EL injection es Java. Si `${7*7}` evalúa pero la pila es PHP o Python, es SSTI y no esto. Una petición de reconocimiento lo resuelve.

**El caso reflejado es el fácil y el menos frecuente.** A diferencia de SSTI, donde el reflejo es la norma, acá la mayoría de los EL son ciegos: la expresión se evalúa en un mensaje de validación o en el procesamiento del framework, y el resultado no vuelve. Por eso las dos ramas ciegas pesan más que la reflejada, al revés que en SSTI.

**El framework que evalúa por diseño es una rama aparte porque el fallo no es de la aplicación.** Los CVE de Struts no están en el código que escribió el desarrollador: están en que el framework evaluaba entrada como OGNL en lugares que nadie marcó. Se ataca por versión y CVE, no por reconocimiento de un reflejo.

## Árbol de decisión — identifiqué el motor, ¿hasta dónde llego?

```
¿Qué motor es?
├─ SpEL / OGNL / MVEL
│  ├─ ¿Sandbox activo?
│  │  ├─ No → RCE directo: T(Runtime) / @Runtime@ / Runtime
│  │  └─ Sí → escapá con reflexión, o bajá a lectura de archivos
│  └─ RCE → proceso hijo del servidor web → misma detección que command injection
└─ JUEL
   └─ Sin Runtime por defecto → leé el contexto (rutas, sesión, config)
      parecido a [[SSTI - lectura sin ejecución]]: es escalada, no consuelo
```

JUEL es el que corrige la expectativa: es el EL de las JSP y **no** da ejecución por defecto. Un EL que resulta ser JUEL puro no es RCE, y tratarlo como si lo fuera es perder el tiempo. Lo que sí da —la ruta física de la aplicación, atributos de sesión, configuración— puede alimentar otro dominio.

## Cheatsheets — entrada directa a los payloads

- [[EL injection - matriz de identificación]] — Delimitadores, distinguir de SSTI, firmas por motor, confirmación ciega, dónde buscar la evaluación indirecta
- [[EL injection payloads - matriz de referencia]] — RCE por motor, la cadena OGNL de Struts, escape de sandbox, lectura de contexto de JUEL, canal ciego

## Orden de aprendizaje

1. [[CWE-917 - Expression Language Injection]] — la entrada como expresión, y por qué es Java
2. [[EL injection - matriz de identificación]] — antes que cualquier payload, y acá también sirve para el caso ciego
3. [[EL - reflejo directo en expresión]] — el caso visible, para fijar el mecanismo
4. [[EL - evaluación indirecta y ciega]] — el caso real y frecuente, que es lo que separa el dominio de SSTI
5. [[EL - OGNL en el framework]] — cuando el fallo es del framework y hay CVE

El punto 4 es el corazón del dominio aunque no sea el más fácil. Si se aprende solo el caso reflejado, EL injection parece un SSTI de Java y se pierde todo lo que lo hace distinto: la evaluación que no se ve.

## Relación con otros dominios

- [[MOC - SSTI]] — el primo por mecanismo. La distinción es la superficie, y la prueba que los separa al principio es la misma —`${7*7}`— más el reconocimiento de la pila. La matriz de payloads de los dos se referencia porque el método de canal ciego es idéntico.
- [[MOC - Command injection]] — convergen en el efecto: ejecución que nace un proceso hijo del servidor web. La misma detección los cubre sin distinguirlos, y la ruptura del contexto de la expresión es la misma idea que la ruptura del contexto del comando.
- [[MOC - Deserialización]] — otro caso de "la aplicación interpreta como código algo que era dato", y en Java los dos se cruzan: varias cadenas de gadgets de deserialización terminan en una evaluación de EL.
- [[MOC - SSRF]] — la confirmación ciega hace que el servidor salga a la red, así que un EL ciego produce el mismo tráfico saliente que un SSRF y lo ven las mismas reglas.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Reflejo directo | [[Proceso hijo del servidor web]] | Intérprete hijo del servidor de aplicación |
| Reflejo / identificación | [[Log de errores del servidor web]] | Ráfaga de `SpelEvaluationException` / `OgnlException` |
| Evaluación ciega | [[Consulta DNS saliente]] · [[Conexión saliente del servidor de aplicación]] | El servidor sale a la red para confirmar |
| OGNL en el framework | [[Registro del WAF]] | Cadenas OGNL largas y características en cabecera o cuerpo |
| Todas → ejecución | [[Proceso hijo del servidor web]] | El efecto compartido con command injection y SSTI |

Dos observaciones que este dominio deja:

**Ninguna detección propia hizo falta: noveno dominio consecutivo cerrado reutilizando reglas.** La ejecución la ve [[Intérprete de comandos como hijo del servidor web]], la identificación ruidosa [[Ráfaga de errores del servidor desde un mismo origen]], y el canal ciego las reglas de red de SSRF. La convergencia en el efecto vuelve a pagar: reglas escritas para command injection y SSRF cubren un dominio que no existía cuando se escribieron.

**El caso de OGNL en el framework es de los pocos donde la firma rinde.** Las cadenas de los CVE de Struts —`#_memberAccess`, `@java.lang.Runtime@`— son largas, específicas y no aparecen en tráfico legítimo, así que [[Registro del WAF]] y [[Payload de inyección en parámetros de la URL]] las cazan bien. Es la misma excepción a la regla de "efecto sobre firma" que [[MOC - Prototype pollution]], y por la misma razón: la cadena no tiene forma legítima. La letra chica también es la misma: esos payloads entran por cabeceras y cuerpo, que solo ve el WAF, no [[Log de acceso del servidor web]].

## Huecos conocidos

- [x] Las tres superficies — reflejada, ciega, framework
- [x] Los cuatro motores, con JUEL marcado como el sin-RCE
- [x] Identificación y payloads — dos matrices
- [x] Cara azul — cubierta por las reglas de command injection y SSRF existentes
- [ ] El escape de sandbox de SpEL y OGNL está en la matriz de payloads pero no como nota de criterio propia: si aparece un caso donde la decisión de escapar contra bajar a lectura sea recurrente, merece su tradecraft, como lo tiene [[SSTI - escape del entorno restringido]]
- [ ] Expresiones en otros componentes de Java —Camel, seguridad de Spring, colas— con la misma clase y superficies nuevas
