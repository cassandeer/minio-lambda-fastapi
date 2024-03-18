# minio-lambda-fastapi

I've made this simple project to have a better understanding of [Minio's Object Lambda](https://min.io/docs/minio/linux/developers/transforms-with-object-lambda.html). My lambda function generates a thumbnail from an image.

## Requirements

- [Docker](https://www.docker.com/) (25.0.4)
- [docker-compose](https://docs.docker.com/compose/) (1.29.2)
- A working [Minio+Keycloak instance](https://github.com/cht42/minio-keycloak) with [minio docker image](https://quay.io/repository/minio/minio?tab=tags&tag=latest) (RELEASE.2022-01-03T18-22-58Z) and [keycloak docker image](https://quay.io/repository/keycloak/keycloak) (15.0.0)
- [Minio Client](https://github.com/minio/mc)
- Python3.10

## API / Lambda handler setup

Run your api:

```bash
docker-compose build && docker-compose up -d
```

> You can access the swagger of your new API at `http://172.17.0.1:10666/docs`

## Minio setup

You have to enable your new lambda handler called `function` in your Minio instance by adding these variables:

```bash
MINIO_LAMBDA_WEBHOOK_ENABLE_function=on 
MINIO_LAMBDA_WEBHOOK_ENDPOINT_function=http://172.17.0.1:10666
```

And then restart your minio service.

## Test your handler

Set up your environement variables in `.env`: 

```bash
cp .env.example .env
nano .env
```

Add an alias to your minio deployment and create your bucket:

```bash
mc alias set myminio/ http://localhost:9000 <minio_user> <minio_password>
mc mb myminio/raw-data
```

Find a picture and put it in your newly created bucket:

```bash
mc cp cat.png myminio/raw-data/
```
> For this example, I've used a picture of a cat

Print the presigned URL that your Lambda handler have generated:

```bash
python3.10 -m test
```

You can do a `GET` request on this newly generated presigned url to see your new thumbnail. In my case, I've used [Insomnia](https://docs.insomnia.rest/insomnia/install)

![insomnia screenshot](example/insomnia_examples.png)

