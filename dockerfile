FROM python:3

RUN mkdir /P2P_Project

WORKDIR /P2P_Project

COPY requirements.txt /P2P_Project/

RUN pip install -r requirements.txt

COPY . /P2P_Project/

# Usa un archivo temporal para almacenar la IP
RUN curl -s http://169.254.169.254/latest/meta-data/public-ipv4 > /tmp/public-ip.txt

# Luego, léelo en una variable de entorno
RUN export PUBLIC_IP=$(cat /tmp/public-ip.txt)


CMD ["python", "./run_node.py", "44.223.125.103", "7000"]