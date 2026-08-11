---
tipo: tradecraft
clase: "[[T1087.002 - Domain Account Discovery]]"
eje: fase
implementacion: "Consultar LDAP con una credencial válida para mapear cuentas, grupos y relaciones"
opsec: limpio
telemetria: ["[[Windows 4624 - Successful logon]]"]
requisitos: [una-credencial-de-dominio]
coste: bajo
alternativas: []
probado: nunca
contexto: [lab-ad]
aliases:
  - enumeración de dominio
  - BloodHound
tags:
  - dominio/ad
---

# Enumeración LDAP del directorio

## Cuándo lo elijo

Primero, siempre, apenas hay una credencial válida cualquiera. Es el paso que convierte "tengo un usuario" en "sé exactamente a dónde ir". Todo lo demás del dominio —[[Kerberoasting]], [[AS-REP roasting]], las cadenas de permisos— se elige mirando lo que esta consulta devuelve.

Se hace antes de tocar nada más porque es barato, es silencioso, y ahorra todo lo que sigue. Ir a explotar sin haber enumerado es probar a ciegas.

## Por qué funciona

Porque el directorio es una base de datos de lectura pública para cualquiera que esté autenticado. No hay que romper nada: se pregunta, y contesta con todo — cuentas, grupos, equipos, atributos, y los permisos de cada objeto sobre cada otro.

Lo que cambió la práctica es el **análisis de grafo**: en vez de leer permisos de a uno, se calculan rutas completas desde la cuenta que uno tiene hasta administrador de dominio. Esas rutas existen por acumulación histórica y nadie las ve mirando permisos sueltos.

## Cómo falla

- **Rara vez falla en conseguir datos**, porque leer el directorio es funcionalidad básica. Falla en pasar desapercibido si hay auditoría fina.
- **Consultas muy amplias y ruidosas** pueden destacar contra la línea base, si alguien la mide — que casi nadie hace.
- **Directorios endurecidos** limitan qué atributos ve un usuario común, aunque el grueso sigue siendo legible.
- **Herramientas conocidas** dejan artefactos propios en el endpoint desde el que corren — proceso, conexiones, a veces archivos. La consulta es limpia; la herramienta que la hace, no siempre.

## Coste

El más bajo del dominio. Una credencial y una consulta. El resultado es el mapa completo.

## Huella esperada

`opsec: limpio` en su sentido más fuerte: **es tráfico legítimo indistinguible del de cualquier aplicación integrada al dominio**. Es el punto ciego clásico de AD, y por tres razones que se suman —es legítimo, requiere auditoría específica que no viene por defecto, y no produce ninguna consecuencia observable en el momento.

- [[Windows 4624 - Successful logon]] registra el acceso que precede a la consulta, pero no la consulta.
- La enumeración LDAP en sí solo se ve con auditoría específica del directorio, que genera mucho volumen y casi nadie recolecta.
- Lo que sí se ve es **el ataque siguiente**: el pico de peticiones de tickets de servicio de [[Kerberoasting]], la petición sin preautenticación de [[AS-REP roasting]]. La enumeración se detecta por lo que viene después, no por sí misma.

Por eso, del lado azul, la recomendación es reducir lo que el mapa revela —permisos acumulados, nombres de servicio innecesarios— más que intentar detectar la lectura.
