---
tipo: meta
aliases:
  - Rutas web sensibles - matriz
  - well-known files - matriz
  - rutas web a revisar
tags:
  - meta/referencia
  - dominio/red
---

# Rutas web sensibles - matriz de referencia

> [!info] Referencia pura, no un zettel
> Rutas y archivos que conviene pedir **a mano** en todo objetivo web: filtran estructura, config, secretos y paneles sin necesidad de fuzzear. Complementa el [[Crawling web - matriz de referencia]] (que sigue enlaces) y el content discovery (que brute-ea rutas). `HOST` es el objetivo.

## Descubrimiento estándar

| Ruta | Qué da |
|---|---|
| `/robots.txt` | Rutas que pidieron **no** indexar — apuntan a lo que quieren esconder |
| `/sitemap.xml` | Mapa de URLs del sitio |
| `/humans.txt` · `/crossdomain.xml` · `/clientaccesspolicy.xml` | Info de la app y políticas cross-domain (a veces `*` = laxo) |
| `/.well-known/security.txt` | Contacto de seguridad (y a veces infra) |
| `/.well-known/openid-configuration` | Endpoints OIDC → [[OAuth - matriz de reconocimiento]] |
| `/.well-known/jwks.json` | Claves públicas JWT → [[JWT - matriz de referencia]] |

## Config y secretos expuestos

| Ruta | Qué da |
|---|---|
| `/.git/` | Repo expuesto → reconstruir el código con `git-dumper http://HOST/.git out/` |
| `/.env` | Variables de entorno: credenciales, claves de API |
| `/.svn/` · `/.hg/` · `/.DS_Store` | Metadatos de control de versiones / listados de directorio |
| Backups: `index.php.bak`, `config.php~`, `.old`, `site.zip`, `backup.tar.gz` | Código o config en claro |
| `/wp-config.php.bak` · `/web.config` · `/.htaccess` | Config del server / de la app |

## Estado y diagnóstico

| Ruta | Qué da |
|---|---|
| `/server-status` · `/server-info` (Apache) | Peticiones en vivo, módulos, rutas internas |
| `/nginx_status` | Estado de nginx |
| `/phpinfo.php` · `/info.php` | Toda la config de PHP y del entorno |
| `/metrics` (Prometheus) | Métricas, a veces con datos internos |
| `/actuator` (Spring Boot) | `/actuator/env`, `/actuator/health`, `/actuator/heapdump` (¡memoria!) |

## Paneles y admin

| Ruta | Qué es |
|---|---|
| `/admin` · `/administrator` · `/wp-admin` | Paneles de administración |
| `/manager/html` (Tomcat) | Manager → deploy de WAR = RCE |
| `/phpmyadmin` · `/adminer.php` | Gestión de base de datos |
| `/console` · `/_console` | Consolas de framework (a veces con REPL) |

## API y documentación

| Ruta | Qué da |
|---|---|
| `/api` · `/api/v1` | Base de la API |
| `/swagger-ui` · `/swagger.json` · `/openapi.json` · `/api-docs` | Especificación completa de la API — todos los endpoints |
| `/graphql` · `/graphiql` | Endpoint GraphQL → [[MOC - GraphQL]] |

## Barrido rápido

Wordlists de SecLists que juntan muchas de estas: `Discovery/Web-Content/common.txt`, `raft-*-files.txt`, `quickhits.txt`. Pasarlas con content discovery (`feroxbuster`/`ffuf` dir) cubre el resto.

## Errores / notas

| Punto | Detalle |
|---|---|
| `/.git/` sin listado | igual sirve: `git-dumper` reconstruye desde `/.git/HEAD` y objetos |
| `200` en todo | catch-all que responde siempre — mirar el contenido, no el código |
| paneles detrás de WAF | probar variantes de ruta y método; ver [[Fingerprinting - matriz de referencia]] |
