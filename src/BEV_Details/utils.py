import boto3
from botocore.exceptions import NoCredentialsError,PartialCredentialsError
from dotenv import load_dotenv
import os
from datetime import date



def year_sequence():
    latest_year = date.today().year - 1
    latest_2_year = latest_year -1
    latest_3_year = latest_2_year -1

    return latest_year,latest_2_year,latest_3_year


def upload_file_s3(folder_name = 'my-folder1/'):
    load_dotenv()

# Initialize the S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id = os.getenv('aws_access_key_id'),
        aws_secret_access_key = os.getenv('aws_secret_access_key'),
        region_name='eu-north-1'  # Replace with your region
    )
    # Replace with your bucket name
    bucket_name = 'fbexofile'

    # Folder (prefix) to create
      # Must end with a slash to simulate a folder

    # Create the "folder" by uploading an empty object with the folder name
    try:
        s3.put_object(Bucket=bucket_name, Key=folder_name)
        print(f"Folder '{folder_name}' created successfully in bucket '{bucket_name}'.")
    except NoCredentialsError:
        print("AWS credentials not found.")


     #File to upload
    file_path = r'D:\Client_pro\Fiverr\USA\Notebook\sdn.csv'
    file_key = f'{folder_name}sdn.csv'  # Path in S3 (folder + file name)

    # Upload the file
    try:
        s3.upload_file(file_path, bucket_name, file_key)
        print(f"File uploaded successfully to '{file_key}'.")
    except FileNotFoundError:
        print("The file was not found.")
    except NoCredentialsError:
        print("AWS credentials not found.")    





def upload_file_Obj(file,S3_BUCKET = 'fbexofile'):

    load_dotenv()

# Initialize the S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id = os.getenv('aws_access_key_id'),
        aws_secret_access_key = os.getenv('aws_secret_access_key'),
        region_name='eu-north-1'  # Replace with your region
    )
    # Replace with your bucket name
    try:

         s3.upload_fileobj(
            file,                # File-like object
            S3_BUCKET,           # S3 bucket name
            file.filename,       # S3 object key (file name in bucket)
            ExtraArgs={          # Optional: Set permissions and metadata
                'ContentType': file.content_type,
                'ACL': 'public-read'  # Set appropriate permissions
            }
        )

         print(file.filename)



    except Exception as e:
        print(e)




def upload_to_s3(file, bucket_name, object_name, content_type):
    """
    Upload a file-like object to S3.
    
    :param file: File-like object to upload.
    :param bucket_name: S3 bucket name.
    :param object_name: S3 object key (file name in bucket).
    :param content_type: Content type of the file.
    :return: Public URL of the uploaded file.
    """
    load_dotenv()

    try:
        s3_client = boto3.client(
             's3',
        aws_access_key_id = os.getenv('aws_access_key_id'),
        aws_secret_access_key = os.getenv('aws_secret_access_key'),
        region_name='eu-north-1'  # Replace with your region
        )

        # Upload file to S3
        s3_client.upload_fileobj(
            file,
            bucket_name,
            object_name,
            ExtraArgs={
                'ContentType': content_type,
                'ACL': 'public-read'  # Set appropriate permissions
            }
        )

        # Return the file URL
        # file_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{object_name}"
        # return file_url

    except NoCredentialsError:
        raise Exception("AWS credentials not provided")
    except PartialCredentialsError:
        raise Exception("Incomplete AWS credentials")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")        





