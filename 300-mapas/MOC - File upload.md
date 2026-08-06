---
tipo: moc
dominio: web
aliases:
  - MOC File upload
  - File upload
tags:
  - dominio/web
---

# MOC - File upload

> [!abstract] Nota de referencia paraguas
> La definición vive en [[CWE-434 - Unrestricted File Upload]]. Acá vive **la decisión**. Se encadena con [[MOC - File inclusion]].

Intersección de ejes ortogonales.

| Eje | Valores |
|---|---|
| Validación evadida | extensión · MIME/`Content-Type` · magic bytes · doble extensión · contenido |
| Ejecución | ¿cae en webroot y corre? · ruta controlable · sobrescritura de archivo |
| Payload | webshell (php/jsp/aspx) · polyglot · SVG-XSS · XXE vía SVG/DOCX |
| Impacto | RCE · XSS almacenado · path traversal en el nombre · sobrescritura · DoS |

## Árbol de decisión — qué valida el server

```
Subí una webshell .php simple. ¿Qué la rechaza?
├─ La extensión              → extensiones alternativas / doble ext / mayúsculas → matriz § extensión
├─ El Content-Type           → cambiar el header a image/png en la request → matriz § MIME
├─ Los magic bytes           → prepender GIF89a; / polyglot → matriz § magic bytes
├─ Nada, pero no ejecuta     → ¿dónde cayó? ver árbol de ejecución
└─ Se sube pero no la encuentro → path traversal en el nombre para elegir dónde cae
```

## Árbol de decisión — se subió pero ¿ejecuta?

```
¿El archivo subido ejecuta?
├─ Sí, cae en el webroot y corre        → RCE directo → [[Webshell]]
├─ Cae en el webroot pero no ejecuta    → .htaccess para mapear la extensión / otra ext
└─ Cae fuera del webroot                → incluirlo con [[LFI - inclusión local]]  ← el combo
```

## Cheatsheets — entrada directa a los payloads

| Matriz | Cubre |
|---|---|
| [[File upload bypass - matriz de referencia]] | Evasión de extensión, MIME, magic bytes, doble extensión, `.htaccess` |
| [[Webshells - matriz de referencia]] | Webshells mínimas por lenguaje, polyglots, one-liners de reverse shell |

## Orden de aprendizaje

1. [[CWE-434 - Unrestricted File Upload]] — qué es y por qué validar bien es difícil
2. [[File upload - bypass de validación]] — evadir cada capa
3. [[File upload bypass - matriz de referencia]] — la sintaxis de cada bypass
4. [[Webshell]] → [[Webshells - matriz de referencia]] — el payload
5. El combo cuando no ejecuta: [[File upload + LFI]]

## Cara azul

| Qué | Telemetría | Firma |
|---|---|---|
| Subida maliciosa | [[Log de acceso del servidor web]] | `POST` multipart con extensión ejecutable o doble extensión |
| Ejecución de la webshell | [[Log de acceso del servidor web]] | `GET` al archivo subido con parámetro de comando; hijo de proceso del web server |

## Huecos conocidos

- [ ] Bypass + webshell + combo — en construcción
- [ ] SVG-XSS y XXE vía archivo (DOCX/SVG) como impacto propio
- [ ] Sobrescritura de archivos por path traversal en el nombre
