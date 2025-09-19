# from src.BEV_Details.Pipeline.report_generation_pipeline import ReportGenerationPipeline
# from src.BEV_Details.S3_Bucket_upload import s3_upload
# from src.login import logger
# import pdfkit




# class BEVReportUpload:
#     def __init__(self, file_path_or_url, output_pdf_path):
#         self.file_path_or_url = file_path_or_url
#         self.output_pdf_path = output_pdf_path
#         self.s3_uploader = s3_upload()


#     def generate_report_pipeline(self):
#         report_pipeline = ReportGenerationPipeline(self.file_path_or_url)
#         reports = report_pipeline.generate_reports()
        
#         if reports:
#             logger.info(f"Generated reports: {list(reports.keys())}")
#             # Log which reports have content
#             for key, value in reports.items():
#                 if value and value != "":
#                     logger.info(f"{key}: Content generated successfully")
#                 else:
#                     logger.warning(f"{key}: No content or empty")
            
#             # default numeric order: page01, page02, … page13
#             page_order = [f"page{str(i).zfill(2)}" for i in range(1, 14)]

#             # 3) concatenate all HTML snippets
#             full_html = ""
#             pages_added = 0
#             for key in page_order:
#                 html = reports.get(key, "")
#                 if html and html != "":
#                     # you may want to wrap each page in a <div style="page-break-after: always;"> … </div>
#                     full_html += f'<div style="page-break-after: always;">{html}</div>'
#                     pages_added += 1
#                     logger.info(f"Added {key} to PDF")
#                 else:
#                     logger.warning(f"Skipped {key} - no content")

#             if full_html:
#                 # 4) render to PDF
#                 # make sure you have wkhtmltopdf installed and on PATH
#                 pdfkit.from_string(full_html, self.output_pdf_path)
#                 logger.info(f"Report generated successfully with {pages_added} pages: {self.output_pdf_path}")
#             else:
#                 logger.error("No content to generate PDF")
#         else:
#             logger.error("No reports generated")
        
#         logger.info("Report generation pipeline completed.")



    
# # if __name__ == "__main__":
# #     file_path = r"D:\Client_pro\Fiverr\USA\Notebook\Data\GM2023FinStatements.pdf"
# #     output_pdf_path = r"D:\Client_pro\Fiverr\USA\Notebook\Data\GM2023FinStatements_outputREPORT.pdf"

# #     report_generator = BEVReportGeneration(file_path, output_pdf_path)
# #     report_generator.generate_report_pipeline()

from src.BEV_Details.Pipeline.report_generation_pipeline import ReportGenerationPipeline
from src.BEV_Details.S3_Bucket_upload import s3_upload
from src.login import logger
import pdfkit
import tempfile
import os
import uuid
from datetime import datetime

class BEVReportUpload:
    def __init__(self, file_path_or_url:list, output_pdf_filename=None):
        self.file_path_or_url = file_path_or_url
        self.s3_uploader = s3_upload()
        
        # Generate unique filename if not provided
        if output_pdf_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            self.output_pdf_filename = f"BEV_Report_{timestamp}_{unique_id}.pdf"
        else:
            self.output_pdf_filename = output_pdf_filename
        
        # Create temporary directory for PDF storage
        self.temp_dir = tempfile.mkdtemp(prefix="bev_reports_")
        self.output_pdf_path = os.path.join(self.temp_dir, self.output_pdf_filename)
        
        logger.info(f"Temporary directory created: {self.temp_dir}")
        logger.info(f"PDF will be saved as: {self.output_pdf_path}")

    def generate_report_pipeline(self, ein):
        """
        Generate the report pipeline and upload to S3.
        Returns the S3 public URL of the uploaded PDF.
        """
        try:
            report_pipeline = ReportGenerationPipeline(self.file_path_or_url)
            reports = report_pipeline.generate_reports()
            
            if reports:
                logger.info(f"Generated reports: {list(reports.keys())}")
                # Log which reports have content
                for key, value in reports.items():
                    if value and value != "":
                        logger.info(f"{key}: Content generated successfully")
                    else:
                        logger.warning(f"{key}: No content or empty")
                
                # default numeric order: page01, page02, … page13
                page_order = [f"page{str(i).zfill(2)}" for i in range(1, 14)]

                # 3) concatenate all HTML snippets
                full_html = ""
                pages_added = 0
                for key in page_order:
                    html = reports.get(key, "")
                    if html and html != "":
                        # you may want to wrap each page in a <div style="page-break-after: always;"> … </div>
                        full_html += f'<div style="page-break-after: always;">{html}</div>'
                        pages_added += 1
                        logger.info(f"Added {key} to PDF")
                    else:
                        logger.warning(f"Skipped {key} - no content")

                if full_html:
                    # 4) render to PDF in temporary directory
                    # make sure you have wkhtmltopdf installed and on PATH
                    pdfkit.from_string(full_html, self.output_pdf_path)
                    logger.info(f"Report generated successfully with {pages_added} pages: {self.output_pdf_path}")
                    
                    # 5) Upload to S3 and get public URL
                    s3_url = self.upload_to_s3(ein=ein)

                    # 6) Cleanup temporary files
                    self.cleanup_temp_files()
                    
                    return s3_url
                    
                else:
                    logger.error("No content to generate PDF")
                    self.cleanup_temp_files()
                    return None
            else:
                logger.error("No reports generated")
                self.cleanup_temp_files()
                return None
                
        except Exception as e:
            logger.error(f"Error in report generation pipeline: {str(e)}")
            self.cleanup_temp_files()
            return None
        
        finally:
            logger.info("Report generation pipeline completed.")

    def upload_to_s3(self, ein):
        """
        Upload the generated PDF to S3 bucket and return public URL.
        """
        try:
            if not os.path.exists(self.output_pdf_path):
                logger.error(f"PDF file not found: {self.output_pdf_path}")
                return None
            
            logger.info(f"Uploading PDF to S3: {self.output_pdf_path}")
            
            # Upload to S3 using the s3_upload function
            s3_url = self.s3_uploader.s3_upload_generated_pdf_report(
                ein=ein,
                url=self.output_pdf_path
            )
            
            if s3_url:
                logger.info(f"PDF successfully uploaded to S3: {s3_url}")
                return s3_url
            else:
                logger.error("Failed to upload PDF to S3")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return None

    def cleanup_temp_files(self):
        """
        Clean up temporary files and directory.
        """
        try:
            if os.path.exists(self.output_pdf_path):
                os.remove(self.output_pdf_path)
                logger.info(f"Removed temporary PDF file: {self.output_pdf_path}")
            
            if os.path.exists(self.temp_dir):
                os.rmdir(self.temp_dir)
                logger.info(f"Removed temporary directory: {self.temp_dir}")
                
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")

    def get_temp_pdf_path(self):
        """
        Get the temporary PDF file path (useful for debugging).
        """
        return self.output_pdf_path

# Usage example
if __name__ == "__main__":
    # Example usage
    file_path_or_url = "https://your-bucket.s3.amazonaws.com/path/to/input.pdf"
    # or local file path: r"D:\Client_pro\Fiverr\USA\Notebook\Data\GM2023FinStatements.pdf"
    
    report_uploader = BEVReportUpload(file_path_or_url)
    s3_public_url = report_uploader.generate_report_pipeline()
    
    if s3_public_url:
        print(f"Report successfully generated and uploaded: {s3_public_url}")
    else:
        print("Failed to generate or upload report")