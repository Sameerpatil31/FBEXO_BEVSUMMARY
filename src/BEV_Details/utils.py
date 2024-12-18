import boto3
from botocore.exceptions import NoCredentialsError,PartialCredentialsError
# from dotenv import load_dotenv
import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


def year_sequence():
    latest_year = date.today().year - 1
    latest_2_year = latest_year -1
    latest_3_year = latest_2_year -1

    return latest_year,latest_2_year,latest_3_year


def upload_file_s3(file_path,folder_name = 'my-folder1/'):
    
    try:
        load_dotenv()
        aws_access_key_id = os.getenv('aws_access_key_id')
        aws_secret_access_key = os.getenv('aws_secret_access_key')
        bucket_name = 'fbexofile'
        if not aws_access_key_id or not aws_secret_access_key:
            raise ValueError("AWS credentials are missing. Check your .env file.")

        s3 = boto3.client(
            's3',
            aws_access_key_id= aws_access_key_id,
            aws_secret_access_key= aws_secret_access_key,
            region_name='eu-north-1'  # Replace with your region
        )
    
        # Ensure folder_name ends with a slash
        if not folder_name.endswith('/'):
            folder_name += '/'

        print(f"folder name is {folder_name}")    

        # Extract file name from the file path
        file_name = os.path.basename(file_path)

        # S3 key: Folder + File Name
        file_key = f'{folder_name}{file_name}'

    
        s3.put_object(Bucket=bucket_name, Key=folder_name)
        print(f"Folder '{folder_name}' created successfully in bucket '{bucket_name}'.")
    
        s3.upload_file(file_path, bucket_name, file_key)
        print(f"File '{file_name}' uploaded successfully to '{file_key}'.")

        # Generate the file's public URL
        public_url = f"https://{bucket_name}.s3.eu-north-1.amazonaws.com/{file_key}"
        print(f"Public URL: {public_url}")

        return public_url

    except FileNotFoundError:
        print("The file was not found.")
        return "None"
    except NoCredentialsError:
        print("AWS credentials not found.")
        return "None"
    except Exception as e:
        print(f"An error occurred: {e}")
        return "None"


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





import requests
import os

# URL of the PDF
# url = "https://fbexo.com/wp-content/uploads/2024/12/Houston_Small_Business_Incorporation_Certificate.pdf"

# Function to extract the file name from the URL
def get_filename_from_url(url):
    return os.path.basename(url)

# Function to download and save the PDF
def download_BEV_pdf(url,folder_name):
    filename = get_filename_from_url(url) 
    # Create the output folder if it doesn't exist
    # if not os.path.exists(folder_name):
    #     os.makedirs(folder_name)
    #     print(f"Created folder: {folder_name}")
    
    # Full file path to save the PDF
    file_path = os.path.join(folder_name, filename) # Extract file name
    try:
        response = requests.get(url, stream=True)  # Streaming for large files
        response.raise_for_status()  # Raise an exception for bad status codes

        with open(file_path, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    pdf_file.write(chunk)  # Write file in chunks
        print(f"PDF downloaded successfully and saved as: {filename}")

        return file_path

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")



def create_folders_bev(pdf_process_dir= "BEV_PDF", 
                   EIN = "EIN", 
                   pdf_file = "pdf_files", 
                  
                  
                   ):

    try:
        # Define the parent folder path
        parent_path = Path(pdf_process_dir)

        # Define the subfolder paths
        parent_dir = parent_path / EIN
        pdf_folder_dir = parent_dir / pdf_file
        
        

        # Create the parent folder and subfolders
        parent_dir.mkdir(parents=True, exist_ok=True)
        pdf_folder_dir.mkdir(parents=True, exist_ok=True)
       
       

        # Return the paths of the subfolders
        return parent_dir, pdf_folder_dir
    except Exception as e:
        raise e            





