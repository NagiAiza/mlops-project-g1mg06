import boto3
import os
import sys

BUCKET_NAME = "s3-g1mg06"  
LOCAL_FILE_PATH = "Sleep_health_and_lifestyle_dataset.csv" 
S3_KEY_RAW = "raw/sleep_data.csv"

def upload_to_s3():
    s3 = boto3.client("s3")
    
    if not os.path.exists(LOCAL_FILE_PATH):
        print(f"Error: File '{LOCAL_FILE_PATH}' not found")
        sys.exit(1)

    print(f"Uploading {LOCAL_FILE_PATH} to s3://{BUCKET_NAME}/{S3_KEY_RAW}...")
    s3.upload_file(LOCAL_FILE_PATH, BUCKET_NAME, S3_KEY_RAW)
    print("Upload successful!")

if __name__ == "__main__":
    upload_to_s3()