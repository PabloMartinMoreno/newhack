# NewHack — vault Obsidian rojo + azul

Vault zettelkasten único. **No es** el vault `~/hacking/obsidian/Hack/`: modelo distinto e incompatible. No aplicar acá las convenciones de aquel (categorías Primary/Secondary/Tertiary, hubs con tabs, cheatsheets de comandos).

## Fuente de verdad

Antes de crear o modificar notas, leer:

- [900-meta/Estructura del vault.md](900-meta/Estructura del vault.md) — carpetas, regla de filtro, anti-patrones
- [900-meta/Esquema de frontmatter.md](900-meta/Esquema de frontmatter.md) — propiedades canónicas por tipo
- [900-meta/Convenciones de nombres.md](900-meta/Convenciones de nombres.md)

Si algo de este archivo contradice esas notas, **ganan esas notas** — se actualiza este archivo, no al revés.

## Skills

- `obsidian-markdown` — **siempre**, antes de escribir cualquier `.md` de este vault.
- `vault-newhack` — flujo de creación de notas y consultas del vault.
- `superpowers:brainstorming` — antes de modelar un dominio nuevo (taxonomía de ejes, MOC nuevo). El retrabajo por taxonomía mal fijada es garantizado.
- `context7` — al documentar APIs/herramientas externas.

## No negociable

1. **Regla de filtro.** Si la nota no responde *"cuándo elijo esto en vez de la alternativa"*, es un payload. No va al vault: va a una matriz en `900-meta/` o a un repo.
2. **Una nota por eje, no por combinación.** Las técnicas grandes son intersecciones de ejes ortogonales.
3. **`telemetria:`** es el mismo campo en tradecraft y en detecciones. Es la bisagra operativa; sin ella la fusión es nominal.
4. **`opsec:`, `probado:`, `contexto:`** en toda nota de tradecraft. El conocimiento rojo caduca; sin esos campos el vault miente.
5. **`visibilidad:`** en toda nota, desde la primera.
6. **Cero datos de cliente.** Hostnames, IPs, credenciales y evidencia van al vault de engagements, aparte y cifrado.
7. **Nada organizado por herramienta.** La herramienta es una entidad en `400-entidades/`, nunca una carpeta.
8. **Idioma — la regla del corpus externo.** Si el término aparece literal en una fuente externa (ATT&CK, CWE, WSTG, docs de vendor, Sigma), el nombre va en **inglés**; si lo escribiste vos, en **español**. `500-tecnicas/` usa el nombre oficial en inglés sin excepción. El término del otro idioma va siempre como alias.
9. **Los MOCs son árboles de decisión**, no listas de enlaces. Se escriben ordenados por dependencia conceptual porque también son temario de clase.

## Al crear notas

Plantillas en `999-plantillas/`. El cuerpo de tradecraft tiene cuatro secciones fijas — **Cuándo lo elijo · Por qué funciona · Cómo falla · Coste** — y ninguna lleva sintaxis.

Enlaces por wikilink siempre; referencias a bloques por `^block-id`, nunca por `#Heading`.

Registrar decisiones de estructura en [900-meta/Avances.md](900-meta/Avances.md). Cambios de contenido, no.
