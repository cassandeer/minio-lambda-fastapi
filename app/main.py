from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import requests

app = FastAPI()

@app.post('/')
async def get_webhook(event: dict):
    # Get the object context
    object_context = event["getObjectContext"]

    # Get the presigned URL
    # Used to fetch the original object from MinIO
    s3_url = object_context["inputS3Url"]

    # Extract the route and request tokens from the input context
    request_route = object_context["outputRoute"]
    request_token = object_context["outputToken"]

    # Get the original S3 object using the presigned URL
    r = requests.get(s3_url)
    original_object = r.content.decode('utf-8')

    # Transform the text in the object by swapping the case of each char
    transformed_object = original_object.upper()

    # Return the object back to Object Lambda, with required headers
    # This sends the transformed data to MinIO
    # and then to the user
    headers = {
        'x-amz-request-route': request_route,
        'x-amz-request-token': request_token
    }
    return Response(transformed_object, status_code=200, headers=headers)

@app.exception_handler(400)
async def bad_request_exception_handler(request, exc):
    return HTTPException(status_code=400, detail="Bad Request")
