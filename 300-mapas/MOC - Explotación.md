---
tipo: moc
dominio: fase
aliases:
  - MOC explotación
  - Explotación
tags:
  - fase
---

# MOC - Explotación

> [!abstract] Fase del engagement
> Conseguir ejecución o acceso no autorizado, una vez mapeada la superficie en [[MOC - Reconocimiento]]. Enruta **por superficie** a los mapas de dominio, que siguen existiendo como vista propia. Lo que sigue a la ejecución, en [[MOC - Post-explotación]].

Esta fase no tiene técnica propia: es el **triage por superficie**. El nodo raíz es qué tenés delante; a partir de ahí se entra al mapa del dominio, que ordena internamente por su propio eje (web por mecanismo, AD por lo que tenés).

## Adónde enruta

| Cuándo | Va a | Qué trae |
|---|---|---|
| Aplicación web | [[MOC - Explotación web]] | las seis familias por mecanismo |
| AD — sin credencial (solo red) | [[MOC - AD envenenamiento y relay]] · [[MOC - AD roasting]] | primer hash: relay/poisoning; AS-REP roasting |
| AD — con una credencial de dominio | [[MOC - AD roasting]] · [[MOC - ADCS]] | Kerberoasting; PKI mal configurada |
| AD — la cadena completa, contada entera | [[MOC - Active Directory]] | el hub |

La enumeración de AD **no** vive acá: es reconocimiento ([[MOC - AD enumeración]]). Acá va lo que se hace con lo que encontró: romper, relayar, abusar la PKI. Un dominio aparece en varias fases (es una vista): AD figura también en [[MOC - Reconocimiento]], [[MOC - Post-explotación]], [[MOC - Movimiento lateral]] y [[MOC - Persistencia]].

## Relación con otras fases

- **Antes:** [[MOC - Reconocimiento]] mapea la superficie; [[MOC - Pre-explotación]] deja listo el arsenal (shell/payload) que esta fase entrega.
- **Después:** [[MOC - Post-explotación]] — con ejecución en mano; de ahí a [[MOC - Movimiento lateral]] y [[MOC - Persistencia]].

## Huecos conocidos

- [x] Enruta las dos superficies con contenido: web (hub por mecanismo) y AD (acceso/escalada).
- [ ] **Acceso inicial del lado cliente** — macros de Office, archivos LNK/iCal/JScript maliciosos, DLL hijacking por archivo. Es la rama "client-side" del ejemplo; sin dominio propio.
- [ ] **Explotación de servicios** — SSH, MSSQL (`xp_cmdshell`), RDP como vía de ejecución. Hoy vive dentro de cada matriz de [[MOC - Servicios de red]]; podría agruparse acá como rama propia.
- [ ] Otras superficies sin abrir (cloud, móvil, Wi-Fi): entran acá cuando existan como dominio.
