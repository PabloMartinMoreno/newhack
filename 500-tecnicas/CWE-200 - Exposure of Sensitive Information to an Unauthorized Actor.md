---
tipo: tecnica
taxonomia: cwe
identificador: CWE-200
wstg: WSTG-INFO-05
tacticas: []
aliases:
  - CWE-200
  - information disclosure
  - exposición de información
tags:
  - dominio/web
---

# CWE-200 - Exposure of Sensitive Information to an Unauthorized Actor

> [!note] Nota paraguas
> Sin contenido operativo. Su uso en GraphQL vive en [[GraphQL - introspección del esquema]]; el reconocimiento, en [[GraphQL - matriz de reconocimiento]].

## Qué es

La aplicación entrega a quien no debería información que le sirve al atacante: la estructura interna de la API, nombres de campos y tipos, rutas, versiones, mensajes de error con detalle. No es un exploit por sí solo — es lo que hace posible o barato todo lo demás.

## Por qué es la clase de la introspección de GraphQL

En una API REST el atacante tiene que adivinar los endpoints y los parámetros. GraphQL, por diseño, ofrece **introspección**: una consulta que devuelve el esquema entero —cada tipo, cada campo, cada argumento, cada relación—. Cuando está habilitada para usuarios no confiables, es exposición de información en su forma más pura: el atacante recibe el mapa completo de la API sin adivinar nada.

Eso no es una vulnerabilidad grave por sí misma —el esquema no son datos de usuario— pero cambia la economía de todo el resto: con el esquema en la mano, encontrar el resolver sin control de acceso o el campo que llega a una inyección deja de ser adivinar y pasa a ser leer.

## Por qué la mitigación no cierra el problema

Deshabilitar la introspección ayuda pero no alcanza, y conviene decirlo en el informe para no dar falsa tranquilidad: aunque esté apagada, el esquema se reconstruye por **sugerencia de campos** —el servidor corrige nombres mal escritos y con eso confirma los válidos— y por fuerza bruta de nombres. La introspección apagada sube el costo del reconocimiento; no lo elimina.

La mitigación real es tratar cada resolver como una frontera de autorización, de modo que conocer el esquema no habilite nada. El esquema puede ser público sin que eso sea un problema si los datos detrás están protegidos.

## Referencias canónicas

- [CWE-200](https://cwe.mitre.org/data/definitions/200.html)
- WSTG-INFO-05
- OWASP API Security — API3 Excessive Data Exposure
