FROM python:3.12

WORKDIR /dns
COPY custom_dns_server.py /dns/custom_dns_server.py

RUN pip install dnslib
RUN apt-get update
RUN apt-get install dnsutils -y
RUN apt install iproute2 -y

CMD ["python", "/dns/custom_dns_server.py"]