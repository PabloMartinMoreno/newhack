---
tipo: meta
aliases:
  - Hashcat rules
  - reglas de hashcat
  - custom rules hashcat
  - rule functions
tags:
  - meta/referencia
  - dominio/post-explotacion
---

# Hashcat rules - matriz de referencia

> [!info] Referencia pura, no un zettel
> El lenguaje de **reglas** de hashcat: cada regla muta cada palabra de la wordlist en candidatos nuevos. Es el detalle del `-a 0 -r` de [[Cracking offline - matriz de referencia]] § ataques. El dominio, en [[MOC - Ataques de contraseña]].

## Cómo funciona

Un archivo de reglas tiene **una regla por línea**; cada línea es una secuencia de funciones que se aplica, en orden, a **cada palabra** de la wordlist. hashcat corre **todas** las reglas sobre **cada** palabra: candidatos = palabras × reglas. Por eso una wordlist chica + reglas buenas rinde más que una wordlist enorme sin reglas.

```sh
hashcat -m 1000 hash.txt rockyou.txt -r mi.rule
```

## Funciones (sobre la palabra `pass`)

| Función | Qué hace | `pass` → |
|---|---|---|
| `:` | nada (passthrough) | `pass` |
| `l` / `u` | todo minús / MAYÚS | `pass` / `PASS` |
| `c` / `C` | Capitaliza / inversa | `Pass` / `pASS` |
| `t` / `TN` | invertir mayús todo / en posición N | `PASS` / `T0`→`Pass` |
| `r` | reverso | `ssap` |
| `d` / `f` | duplicar / reflejar | `passpass` / `passssap` |
| `{` / `}` | rotar izquierda / derecha | `assp` / `spas` |
| `$X` / `^X` | agregar X al final / al principio | `$1`→`pass1` · `^1`→`1pass` |
| `[` / `]` | borrar primer / último char | `ass` / `pas` |
| `DN` | borrar char en posición N | `D0`→`ass` |
| `sXY` | sustituir todas las X por Y | `sa@`→`p@ss` |
| `@X` | eliminar todas las X | `@s`→`pa` |
| `zN` / `ZN` | duplicar N veces el primer / último char | `z1`→`ppass` |

Las posiciones son `0-9` y después `A-Z` (posición 10 = `A`).

## Reglas completas (varias funciones por línea)

| Objetivo | Regla | `pass` → |
|---|---|---|
| Capitalizar + año | `c $2 $0 $2 $4` | `Pass2024` |
| Leet básico | `sa@ so0 se3` | `p@ss` |
| Sufijo típico | `$! ` | `pass!` |
| Mayús + leet + número | `c sa@ $1` | `P@ss1` |

## Probar la regla sin crackear

Clave para depurar: `--stdout` imprime los candidatos que la regla genera, sin tocar ningún hash.

```sh
hashcat -r mi.rule --stdout wordlist.txt | less
echo 'pass' | hashcat -r mi.rule --stdout
```

## Reglas que ya vienen

En `/usr/share/hashcat/rules/`:

| Archivo | Para qué |
|---|---|
| `best64.rule` | 64 mutaciones de alto rinde; la primera que se prueba |
| `rockyou-30000.rule` | derivada de patrones reales de rockyou |
| `dive.rule` · `OneRuleToRuleThemAll.rule` | exhaustivas, lentas (la segunda es de la comunidad) |
| `leetspeak.rule` · `toggles*.rule` | solo leet / solo cambios de mayúsculas |

Apilar reglas multiplica: `-r a.rule -r b.rule` aplica el **producto cartesiano** de ambas (cuidado con el tiempo).

## Armar reglas a medida

- **De la política del objetivo**: si exige mayúscula inicial + 4 dígitos + símbolo, la regla es `c $2$0$2$4 $!` sobre una wordlist de palabras base.
- **De hashes ya rotos**: mirá el patrón de las que cayeron y escribí reglas que lo repliquen sobre el resto.

Visto en acción, con OSINT + política de contraseñas: [[Cracking dirigido por OSINT - ejemplo]].
- **Aleatorias**: `hashcat --generate-rules 10000 > random.rule` genera reglas al azar (fuerza bruta de reglas).

## Errores / notas

| Síntoma | Causa | Salida |
|---|---|---|
| La regla "no hace nada" | función inválida → hashcat la ignora | `--stdout` para ver qué genera; `--debug-mode=1` muestra la regla que pegó |
| Candidatos duplicados | varias reglas producen lo mismo | normal; no afecta la corrección, sí el tiempo |
| Tardó muchísimo | apilaste reglas (producto cartesiano) | una sola regla, o wordlist más chica |
| Posición > 9 no funciona | se indexa con letras | posición 10 = `A`, 11 = `B`, … |
