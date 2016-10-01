FROM ubuntu:16.04

# config locales to Unicode
# RUN locale-gen en_US.UTF-8
# ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN apt-get update && apt-get install -y python-pip supervisor

ADD ./requirements.txt /app/requirements.txt
ADD ./misc/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN pip install -r /app/requirements.txt

ADD . /app

VOLUME ["/app/databases"]
EXPOSE 8080 9000

CMD ["bash", "/app/misc/entrypoint.sh"]
