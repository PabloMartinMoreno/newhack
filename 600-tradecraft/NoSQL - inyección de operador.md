---
tipo: tradecraft
clase: "[[CWE-943 - Improper Neutralization of Special Elements in Data Query Logic]]"
eje: familia
implementacion: "Contrabandear un operador de consulta donde la aplicación espera un dato, cambiando el tipo de la entrada"
opsec: ruidoso
telemetria: ["[[Log de autenticación de la aplicación]]", "[[Registro del WAF]]"]
requisitos: [entrada-que-llega-a-un-objeto-de-consulta]
coste: bajo
alternativas: ["[[NoSQL - extracción ciega]]", "[[NoSQL - inyección de JavaScript]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - operator injection
  - NoSQL auth bypass
  - $ne bypass
tags:
  - dominio/web
---

# NoSQL - inyección de operador

## Cuándo lo elijo

Es el caso base del dominio y el primero a probar. Se reconoce por el contexto de entrada —un cuerpo JSON, o una query string que el framework parsea a objetos— y se confirma metiendo un operador donde la aplicación espera una cadena, viendo si la respuesta cambia.

El objetivo natural es el **salto de autenticación**: una consulta de login `{"user": X, "pass": Y}` se vuelve trivial si se cambia `pass` por un operador que siempre es verdadero. Si la entrada se fuerza a cadena y el operador no entra, la rama de estructura se cierra y queda [[NoSQL - inyección de JavaScript]] si hay un sink que evalúe código.

## Por qué funciona

En Mongo la consulta es un objeto, no una cadena, y los operadores son claves que empiezan con `$`. Si la entrada del usuario se coloca dentro de ese objeto sin forzar su tipo, el atacante manda un objeto en vez de un valor y **cambia el significado de la consulta sin romper ninguna sintaxis**:

```
esperado:  {"user": "admin", "pass": "1234"}
inyectado: {"user": "admin", "pass": {"$ne": null}}
```

`$ne: null` significa "distinto de nulo" — cualquier contraseña lo cumple, así que la consulta hace login como `admin` sin conocer la contraseña. No hubo comilla, no hubo error: se contrabandeó una estructura donde iba un dato.

Los operadores útiles y los contextos de entrada están en [[NoSQL operadores - matriz de referencia]]. Los más frecuentes:

- `{"$ne": null}` — distinto de nulo, el salto de login clásico.
- `{"$gt": ""}` — mayor que la cadena vacía, otro siempre-verdadero.
- `{"$regex": "^adm"}` — coincidencia parcial, para enumerar o afinar.
- `{"$in": [...]}` — lista de valores.

La misma inyección por query string, cuando el framework la parsea:

```
user=admin&pass[$ne]=
```

que se convierte en `{"user": "admin", "pass": {"$ne": ""}}`. Es el caso que aparece en formularios que no usan JSON, y el que más se pasa por alto porque la petición parece inocente.

## Cómo falla

Falla cuando el código **fuerza el tipo** de la entrada a cadena antes de la consulta: `String(pass)` convierte `{"$ne": null}` en el texto literal `"[object Object]"`, que no es un operador. Es la mitigación correcta y la más barata.

Falla cuando el framework valida el esquema de la entrada y rechaza claves con `$` o `.`.

Y falla cuando la entrada nunca llega a un objeto de consulta —se usa en un `$where` de JavaScript, o en una cadena—: ahí la rama es otra.

## Coste

Bajo, el más bajo del dominio. El salto de login son dos o tres peticiones con el operador en el campo de contraseña. La forma por query string es igual de barata y a veces pasa el WAF porque no parece un payload.

El reconocimiento previo —confirmar que la entrada llega a un objeto y no se fuerza a cadena— es lo único que puede llevar tiempo, y se resuelve probando un operador y mirando si algo cambia.

## Huella esperada

Firma razonable y un efecto anómalo claro:

- La petición lleva **una clave que empieza con `$`** —`$ne`, `$gt`— en el cuerpo JSON o como `campo[$op]` en la query. Es una firma sobre el cuerpo que ve [[Registro del WAF]] si lo inspecciona, y no [[Log de acceso del servidor web]], que no registra cuerpos. Una clave con `$` en la entrada no aparece en tráfico legítimo casi nunca — es de las firmas que rinden, como las de [[MOC - Prototype pollution]].
- El salto de login deja **un inicio de sesión exitoso sin la secuencia de fallos que precede a un ataque de contraseña** —o directamente un login a una cuenta administrativa desde un origen nuevo—. Lo ve [[Log de autenticación de la aplicación]], y se cruza con [[Accesos exitosos contra muchas cuentas desde un origen]] cuando se prueba en volumen, aunque el salto de operador suele acertar a la primera y no genera fallos.

Ese acierto a la primera es la contracara defensiva: a diferencia de la fuerza bruta, la inyección de operador **no deja ráfaga de fallos**, así que la detección por volumen no la ve. La firma de la clave `$` en el cuerpo es la señal real, y depende de instrumentar el cuerpo — el hueco de fuente compartido. Anotado en [[MOC - NoSQL injection]].
