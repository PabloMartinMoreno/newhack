---
tipo: moc
dominio: web
aliases:
  - MOC LDAP
tags:
  - dominio/web
---

# MOC - LDAP injection

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-90 - LDAP Injection]]. La sintaxis del filtro, en [[LDAP filtro - matriz de referencia]]. Acá vive **la decisión**.

Es la tercera hermana de las inyecciones de consulta, con [[MOC - SQL injection]] y [[MOC - NoSQL injection]]. Comparten la clase padre y varios conceptos —canal reflejado contra ciego, extracción carácter por carácter, salto de autenticación— pero LDAP tiene una sintaxis de **notación prefija con paréntesis** que cambia toda la mecánica: no se rompe una cadena con una comilla, se reescribe una lógica booleana cerrando paréntesis.

| Eje | Valores |
|---|---|
| Canal | reflejado · ciego booleano |
| Objetivo | salto de autenticación · divulgación de atributos |
| Contexto | filtro de búsqueda · DN de bind → matriz |
| Directorio | AD · OpenLDAP · otros → matriz |

**El canal es el eje raíz**, heredado de SQLi, porque LDAP no tiene la bifurcación operador-contra-código de NoSQL: hay un solo mecanismo de inyección —manipular el filtro— y lo que decide el trabajo es si el resultado se refleja o hay que inferirlo. El contexto (filtro contra DN) y el directorio van a matriz, mismo criterio que el motor en las hermanas.

## Árbol de decisión — qué canal y qué objetivo

```
¿La entrada llega a un filtro LDAP sin escapar?  → [[LDAP filtro - matriz de referencia]] § 1
├─ Meté un * o un ) → ¿el filtro se rompe o amplía?
│  └─ No cambia nada → se escapa, no hay dominio
└─ Sí, inyecta
   │
   ├─ ¿El objetivo es entrar?
   │     → [[LDAP - manipulación del filtro]]   ← PRIMERO, salto de autenticación
   │       * en la contraseña, o admin)(&) para anular
   │
   ├─ ¿El objetivo es sacar datos Y se reflejan?
   │     → misma nota: amplía el filtro, cambia & por |, pide de más
   │
   └─ ¿Sacar datos y NO se reflejan?
         → [[LDAP - extracción ciega]] con el comodín como oráculo
           OJO: LDAP no tiene canal temporal — necesita oráculo booleano sí o sí
```

Tres cosas que este orden codifica:

**El salto de autenticación va primero porque es el impacto típico.** LDAP se usa para autenticar, así que un filtro siempre-verdadero es login directo, y es dos o tres peticiones con un catálogo acotado de payloads. Sacar datos es el segundo premio.

**El comodín es la herramienta central.** Un `*` en la contraseña la vuelve "cualquiera"; un `*` como patrón es el oráculo de la extracción ciega. Toda la mecánica del dominio gira alrededor de ese carácter y de los paréntesis.

**LDAP no tiene salida temporal.** A diferencia de SQLi (`SLEEP`) y NoSQL (`sleep` en JavaScript), LDAP no ofrece un canal de tiempo. Si no hay oráculo booleano, la extracción ciega se corta — es la limitación propia del dominio y hay que saberla antes de invertir.

## Árbol de decisión — qué consigo

```
¿Qué inyecté?
├─ Filtro siempre-verdadero en login → salto de autenticación → [[MOC - Autenticación]]
├─ & convertido en | → devuelve todos los objetos → divulgación de directorio
├─ Comodín como oráculo → extracción de atributos (mail, memberOf, roles)
└─ Inyección en el DN de bind → cambiar la rama de autenticación (raro)
```

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[LDAP filtro - matriz de referencia]] | La sintaxis, confirmar, salto de auth por contexto, ampliar el resultado, inyección en DN, escape |
| [[LDAP extracción ciega - matriz de referencia]] | Oráculo booleano, enumerar atributos y usuarios, extracción con comodín, bisección con `>=`/`<=` |

## Orden de aprendizaje

