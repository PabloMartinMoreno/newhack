---
tipo: tradecraft
clase: "[[CWE-444 - Inconsistent Interpretation of HTTP Requests]]"
eje: primitiva-de-desincronización
implementacion: "Hacer que el navegador de la víctima envíe una petición desincronizada contra el servidor, sin proxy intermedio"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]", "[[Registro del WAF]]"]
requisitos: [servidor-que-desincroniza-con-el-propio-navegador]
coste: alto
alternativas: ["[[Request smuggling - CL.TE y TE.CL]]", "[[XSS - almacenado]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - client-side desync
  - CL.0
  - browser-powered smuggling
tags:
  - dominio/web
---

# Request smuggling - desincronización del cliente

## Cuándo lo elijo

Cuando no hay una cadena de dos servidores que desincronizar —o la hay pero está mitigada— y aun así el servidor procesa mal el largo de ciertas peticiones. Es la variante que **no necesita un proxy intermedio**: el desync ocurre entre el navegador de la víctima y el servidor, y el ataque se dispara desde una página del atacante que la víctima visita.

Es la rama más nueva y la más cara. Se elige cuando las dos clásicas no aplican pero el sondeo muestra que el servidor deja bytes sobrantes en la conexión, o cuando el objetivo es explotable solo desde el navegador de una víctima real.

## Por qué funciona

Las dos ideas que la sostienen:

**CL.0** — el servidor **ignora el `Content-Length`** en ciertos endpoints y lo trata como cero. Pasa con endpoints que no esperan cuerpo —archivos estáticos, redirecciones, algunos manejadores de error—: el servidor responde sin leer el cuerpo, y ese cuerpo, que el atacante controló, queda al principio de la siguiente petición de la conexión. No hace falta `Transfer-Encoding` ni un back distinto: alcanza un solo servidor que no lee lo que dijo que iba a leer.

**Desincronización del lado del cliente** — el navegador reutiliza conexiones para el mismo origen. Si el atacante consigue que el navegador de la víctima mande una petición con un sobrante, ese sobrante se antepone a la **siguiente** petición que el navegador haga a ese origen —una petición legítima, con las cookies de la víctima—. La página del atacante hace `fetch` con `credentials:'include'` para forzar la conexión y colar el sobrante.

Eso convierte el smuggling en un ataque **al navegador de la víctima**, no a la infraestructura, y por eso su alcance se parece más al de [[XSS - almacenado]]: se roba la sesión, se envenena la respuesta que ve la víctima, se encadena con un endpoint que refleje para lograr ejecución. La diferencia con XSS es que no necesita un sink de HTML: funciona donde no hay ninguno.

Las construcciones de CL.0 y las cadenas del lado del cliente están en [[Request smuggling - matriz de explotación]].

## Cómo falla

Falla cuando el servidor lee y descarta el cuerpo de toda petición aunque no lo espere, en vez de ignorarlo. Es la corrección de CL.0.

Falla cuando el servidor no reutiliza la conexión con el cliente, o cuando el navegador no la reutiliza para el origen objetivo — sin reutilización, el sobrante no contamina nada.

Y falla porque depende de una víctima que visite la página del atacante y tenga una sesión activa, igual que el resto de los ataques del lado del cliente. Es un techo de severidad que hay que reflejar.

## Coste

Alto, el más alto del dominio. Encontrar un endpoint CL.0 es reconocimiento fino —hay que probar muchos manejadores buscando el que ignora el cuerpo—, y construir la cadena del lado del cliente que funcione desde un navegador real, con sus reglas de reutilización de conexión, es delicado y frágil.

La herramienta —el modo de desincronización del lado del cliente de HTTP Request Smuggler— reduce el reconocimiento, pero la explotación fiable sigue siendo trabajo. Conviene fijar presupuesto y, si el objetivo se explota por la vía clásica, no invertir acá.

## Huella esperada

Distinta del resto del dominio, y más difícil de detectar para el defensor.

Como no hay proxy intermedio, no existe el desajuste de conteo entre dos capas que delata a las variantes clásicas. La petición desincronizada llega al servidor como una sola conexión, y lo anómalo es interno a ella.

- [[Registro del WAF]] y [[Log de acceso del servidor web]] pueden ver un cuerpo sobre un endpoint que no debería recibirlo —un `POST` con cuerpo a un archivo estático o a una redirección—, que es la firma de CL.0 y no ocurre en tráfico legítimo. Es la única señal aprovechable, y es de fuente: hay que registrar el cuerpo, que el log de acceso no hace.
- El ataque en sí, desde el navegador de la víctima, llega con su sesión y aspecto normal salvo por ese sobrante. Ninguna detección del vault lo cubre.

Es el caso del dominio con menos huella y el que más se parece, defensivamente, a un ataque del lado del cliente: la señal está en el navegador de la víctima, no en el servidor. Anotado como el hueco propio de esta rama en [[MOC - Request smuggling]].
