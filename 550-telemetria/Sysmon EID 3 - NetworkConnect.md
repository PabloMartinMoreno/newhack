---
tipo: telemetria
plataforma: [windows]
producto: Sysmon
identificador: "EID 3"
por-defecto: false
coste: alto
aliases:
  - conexión de red Sysmon
  - NetworkConnect
tags:
  - plataforma/windows
---

# Sysmon EID 3 - NetworkConnect

## Qué lo genera

Cada conexión TCP o UDP que un proceso inicia.

Lo que lo distingue de cualquier fuente de red es un solo campo: **el proceso que la abrió**. Netflow y los registros de firewall dan origen, destino y puerto; ninguno dice quién. Y sin eso, una conexión al 443 de una IP externa es indistinguible entre un navegador y una baliza de mando y control.

Es el equivalente de [[Conexión saliente del servidor de aplicación]] en el mundo de endpoint.

## Campos relevantes

| Campo | Qué trae | Para qué sirve |
|---|---|---|
| `Image` | Proceso que conecta | **El campo que justifica la fuente** |
| `ProcessGuid` | Identificador del proceso | Une con [[Sysmon EID 1 - ProcessCreate]] |
| `DestinationIp` / `Port` | A dónde | El destino |
| `DestinationHostname` | Nombre, si resolvió | Más legible que la IP |
| `SourceIp` / `Port` | Desde dónde | Puerto de origen |
| `Protocol` | TCP o UDP | — |
| `User` | Contexto | Un proceso de sistema conectando como usuario es raro |
| `Initiated` | Si la abrió este equipo | Distingue saliente de entrante |

## Coste de recolección

Muy alto, el mayor de los artefactos de Sysmon junto con la carga de módulos. Un equipo de escritorio abre miles de conexiones por hora, casi todas del navegador y de actualizaciones.

Se domina filtrando **por proceso** en la configuración: excluir navegadores y actualizadores baja el volumen un orden de magnitud, y lo que queda es lo interesante. Filtrar por destino, en cambio, es un error — las direcciones cambian y las exclusiones envejecen mal.

## Cómo se activa

Con la sección correspondiente en la configuración de Sysmon. Suele venir desactivada en las plantillas justamente por volumen, y encenderla es una decisión consciente.

## Limitaciones

- **No ve el contenido.** Sabe que hubo conexión, no qué se transmitió.
- **Conexiones de vida muy corta pueden perderse**, según cómo esté configurado.
- **No cubre tráfico que no pasa por la pila de red del host** — máquinas virtuales con red propia, túneles ya establecidos.
- **El destino puede ser legítimo y el uso no.** Mando y control sobre servicios de nube conocidos usa dominios que están en toda lista blanca.
- **Sin correlación con la creación del proceso, el contexto es pobre.** El campo de identificador de proceso es lo que lo arregla, y solo si el SIEM une por él.

## Quién lo emite / quién lo consume

Rojo: pendiente — ver [[MOC - Telemetría de Windows]]
Azul: pendiente
