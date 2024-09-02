### Tópicos Especiales en Telemática: C2466-ST0263-1716

## Estudiantes
- **Isis Catitza Amaya Arbeláez**, [icamayaa@eafit.edu.co](mailto:icamayaa@eafit.edu.co)
- **Santiago Alberto Rozo Silva**, [sarozos@eafit.edu.co](mailto:sarozos@eafit.edu.co)

## Profesor
- **Álvaro Enrique Ospina Sanjuan**, [aeospinas@eafit.edu.co](mailto:aeospinas@eafit.edu.co)

# Reto No 1

## 1. Breve descripción de la actividad
La actividad consiste en diseñar e implementar un sistema P2P (peer-to-peer) que permita la compartición de archivos de manera distribuida y descentralizada. Este sistema debe estar basado en una red P2P estructurada (como Chord/DHT) o no estructurada (con superpeer o pura). Cada nodo o peer en la red actuará como servidor y cliente al mismo tiempo, conteniendo microservicios que manejarán el mantenimiento de la red, la localización de recursos y servicios dummy para la transferencia de archivos.

## 1.1. Aspectos cumplidos o desarrollados
- Diagrama de arquitectura.
- Conexión entre los diferentes peers mediante gRPC usando el algoritmo de Chord.
- Simulación de descarga (download) de archivos.
- Simulación de carga (upload).
- Listado de archivos que posee cada peer.
- Compartir lista de archivos entre peers.
- Simulación de transferencia de archivos entre peers.
- Búsqueda de archivos en la red Chord.
- Despliegue en AWS con Docker.
- Documentación.

## 1.2. Aspectos NO cumplidos o desarrollados
- (Aquí se incluirían los aspectos que no se cumplieron o desarrollaron, si los hay.)

### 2. Información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas
El proyecto se cimenta sobre una red peer-to-peer (P2P) estructurada basada en el algoritmo Chord, que utiliza gRPC para la comunicación entre nodos.

