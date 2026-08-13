---
tipo: tradecraft
clase: "[[CWE-524 - Use of Cache Containing Sensitive Information]]"
eje: dirección
implementacion: "Hacer que la caché guarde la respuesta privada de la víctima como si fuera estática, y leerla"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Log de auditoría de la aplicación]]"]
requisitos: [caché-que-decide-por-la-url, discrepancia-de-ruta-caché-vs-servidor]
coste: medio
alternativas: ["[[Web cache - envenenamiento por entrada sin clave]]", "[[Control de acceso - IDOR]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - engaño de la caché
tags:
  - dominio/web
---

# Web cache - engaño de caché

## Cuándo lo elijo

Cuando el objetivo es **robar los datos de la víctima**, no empujar contenido. Es la dirección opuesta del dominio: en vez de meter algo malo en una entrada pública, se hace que la caché guarde la respuesta privada de la víctima y se la lee después.

Se elige cuando hay una caché que decide qué guardar por la **forma de la URL** —extensión o prefijo de ruta— en vez de por el contenido real, y cuando existe una página personalizada que valga la pena robar: la de cuenta, la de perfil, una que muestre un token.

Si la meta fuera empujar un payload a todos, el dominio es el opuesto, [[Web cache - envenenamiento por entrada sin clave]]. Si se puede leer los datos de otro directamente cambiando un identificador, quizá alcance con [[Control de acceso - IDOR]] y no haga falta la caché.

## Por qué funciona

La caché guarda contenido estático para no molestar al servidor, y decide qué es estático con una regla barata: "si la URL termina en `.css`, `.js`, `.jpg`, es estático, guardalo y serví lo guardado a todos". El servidor de aplicación, en cambio, resuelve la ruta a su manera y a menudo **ignora un sufijo que no entiende**.

El ataque explota esa diferencia:

1. Se arma una URL como `https://objetivo.com/cuenta/perfil.css`.
2. La víctima —autenticada— la abre, engañada por el atacante.
3. El servidor ignora el `perfil.css` que no existe y sirve `/cuenta/perfil`, la página personalizada de la víctima, con sus datos y con su sesión aplicada.
4. La caché ve la extensión `.css`, cree que es un recurso estático público, y **guarda esa respuesta personalizada**.
5. El atacante pide la misma URL `https://objetivo.com/cuenta/perfil.css` y recibe la copia cacheada, con los datos de la víctima.

Las variantes de confusión de ruta —qué sufijo engaña a qué par caché/servidor— están en [[Web cache entradas sin clave - matriz de referencia]]:

`/cuenta/perfil.css` — sufijo inexistente que la app ignora
`/cuenta/perfil%00.css` — byte nulo
`/cuenta/perfil;.css` — punto y coma como delimitador
`/cuenta/perfil%2f..%2f.css` — recorrido que vuelve al recurso

Es la misma familia de discrepancia entre dos parsers que [[MOC - Request smuggling]] y que [[Web cache - manipulación de la clave]], aplicada a la ruta.

## Cómo falla

Falla cuando la caché guarda por el **`Content-Type` real** de la respuesta en vez de por la extensión de la URL: una página que devuelve `text/html` no se guarda como estática por más `.css` que lleve el nombre.

Falla cuando la caché respeta las cabeceras `Cache-Control: private` o `no-store` de la respuesta —que las páginas personalizadas bien hechas mandan— en vez de decidir por la URL.

Y falla cuando el servidor no ignora el sufijo sino que devuelve `404`: sin la discrepancia de ruta no hay engaño.

## Coste

Medio. Confirmar la discrepancia de ruta es barato —se prueban los sufijos contra una página propia y se mira si la caché guarda—. Lo que agrega coste es que necesita **una víctima autenticada que abra la URL**, igual que los ataques del lado del cliente, lo que pone un techo de severidad y obliga a una prueba de concepto con dos sesiones.

Confirmarlo con la propia cuenta es limpio y seguro: se abre la URL autenticado, se cierra sesión, y se pide de nuevo sin sesión — si vuelven los datos propios, la caché guardó lo privado.

## Huella esperada

La firma más aprovechable del dominio entero, y es una que sí rinde:

- **Una respuesta con `Set-Cookie` o `Cache-Control: private` que aun así se cacheó** es la señal directa del engaño, y no ocurre por accidente. Vive en [[Log de acceso del servidor web]] cruzado con las cabeceras de respuesta, y es de alta fidelidad porque una respuesta personalizada guardada como estática es, por definición, el fallo.
- **Una URL con extensión estática que devuelve contenido dinámico** —`.css` que responde `text/html`— es la otra cara de la misma señal.
- El acceso del atacante a la copia cacheada queda en [[Log de auditoría de la aplicación]] como una lectura de datos de la víctima desde otra sesión, parecido al perfil de [[Acceso a un objeto de otro usuario]].

Ninguna detección del vault la implementa, pero a diferencia del envenenamiento, acá la señal **es de fuente disponible**: las cabeceras de respuesta se registran más seguido que los cuerpos. Es el caso del dominio con la cara azul más cercana a escribible, y queda anotado en [[MOC - Web cache]] como candidato a detección propia cuando se abra esa fase.
