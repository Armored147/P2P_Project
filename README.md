### Tópicos Especiales en Telemática: C2466-ST0263-1716
## Estudiantes: Isis Catitza Amaya Arbeláez, icamayaa@eafit.edu.co/Santiago Alberto Rozo Silva, sarozos@eafit.edu.co
## Profesor: Álvaro Enrique Ospina Sanjuan, aeospinas@eafit.edu.co

### Reto No 1

## 1. Breve descripción de la actividad
La actividad consiste en diseñar e implementar un sistema P2P (peer-to-peer) que permita la compartición de archivos de manera distribuida y descentralizada. Este sistema debe estar basado en una red P2P estructurada (como Chord/DHT) o no estructurada (con superpeer o pura). Cada nodo o peer en la red actuará como servidor y cliente al mismo tiempo, conteniendo microservicios que manejarán el mantenimiento de la red, la localización de recursos y servicios dummy para la transferencia de archivos.

## 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
* Diagrama de arquitectura.
* Conexión entre los diferentes peers mediante gRPC usando el algoritmo de Chord.
* Simulación de descarga (download) de archivos.
* Simulación de carga (upload).
* Listado de archivos que posee cada peer.
* Compartir lista de archivos entre peers.
* Simulación de transferencia de archivos entre peers.
* Busqueda de archivos en la red Chord.
* Despliegue en AWS con Docker.
* Documentación.
## 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)

### 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.
El proyecto se cimenta sobre de una red peer-to-peer (P2P) estructurada basada en el algoritmo Chord, que utiliza gRPC para la comunicación entre nodos.

![P2P](https://github.com/user-attachments/assets/48f152bf-87f8-4818-ac21-65429d5d6fdb)

## 2.1.1. Componentes principales:
* Nodos (Peers):
Los nodos o peers son los componentes principales de la red peer-to-peer, cada peer cuenta con un ID único generado mediante hashing consistente (SHA-1), que determina su posición en el anillo de Chord.
El servicio Chord Maneja las operaciones del protocolo Chord, como la creación y mantenimiento de la finger table(Cada nodo mantiene una finger table que contiene referencias a otros nodos en posiciones específicas del anillo, permitiendo búsquedas eficientes en tiempo logarítmico), unión y salida de nodos, y la estabilización del anillo, todo esto mediante la comunicación de los peers a través de gRPC. Además de lo anterior, se implementó un servicios dummy para simular la carga (upload) y descarga (download) de archivos.

## 2.1.2. Comunicación con gRPC:
Se define métodos RPC necesarios para el funcionamiento del algoritmo Chord, tales como find_successor, closest_preceding_node, join, notify, stabilize, fix_fingers entre otras.
Se define métodos RPC como UploadFile y DownloadFile que simulan la transferencia de archivos entre nodos.

## 2.1.3. Interacción Entre Nodos:
Se Crea la finger table Utilizando gRPC, los nodos se comunican para encontrar sus sucesores y llenar sus finger tables. Por ejemplo, un nodo P1 puede llamar al método find_successor de P2 para actualizar su finger table.
Cuando un nodo necesita simular la transferencia de un archivo, utiliza gRPC para llamar a los servicios UploadFile o DownloadFile del nodo correspondiente que "posee" el archivo.







