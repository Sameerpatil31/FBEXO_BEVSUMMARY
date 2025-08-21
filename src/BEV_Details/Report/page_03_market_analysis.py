# import streamlit as st
from agno.agent import Agent
# from agno.models.openai import OpenAIChat
# from agno.models.azure import ai_foundry
from src.login import logger
# from agno.models.azure import AzureOpenAI
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.team import Team
from agno.models.azure import AzureOpenAI
from agno.tools.serpapi import SerpApiTools
from agno.tools.reasoning import ReasoningTools
from src.BEV_Details.sql_db_operation import fetch_query
from src.LLM.azure_openai import AzureOpenAIClient
from sqlalchemy import text
import os
import json
from dotenv import load_dotenv
load_dotenv()



class MarketAnalysisReportGeneration:
    def __init__(self, report_data):
        self.report_data = report_data
        # self.azure_client = AzureOpenAIClient()
        # self.client_ = self.azure_client.get_client()
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("ENDPOINT_URL"),
            azure_deployment=os.getenv("DEPLOYMENT_NAME"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version='2024-12-01-preview',
        )



    def market_analysis_research_agent(self) -> str:
        try:
            query = text("SELECT [market_analysis_research_agent] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for market analysis research agent")
                return None
            return result[0]['market_analysis_research_agent']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching market analysis research agent data: {e}")
            return None

    def market_analysis_writer_agent(self) -> str:
        try:
            query = text("SELECT [market_analysis_writer_agent] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for market analysis writer agent")
                return None
            return result[0]['market_analysis_writer_agent']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching market analysis writer agent data: {e}")
            return None
        

    def market_analysis_team_agent(self) -> str:
        try:
            query = text("SELECT [market_analysis_team_agents] FROM prompt_valuation_reports WHERE id = :id")
            params = {"id": 1}
            result = fetch_query(query, params)
            if not result:
                logger.error("No data found for market analysis team agents")
                return None
            return result[0]['market_analysis_team_agents']  # Assuming we want the first record
        except Exception as e:
            logger.error(f"Error fetching market analysis team agents data: {e}")
            return None

    def market_analysis_report(self,topic, research_agent_prompt,writer_agent_prompt, team_agent_prompt):
        """
        Generates a market analysis report dynamically based on the user's topic and instructions.
        """
        
        # azure_model_config= AzureOpenAI(
        #     azure_endpoint=os.getenv("ENDPOINT_URL"),
        #     azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        #     api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        #     api_version="2025-01-01-preview"
        # )

    
        # # Configure the LLM model
        # model_config = OpenAIChat(
        #     id=os.getenv("openai_model"),
        #     api_key=os.getenv("open_api_key"),
        # )

        # Define web agent for market research
        web_agent = Agent(
            name="Web Agent Researcher",
            role="Market Researcher from Internet",
            model=self.client,
            tools=[SerpApiTools(api_key=os.getenv("SerpApi")),DuckDuckGoTools()],
            instructions=research_agent_prompt,
            markdown=True,  # Enable markdown rendering for the response
        )

        # Define finance report writer agent
        finance_report_writer_agent = Agent(
            name="Finance Report Writer Agent",
            role="Senior Market Analyst",
            model=self.client,
            tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True),ReasoningTools(add_instructions=True),],
            instructions=writer_agent_prompt,reasoning=True,markdown=True,
        )

        # Combine agents into a team
        agent_team = Team(
            members=[web_agent, finance_report_writer_agent],
            model=self.client,
            instructions=team_agent_prompt,
            reasoning=True
        )

        try:
            # Run the team to generate the report
            response = agent_team.run(
                f"""{topic} US - Market Research Report (2014-2029)""",
            # stream=True # Enable streaming and markdown rendering
            )
            return response.content  # Return the generated HTML report
        except Exception as e:
            # st.error(f"Error occurred: {str(e)}")
            print(f"Error occurred: {str(e)}")
            return None
        

    def generate_report(self):
        try:
            # Implement report generation logic here
            research_agent_prompt = self.market_analysis_research_agent()
            writer_agent_prompt = self.market_analysis_writer_agent()
            team_agent_prompt = self.market_analysis_team_agent()

            if not research_agent_prompt or not writer_agent_prompt or not team_agent_prompt:
                logger.error("Failed to fetch required prompts for market analysis")
                return None

            # Parse the JSON string to get the actual company info
            company_info = json.loads(self.report_data['company_info'])
            industry = company_info.get('industry', 'General Business')

            return self.market_analysis_report(
                topic=industry,
                research_agent_prompt=research_agent_prompt,
                writer_agent_prompt=writer_agent_prompt,
                team_agent_prompt=team_agent_prompt
            )
        except Exception as e:
            logger.error(f"Error generating market analysis report: {e}")
            return None