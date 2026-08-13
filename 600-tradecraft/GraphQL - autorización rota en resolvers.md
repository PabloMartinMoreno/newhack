---
tipo: tradecraft
clase: "[[CWE-862 - Missing Authorization]]"
eje: fase
implementacion: "Pedir campos o mutaciones que la interfaz no ofrece, aprovechando que el control de acceso no está en cada resolver"
opsec: limpio
telemetria: ["[[Log de auditoría de la aplicación]]"]
requisitos: [esquema-conocido, control-de-acceso-ausente-en-algún-resolver]
coste: medio
alternativas: ["[[Control de acceso - IDOR]]", "[[Control de acceso - escalada vertical]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - GraphQL BOLA
  - resolver authz
tags:
  - dominio/web
---

# GraphQL - autorización rota en resolvers

## Cuándo lo elijo

Después de [[GraphQL - introspección del esquema]], que da el mapa. Es la rama de mayor impacto directo del dominio: se piden campos y mutaciones que la aplicación nunca expone en su interfaz, apostando a que el control de acceso no esté puesto donde GraphQL lo necesita.

Es el mismo problema que [[MOC - Broken access control]] —falta de autorización— pero con una superficie que GraphQL agranda de forma característica, y por eso vive acá aunque comparta `clase:` con aquel dominio.

## Por qué funciona

En REST, cada endpoint es un punto donde poner el control de acceso, y aunque falten algunos, la superficie es acotada y visible. En GraphQL hay **un solo endpoint** y el control tiene que estar en **cada resolver de cada campo** — y el modelo de datos en grafo hace que se llegue al mismo dato por muchos caminos.

De ahí tres patrones que la introspección deja servidos:

- **Campos que la interfaz no pide pero el esquema expone.** El desarrollador protegió el flujo que la UI usa y olvidó que el mismo tipo tiene un campo `passwordHash` o `isAdmin` que se puede pedir directo.
- **Mutaciones no listadas.** El esquema revela mutaciones —crear, borrar, cambiar rol— que ninguna pantalla ofrece y que no validan quién las llama.
- **Acceso por relación.** Se pide un objeto propio y, siguiendo una relación del grafo, se llega a datos de otro usuario: `miPedido { usuario { otrosPedidos { … } } }`. El resolver del primer campo valida; los anidados, no. Es IDOR a través del grafo — [[Control de acceso - IDOR]] con la vuelta que da GraphQL.

El método de prueba es el de [[Control de acceso - matriz de pruebas]] aplicado al esquema: por cada campo y mutación sensible, ¿responde a un usuario que no debería? La diferencia es que acá la lista de qué probar sale entera de la introspección, no hay que adivinarla.

## Cómo falla

Falla cuando el control de acceso está en la capa de datos —no en el resolver— de modo que da igual por qué camino del grafo se pida: el dato se filtra en la fuente. Es la mitigación correcta y la que hay que recomendar, porque poner el control en cada resolver a mano garantiza que alguno falte.

Falla cuando el esquema está segmentado por rol y el servidor no expone siquiera los campos que el usuario no puede ver — aunque eso es más raro y más frágil que proteger el dato.

Y no aplica cuando la introspección no dio nada y no se reconstruyó el esquema: sin el mapa, esta rama vuelve a ser adivinar, que es lo que GraphQL evita.

## Coste

Medio. Con el esquema en la mano, probar cada campo y mutación sensible es mecánico —una consulta por candidato— pero puede haber muchos, y hay que hacerlo con cuentas de distintos roles para comparar. La parte de relaciones del grafo es la más creativa: hay que encontrar el camino que salta de lo propio a lo ajeno.

Es de las ramas de mejor retorno del dominio: no necesita romper nada, las peticiones son válidas, y el impacto —datos de otros usuarios, acciones administrativas— es directo.

## Huella esperada

Limpia, y de ahí el `opsec: limpio`. Las peticiones son GraphQL válidas contra el endpoint normal, con la sesión del atacante. No hay payload, no hay error, no hay nada sintácticamente anómalo — solo se pide lo que no se debería.

La señal está en [[Log de auditoría de la aplicación]] y es exactamente la de [[MOC - Broken access control]]: **un actor accediendo a un objeto o ejecutando una acción que su rol no autoriza**. Lo cubre [[Acceso a un objeto de otro usuario]] para las lecturas y [[Cambio de privilegio fuera del flujo administrativo]] para las mutaciones — las dos sin saber que fue por GraphQL.

Y hereda su límite: esas detecciones dependen de que el registro incluya el **dueño del objeto** y el **actor**, que es el campo que casi nunca está instrumentado. Sin él, la petición de GraphQL parece idéntica a una legítima. Es el mismo hueco de [[Un log sin identidad es un historial, no una detección]], y en GraphQL se agrava porque todo pasa por un endpoint: el log de acceso ve siempre la misma URL, así que sin registro a nivel de resolver no hay nada que distinguir.
