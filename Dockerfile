FROM python:3.11-slim
COPY . /app
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Moscow
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN apt update && apt install -y --no-install-recommends nano git  \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r /app/requirements.txt
EXPOSE 3040

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]