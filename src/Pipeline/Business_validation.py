from src.BEV_Details.Business_Entity_Validation import BEV
from src.BEV_Details.S3_Bucket_upload import s3_upload
from src.BEV_Details.utils import upload_to_s3
from src.login import logger
import shutil
import os
import json


class BEV_Validation:
    def __init__(self):
        pass


    def return_result(self,ein):
        bev_obj = BEV(ein)
        result = bev_obj.return_validation_json()
        if result is not None:
            print(result)
            return json.loads(result)
    

    def return_public_url(self,ein,url:dict):
        obj_s3 = s3_upload()
        public_url = obj_s3.return_public_url(ein=ein,url=url)
        
        folder_to_remove = os.path.join("BEV_PDF", f"{ein}")
        if os.path.exists(folder_to_remove):
           shutil.rmtree(folder_to_remove)
           logger.info(f"Folder removed : {folder_to_remove}")
           

        return public_url


if __name__ == '__main__':

    obj= BEV_Validation()
    obj.return_result()
