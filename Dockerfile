FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y tzdata build-essential unzip

COPY core/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN playwright install
RUN playwright install-deps
WORKDIR /app

# download and unzip PocketBase
ADD https://github.com/pocketbase/pocketbase/releases/download/v0.23.4/pocketbase_0.23.4_linux_amd64.zip /tmp/pb.zip
# for arm device
# ADD https://github.com/pocketbase/pocketbase/releases/download/v0.23.4/pocketbase_0.23.4_linux_arm64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

EXPOSE 8090
# EXPOSE 8077

CMD tail -f /dev/null