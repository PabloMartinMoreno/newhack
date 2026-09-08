#!/usr/bin/env python3
"""Consultas cruzadas rojo/azul del vault NewHack, sobre el frontmatter.

Reemplaza a Dataview. Indexa solo los enlaces declarados en el frontmatter
(telemetria, clase, tecnicas, alternativas): son relaciones afirmadas, no
menciones de paso en el cuerpo.

Uso:
    consultas.py <comando> [--vault RUTA] [--meses N]

Comandos:
    revalidacion     tradecraft sin probar hace más de N meses (default 6)
    huecos           telemetría que emite tradecraft y no consume detección
    sin-probar       detecciones que ninguna variante de tradecraft dispara
    contradicciones  tradecraft 'limpio' con detección propia en producción
    spof             telemetría ordenada por detecciones que dependen de ella
    cobertura        técnicas y cuántas caras tiene cada una
    higiene          frontmatter, enlaces rotos, alias duplicados, MOC sin indexar, inbox
    indice [término] nombre, tipo y aliases de cada nota; filtra por nombre o alias
    todo             todas las anteriores menos indice

`higiene` sale con código distinto de cero si encuentra algo que rompe el índice,
para que sirva de pre-commit y de CI. No cuentan como error los enlaces rotos en
`alternativas:` (roadmap declarado) ni el inbox estancado (recordatorio).
"""

import os
import re
import sys
import datetime

try:
    import yaml
except ImportError:
    sys.exit("falta pyyaml — instalar con: pacman -S python-yaml")

FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.S)
WIKILINK = re.compile(r"\[\[([^\]|#^]+)")
EXCLUIDAS = ("999-plantillas", ".obsidian", ".git")

LISTAR_NUNCA = False
FILTRO = ""

ENUMS = {
    "opsec": {"limpio", "ruidoso", "requiere-bypass", "quemado"},
    "estado": {"idea", "borrador", "produccion", "retirada"},
    "coste": {"bajo", "medio", "alto"},
    "severidad": {"critica", "alta", "media", "baja", "informativa"},
    "fidelidad": {"alta", "media", "baja"},
    "forma": {"evento", "correlacion", "agregado", "invariante"},
}


class Nota:
    def __init__(self, ruta, raiz):
        self.ruta = ruta
        self.rel = os.path.relpath(ruta, raiz)
        self.nombre = os.path.basename(ruta)[:-3]
        self.fm = {}
        self.error = None
        self.enlaces = []
        self.entrantes = []

        texto = open(ruta, encoding="utf-8").read()
        m = FRONTMATTER.match(texto)
        if not m:
            self.error = "sin frontmatter"
            return
        try:
            self.fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            self.error = f"YAML inválido: {str(e).splitlines()[0]}"
            return
        for campo, valor in self.fm.items():
            for crudo in (valor if isinstance(valor, list) else [valor]):
                if not isinstance(crudo, str):
                    continue
                for t in WIKILINK.findall(crudo):
                    if t.strip():
                        self.enlaces.append((campo, t.strip()))

    @property
    def tipo(self):
        return self.fm.get("tipo")

    @property
    def aliases(self):
        return [str(a) for a in (self.fm.get("aliases") or []) if a]

    def get(self, campo, default=""):
        v = self.fm.get(campo)
        return default if v is None else v

    def fecha(self, campo):
        v = self.fm.get(campo)
        if isinstance(v, datetime.datetime):
            return v.date()
        if isinstance(v, datetime.date):
            return v
        if isinstance(v, str) and v.strip():
            try:
                return datetime.date.fromisoformat(v.strip())
            except ValueError:
                return None
        return None

    def entrantes_de(self, tipo):
        return [n for n in self.entrantes if n.tipo == tipo]


