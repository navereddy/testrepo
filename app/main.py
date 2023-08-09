from http import HTTPStatus
from typing import Annotated
import string
from fastapi import FastAPI, File, UploadFile, HTTPException
import re
from azure.storage.blob.aio import BlobServiceClient

# from app.routers import order

app = FastAPI(
    title='TACIT',
    version='1.0.0',
    description='',
    root_path=''
)


# app.include_router(order.router)


@app.get('/', status_code=HTTPStatus.OK)
async def root():
    """
    basic connectivity test.
    """
    return {'message': 'working'}


# app = FastAPI()


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def upload_file(file: UploadFile):
    """
        upload file here:
    """
    # print(file.filename[-3:])
    validate_file_type(file)
    validate_file_name(file)
    return {"SUCCESS: Successfully uploaded file": file.filename}


def validate_file_type(input_file: UploadFile):
    if input_file.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=415, detail="ERR0R: Unable to upload file. Please ensure that you are "
                                                    "uploading a pdf or txt file.")
    # return {"SUCCESS: Successfully uploaded file": input_file.filename}


def validate_file_name(input_file: UploadFile):
    ALPHA = string.ascii_letters
    # special_characters = set(r"""`~!@#$%^&*()+={[}}|\:;"'<,>.?/""")

    # everything but - and _
    # are spaces allowed?
    if not input_file.filename.startswith(tuple(ALPHA)):
        raise HTTPException(status_code=422, detail="ERR0R: File name must begin with a letter.")
    if not has_special_char(input_file.filename):
        # elif containsAny(input_file.filename, special_characters):
        raise HTTPException(status_code=422, detail="ERR0R: File name must not contain any special characters aside "
                                                    "from - and _ (hyphen and underscore).")
    # elif not input_file.filename.isalnum():
    # raise HTTPException(status_code=422, detail="ERR0R: File name must be alphanumeric.")
    # return {"SUCCESS: Successfully uploaded file": input_file.filename}
    parse_date(input_file)


def has_special_char(text: str) -> bool:
    return any(c for c in text if not c.isalnum() and not c.isspace() and not c in "-" and not c in "_")


def parse_date(file_name: UploadFile):
    pattern = r'\d{2}.\d{2}.\d{4}'
    # print("\n".join(re.findall(pattern,fileName)))
    results = []
    results += re.findall(pattern, file_name.filename) or ["Error: invalid format"]
    for result in results:
        if result == "Error: invalid format":
            raise HTTPException(status_code=422, detail="ERR0R: Incorrect data format, date included in file name "
                                                        "should be in the format MM-DD-YYYY")
        else:
            pass


@app.post("/uploadfiletestdatabase")
async def upload_file_databasetest(file: UploadFile):
    name = file.filename
    type = file.content_type
    return await uploadtoazure(file, name, type)


async def uploadtoazure(file: UploadFile, file_name: str, file_type: str):
    connect_str = "DefaultEndpointsProtocol=https;AccountName=evanketacitstorage;AccountKey" \
                  "=vOrqUJrvZOao0P6tEfNBkvwi4FEWBoWCCwV9c7IRtyGoFWNLBo2TlyHL0xO3YjjyD0D5Ueart6Kr+AStEr5P7Q" \
                  "==;EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = "test" #adjust
    async with blob_service_client:
        container_client = blob_service_client.get_container_client(container_name)
        try:
            blob_client = container_client.get_blob_client(file_name)
            f = await file.read()
            await blob_client.upload_blob(f)
        except Exception as e:
            print(e)
            return HTTPException(500, "ERROR")

    return "{'successful?':'yes'}"
