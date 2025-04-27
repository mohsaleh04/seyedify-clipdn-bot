FROM python:3.13.2

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libavcodec-extra \
        libavformat58 \
        libavutil56 \
        libswscale5 \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