1. [[CWE-90 - LDAP Injection]] — la notación prefija y por qué romper un filtro no es cerrar una comilla
2. [[LDAP - manipulación del filtro]] — el caso base, el salto de autenticación
3. [[LDAP - extracción ciega]] — el paralelo de las hermanas, con el comodín como oráculo

El punto 2 va primero porque el salto de autenticación es lo que hace de LDAP un objetivo de alto impacto: no es solo leer datos, es entrar sin credenciales al sistema que autentica.

## Relación con otros dominios

- [[MOC - SQL injection]] y [[MOC - NoSQL injection]] — las hermanas. El canal ciego, la extracción por carácter y el salto de autenticación se trasladan; [[LDAP - extracción ciega]], [[NoSQL - extracción ciega]] y [[SQLi ciego - matriz de referencia]] comparten estructura. Lo que no se traslada es el canal temporal —LDAP no lo tiene—.
- [[MOC - Autenticación]] — el salto de filtro es un bypass de autenticación por otra vía, `CWE-90` en vez de `CWE-287`. Como el salto de operador de NoSQL, entra sin tocar las credenciales.
- [[MOC - Active Directory]] — LDAP es el protocolo de consulta de AD. La inyección web contra un directorio corporativo puede revelar los mismos atributos que enumera [[Enumeración LDAP del directorio]] desde adentro, pero desde una aplicación web sin credencial de dominio. La matriz de atributos se comparte con [[AD enumeración - matriz de referencia]].
- [[MOC - GraphQL]] y [[MOC - WebSocket]] — LDAP puede ser el sink de un argumento o de un mensaje, igual que las otras inyecciones. El canal es el vector, esta es la clase.

## Cara azul

| Variante | Telemetría | Firma |
|---|---|---|
| Manipulación del filtro | [[Registro del WAF]] | Metacaracteres `*` `)(` `)(&` en un campo de usuario |
| Salto de autenticación | [[Log de autenticación de la aplicación]] | Login exitoso sin la contraseña correcta, sin ráfaga de fallos previa |
| Extracción ciega | [[Log de acceso del servidor web]] | Cientos de consultas casi idénticas con variación mínima |

La observación es la misma que en NoSQL, y refuerza el patrón acumulado de las inyecciones:

**La firma del metacarácter rinde y la asimetría se repite.** Los caracteres `*`, `)(`, `)(&` en un campo que normalmente es un nombre de usuario no aparecen en tráfico legítimo — quinta firma de cuerpo que rinde, tras prototype pollution, OGNL, request smuggling y NoSQL. Y la asimetría del salto contra la extracción es idéntica a la de NoSQL: **el salto de autenticación acierta a la primera y no deja ráfaga de fallos**, así que las reglas de fuerza bruta no lo ven —solo la firma del metacarácter—; la extracción ciega es cientos de consultas casi idénticas, `forma: agregado` detectable por volumen sin instrumentar el cuerpo.

Décimo sexto dominio cerrado sin detección nueva. Los dos candidatos escribibles son los mismos que en NoSQL —la firma del metacarácter sobre el WAF y el agregado de la extracción ciega—, lo que sugiere que una sola detección de firma de inyección sobre el cuerpo cubriría a las tres hermanas a la vez. Anotado abajo.

## Huecos conocidos

- [x] Los dos canales — reflejado y ciego
- [x] Salto de autenticación y divulgación de atributos
- [x] Sintaxis, payloads de bypass y extracción con comodín — dos matrices
- [x] Cara azul de firma — misma que las hermanas de inyección
- [ ] **Una detección de firma de inyección sobre el cuerpo cubriría SQLi, NoSQL y LDAP juntas.** Los metacaracteres son distintos —`'`, `$`, `*)(`— pero el patrón es el mismo: caracteres de estructura de consulta en un campo de datos. Candidato de detección transversal, hueco de trabajo
- [ ] Inyección en el DN de bind como caso propio, más específico del despliegue
- [ ] `ldap://` como esquema de SSRF —el vector que ya menciona [[SSRF esquemas - matriz de referencia]]— es otra superficie, no esta
