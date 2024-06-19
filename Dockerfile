FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -yq tzdata build-essential && \
    apt-get clean

RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

WORKDIR /app

COPY core/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY core .

# download and unzip PocketBase
ADD https://github.com/pocketbase/pocketbase/releases/download/v0.22.13/pocketbase_0.22.13_linux_amd64.zip /tmp/pb.zip
# for arm user
# ADD https://github.com/pocketbase/pocketbase/releases/download/v0.22.13/pocketbase_0.22.13_linux_arm64.zip /tmp/pb.zip
RUN unzip /tmp/pb.zip -d /pb/

RUN mkdir -p /pb

COPY ./pb/pb_migrations /pb/pb_migrations
COPY ./pb/pb_hooks /pb/pb_hooks
COPY --from=builder /app/dist /pb/pb_public

EXPOSE 8090
EXPOSE 8077

CMD tail -f /dev/null