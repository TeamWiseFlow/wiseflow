FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -yq tzdata build-essential unzip && \
    apt-get clean

WORKDIR /app

COPY core/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY core .

# download and unzip PocketBase
ADD https://github.com/pocketbase/pocketbase/releases/download/v0.22.13/pocketbase_0.22.13_linux_amd64.zip /tmp/pb.zip
# for arm device
# ADD https://github.com/pocketbase/pocketbase/releases/download/v0.22.13/pocketbase_0.22.13_linux_arm64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /app/pb/

EXPOSE 8090
EXPOSE 8077

CMD tail -f /dev/null