from src.BEV_Details.sql_db_operation import execute_query,fetch_query
from src.login import logger




class BEVDetailReportGenerationSaveDB:
    def __init__(self):
        pass
        

    def get_pdf_url_by_ein(ein):
        """
        Retrieve PDF URL by EIN from url_links table
        
        Args:
            ein (str): EIN number
            
        Returns:
            str: PDF URL if found, None otherwise
        """
        try:
            query = "SELECT url FROM url_links WHERE ein = ?"
            result = fetch_query(query, (ein,))
            
            if result:
                logger.info(f"✅ Retrieved PDF URL for EIN: {ein}")
                return result[0]['url']
            else:
                logger.warning(f"⚠️ No PDF URL found for EIN: {ein}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving PDF URL for EIN {ein}: {e}")
            return None
        

    def insert_report_generated(self, ein, order_id, generated_report_url):
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
        insert_query = """
        INSERT INTO reportgenerated (ein, order_id, generated_report_url) 
        VALUES (?, ?, ?)
        """
        
        try:
            execute_query(insert_query, (ein, order_id, generated_report_url))
            logger.info(f"✅ Successfully inserted report: EIN={ein}, Order_ID={order_id}, URL={generated_report_url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to insert report: EIN={ein}, Order_ID={order_id}, URL={generated_report_url}, Error: {e}")
            raise e   



    def get_generated_report_by_ein_order(self, ein, order_id):
        """
        Retrieve generated report URL by EIN and order_id from reportgenerated table
        
        Args:
            ein (str): EIN number
            order_id (str): Order ID
            
        Returns:
            str: Generated report URL if found, None otherwise
        """
        try:
            query = "SELECT generated_report_url FROM reportgenerated WHERE ein = ? AND order_id = ?"
            result = fetch_query(query, (ein, order_id))
            
            if result:
                logger.info(f"✅ Retrieved generated report for EIN: {ein}, Order_ID: {order_id}")
                return result[0]['generated_report_url']
            else:
                logger.warning(f"⚠️ No generated report found for EIN: {ein}, Order_ID: {order_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving generated report for EIN {ein}, Order_ID {order_id}: {e}")
            return None       