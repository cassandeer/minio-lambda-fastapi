# minio-lambda-fastapi

I've made this simple project to have a better understanding of [Minio's Object Lambda](https://min.io/docs/minio/linux/developers/transforms-with-object-lambda.html). My lambda function transforms a text content in upper case.

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

Create a new object and put it in your newly created bucket:

```bash
cat > testobject << EOF
MinIO is a High Performance Object Storage released under GNU Affero General Public License v3.0. It is API compatible with Amazon S3 cloud storage service. Use MinIO to build high performance infrastructure for machine learning, analytics and application data workloads.
EOF

mc cp testobject myminio/raw-data/
```

Run your test:

```bash
curl -v $(python3.10 -m test)
```

You can verify that your original data is still the same after the call of the Lambda function:

```bash
mc cat myminio/raw-data/testobject
```
