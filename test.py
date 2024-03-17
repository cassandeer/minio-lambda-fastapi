import os
import json
from os.path import join, dirname
from datetime import timedelta
from minio import Minio
import requests
import base64
import xml.etree.ElementTree as ET
from dotenv import load_dotenv, find_dotenv, dotenv_values

# Load environment variables from .env file
load_dotenv()

# Keycloak
username = os.environ.get("KEYCLOAK_USERNAME")
password = os.environ.get("KEYCLOAK_PASSWORD")
client_id = os.environ.get("KEYCLOAK_CLIENT")
client_secret = os.environ.get("KEYCLOAK_CLIENT_CREDENTIALS")
realm = os.environ.get("KEYCLOAK_CLIENT_REALM")
keycloak_url = os.environ.get("KEYCLOAK_URL")

# Minio
url_sts = os.environ.get("MINIO_S3_ENDPOINT")
MINIO_URL= os.environ.get("MINIO_URL")


policy = {
   "Version": "2012-10-17",
   "Statement": [
      {
            "Effect": "Allow",
            "Action": [
               "s3:*"
            ],
            "Resource": "arn:aws:s3:::*"
      }
   ]
}


def get_keycloak_token(username, password, client_id, client_secret, realm, keycloak_url):
    token_url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username,
        'password': password,
        'grant_type': 'password'
    }
    response = requests.post(token_url, data=payload, verify=False)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        return access_token
    else:
        print("Failed to obtain token from Keycloak")
        return None

def get_sts(token):
    params = {
        "WebIdentityToken": token,
        "Version": "2011-06-15",
        "DurationSeconds": "86000",
        "Policy": json.dumps(policy),
        "Action":"AssumeRoleWithWebIdentity"
    }
    response = requests.request("POST", url_sts, params=params, verify=False)
    if response.status_code == 200:
        try:
            res = response.content
            ns = {'ns0': 'https://sts.amazonaws.com/doc/2011-06-15/'}
            root = ET.fromstring(res)
            credentials = root.find('.//ns0:Credentials', ns)

            access_key_id = credentials.find("ns0:AccessKeyId", ns).text
            secret_access_key = credentials.find("ns0:SecretAccessKey", ns).text
            session_token = credentials.find("ns0:SessionToken", ns).text
            
            return access_key_id, secret_access_key, session_token
        except KeyError:
            print("Access key not found in the XML response.")
    else:
        print("Error:", response.status_code)
        print("Response:", response.content)

if __name__ == "__main__":
    
    # Get JWT Token
    jwt_token = get_keycloak_token(username, password, client_id, client_secret, realm, keycloak_url)
    
    # Get AssumeRoleWithWebIdentity response
    access_key_id, secret_access_key, session_token = get_sts(jwt_token)


    # Initialize MinIO client object
    minio_client = Minio(
    MINIO_URL,
    access_key=access_key_id,
    secret_key=secret_access_key,
    session_token=session_token,
    secure=False # Set to False if you're not using SSL/TLS
)

    # Set lambda function target via `lambdaArn`
    reqParams = {
        "lambdaArn": "arn:minio:s3-object-lambda::function:webhook"
    }

    # Generate presigned GET url with lambda function
    presigned_url = minio_client.presigned_get_object(
        "raw-data",
        "testobject",
        expires=timedelta(hours=2),
        response_headers=reqParams
    )
    print(presigned_url)

    