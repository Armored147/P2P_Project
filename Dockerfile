FROM python:3

RUN mkdir /P2P_Project

WORKDIR /P2P_Project

COPY requirements.txt /P2P_Project/


RUN pip install -r requirements.txt

COPY . /P2P_Project/

# Otorga permisos de ejecución al archivo Bash
RUN chmod +x ./scripts/master.sh

RUN chmod +x ./scripts/slave.sh

EXPOSE 5000
EXPOSE 6000
EXPOSE 7000
EXPOSE 8000
EXPOSE 9000

CMD ["python", "./run_node.py", "44.223.125.103", "7000"]

# CMD condicional usando variables de entorno
#CMD if [ "$NODE_MODE" = "master" ]; then \
 #       ./scripts/master.sh; \
  #  else \
   #     ./scripts/master.sh; \
    #fi