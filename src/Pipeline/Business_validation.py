from src.BEV_Details.Business_Entity_Validation import BEV
from src.BEV_Details.S3_Bucket_upload import s3_upload
from src.BEV_Details.utils import upload_to_s3



class BEV_Validation:
    def __init__(self):
        pass


    def return_result(self,ein):
        bev_obj = BEV(ein)
        result = bev_obj.return_validation_json()
        print(result)
        return result
    

    def return_public_url(self,ein,url:dict):
        obj_s3 = s3_upload()
        public_url = obj_s3.return_public_url(ein=ein,url=url)

        return public_url


if __name__ == '__main__':

    obj= BEV_Validation()
    obj.return_result()
