from src.BEV_Details.Business_Entity_Validation import BEV
from src.BEV_Details.sql_db_operation import execute_query,fetch_query
from src.BEV_Details.S3_Bucket_upload import s3_upload
from src.BEV_Details.utils import upload_to_s3
from src.login import logger
from sqlalchemy import text
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



    def save_pdf_url(self, ein, url):
        """
        Save PDF URL with EIN to the url_links table
        """
        try:
            # Check if record exists
            check_query = f"SELECT COUNT(*) as count FROM url_links WHERE ein = '{ein}'"
            # Pass parameters as individual arguments or use a dict format
            result = fetch_query(check_query)  # Use dict format
            # Alternative: result = fetch_query(check_query, ein)  # Pass as individual argument

            # Be robust to either dict-rows or tuple-rows
            count = 0
            if result:
                first = result[0]
                count = first['count'] if isinstance(first, dict) else first[0]

            if count > 0:
                # Update existing record
                update_query = text("""
                UPDATE url_links
                SET url = :url, updated_at = GETDATE()
                WHERE ein = :ein
                """)
                # execute_query(update_query, {"url": url, "ein": ein, "url_type": url_type})
                execute_query(update_query, {"url": str(url), "ein": ein})  # Use dict format
                logger.info(f"Updated PDF URL for EIN {ein}")
            else:
                # Insert new record
                insert_query = text("""
                INSERT INTO url_links (ein, url)
                VALUES (:ein, :url)
                """)
                execute_query(insert_query, {"ein": ein, "url": str(url)})  # Use dict format
                logger.info(f"Inserted new PDF URL for EIN {ein}")

            return True

        except Exception as e:
            # Remove emoji to avoid encoding issues
            logger.error(f"SELECT query failed: {check_query}. Params: {ein}. Error: {e}")
            logger.error(f"Error saving PDF URL for EIN {ein}: {e}")
            return False
if __name__ == '__main__':

    obj= BEV_Validation()
    obj.return_result()
