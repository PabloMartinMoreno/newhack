---
tipo: tradecraft
clase: "[[CWE-943 - Improper Neutralization of Special Elements in Data Query Logic]]"
eje: familia
implementacion: "Inyectar en un operador que evalúa JavaScript del lado del servidor —$where, mapReduce— para leer, exfiltrar o denegar"
opsec: ruidoso
telemetria: ["[[Log de errores del servidor web]]", "[[Log de acceso del servidor web]]"]
requisitos: [sink-que-evalúa-javascript-con-entrada]
coste: medio
alternativas: ["[[NoSQL - inyección de operador]]", "[[NoSQL - extracción ciega]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - $where injection
  - server-side JS injection
  - mapReduce injection
tags:
  - dominio/web
---

# NoSQL - inyección de JavaScript

## Cuándo lo elijo

Cuando la entrada llega a un operador que **evalúa JavaScript** en el servidor de base de datos —`$where`, `mapReduce`, `$accumulator`, `$function`— y no a un objeto de consulta. Se reconoce cuando la inyección de operador no aplica pero una expresión de JavaScript en la entrada sí cambia el resultado.

Es la rama menos frecuente y más grave del dominio: es la única que llega a algo parecido a ejecución de código, aunque acotada al intérprete de la base. Se elige cuando el sink evalúa JS; si solo arma un objeto de consulta, la rama es [[NoSQL - inyección de operador]].

## Por qué funciona

Mongo permite pasar una función de JavaScript como filtro con `$where`, y otros operadores evalúan JS por diseño. Si la aplicación construye esa función concatenando entrada del usuario, el atacante escribe la expresión, y el motor la ejecuta:

```
esperado:  {"$where": "this.user == 'admin'"}
inyectado: {"$where": "this.user == 'admin' || '1'=='1'"}
```

La condición inyectada es siempre verdadera, así que la consulta devuelve todo. Es inyección clásica de ruptura de contexto, la misma idea que [[MOC - Command injection]] y SQLi, ahora en un contexto de JavaScript.

Lo que se consigue, en orden:

- **Salto de condición**, como arriba: `|| true` para devolver todo.
- **Extracción ciega**, con un canal temporal propio: `this.pass[0]=='a' && sleep(1000)` retarda si el carácter coincide. Se cruza con [[NoSQL - extracción ciega]], que es a donde va el detalle.
- **Denegación de servicio**: un bucle infinito o un `sleep` largo en el `$where` cuelga el servidor. Es barato y peligroso.
- **Lectura del objeto**: el JS tiene acceso al documento en `this`, así que se leen campos que la consulta no expone.

No llega a ejecución en el sistema operativo: el intérprete de Mongo está aislado y no tiene acceso a `require` ni al proceso. Por eso es "código dentro del motor", no RCE — una distinción que conviene marcar en el informe para no sobrevender el hallazgo. Los payloads están en [[NoSQL extracción ciega - matriz de referencia]] § JavaScript.

## Cómo falla

Falla contra la configuración que **deshabilita la evaluación de JavaScript** en el servidor —`javascriptEnabled: false` en Mongo—, que es la mitigación recomendada y cada vez más el valor por defecto en las versiones nuevas. Sin JS, `$where` no evalúa y la rama se cierra entera.

Falla cuando la aplicación no usa `$where` con entrada del usuario, que es la buena práctica: `$where` es lento y desaconsejado incluso por rendimiento, así que su presencia con entrada es ya un olor a problema.

Y falla, como toda la familia, si la entrada se fuerza a un tipo que no llega al evaluador.

## Coste

Medio. El salto de condición es una petición. La extracción ciega por tiempo hereda el costo alto de [[NoSQL - extracción ciega]]. La denegación es una petición pero **no se prueba a fondo en producción** por lo obvio.

> [!danger] El bucle en $where cuelga el servidor
> Un `while(true)` o un `sleep` largo en `$where` bloquea el hilo de la base y puede tirar la aplicación para todos. Es denegación de servicio real, no teórica. En un objetivo real se demuestra con un retardo corto y medido, no con un bucle infinito. Acordar la ventana.

## Huella esperada

Ruidosa, y con la firma más específica del dominio:

- La petición lleva **una expresión de JavaScript en el cuerpo** —`$where`, `sleep(`, `this.`, operadores de comparación de JS—, que no aparece jamás en tráfico legítimo. Es una firma de alta fidelidad sobre el cuerpo, para [[Registro del WAF]].
- La denegación deja **la señal de efecto más clara**: el servidor de base colgado, tiempos de respuesta disparados, `500`/`503` en [[Log de acceso del servidor web]] y errores de tiempo agotado en [[Log de errores del servidor web]]. Lo ve cualquier monitoreo de disponibilidad, igual que [[GraphQL - denegación por complejidad]].
- La extracción por tiempo deja el mismo patrón de volumen que [[NoSQL - extracción ciega]].

Es la rama con la cara azul más cubierta del dominio, por dos vías: la firma de JS en el cuerpo (si se instrumenta) y el efecto de la denegación (que se ve solo). La lectura y el salto de condición, en cambio, son silenciosos como el resto de NoSQL — una consulta que devuelve de más no se distingue de una legítima sin registro a nivel de consulta. Anotado en [[MOC - NoSQL injection]].
