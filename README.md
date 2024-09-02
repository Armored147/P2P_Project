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
El único aspecto que no se logró cumplir en el proyecto fue el despliegue completo de cuatro nodos en AWS. Esto se debió a una falla que no se pudo resolver, dejando este aspecto inconcluso. La falla presentada ocurrió cuando un tercer nodo se unía a la red, lo que provocaba que todos los servidores gRPC dejaran de responder y por lo tanto la red P2P se caia completamente.

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


### 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.

### 4.1. IP's de las instancias EC2 de AWS.

Se desplegaron cuatro instancias o máquinas virtuales en AWS, cada una con una IP elástica para optimizar la eficiencia en el despliegue del proyecto. Además, para simplificar la configuración, todos los nodos utilizan el puerto `7000`. A continuación, se detallan las IPs de cada instancia.

- **Master:** `IP : 44.223.125.103:7000`. Instancia encargada de iniciar la red P2P y ser el primer nodo. 
- **Nodo-1:** `IP : 54.84.150.553:7000`. Nodo 1 despues del master.
- **Nodo-2:** `IP : 44.198.105.213:7000`. Nodo 2 despues del master.
- **Nodo-3:** `IP : 3.227.81.239:7000`. Nodo 3 despues del master.

Cabe aclarar que no hay orden en que los nodos deban unirse, simplemente es para una mayor claridad y seguimiento de las maquinas virtuales.

### 4.2. Configuracion del proyecto en las instancias EC2 de AWS.

Para deplegar el proyecto en el ambiente de AWS, se deben de seguir los pasos descritos a continuacion.

**1. Instalacion de docker en la instacia y permisos de usuario.**
   - [Se remite a la guia oficial de instalacion de docker](https://docs.docker.com/engine/install/ubuntu/)
   - [Permisos de usuario para docker. Guia oficial](https://docs.docker.com/engine/install/linux-postinstall/)

**2. Clonar el repositorio del proyecto** 
```bash
git clone https://github.com/Armored147/P2P_Project.git
```
y entrar 
```bash
cd P2P_Project
```

**3. Crear la red docker**  
Para el correcto funcionamiento del proyecto, se debe crear una red para el contenedor.
```bash
docker network create --driver=bridge --subnet=ip-publica-instancia/16 nombre-de-red
```
En la bandera subnet, se esta creando una subred para el contenedor por lo tanto la ip debe finalizar en `0.0`

**4. Modificar el archvido de configuracion Yaml**  
Si el peer que se va a unir a las red no es el master, es necesario editar el archivo de configuracion.
```bash
nano ./config/peerSlave_config.yaml
```
En él, se debe de editar el campo `ip: 0.0.0.0` y escribir la ip publica de la instancia EC2.

**5. Crear la imagen Docker**  
A continuacion se crea la imagen Docker a partir del dockerfile del proyecto.
```bash
docker build -t test-aws .
```

Asi el proyecto queda completamente configurado en la maquina virtual, y solo quedaria levantar el contener.

### 4.3. Ejecutar el proyecto
Para ejecutar el proyecto, simplemente es necesario lanzar el siguiente comando, según corresponda al caso.

Para el master
```bash
docker run -it --network=nombre-de-red --ip=44.223.125.103 -p 5000:5000 -p 7000:7000 -e NODE_MODE=master --name master test-aws:latest
```

Para los nodos
```bash
docker run -it --network=nombre-de-red --ip=44.223.125.103 -p 5000:5000 -p 7000:7000 --name nodex test-aws:latest
```

### 4.4. Guia de usuario
Para que el usuario pueda utilizar el proyecto, primero debe cumplir con los requisitos mencionados anteriormente. Una vez cumplidos, el usuario interactuará con la red a través del programa Postman de la siguiente manera:

<img width="960" alt="Postamn" src="https://github.com/user-attachments/assets/745316d1-d8fc-4a0a-b2e7-000eec288ef1">

Se detalla los metodos que se pueden utilizar.

**Metodos API**
- `/finger_table`
- `/get_predecessor`
- `/get_successor`
- `/show_files`
- `/upload_file`
- `/download_file`
- `/search_file`
- `/shutdown`

### 4.5. Resultados

**Instancias EC2**
![image](https://github.com/user-attachments/assets/e750a6cf-db64-4b97-a79d-97725eabfae5)
![image](https://github.com/user-attachments/assets/27ae45d8-6b24-4f3f-adfe-688c493e2441)

**Postman y API**
![image](https://github.com/user-attachments/assets/c5da1eba-4f8f-4fb0-93b3-6308161b171c)
![image](https://github.com/user-attachments/assets/23f9bd03-de17-4ad9-ae25-2b65629ce7d1)


### Referencias

- [Chord (DHT) in Python](https://medium.com/princeton-systems-course/chord-dht-in-python-b8b8985cb80e)
- [Flask HTTP methods, handle GET & POST requests](https://www.geeksforgeeks.org/flask-http-methods-handle-get-post-requests/)
- [Diccionarios en Python](https://ellibrodepython.com/diccionarios-en-python)
- [docker network create](https://docs.docker.com/reference/cli/docker/network/create/)