![P2P](https://github.com/user-attachments/assets/48f152bf-87f8-4818-ac21-65429d5d6fdb)

#### 2.1.1. Componentes principales
- **Nodos (Peers):**
  Los nodos o peers son los componentes principales de la red P2P. Cada peer cuenta con un ID único generado mediante hashing consistente (SHA-1), que determina su posición en el anillo de Chord. El servicio Chord maneja las operaciones del protocolo Chord, como la creación y mantenimiento de la finger table (Cada nodo mantiene una finger table que contiene referencias a otros nodos en posiciones específicas del anillo, permitiendo búsquedas eficientes en tiempo logarítmico), unión y salida de nodos, y la estabilización del anillo, todo esto mediante la comunicación de los peers a través de gRPC. Además, se implementaron servicios dummy para simular la carga (upload) y descarga (download) de archivos.

#### 2.1.2. Comunicación con gRPC
- Se definen métodos RPC necesarios para el funcionamiento del algoritmo Chord, tales como `find_successor`, `closest_preceding_node`, `join`, `notify`, `stabilize`, `fix_fingers`, entre otros.
- Se definen métodos RPC como `UploadFile` y `DownloadFile` que simulan la transferencia de archivos entre nodos.

#### 2.1.3. Interacción Entre Nodos
- Se crea la finger table utilizando gRPC. Los nodos se comunican para encontrar sus sucesores y llenar sus finger tables. Por ejemplo, un nodo P1 puede llamar al método `find_successor` de P2 para actualizar su finger table.
- Cuando un nodo necesita simular la transferencia de un archivo, utiliza gRPC para llamar a los servicios `UploadFile` o `DownloadFile` del nodo correspondiente que "posee" el archivo.

#### 2.2. Patrones
- Estructura Modular y Uso de Servicios gRPC.
- Separación de Responsabilidades.
- Uso de Tablas de Hashing (SHA-1).

#### 2.3. Buenas prácticas
- Manejo de Errores.
- Buena Documentación y Comentarios.
- Buena Práctica en la Gestión de Conexiones (Uso de `with` en gRPC).
- Pruebas y Conexiones.
- Buena Gestión de Recursos.
- Feedback al Usuario.

### 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerías, paquetes, etc., con sus números de versiones.

#### 3.1. Cómo se compila y ejecuta
El proyecto cuenta con dos maneras de ejecutarse, tanto una API haciendo uso de Flask, como una ejecución por consola, en este caso se describirá la ejecución por consola de manera local.
Para compilar y ejecutar el proyecto se requiere instalar las siguientes dependencias haciendo uso de sus respectivos comandos:

- **gRPC:**
  ```bash
  pip install grpcio grpcio-tools
  ```
- **Protobuf:**
  ```bash
  pip install protobuf
  ```
- **Tabulate:**
  ```bash
  pip install tabulate
  ```
- **gRPC Health Checking:**
  ```bash
  pip install grpcio-health-checking
  ```
Para iniciar se debe compilar el archivo proto con el comando:
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. proto/fileservice.proto
```
Habiendo instalado las dependencias necesarias y compilado el archivo proto, podemos proceder a ejecutar el programa. Para iniciar un red lo haremos con el formato <IP> <Puerto> en este caso de manera local sería:
```bash
python run_node.py 127.0.0.1 7000
```
Para unir un peer a una red ya creada se realiza con el fomato `python run_node.py` <IP peer semilla> <Puerto peer semilla> <IP nuevo peer> <Puerto nuevo peer> ejemplo:
```bash
python run_node.py 127.0.0.1 9000  127.0.0.1 7000
```
Teniendo la red inicializada, podemos ir uniendo los diferentes peers a la red para notar su funcionamiento.
#### 3.2. detalles del desarrollo

Usamos solo gRPC para implementar el proyecto P2P porque nos proporciona una comunicación directa y eficiente entre nodos mediante RPC, lo cual es perfecto para las operaciones del algoritmo Chord, como la creación y mantenimiento de la finger table. No utilizamos API REST porque no lo planteamos de esa manera desde el inicio del proyecto. MOM fue descartado porque añade una complejidad innecesaria y no es requerido para las operaciones específicas de Chord, que se basan en mensajes directos y eficientes.
#### 3.3. detalles técnicos
* Lenguaje de programación:
  `Python 3.11.5`
  Extensiones:
* Protobuf
  `Protobuf 5.27.3`
* grpcio-tools 
  `grpcio-tools 1.65.5`
* tabulate 
  `tabulate 0.8.10`
* grpcio-health-checking 
  `grpcio-health-checking 1.66.1`

### 3.3. descripción y como se configura los parámetros del proyecto
El proyecto como se indicio anteriormente, cuenta con una estructura de <IP> <Puerto> para un peer inicial (inicialización de la red) e <IP peer semilla> <Puerto peer semilla> <IP nuevo peer> <Puerto nuevo peer>.
Para replicar el funcionamiento de un ambiente de desarollo para 4 peers con ID's 1, 5, 20 y 28, se recomienda la siguiente implementación:
* Nodo 20= `127.0.0.1 7000`
* Nodo 28= `127.0.0.1 8000 127.0.0.1 7000`
* Nodo 5= `127.0.0.1 9000 127.0.0.1 7000`
* Nodo 1= `127.0.0.1 6000 127.0.0.1 7000`
Todas estas configuraciones se realizan a la hora de ejecutar el programa, demás modificaciones internas dentro del mismo código no son necesarias.

### 3.4. Estructura de directorios y archivos.
```bash
P2P_PROJECT
├── __pycache__
├── .vscode
├── config
├── proto
│   └── fileservice.proto
├── services
│   ├── __pycache__
│   ├── __init__.py
│   ├── chordNode.py
│   ├── file_service.py
│   ├── fileservice_pb2_grpc.py
│   ├── fileservice_pb2.py
├── cliente.py
├── README.md
├── run_node.py
└── server.py
```
### 3.5. Imagenes resultados
Funcionamiento al conectar un peer.

![image](https://github.com/user-attachments/assets/aaff90bc-2a98-41da-b7b8-ed9b9ed55fd0)

Funcionamiento al conectar un peer a una red ya establecida.

![image](https://github.com/user-attachments/assets/0bd6b002-0008-4dd6-8448-e25c5a46604e)









