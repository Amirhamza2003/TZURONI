import json
import os
from typing import List
from .types import SiteMarket, UnifiedProduct
from .logging_config import get_logger

logger = get_logger(__name__)


def generate_sample_markets() -> List[SiteMarket]:
    """Generate sample prediction market data for testing"""
    
    sample_markets = [
        # Election markets
        SiteMarket(
            site="polymarket",
            id="trump-2024",
            title="Will Donald Trump win the 2024 US Presidential Election?",
            price=0.45,
            url="https://polymarket.com/event/trump-2024"
        ),
        SiteMarket(
            site="manifold",
            id="trump-election",
            title="Trump wins 2024 presidential election",
            price=0.42,
            url="https://manifold.markets/trump-2024"
        ),
        SiteMarket(
            site="predictit",
            id="president-2024",
            title="Who will win the 2024 US Presidential Election?",
            price=0.48,
            url="https://predictit.org/markets/2024-president"
        ),
        
        # Crypto markets
        SiteMarket(
            site="polymarket",
            id="btc-100k",
            title="Will Bitcoin reach $100,000 by end of 2024?",
            price=0.35,
            url="https://polymarket.com/event/btc-100k"
        ),
        SiteMarket(
            site="manifold",
            id="bitcoin-100k",
            title="Bitcoin reaches $100k by December 31, 2024",
            price=0.32,
            url="https://manifold.markets/bitcoin-100k"
        ),
        SiteMarket(
            site="predictit",
            id="crypto-bull",
            title="Will Bitcoin exceed $100,000 in 2024?",
            price=0.38,
            url="https://predictit.org/markets/bitcoin-100k"
        ),
        
        # Sports markets
        SiteMarket(
            site="polymarket",
            id="super-bowl-2025",
            title="Who will win Super Bowl LIX in 2025?",
            price=0.25,
            url="https://polymarket.com/event/super-bowl-2025"
        ),
        SiteMarket(
            site="manifold",
            id="superbowl-winner",
            title="Kansas City Chiefs win Super Bowl LIX",
            price=0.28,
            url="https://manifold.markets/superbowl-2025"
        ),
        
        # Technology markets
        SiteMarket(
            site="polymarket",
            id="ai-breakthrough",
            title="Will OpenAI release GPT-5 in 2024?",
            price=0.65,
            url="https://polymarket.com/event/gpt5-2024"
        ),
        SiteMarket(
            site="manifold",
            id="gpt5-release",
            title="OpenAI releases GPT-5 to the public in 2024",
            price=0.62,
            url="https://manifold.markets/gpt5-2024"
        ),
        SiteMarket(
            site="predictit",
            id="ai-advancement",
            title="Will GPT-5 be publicly released in 2024?",
            price=0.68,
            url="https://predictit.org/markets/gpt5-release"
        ),
        
        # Current events
        SiteMarket(
            site="polymarket",
            id="ukraine-peace",
            title="Will Russia and Ukraine sign a peace treaty in 2024?",
            price=0.15,
            url="https://polymarket.com/event/ukraine-peace"
        ),
        SiteMarket(
            site="manifold",
            id="russia-ukraine",
            title="Russia and Ukraine sign peace agreement in 2024",
            price=0.12,
            url="https://manifold.markets/ukraine-peace"
        ),
        
        # Entertainment
        SiteMarket(
            site="polymarket",
            id="oscars-2025",
            title="Who will win Best Picture at the 2025 Oscars?",
            price=0.18,
            url="https://polymarket.com/event/oscars-2025"
        ),
        SiteMarket(
            site="manifold",
            id="best-picture",
            title="Oppenheimer wins Best Picture at 2025 Oscars",
            price=0.22,
            url="https://manifold.markets/oscars-2025"
        ),
    ]
    
    logger.info(f"Generated {len(sample_markets)} sample markets for testing")
    return sample_markets


def create_sample_unified_products() -> List[UnifiedProduct]:
    """Create sample unified products for testing"""
    
    sample_markets = generate_sample_markets()
    
    # Group similar markets manually for testing
    unified_products = [
        UnifiedProduct(
            unified_title="Will Donald Trump win the 2024 US Presidential Election?",
            members=[
                sample_markets[0],  # polymarket
                sample_markets[1],  # manifold
                sample_markets[2],  # predictit
            ],
            confidence_scores=[1.0, 0.95, 0.90]
        ),
        UnifiedProduct(
            unified_title="Will Bitcoin reach $100,000 by end of 2024?",
            members=[
                sample_markets[3],  # polymarket
                sample_markets[4],  # manifold
                sample_markets[5],  # predictit
            ],
            confidence_scores=[1.0, 0.92, 0.88]
        ),
        UnifiedProduct(
            unified_title="Who will win Super Bowl LIX in 2025?",
            members=[
                sample_markets[6],  # polymarket
                sample_markets[7],  # manifold
            ],
            confidence_scores=[1.0, 0.85]
        ),
        UnifiedProduct(
            unified_title="Will OpenAI release GPT-5 in 2024?",
            members=[
                sample_markets[8],  # polymarket
                sample_markets[9],  # manifold
                sample_markets[10], # predictit
            ],
            confidence_scores=[1.0, 0.94, 0.91]
        ),
        UnifiedProduct(
            unified_title="Will Russia and Ukraine sign a peace treaty in 2024?",
            members=[
                sample_markets[11], # polymarket
                sample_markets[12], # manifold
            ],
            confidence_scores=[1.0, 0.87]
        ),
        UnifiedProduct(
            unified_title="Who will win Best Picture at the 2025 Oscars?",
            members=[
                sample_markets[13], # polymarket
                sample_markets[14], # manifold
            ],
            confidence_scores=[1.0, 0.89]
        ),
    ]
    
    logger.info(f"Created {len(unified_products)} unified product groups for testing")
    return unified_products


def run_test_mode(output_path: str = "data/output/test_products.csv") -> None:
    """Run the system in test mode with sample data"""
    
    logger.info("Running in TEST MODE with sample data")
    
    # Create sample unified products
    unified_products = create_sample_unified_products()
    
    # Export to CSV
    from .main import export_csv
    export_csv(unified_products, output_path)
    
    logger.info(f"Test mode completed. Generated {len(unified_products)} product groups")
    logger.info(f"Results saved to: {output_path}")
    
    return unified_products
