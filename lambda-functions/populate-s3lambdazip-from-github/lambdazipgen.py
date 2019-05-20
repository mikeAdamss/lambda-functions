from bs4 import BeautifulSoup

import io
import zipfile
import json
import requests
import boto3
import os

GIT_ACCOUNT = "mikeAdamss"
LAMBDA_DIR = "lambda-trial"
IGNORE_LAMBDA_NAMES = ["ci", "lambdaZipGenerator", "lambdaZipDeployer"]
BUCKET_NAME = "dp-lambda-zips"

# lambda_handler is the entry point, all else is called from here
def lambda_handler(event, context):

    # use the commit info to get a list of lambdas that need updating
    lambdasToUpdate = getLambdasToUpdate(event)
    print("Lambdas to update:" + ",".join(lambdasToUpdate))

    # update them in turn,
    for lambdaName in lambdasToUpdate:

        # Create a zip representing a single lambda function
        print("Attempting to create zip buffer")
        lambdaZipAsBuffer = createLambdaZipBuffer(lambdaName)

        # Upload it to s3
        print("Attempting to upload zip to s3")

        try:
            s3 = boto3.client('s3')
            s3.put_object(Body=lambdaZipAsBuffer.getvalue(), Key=lambdaName + ".zip" ,Bucket=BUCKET_NAME)
            print("Zip upload complete for:", lambdaName)
        except Exception as e:
            print("Zip upload failed for:", lambdaName)
            raise e


# getLambsasToUpdate parses which lambda functions have been updated from the received github webhook POST
def getLambdasToUpdate(payload):

    try:
        payload = json.loads(payload["body"])
    except Exception as e:
        pass

    lambdaNames = []

    # check for expected type
    if type(payload) != dict:
        print("Aborting. Expecting type dict, found type" + type(payload))
        print("Payload as string:" + str(payload))
        os.exit(1)

    # check for expected field
    if "commits" not in payload.keys():
        print("Aborting. Expecting payload to have a 'commits' field.")
        print("Payload as string:" + str(payload))
        os.exit(1)

    for commit in payload["commits"]:
        print("Commit", commit)
        for commitType in ["added", "modified"]:
            for commitFiles in commit[commitType]:

                # listify in case of single files changes
                if type(commitFiles) != list:
                    commitFiles = [commitFiles]

                print("Commitfiles", type(commitFiles), commitFiles)

                for commitFilePath in commitFiles:

                    # get the name of the lambda from the commit filepath
                    lambdaName = commitFilePath.split("/")[0]
                    lambdaNames.append(lambdaName)

    # filter out any lambdas on our ignore list
    lambdaNames = [x for x in lambdaNames if x not in IGNORE_LAMBDA_NAMES]

    return lambdaNames


# createLambdaZip returns a zip object created from an individual lambdas directory in
# github.com/ONSdigital/dp-developer-dashboard-lambdas/
def createLambdaZipBuffer(lambdaName):

    print("Creating Zip for lambda:", lambdaName)
    # get the html of the individual lambda as shown on github
    r = requests.get("https://github.com/" + GIT_ACCOUNT + "/" + LAMBDA_DIR + "/tree/master/" + lambdaName)
    if r.status_code != 200:
        print("Aborting operation. Failing to get lambda from github repo: " + url)
        sys.exit(1)

    # scrape out the file urls
    soup = BeautifulSoup(r.content, 'html.parser')
    items = soup.find_all('a', {"class": "js-navigation-open"})
    fileItems = [x["href"] for x in items if GIT_ACCOUNT + "/" + LAMBDA_DIR in str(x)][1:]
    fileUrls = ["https://github.com/" + x for x in fileItems]
    print("Identified files for zip:", fileUrls)

    # download individual files and create a map of {fileName: FileObjectBuffer}
    print("Creating map of files to be zipped.")
    dataMap = {}
    for url in fileUrls:
        print("Getting:", url)
        response = requests.get(url).content
        print("Got:", url)

        fileName = url.split("/")[-1]
        dataMap.update({fileName: response})

    print("Datamapkeys", dataMap.keys())

    # Zip those up into a ZipFileObjectBuffer
    print("Creating zip buffer.")
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in dataMap.items():
            zip_file.writestr(file_name, data)

    return zip_buffer
