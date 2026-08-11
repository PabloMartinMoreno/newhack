---
tipo: tradecraft
clase: "[[CWE-918 - Server-Side Request Forgery]]"
eje: impacto
implementacion: "Usar el servidor como escáner de puertos y hosts de la red interna"
opsec: quemado
telemetria: ["[[Conexión saliente del servidor de aplicación]]"]
requisitos: [ssrf-confirmado, oraculo-observable]
coste: alto
alternativas: ["[[SSRF - metadatos de instancia cloud]]", "[[SSRF - canal directo]]"]
probado: nunca
contexto: [php8-linux]
aliases:
  - port scan vía SSRF
  - escaneo interno
tags:
  - dominio/web
---

# SSRF - escaneo de la red interna

## Cuándo lo elijo

Cuando el SSRF está confirmado, los metadatos de nube no dan —porque no hay nube, o porque IMDSv2 está puesto— y hace falta saber qué hay adentro antes de decidir el siguiente paso.

Es el uso natural del [[SSRF - canal ciego]], que no sirve para leer pero sí para preguntar. También es lo que convierte un hallazgo abstracto en un informe concreto: "se puede hacer peticiones arbitrarias" pesa mucho menos que "desde la aplicación se alcanza el panel de administración interno en el puerto 8080".

Conviene acotar el alcance antes de empezar: barrer rangos completos es caro, ruidoso y en gran medida innecesario. Los puertos que pagan son pocos y conocidos — bases de datos, cachés, paneles internos, orquestadores —, y están en [[SSRF destinos - matriz de referencia]].

## Por qué funciona

El servidor está adentro del perímetro y responde de forma distinta según lo que encuentre. Esa diferencia es el oráculo:

- **Puerto cerrado** — la conexión se rechaza de inmediato. Respuesta rápida, error de conexión.
- **Puerto filtrado** — no contesta nadie. Se agota el tiempo de espera: respuesta lenta.
- **Puerto abierto con otro protocolo** — la conexión se establece y el cliente HTTP se atraganta con lo que recibe. Rápido, y con un error **distinto** del de puerto cerrado.
- **Puerto abierto con HTTP** — respuesta normal, y con retorno se lee entera.

Tres estados distinguibles por tiempo y tipo de error alcanzan para mapear una red. Es más lento que un escáner de verdad, pero se hace desde adentro, que es lo que ningún escáner externo puede.

## Cómo falla

- **Todos los errores se ven iguales** — sin diferencia de mensaje ni de tiempo, no hay oráculo y el escaneo no arranca.
- **Tiempos de espera largos y uniformes** — si cada puerto filtrado cuesta treinta segundos, barrer mil puertos es inviable en el tiempo de un engagement.
- **Límite de peticiones** — es exactamente el perfil que dispara cualquier control de ritmo: cientos de peticiones idénticas salvo por un número.
- **El cliente solo habla HTTP** — no distingue "abierto con otro protocolo" de "cerrado", y se pierde un estado.
- **Segmentación de red** — el servidor de aplicación está en su propia subred sin visibilidad de lo demás. Es la defensa correcta y deja el escaneo en nada.
- **No hay red interna** — en arquitecturas donde todo son servicios gestionados, no hay `10.0.0.0/8` que barrer.

## Coste

Alto y creciente: una petición por combinación de host y puerto, muchas de ellas esperando un tiempo de espera completo. Se domina reduciendo el espacio de búsqueda —hosts probables, puertos probables— antes que paralelizando, porque paralelizar dispara los límites de ritmo y arruina la medición de tiempos.

## Huella esperada

Es la variante más ruidosa del dominio, y por eso `opsec: quemado`. No hay forma sigilosa de barrer una red.

- [[Conexión saliente del servidor de aplicación]] con **cientos de conexiones fallidas** hacia IP y puertos secuenciales. El patrón —muchos intentos, casi todos fallando, en progresión ordenada— no lo produce ninguna aplicación legítima.
- Conexiones a puertos que la aplicación jamás usa. Una app web habla con su base y su caché; no con el 22, el 3389 ni el 9200.
- Ráfaga de peticiones HTTP entrantes al mismo endpoint, con el parámetro de URL variando de forma sistemática, visible en [[Log de acceso del servidor web]].
- Correlación uno a uno entre peticiones entrantes y conexiones salientes fallidas: la firma más clara, porque establece causa y efecto.

Los rangos, los puertos que pagan y cómo interpretar cada oráculo están en [[SSRF destinos - matriz de referencia]].