class Vault:
    def __init__(self, raiz):
        self.raiz = os.path.abspath(raiz)
        self.notas = []
        self.rotos = []
        self._cargar()
        self._indexar()

    def _cargar(self):
        for root, dirs, archivos in os.walk(self.raiz):
            dirs[:] = [d for d in dirs if d not in EXCLUIDAS and not d.startswith(".")]
            if any(x in root for x in EXCLUIDAS):
                continue
            for f in sorted(archivos):
                if f.endswith(".md") and f not in ("CLAUDE.md", "README.md"):
                    self.notas.append(Nota(os.path.join(root, f), self.raiz))

    def _indexar(self):
        indice = {}
        for n in self.notas:
            indice[n.nombre.lower()] = n
        for n in self.notas:
            for a in n.aliases:
                indice.setdefault(a.lower(), n)
        for n in self.notas:
            for campo, destino in n.enlaces:
                d = indice.get(destino.lower())
                if d is None:
                    self.rotos.append((n, campo, destino))
                elif d is not n:
                    d.entrantes.append(n)
        self.indice = indice

    def por_tipo(self, tipo):
        return [n for n in self.notas if n.tipo == tipo]

    def enlazadas(self, nota, campo):
        v = nota.fm.get(campo)
        crudos = v if isinstance(v, list) else [v]
        salida = []
        for c in crudos:
            if not isinstance(c, str):
                continue
            m = WIKILINK.search(c)
            if m:
                d = self.indice.get(m.group(1).strip().lower())
                if d:
                    salida.append(d)
        return salida


def tabla(cabeceras, filas, vacio="sin resultados"):
    if not filas:
        print(f"  {vacio}\n")
        return
    filas = [[str(c) for c in f] for f in filas]
    anchos = [max(len(cab), *(len(f[i]) for f in filas)) for i, cab in enumerate(cabeceras)]
    print("  " + "  ".join(c.ljust(anchos[i]) for i, c in enumerate(cabeceras)))
    print("  " + "  ".join("-" * a for a in anchos))
    for f in filas:
        print("  " + "  ".join(f[i].ljust(anchos[i]) for i in range(len(cabeceras))))
    print()


def titulo(txt, subtitulo=""):
    print(f"\n\033[1m{txt}\033[0m")
    if subtitulo:
        print(f"\033[2m{subtitulo}\033[0m")


def lista(v):
    if isinstance(v, list):
        return ", ".join(str(x) for x in v) if v else "—"
    return str(v) if v else "—"


def revalidacion(vault, meses):
    titulo(
        f"1. Backlog de revalidación (> {meses} meses)",
        "El conocimiento rojo caduca. Esto es trabajo de laboratorio, no lectura.",
    )
    corte = datetime.date.today() - datetime.timedelta(days=meses * 30)
    filas = []
    nunca = []
    for n in vault.por_tipo("tradecraft"):
        p = n.fecha("probado")
        if p is None:
            nunca.append((n.nombre, n.get("opsec", "—"), "NUNCA", "—", lista(n.get("contexto"))))
        elif p < corte:
            dias = (datetime.date.today() - p).days
            filas.append((n.nombre, n.get("opsec", "—"), p.isoformat(), dias, lista(n.get("contexto"))))
    filas.sort(key=lambda f: f[2])

    # Las nunca probadas se resumen en vez de listarse: son la mayoría del vault
    # mientras no haya laboratorio, y a 60 filas la consulta deja de leerse.
    if nunca and not LISTAR_NUNCA:
        print(f"  {len(nunca)} variantes nunca probadas — verlas con: consultas.py revalidacion --nunca\n")
    elif nunca:
        filas = nunca + filas

    tabla(["Variante", "OPSEC", "Probado", "Días", "Contexto"], filas,
          "sin backlog por fecha" if nunca else "todo el tradecraft está vigente")


def huecos(vault, _):
    titulo(
        "2. Huecos defensivos propios",
        "Artefactos que tu tradecraft emite y ninguna detección tuya consume.",
    )
    filas = []
    for n in vault.por_tipo("telemetria"):
        rojo = n.entrantes_de("tradecraft")
        if rojo and not n.entrantes_de("deteccion"):
            filas.append((n.nombre, len(rojo), ", ".join(x.nombre for x in rojo)))
    filas.sort(key=lambda f: -f[1])
    tabla(["Artefacto", "Emisores", "Variantes que lo emiten"], filas, "sin huecos")


def sin_probar(vault, _):
    titulo(
        "3. Detecciones nunca puestas a prueba",
        "Sobre el papel funcionan; ninguna variante de tradecraft las disparó.",
    )
    filas = []
    for n in vault.por_tipo("deteccion"):
        fuentes = vault.enlazadas(n, "telemetria")
        if not fuentes:
            filas.append((n.nombre, n.get("estado", "—"), "sin telemetría declarada"))
        elif not any(f.entrantes_de("tradecraft") for f in fuentes):
            filas.append((n.nombre, n.get("estado", "—"), ", ".join(f.nombre for f in fuentes)))
    tabla(["Detección", "Estado", "Telemetría que consume"], filas, "todas fueron atacadas")


