from src.BEV_Details.Report.page_01_executive_summary import ExecutiveSummaryReportGeneration
from src.BEV_Details.Report.page_02_about_industry import AboutIndustryReportGeneration
from src.BEV_Details.Report.page_03_market_analysis import MarketAnalysisReportGeneration
from src.BEV_Details.Report.page_04_FNL import Page04ReportGeneration
from src.BEV_Details.Report.page_05_BalanceSheetAnalysis import Page05ReportGeneration
from src.BEV_Details.Report.page_6_cashflow import Page06CashFlowReportGeneration
from src.BEV_Details.Report.page_7_ValuationAnalyzer import ValuationAnalyzer
from src.BEV_Details.Report.page_8_DCFCalculator import DCFCalculator
from src.BEV_Details.Report.page_9_CCACalculator import CCACalculator
from src.BEV_Details.Report.page_10_hc_assessment import HumanCapitalAssessment
from src.BEV_Details.Report.page_11_OperationalAssessment import OperationalAssessmentTool
from src.BEV_Details.Report.page_12_LegalCompliance import LegalComplianceAssessmentTool
from src.BEV_Details.Report.page_13_RiskAssessment import RiskAssessmentTool
from src.BEV_Details.Data_Extraction_File import CompanyReport,PDFCompanyExtractor
from src.login import logger
import pdfkit



class ReportGenerationPipeline:
    def __init__(self,file_path:list):
        try:
            self.file_path = file_path
            self.company_extractor = PDFCompanyExtractor()
            self.company_report = self.company_extractor.extract_all(self.file_path)
            print("Company report extracted successfully.")
            print(self.company_report)
        except Exception as e:
            logger.error(f"Error initializing ReportGenerationPipeline: {e}")

    def generate_reports(self):
        try:
            page01 = ""
            executive_summary = ExecutiveSummaryReportGeneration(self.company_report)
            page01 = executive_summary.finance_report()
            
        except Exception as e:
            logger.error(f"Error generating Executive Summary report: {e}")
            page01 = ""

        try:
            page02 = ""
            about_industry = AboutIndustryReportGeneration(self.company_report)
            page02 = about_industry.generate_report_for_industry()
            
        except Exception as e:
            logger.error(f"Error generating About Industry report: {e}")
            page02 = ""

        try:
            page03 = ""
            market_analysis = MarketAnalysisReportGeneration(self.company_report)
            page03 = market_analysis.generate_report()
            
        except Exception as e:
            logger.error(f"Error generating Market Analysis report: {e}")
            page03 = ""

        try:
            page04 = ""
            page_04 = Page04ReportGeneration(self.company_report)
            page04 = page_04.generate_report()
        except Exception as e:
            logger.error(f"Error generating Page 04 report: {e}")
            page04 = ""

        try:
            page05 = ""
            page_05 = Page05ReportGeneration(self.company_report)
            page05 = page_05.generate_report()
        except Exception as e:
            logger.error(f"Error generating Page 05 report: {e}")
            page05 = ""

        try:
            page06 = ""
            page_06 = Page06CashFlowReportGeneration(self.company_report)
            page06 = page_06.generate_report()
        except Exception as e:
            logger.error(f"Error generating Page 06 report: {e}")
            page06 = ""

        try:
            page07 = ""
            page_07 = ValuationAnalyzer(self.company_report)
            page07 = page_07.generate_report()
        except Exception as e:
            logger.error(f"Error generating Page 07 report: {e}")
            page07 = ""

        try:
            page08 = ""
            page_08 = DCFCalculator(self.company_report)
            page08 = page_08.generate_report()
        except Exception as e:
            logger.error(f"Error generating Page 08 report: {e}")
            page08 = ""

        try:
            page09 = ""
            page_09 = CCACalculator(self.company_report)
            page09 = page_09.generate_cca_report()
        except Exception as e:
            logger.error(f"Error generating Page 09 report: {e}")
            page09 = ""

        try:
            page10 = ""
            page_10 = HumanCapitalAssessment(self.company_report)
            page10 = page_10.generate_report()
        except Exception as e:
            logger.error(f"Error generating Page 10 report: {e}")
            page10 = ""

        try:
            page11 = ""
            page_11 = OperationalAssessmentTool()
            page11 = page_11.generate_report()
        except Exception as e:
            logger.error(f"Error generating Page 11 report: {e}")
            page11 = ""

        try:
            page12 = ""
            page_12 = LegalComplianceAssessmentTool()
            page12 = page_12.generate_all()
        except Exception as e:
            logger.error(f"Error generating Page 12 report: {e}")
            page12 = ""

        try:
            page13 = ""
            page_13 = RiskAssessmentTool()
            page13 = page_13.generate_all()
        except Exception as e:
            logger.error(f"Error generating Page 13 report: {e}")
            page13 = ""

        return {
            "page01": page01,
            "page02": page02,
            "page03": page03,
            "page04": page04,
            "page05": page05,
            "page06": page06,
            "page07": page07,
            "page08": page08,
            "page09": page09,
            "page10": page10,
            "page11": page11,
            "page12": page12,
            "page13": page13
        }    

        



if __name__ == "__main__":
    file_path = r"D:\Client_pro\Fiverr\USA\Notebook\Data\Resume25022025.pdf"
    output_pdf_path = r"D:\Client_pro\Fiverr\USA\Notebook\Data\Resume25022025_outputREPORT.pdf"
    report_pipeline = ReportGenerationPipeline(file_path)
    reports = report_pipeline.generate_reports()
    if reports:
            # default numeric order: page01, page02, … page13
        page_order = [f"page{str(i).zfill(2)}" for i in range(1, 14)]

        # 3) concatenate all HTML snippets
        full_html = ""
        for key in page_order:
            html = reports.get(key, "")
            if html:
                # you may want to wrap each page in a <div style="page-break-after: always;"> … </div>
                full_html += f'<div style="page-break-after: always;">{html}</div>'

        # 4) render to PDF
        # make sure you have wkhtmltopdf installed and on PATH
        pdfkit.from_string(full_html, output_pdf_path)
    logger.info("All reports generated successfully.")