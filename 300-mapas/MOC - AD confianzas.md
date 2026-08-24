---
tipo: moc
dominio: ad
aliases:
  - MOC AD confianzas
tags:
  - dominio/ad
---

# MOC - AD confianzas

> [!abstract] Fase de la kill chain de AD
> El límite de seguridad es el **bosque**, no el dominio. Hub: [[MOC - Active Directory]]. Cheatsheet: [[AD confianzas - matriz de referencia]]. Clase: [[T1134.005 - SID-History Injection]].

Con un dominio comprometido, la confianza se convierte en la vía al resto. Se elige por **hacia dónde** va la relación: a la raíz del propio bosque, o a otro bosque.

## Árbol de decisión

```
Tengo admin de un dominio (su hash de krbtgt). ¿Hacia dónde escalo?
├─ El dominio NO es la raíz del bosque
│  └─ inyecto el SID de Enterprise Admins de la raíz en un ticket forjado  → [[Escalada intra-bosque por SID History]]
│     └─ el filtrado de SID está deshabilitado dentro del bosque por defecto
└─ Hay una confianza hacia OTRO bosque
   └─ forjo un TGT inter-reino con la clave de confianza  → [[Movimiento entre bosques por la clave de confianza]]
      └─ acá el filtrado de SID SÍ está activo por defecto → no sirve inyectar SIDs privilegiados
```

El principio que este MOC fija: **no hace falta comprometer la raíz del bosque**, alcanza con el dominio más débil y el salto por SID History. Un bosque con un dominio de laboratorio mal protegido es un bosque comprometido. La diferencia intra/inter bosque es el filtrado de SID: apagado adentro, encendido afuera.

## Orden de aprendizaje

1. [[Escalada intra-bosque por SID History]] — hijo → raíz del bosque, sin filtrado de SID
2. [[Movimiento entre bosques por la clave de confianza]] — TGT inter-reino, con filtrado activo

## Cara roja

- [[Escalada intra-bosque por SID History]] · [[Movimiento entre bosques por la clave de confianza]]
- Comandos: [[AD confianzas - matriz de referencia]] — enumerar confianzas, SID History a la raíz del bosque, clave de confianza inter-reino, filtrado de SID.

## Cara azul

| Técnica | Emite | Detección |
|---|---|---|
| [[Escalada intra-bosque por SID History]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | en parte, la de golden |
| [[Movimiento entre bosques por la clave de confianza]] | [[Windows 4769 - Kerberos service ticket requested\|4769]] | sin detección propia |

La escalada por ticket **no toca el directorio**: mete el SID en el PAC de un ticket forjado, así que no deja firma de escritura. La de golden lo ve como un golden cualquiera. La señal de mayor retorno contra el SID History sigue siendo auditar el atributo en reposo — que es lo que detecta la **persistencia**, en [[MOC - AD persistencia]], no la escalada momentánea.

## Huecos conocidos

- [x] Las dos direcciones (intra-bosque e inter-bosque), con el principio "el límite es el bosque"
- [ ] **Escalada por ticket forjado sin firma de escritura por diseño** — no toca el directorio; es un límite de la técnica, no un hueco de contenido
- [ ] Movimiento inter-bosque **sin detección propia** — ticket inter-reino anómalo por dirección o cuenta, necesita línea base