def contradicciones(vault, _):
    titulo(
        "4. Contradicciones",
        "Tradecraft 'limpio' cuya huella dispara una detección propia en producción.",
    )
    filas = []
    for n in vault.por_tipo("tradecraft"):
        if n.get("opsec") != "limpio":
            continue
        for t in vault.enlazadas(n, "telemetria"):
            for d in t.entrantes_de("deteccion"):
                if d.get("estado") == "produccion":
                    filas.append((n.nombre, t.nombre, d.nombre))
    tabla(["Tradecraft limpio", "Artefacto", "Detección en producción"], filas,
          "sin contradicciones — o está mal una etiqueta o está mal una regla")


def spof(vault, _):
    titulo(
        "5. Puntos únicos de fallo",
        "Si el cliente no recolecta esto, sabés qué se apaga — y qué se te habilita.",
    )
    filas = []
    for n in vault.por_tipo("telemetria"):
        filas.append((
            n.nombre,
            len(n.entrantes_de("deteccion")),
            len(n.entrantes_de("tradecraft")),
            "sí" if n.get("por-defecto") is True else "no",
            n.get("coste", "—"),
        ))
    filas.sort(key=lambda f: (-f[1], -f[2]))
    tabla(["Artefacto", "Detecciones", "Tradecraft", "Por defecto", "Coste"], filas)


def cobertura(vault, _):
    titulo("6. Cobertura por técnica", "Dónde hay taxonomía sin contenido.")
    filas = []
    for n in vault.por_tipo("tecnica"):
        r = len(n.entrantes_de("tradecraft"))
        a = len(n.entrantes_de("deteccion"))
        marca = "—" if r and a else ("solo rojo" if r else ("solo azul" if a else "VACÍA"))
        filas.append((n.nombre, r, a, marca))
    filas.sort(key=lambda f: (f[1] + f[2], f[0]))
    tabla(["Técnica", "Tradecraft", "Detecciones", "Estado"], filas)


def fecha_o_nunca(nota, campo):
    """`probado`/`validada` sin fecha son 'nunca'. Una fecha mal escrita cae en
    ese mismo hueco y pasa desapercibida: acá se separa el vacío del typo."""
    v = nota.fm.get(campo)
    if not v or str(v) == "nunca":
        return []
    f = nota.fecha(campo)
    if f is None:
        return [(nota.rel, f"{campo}={v} — debe ser fecha ISO o 'nunca'")]
    if f > datetime.date.today():
        return [(nota.rel, f"{campo}={f.isoformat()} está en el futuro")]
    return []


def indice(vault, _):
    titulo(
        "8. Índice de nombres y aliases",
        "Con qué palabras se llega a cada nota. El quick switch de nvim solo ve la columna Nota.",
    )
    filas = []
    for n in sorted(vault.notas, key=lambda x: x.rel):
        if FILTRO:
            campos = [n.nombre] + n.aliases
            if not any(FILTRO in c.lower() for c in campos):
                continue
        filas.append((n.nombre, n.tipo or "—", " · ".join(n.aliases) or "—"))
    vacio = f"nada coincide con «{FILTRO}»" if FILTRO else "vault vacío"
    tabla(["Nota", "Tipo", "Aliases"], filas, vacio)
    print(f"  {len(filas)} nota(s)\n")


