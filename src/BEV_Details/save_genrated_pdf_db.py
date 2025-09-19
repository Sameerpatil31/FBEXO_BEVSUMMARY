from src.BEV_Details.sql_db_operation import execute_query,fetch_query,fetch_query_one
from src.login import logger
from sqlalchemy import text
import ast


class BEVDetailReportGenerationSaveDB:
    def __init__(self, ein, order_id):
        self.ein = ein
        self.order_id = order_id

 

    # def get_pdf_url_by_ein(self):
    #     try:
    #         query = text("SELECT url FROM url_links WHERE ein = :ein")
    #         result = fetch_query(query, {"ein": self.ein})

    #         if result and len(result) > 0:
    #             url_value = result[0]['url'] if isinstance(result[0], dict) else result[0][0]

    #             # If url_value is JSON stored as string, parse it
    #             if isinstance(url_value, str):
    #                 import json
    #                 url_value = json.loads(url_value)

    #             logger.info(f"Retrieved PDF URL for EIN {self.ein}: {url_value}")

    #             # Access Business_Incorporation directly
    #             pdf_url = url_value.get("Business_Incorporation")
    #             if pdf_url:
    #                 print("pdf_url:", pdf_url)
    #                 return pdf_url
    #             else:
    #                 logger.warning(f"No Business_Incorporation key found for EIN {self.ein}")
    #                 return None

    #         else:
    #             logger.warning(f"No PDF URL found for EIN: {self.ein}")
    #             return None

    #     except Exception as e:
    #         logger.error(f"Error retrieving PDF URL for EIN {self.ein}: {e}")
    #         return None

    def get_pdf_url_by_ein(self)->list:
        try:
            query = text("SELECT url FROM url_links WHERE ein = :ein")
            result = fetch_query(query, {"ein": self.ein})

            if result and len(result) > 0:
                url_value = result[0]['url'] if isinstance(result[0], dict) else result[0][0]

                # If url_value is JSON stored as string, parse it
                if isinstance(url_value, str):
                    import json
                    url_value = json.loads(url_value)

                logger.info(f"Retrieved URL data for EIN {self.ein}: {url_value}")

                # Collect only valid URLs (values that are strings starting with http)
                if isinstance(url_value, dict):
                    all_urls = [v for v in url_value.values() if isinstance(v, str) and v.startswith("http")]
                    if all_urls:
                        print("all_urls:", all_urls)
                        return all_urls
                    else:
                        logger.warning(f"No valid URLs found for EIN {self.ein}")
                        return []
                else:
                    logger.warning(f"URL data for EIN {self.ein} is not a dictionary")
                    return []

            else:
                logger.warning(f"No URL found for EIN: {self.ein}")
                return []

        except Exception as e:
            logger.error(f"Error retrieving URLs for EIN {self.ein}: {e}")
            return []

    def insert_report_generated(self, generated_report_url):
        """
        Insert a single record into reportgenerated table
        
        Args:
            ein (str): EIN number
            order_id (str): Order ID
            generated_report_url (str): Generated report URL
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            Exception: If insertion fails
        """
        insert_query = text("""
        INSERT INTO reportgenerated (ein, order_id, generated_report_url) 
        VALUES (:ein, :order_id, :generated_report_url)
        """)

        try:
            execute_query(insert_query, {"ein": self.ein, "order_id": self.order_id, "generated_report_url": generated_report_url})
            logger.info(f"✅ Successfully inserted report: EIN={self.ein}, Order_ID={self.order_id}, URL={generated_report_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to insert report: EIN={self.ein}, Order_ID={self.order_id}, URL={generated_report_url}, Error: {e}")
            raise e



    def get_generated_report_by_ein_order(self):
        """
        Retrieve generated report URL by EIN and order_id from reportgenerated table
        
        Args:
            ein (str): EIN number
            order_id (str): Order ID
            
        Returns:
            str: Generated report URL if found, None otherwise
        """
        try:
            query = text("SELECT generated_report_url FROM reportgenerated WHERE ein = :ein AND order_id = :order_id")
            result = fetch_query(query, {"ein": self.ein, "order_id": self.order_id})

            if result:
                logger.info(f"✅ Retrieved generated report for EIN: {self.ein}, Order_ID: {self.order_id}")
                return result[0]['generated_report_url']
            else:
                logger.warning(f"⚠️ No generated report found for EIN: {self.ein}, Order_ID: {self.order_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving generated report for EIN {self.ein}, Order_ID {self.order_id}: {e}")
            return None




if "__name__" == "__main__":
    ein = "320510248"
    order_id = 3837
    bev_db = BEVDetailReportGenerationSaveDB(ein=ein, order_id=order_id)
    pdf_url = bev_db.get_pdf_url_by_ein()

