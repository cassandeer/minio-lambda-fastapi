from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import requests
from PIL import Image
from io import BytesIO

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
    image = Image.open(BytesIO(r.content))

    # Generate a thumbnail from the original S3 object
    thumbnail_size = (100, 100)
    image.thumbnail(thumbnail_size)
    thumbnail_bytes = BytesIO()
    image.save(thumbnail_bytes, format='PNG')

    # Return the object back to Object Lambda, with required headers
    # This sends the transformed data to MinIO
    # and then to the user
    headers = {
        'x-amz-request-route': request_route,
        'x-amz-request-token': request_token
    }
    return Response(content=thumbnail_bytes.getvalue(), status_code=200, headers=headers, media_type="image/png")

@app.exception_handler(400)
async def bad_request_exception_handler(request, exc):
    return HTTPException(status_code=400, detail="Bad Request")
