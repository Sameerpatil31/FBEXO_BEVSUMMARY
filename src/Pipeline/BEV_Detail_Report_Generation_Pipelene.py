# from src.BEV_Details.Pipeline.report_generation_pipeline import ReportGenerationPipeline

# from src.login import logger
# import pdfkit




# class BEVReportGeneration:
#     def __init__(self, file_path_or_url, output_pdf_path):
#         self.file_path_or_url = file_path_or_url
#         self.output_pdf_path = output_pdf_path

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

# if __name__ == "__main__":
#     file_path = r"D:\Client_pro\Fiverr\USA\Notebook\Data\GM2023FinStatements.pdf"
#     output_pdf_path = r"D:\Client_pro\Fiverr\USA\Notebook\Data\GM2023FinStatements_outputREPORT.pdf"

#     report_generator = BEVReportGeneration(file_path, output_pdf_path)
#     report_generator.generate_report_pipeline()

#     # report_pipeline = ReportGenerationPipeline(file_path)
#     # reports = report_pipeline.generate_reports()
#     # if reports:
#     #         # default numeric order: page01, page02, … page13
#     #     page_order = [f"page{str(i).zfill(2)}" for i in range(1, 14)]

#     #     # 3) concatenate all HTML snippets
#     #     full_html = ""
#     #     for key in page_order:
#     #         html = reports.get(key, "")
#     #         if html:
#     #             # you may want to wrap each page in a <div style="page-break-after: always;"> … </div>
#     #             full_html += f'<div style="page-break-after: always;">{html}</div>'

#     #     # 4) render to PDF
#     #     # make sure you have wkhtmltopdf installed and on PATH
#     # pdfkit.from_string(full_html, output_pdf_path)
#     # logger.info("All reports generated successfully.")


from src.BEV_Details.Pipeline.reportupload_pipeline import BEVReportUpload


class BEVDetailReportGenerationPipeline:
    def __init__(self, file_path_or_url):  
        self.file_path_or_url = file_path_or_url

    def run_pipeline(self):
        report_uploader = BEVReportUpload(self.file_path_or_url)
        return report_uploader.generate_report_pipeline()
    




