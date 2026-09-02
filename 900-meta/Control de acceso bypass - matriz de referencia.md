---
tipo: meta
aliases:
  - Bypass de autorización
  - 403 bypass
tags:
  - meta/referencia
  - dominio/web
---

# Control de acceso bypass - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué probar cuando la ruta responde `403`, cuando el identificador no es predecible, o cuando falta descubrir la superficie. El método sistemático está en [[Control de acceso - matriz de pruebas]].

## Verbos

Lo primero ante un `403`. La inconsistencia entre verbos es real y frecuente.

```
GET  POST  PUT  PATCH  DELETE  HEAD  OPTIONS  TRACE
```

`OPTIONS` suele revelar qué verbos acepta la ruta, incluidos los que la interfaz nunca usa. `HEAD` a veces pasa filtros escritos solo para `GET` y confirma la existencia del recurso.

```http
X-HTTP-Method-Override: PUT
X-Method-Override: DELETE
_method=PUT
```

Sobreescritura de método. Muchos marcos de trabajo la respetan y muchos filtros de seguridad, no: el filtro ve un `POST` y la aplicación ejecuta un `PUT`.

## Cabeceras

```http
X-Original-URL: /admin/users
X-Rewrite-URL: /admin/users
```

Se pide `/` con la cabecera puesta. Si hay un proxy que enruta por ella, el control aplicado a la ruta pedida no se aplica a la ruta servida. Es la discrepancia clásica proxy/aplicación.

```http
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
```

Contra controles por IP que confían en cabeceras. Aparece en paneles restringidos "a la red interna".

```http
X-Forwarded-Host: interno
Referer: https://objetivo/admin/
```

El `Referer` importa más de lo que parece: algunos controles verifican que se venga de una página administrativa, lo que convierte el control en una cabecera que el cliente escribe.

## Normalización de rutas

La discrepancia entre cómo normaliza el proxy y cómo normaliza la aplicación.

```
/admin        /Admin        /ADMIN
/admin/       /admin//      //admin
/admin/.      /./admin      /admin/./
/%61dmin      /%2561dmin
/admin%20     /admin%09     /admin%00
/admin?       /admin#       /admin;x
/..;/admin
```

`/..;/` es específico de ciertos servidores de aplicaciones Java, donde el punto y coma inicia parámetros de ruta y el proxy no lo interpreta igual.

```
/api/v1/admin   →   /api/v2/admin
/api/admin      →   /admin
```

Versiones y prefijos alternativos. La v1 sigue en pie por compatibilidad y su filtro quedó viejo.

## Descubrir rutas

Antes de romper nada hay que saber qué existe.

```
/robots.txt
/sitemap.xml
/.well-known/
/swagger.json  /openapi.json  /api-docs  /graphql
/.git/config
```

Los primeros dos suelen listar precisamente lo que se quiso ocultar de los buscadores.

**Los bundles de JavaScript son la mejor fuente.** Contienen todas las rutas de la API, incluidas las administrativas, porque el mismo código se sirve a todos los usuarios y la interfaz solo oculta los botones. Los `source maps` reconstruyen el código original y con él los nombres de las funciones administrativas.

Otras fuentes que pagan: archivos históricos de la web, repositorios públicos de la organización, y las respuestas de error verbosas que citan rutas internas.

## Identificadores no predecibles

Un UUID no es una defensa: es un identificador que hay que **encontrar** en vez de adivinar. Dónde se filtran:

- **Listados y buscadores** — cualquier endpoint que devuelva varios objetos.
- **Exportaciones** — CSV y PDF suelen incluir identificadores internos.
- **Notificaciones y correos** — enlaces con el identificador en la URL.
- **Contenido compartido** — un objeto compartido con el atacante revela su identificador y a veces el de sus relacionados.
- **Respuestas de otros endpoints** — el identificador del objeto de B aparece en un comentario, una mención, un historial.
- **Mensajes de error** — "el objeto X ya existe".

Cuando de verdad no se filtra en ningún lado, se mira el **tipo**: los UUID de versión 1 incorporan marca de tiempo y dirección MAC, lo que los vuelve parcialmente predecibles. Los identificadores derivados de marcas de tiempo o de contadores codificados también.

## Parámetros

```
id=1&id=2
id[]=1&id[]=2
{"id": 1, "id": 2}
```

Contaminación de parámetros. El filtro lee el primero, la aplicación usa el último — o al revés.

```
{"id": "1", "user_id": "2"}
```

Agregar el parámetro que el endpoint no espera pero el modelo sí usa.

**Cambiar el formato del cuerpo.** Si el endpoint acepta JSON, probar `form-encoded` o XML: la validación suele estar escrita para un solo formato. Es además la puerta a [[MOC - XXE]].

## Campos para mass assignment

Los que más veces existen y menos veces están protegidos:

```
role  roles  role_id  user_role  user_type  type
admin  is_admin  isAdmin  isadmin  superuser
permissions  scopes  groups  group_id
verified  is_verified  email_verified  active  is_active
status  state  approved  confirmed
balance  credit  price  amount  discount
owner  owner_id  user_id  created_by  tenant_id
```

Se prueban en creación **y** en actualización: son rutas distintas con validaciones distintas. El criterio está en [[Control de acceso - mass assignment]].

Anidar a veces esquiva el validador:

```json
{"nombre": "x", "usuario": {"is_admin": true}}
```

## Cuando nada entra

Si el control responde `403` con todo verbo, toda cabecera, toda normalización y toda versión, está bien puesto. La conclusión correcta no es "la aplicación es segura" sino **"este endpoint lo es"**: la cobertura desigual es la norma del dominio, y el siguiente endpoint puede no tener nada. Volver a [[Control de acceso - matriz de pruebas]] y seguir recorriendo.
