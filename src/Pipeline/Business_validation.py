from src.BEV_Details.Business_Entity_Validation import BEV
from src.BEV_Details.sql_db_operation import execute_query,fetch_query
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



    def save_pdf_url(self, ein, url):
        """
        Save PDF URL with EIN to the url_links table

        Args:
            ein (str): EIN number
            url (str): PDF URL to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if record exists
            check_query = "SELECT COUNT(*) as count FROM url_links WHERE ein = ?"
            # Pass a list of tuples for executemany-style helpers
            result = fetch_query(check_query, [(ein,)])  # changed

            # Handle both dict-row and tuple-row shapes robustly
            if result:
                first = result
                count = first['count'] if isinstance(first, dict) else first
            else:
                count = 0

            if count > 0:
                # Update existing record
                update_query = """
                UPDATE url_links
                SET url = ?, updated_at = GETDATE()
                WHERE ein = ?
                """
                execute_query(update_query, [(url, ein)])  # changed
                logger.info(f"Updated PDF URL for EIN {ein}")
            else:
                # Insert new record
                insert_query = """
                INSERT INTO url_links (ein, url)
                VALUES (?, ?)
                """
                execute_query(insert_query, [(ein, url)])  # changed
                logger.info(f"Inserted new PDF URL for EIN {ein}")

            return True

        except Exception as e:
            logger.error(f"Error saving PDF URL for EIN {ein}: {e}")
            return False

if __name__ == '__main__':

    obj= BEV_Validation()
    obj.return_result()