def higiene(vault, _):
    titulo("7. Higiene", "Frontmatter inválido, enlaces rotos, inbox estancado.")

    filas = []
    for n in vault.notas:
        if n.error:
            filas.append((n.rel, n.error))
            continue
        if not n.tipo:
            filas.append((n.rel, "falta tipo"))
        for campo, validos in ENUMS.items():
            v = n.fm.get(campo)
            if v not in (None, "") and str(v) not in validos:
                filas.append((n.rel, f"{campo}={v} fuera de enum"))
        if n.tipo == "tradecraft":
            for campo in ("opsec", "probado", "contexto"):
                if not n.fm.get(campo):
                    filas.append((n.rel, f"tradecraft sin {campo}"))
            if not n.fm.get("telemetria"):
                filas.append((n.rel, "tradecraft sin telemetria — regla 3, la bisagra"))
            filas += fecha_o_nunca(n, "probado")
        if n.tipo == "teoria" and not n.fm.get("habilita"):
            filas.append((n.rel, "teoria sin habilita — huérfana, es un apunte"))
        if n.tipo == "deteccion":
            filas += fecha_o_nunca(n, "validada")
            forma = n.fm.get("forma")
            if not forma:
                filas.append((n.rel, "deteccion sin forma"))
            elif forma in ("agregado", "invariante") and not n.fm.get("ventana"):
                filas.append((n.rel, f"forma={forma} sin ventana"))
    tabla(["Nota", "Problema"], filas, "frontmatter limpio")

    rompen = [(n.rel, campo, d) for n, campo, d in vault.rotos if campo != "alternativas"]
    roadmap = [(n.rel, d) for n, campo, d in vault.rotos if campo == "alternativas"]

    print("  Enlaces rotos en frontmatter (rompen el índice en silencio):")
    tabla(["Origen", "Campo", "Destino inexistente"], rompen, "ninguno")

    print("  Roadmap en alternativas: (notas todavía no escritas, no es error):")
    tabla(["Origen", "Destino pendiente"], roadmap, "ninguno")

    dueños = {}
    for n in vault.notas:
        for a in n.aliases:
            dueños.setdefault(a.lower(), []).append(n.nombre)
    nombres = {n.nombre.lower() for n in vault.notas}
    choques = []
    for alias, notas in sorted(dueños.items()):
        if len(notas) > 1:
            choques.append((alias, " · ".join(notas)))
        elif alias in nombres and notas[0].lower() != alias:
            choques.append((alias, f"{notas[0]} · choca con la nota homónima"))
    print("  Alias en más de una nota (Obsidian resuelve al azar):")
    tabla(["Alias", "Notas que lo declaran"], choques, "un alias, una dueña")

    try:
        with open(os.path.join(vault.raiz, "Inicio.md"), encoding="utf-8") as f:
            inicio = f.read()
    except OSError:
        inicio = ""
    sin_indexar = [(n.nombre, n.fm.get("dominio", "—"))
                   for n in vault.notas
                   if n.tipo == "moc" and f"[[{n.nombre}]]" not in inicio]
    print("  MOC no indexados en Inicio.md:")
    tabla(["MOC", "Dominio"], sin_indexar, "todos los dominios indexados")

    corte = datetime.date.today() - datetime.timedelta(days=14)
    viejas = []
    for n in vault.notas:
        if not n.rel.startswith("000-inbox"):
            continue
        mtime = datetime.date.fromtimestamp(os.path.getmtime(n.ruta))
        if mtime < corte:
            viejas.append((n.nombre, mtime.isoformat()))
    print("  Inbox estancado (> 14 días):")
    tabla(["Nota", "Modificada"], viejas, "inbox al día")

    return len(filas) + len(rompen) + len(choques) + len(sin_indexar)


COMANDOS = {
    "revalidacion": revalidacion,
    "huecos": huecos,
    "sin-probar": sin_probar,
    "contradicciones": contradicciones,
    "spof": spof,
    "cobertura": cobertura,
    "higiene": higiene,
    "indice": indice,
}

# `todo` es el barrido de salud del vault; el índice es una consulta de búsqueda
# y listar 448 notas ahí adentro tapa el resto.
FUERA_DE_TODO = {"indice"}


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    comando = args[0]

    # Lo usa el atajo de nvim para armar el menú sin hardcodear los comandos.
    if comando == "--ayuda-comandos":
        print("todo")
        for nombre in COMANDOS:
            print(nombre)
        return 0

    vault_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    meses = 6
    global LISTAR_NUNCA, FILTRO
    saltar = set()
    for i, a in enumerate(args):
        if a == "--vault" and i + 1 < len(args):
            vault_dir = args[i + 1]
            saltar.add(i + 1)
        if a == "--meses" and i + 1 < len(args):
            meses = int(args[i + 1])
            saltar.add(i + 1)
        if a == "--nunca":
            LISTAR_NUNCA = True
    FILTRO = next(
        (a.lower() for i, a in enumerate(args[1:], 1) if not a.startswith("-") and i not in saltar),
        "",
    )

    if comando not in COMANDOS and comando != "todo":
        print(f"comando desconocido: {comando}\n")
        print(__doc__)
        return 1

    vault = Vault(vault_dir)
    print(f"\033[2mvault: {vault.raiz} — {len(vault.notas)} notas\033[0m")

    problemas = 0
    if comando == "todo":
        elegidas = [fn for nombre, fn in COMANDOS.items() if nombre not in FUERA_DE_TODO]
    else:
        elegidas = [COMANDOS[comando]]
    for fn in elegidas:
        problemas += fn(vault, meses) or 0
    if problemas:
        print(f"\033[1m{problemas} problema(s) de higiene — el índice está roto\033[0m")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
