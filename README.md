# Práctica Formativa Integradora: Consolidación de Almacenamiento, Integridad del Dato y Toma de Contacto con HDFS

**Autor:** Antonio César Gavira Piñero

---

## Sección 1: Integridad y Control de Calidad del Dato (Módulo 5075)

Antes de realizar la ingesta distribuida, se verificó la firma criptográfica del dataset en bruto `telemetria_envios.csv` y se depuraron las incoherencias detectadas.

### Registro Comparativo de Hashes SHA-256

| Estado del Dataset | Archivo | Algoritmo | Hash SHA-256 Resumen |
| :--- | :--- | :--- | :--- |
| **Original (Raw)** | `telemetria_envios.csv` | SHA-256 | `317f5047ddc0407b36fe4b8af54b919e5a2f815555c5c1b0c176cff4e0df0181` |
| **Saneado (Clean)** | `telemetria_limpia.csv` | SHA-256 | `7CFE63DF86D8D231E4BAE22CB700BC062D563E23B1307E056F9471BD956792EB ` |

### Tratamiento de Anomalías
Se depuraron 8 registros que no cumplían las reglas de calidad en origen:
1. **Registros Duplicados:** 2 filas identicas removidas mediante `drop_duplicates()`.
2. **Valores Nulos:** 3 filas descartadas por carecer de campos indispensables (`temp_celsius`, `peso_kg`, `destino`).
3. **Incongruencias y Valores Fuera de Rango:** 
   - 1 registro con peso negativo (`peso_kg = -45.50 kg`).
   - 1 registro con temperatura errónea fuera de la cadena de frío (`temp_celsius = 98.4 °C`).
   - 1 registro con estado de envío corrupto (`DESCONOCIDO_ERROR`).

---

## Sección 2: Despliegue y Operativa HDFS (Módulo 5074)

Se desplegó un entorno monocontenedor Apache Hadoop 3.4.0 mediante Docker Compose.

### Puertos Mapeados y Servicios
* `http://localhost:9872`: Interfaz Web del NameNode (HDFS Management & File Browser).
* `http://localhost:8088`: Interfaz Web del YARN ResourceManager.

### Verificación de Procesos (Command `jps`)
Al ejecutar el comando `jps` dentro del contenedor se corroboró la ejecución activa del servicio en modo standalone con los principales daemons en ejecución.

### Comandos de Ingesta Ejecutados
* `hdfs dfs -mkdir -p /empresa/logistica/input`
* `hdfs dfs -put /workspace/telemetria_limpia.csv /empresa/logistica/input/`
* `hdfs dfs -ls /empresa/logistica/input/`
* `hdfs fsck /empresa/logistica/input/telemetria_limpia.csv -files -blocks -locations`

---

## Sección 3: Análisis Crítico sobre la Tolerancia a Fallos en HDFS

El Sistema de Archivos Distribuido de Hadoop (HDFS) garantiza la persistencia, disponibilidad e integridad de los datos en entornos de producción masivos mediante un mecanismo nativo de **división en bloques y replicación redundante**. Cuando un cliente sube un archivo a HDFS, el sistema divide dicho archivo en fragmentos continuos de tamaño fijo (por defecto 128 MB en Hadoop 3.x). Cada uno de estos bloques no se almacena en un único servidor, sino que se distribuye de forma transparente entre múltiples nodos de datos (*DataNodes*) que conforman el clúster empresarial.

La clave de la tolerancia ante fallos de hardware reside en la política de replicación de HDFS (cuyo factor de replicación por defecto es de 3). El máster del clúster (*NameNode*) no guarda datos de usuario, sino únicamente los metadatos (mapa del sistema de ficheros y ubicación exacta de los bloques). El NameNode se encarga de instruir que cada bloque físico sea copiado en al menos tres DataNodes distintos, distribuyéndolos habitualmente entre diferentes cabinas o bastidores (*racks*). Los DataNodes envían constantemente mensajes de latido (*heartbeats*) y reportes de bloques (*block reports*) al NameNode. Si un DataNode sufre una avería, un corte eléctrico o se desconecta de la red, el NameNode detecta la falta de *heartbeat*, declara el nodo en estado inactivo y activa inmediatamente una tarea de autorrecuperación (*re-replication*): consulta en su tabla de metadatos dónde se encuentran las copias supervivientes de los bloques que estaban en el nodo caído y ordena a otro DataNode saludable clonar dichos bloques.

Gracias a esta arquitectura desacoplada y descentralizada en el plano de almacenamiento, los procesos analíticos superiores (como Apache Spark o MapReduce) continúan operando sin interrupción leída desde las réplicas redundantes disponibles. El usuario final o script analítico percibe la estructura del sistema de ficheros como un único espacio de nombres unificado, totalmente inmune a la pérdida física de DataNodes individuales.

---

## Sección 4: Evidencias Gráficas

Las capturas de pantalla de la ejecución se ubican en el directorio `/evidencias`:

1. `evidencias/01_hashes_sha256.png`: Cálculo terminal de huellas SHA-256.
2. `evidencias/02_jps_servicios.png`: Resultado del comando `jps` con los servicios levantados.
3. `evidencias/03_hdfs_comandos_fsck.png`: Salida de la ingesta en HDFS y la auditoría `hdfs fsck`.
4. `evidencias/04_webui_hdfs_browse.png`: Visualización del archivo `telemetria_limpia.csv` en el explorador Web UI (`http://localhost:9872`).