---
tipo: tradecraft
clase: "[[T1046 - Network Service Discovery]]"
eje: profundidad
implementacion: "Conectar al puerto abierto y provocar respuestas hasta identificar producto y versión"
opsec: quemado
telemetria: ["[[Sysmon EID 3 - NetworkConnect]]", "[[Log de acceso del servidor web]]", "[[Log de errores del servidor web]]"]
requisitos: [puerto-abierto-confirmado]
coste: medio
alternativas: ["[[Escaneo - sondeo SYN de puertos TCP]]"]
probado: nunca
contexto: [lab-ad, web-generica]
aliases:
  - service detection
  - version detection
  - banner grabbing
tags:
  - dominio/red
---

# Escaneo - identificación de servicio y versión

## Cuándo lo elijo

Después de tener puertos abiertos, y sólo sobre los que voy a atacar. Es el paso que convierte *hay algo en el 8080* en *hay un Tomcat 9.0.30*, y sin él la fase siguiente es probar a ciegas.

La decisión es **de alcance, no de sí o no**: identificar versión sobre todo lo abierto multiplica el ruido y el tiempo sin agregar nada sobre los puertos que no pienso tocar. Se elige la lista corta.

Y es el primer paso del reconocimiento que **deja de ser pasivo de verdad**: acá se completan handshakes, se mandan cargas específicas por protocolo y se llega a la aplicación. Todo lo anterior se quedaba en la pila.

## Por qué funciona

Porque los servicios se identifican solos. Muchos anuncian producto y versión en el banner sin que nadie pregunte; los que no, se delatan por cómo responden a entradas inesperadas —qué error devuelven, en qué orden negocian, qué extensiones ofrecen—. Una huella de comportamiento identifica igual que una cadena de versión, y no se puede desactivar sin cambiar el servicio.

Sobre puertos que hablan TLS, el certificado suele regalar nombres de host y dominios internos que no estaban en ningún lado.

## Cómo falla

Falla contra banners editados o falsos, y contra servicios detrás de un proxy que responde por ellos: se identifica el intermediario, no el destino. Falla también cuando la versión anunciada no es la real —parcheo de distribución que mantiene el número viejo—, y eso convierte un hallazgo de "versión vulnerable" en un falso positivo de informe.

Del lado del sigilo es lo más ruidoso del dominio y por eso `opsec: quemado`: las cargas de identificación son fijas, conocidas y firmadas por cualquier IDS, y a diferencia del resto de la fase **quedan en el log de la aplicación** — una ráfaga de peticiones raras contra un servidor web es exactamente [[Ráfaga de errores del servidor desde un mismo origen]].

## Coste

Medio por puerto y alto en atención: es donde el reconocimiento pasa de invisible a evidente. En un engagement con requisito de sigilo, esta fase se hace a mano y sobre tres puertos, no automatizada sobre todos.
