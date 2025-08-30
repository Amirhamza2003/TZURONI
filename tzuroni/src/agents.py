import os
import json
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from litellm import completion
from .types import SiteMarket, UnifiedProduct
from .matching import cluster_markets
from .config import get_litellm_model, get_litellm_api_key


def make_data_collector_agent() -> Agent:
    """Agent 1: X Data Collector - Scrapes data from prediction market sites"""
    return Agent(
        role="X Data Collector",
        goal="Scrape and collect prediction market data from multiple websites using browser tools",
        backstory="""You are an expert data collector specializing in prediction markets. 
        You use browser automation tools to scrape data from various prediction market platforms 
        and return structured JSON data.""",
        verbose=True,
        llm_model=get_litellm_model(),
        allow_delegation=False
    )


def make_identifier_agent() -> Agent:
    """Agent 2: Product Identifier - Identifies and matches similar products"""
    return Agent(
        role="Product Identifier",
        goal="Analyze collected data and identify which markets represent the same product across different sites",
        backstory="""You are an expert market analyst who specializes in identifying 
        similar prediction markets across different platforms. You use semantic analysis 
        and pattern matching to determine if markets are the same product.""",
        verbose=True,
        llm_model=get_litellm_model(),
        allow_delegation=False
    )


def make_presenter_agent() -> Agent:
    """Agent 3: Presenter - Creates unified CSV output"""
    return Agent(
        role="Presenter",
        goal="Create a unified CSV report with product prices across different sites and confidence scores",
        backstory="""You are a data presentation specialist who creates clear, 
        comprehensive reports from unified market data. You ensure the output is 
        well-formatted and includes all necessary information.""",
        verbose=True,
        llm_model=get_litellm_model(),
        allow_delegation=False
    )


def create_collection_task(agent: Agent, sites: List[str]) -> Task:
    """Task for Agent 1: Collect data from prediction market sites"""
    return Task(
        description=f"""Collect prediction market data from the following sites: {', '.join(sites)}
        
        For each site, you need to:
        1. Navigate to the site using browser tools
        2. Extract market information including:
           - Market ID/identifier
           - Market title/question
           - Current price/probability
           - Market URL
        3. Return the data in JSON format with structure:
           {{
             "site": "site_name",
             "id": "market_id", 
             "title": "market_title",
             "price": 0.75,
             "url": "market_url"
           }}
        
        Focus on active markets and ensure you collect at least 50 markets per site.
        """,
        agent=agent,
        expected_output="JSON array of market objects with site, id, title, price, and url fields"
    )


def create_identification_task(agent: Agent, collected_data: str) -> Task:
    """Task for Agent 2: Identify and match similar products"""
    return Task(
        description=f"""Analyze the following collected market data and identify which markets 
        represent the same product across different sites:
        
        {collected_data}
        
        Your analysis should:
        1. Compare market titles for semantic similarity
        2. Consider market context and subject matter
        3. Group similar markets together
        4. Assign confidence scores (0-1) for matches
        5. Choose a representative title for each group
        
        Return your analysis as JSON with structure:
        {{
          "unified_products": [
            {{
              "unified_title": "representative_title",
              "members": [
                {{
                  "site": "site_name",
                  "id": "market_id",
                  "title": "original_title", 
                  "price": 0.75,
                  "confidence": 0.95
                }}
              ]
            }}
          ]
        }}
        """,
        agent=agent,
        expected_output="JSON object with unified_products array containing matched markets"
    )


def create_presentation_task(agent: Agent, unified_data: str) -> Task:
    """Task for Agent 3: Create CSV output"""
    return Task(
        description=f"""Create a unified CSV report from the following matched market data:
        
        {unified_data}
        
        The CSV should have these columns:
        - unified_title: The representative title for the product group
        - site: Source website name
        - site_product_id: Original market ID from the site
        - price: Current price/probability (0-1 scale)
        - confidence: Confidence score for the match (0-1)
        
        Ensure the CSV is properly formatted and includes all market entries.
        Sort by unified_title for better readability.
        """,
        agent=agent,
        expected_output="CSV formatted string with headers and all market data rows"
    )


def run_crew_pipeline(sites: List[str] = None) -> str:
    """Run the complete CrewAI pipeline"""
    if sites is None:
        sites = ["polymarket.com", "prediction-market.com", "kalshi.com"]
    
    # Create agents
    collector = make_data_collector_agent()
    identifier = make_identifier_agent()
    presenter = make_presenter_agent()
    
    # Create tasks
    collection_task = create_collection_task(collector, sites)
    identification_task = create_identification_task(identifier, "{{collection_result}}")
    presentation_task = create_presentation_task(presenter, "{{identification_result}}")
    
    # Create crew
    crew = Crew(
        agents=[collector, identifier, presenter],
        tasks=[collection_task, identification_task, presentation_task],
        verbose=True,
        process=Process.sequential
    )
    
    # Execute
    result = crew.kickoff()
    return result


def run_pipeline(collected: List[SiteMarket]) -> List[UnifiedProduct]:
    """Fallback pipeline using local matching logic"""
    return cluster_markets(collected)
