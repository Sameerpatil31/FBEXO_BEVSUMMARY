from src.BEV_Details.utils import create_folders_bev,upload_file_s3,download_BEV_pdf
from src.login import logger



class s3_upload:
    def __init__(self):
        pass



    def save_local(self,ein,url:dict):
        file_path_list_for_upload={}
        try:

            for k,v in url.items():
                parentdir, folderpath= create_folders_bev(EIN=ein,pdf_file=k)
                filepath = download_BEV_pdf(url=v,folder_name=folderpath)

                file_path_list_for_upload[k] = filepath
                logger.info(f"pdf path is {filepath}")


            return file_path_list_for_upload
        except Exception as e:
            logger.error(f"Error in save_local function and error is {e}")


    def s3_upload_generated_pdf_report(self, ein, url):
        root_folder = "List_Business_For_Sale_PDF"

        try:
            s3_url = upload_file_s3(file_path=url,folder_name=f"{root_folder}/{ein}/generated_report")
            return s3_url
        except Exception as e:
            logger.error(f"Error in s3_upload_generated_pdf_report function and error is {e}")
            return None

    def s3_upload(self,filepathlist:dict,foldername): 
        
        public_pdf_list={}
        root_folder = "List_Business_For_Sale_PDF"
        try:
            for k,file in filepathlist.items():

                url_public = upload_file_s3(file_path=file,folder_name=f"{root_folder}/{foldername}/{k}")
                public_pdf_list[k] = url_public
                logger.info(f"Public url is {url_public}")


            return public_pdf_list    
        
        except Exception as e:
            logger.error(f"Error in s3_upload function and error is {e}")





    def return_public_url(self,ein,url:dict):

        list_file = self.save_local(ein=ein,url=url)
        public_url = self.s3_upload(filepathlist=list_file,foldername=ein)

        return public_url





