from src.BEV_Details.Business_Entity_Validation import BEV
from src.BEV_Details.utils import upload_to_s3



class BEV_Validation:
    def __init__(self):
        pass


    def return_result(self,ein):
        bev_obj = BEV(ein)
        result = bev_obj.return_validation_json()
        print(result)
        return result
    

    def upload_bev_files_s3(self,file,object_name,content_type):
        upload_to_s3(file,bucket_name="fbexofile",object_name=object_name,content_type=content_type)


if __name__ == '__main__':

    obj= BEV_Validation()
    obj.return_result()
