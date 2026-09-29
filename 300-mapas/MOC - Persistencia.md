---
tipo: moc
dominio: fase
aliases:
  - MOC persistencia
  - Persistencia
tags:
  - fase
---

# MOC - Persistencia

> [!abstract] Fase del engagement
> Volver a entrar después de que roten credenciales o cierren el incidente. Cierra la cadena que abre [[MOC - Explotación]] y sigue a [[MOC - Movimiento lateral]]. Enruta **por qué tan profundo** sobrevive el acceso.

> [!note] Hoy es casi todo Active Directory
> La persistencia con contenido vive en AD: forjar identidad, atributos que no aparecen en las membresías, certificados de larga vida. Esta fase enruta hacia esos MOCs; el detalle vive en ellos.

## Adónde enruta

```
¿Qué tan profundo quiero sobrevivir?
├─ Forjar identidad con el secreto del dominio
│  └─ [[MOC - AD persistencia]]   ← golden ticket, SID history
├─ Un acceso que sobrevive al cambio de contraseña
│  └─ [[MOC - ADCS]]   ← certificado de larga vida (no se invalida rotando credenciales)
└─ Cruzar el límite de confianza
   └─ [[MOC - AD confianzas]]   ← del dominio a la raíz del bosque, y entre bosques
```

El certificado es la peor persistencia porque no se invalida cambiando la contraseña: vale por años y sobrevive a la respuesta a incidentes que rota credenciales y cierra el caso. La cadena de AD entera, en [[MOC - Active Directory]].

## Relación con otras fases

- **Antes:** [[MOC - Movimiento lateral]] — se persiste una vez alcanzado el activo que vale.
- La persistencia de aplicación (un webshell en disco) es un artefacto de [[MOC - Shells]], no de esta fase — se decide en [[MOC - Post-explotación]].

## Huecos conocidos

- [x] Enruta la persistencia de AD: golden/SID history, certificado, confianzas.
- [ ] Persistencia no-AD (cron/servicios/claves SSH en Linux, Run keys/tareas en Windows) sin dominio propio — hoy solo mencionada en la matriz de impacto de command injection, con el aviso de que está fuera de alcance salvo autorización.
