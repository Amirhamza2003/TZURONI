import argparse
import os
import csv
import json
import time
from typing import List

from .config import get_proxy, get_litellm_api_key
from .types import SiteMarket, UnifiedProduct
from .scrapers.polymarket import fetch_polymarket
from .scrapers.manifold import fetch_manifold
from .scrapers.predictit import fetch_predictit
from .agents import (
    make_data_collector_agent, 
    make_identifier_agent, 
    make_presenter_agent, 
    run_pipeline,
    run_crew_pipeline,
    create_collection_task,
    create_identification_task,
    create_presentation_task
)
from .logging_config import setup_logging, get_logger, MetricsTracker
from .rag_system import ProductRAG
from .test_mode import run_test_mode


def collect_all(limit: int, proxy: str | None, metrics: MetricsTracker) -> List[SiteMarket]:
    """Fallback: Collect data using local scrapers"""
    logger = get_logger(__name__)
    markets: List[SiteMarket] = []
    
    try:
        polymarket_markets = fetch_polymarket(limit=limit, proxy=proxy)
        markets.extend(polymarket_markets)
        logger.info(f"Collected {len(polymarket_markets)} markets from Polymarket")
        metrics.log_metric("sites_scraped", "polymarket")
    except Exception as e:
        logger.error(f"Error collecting from Polymarket: {e}")
        metrics.log_error(e, "polymarket_scraping")
    
    try:
        manifold_markets = fetch_manifold(limit=limit, proxy=proxy)
        markets.extend(manifold_markets)
        logger.info(f"Collected {len(manifold_markets)} markets from Manifold")
        metrics.log_metric("sites_scraped", "manifold")
    except Exception as e:
        logger.error(f"Error collecting from Manifold: {e}")
        metrics.log_error(e, "manifold_scraping")
    
    try:
        predictit_markets = fetch_predictit(limit=limit, proxy=proxy)
        markets.extend(predictit_markets)
        logger.info(f"Collected {len(predictit_markets)} markets from PredictIt")
        metrics.log_metric("sites_scraped", "predictit")
    except Exception as e:
        logger.error(f"Error collecting from PredictIt: {e}")
        metrics.log_error(e, "predictit_scraping")
    
    metrics.log_metric("markets_collected", len(markets))
    return markets


def export_csv(unified: List[UnifiedProduct], output_path: str) -> None:
    """Export unified products to CSV"""
    # Create directory if it doesn't exist and path has directory
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["unified_title", "site", "site_product_id", "price", "confidence"])
        for up in unified:
            for member, conf in zip(up.members, up.confidence_scores):
                writer.writerow([
                    up.unified_title,
                    member.site,
                    member.id,
                    "" if member.price is None else f"{member.price:.4f}",
                    f"{conf:.3f}",
                ])


def run_crewai_mode(sites: List[str], output_path: str) -> None:
    """Run the full CrewAI pipeline with browser automation"""
    print("Running CrewAI pipeline with browser automation...")
    
    # Check if API key is set
    api_key = get_litellm_api_key()
    if not api_key:
        print("Warning: LITELLM_API_KEY not set. Please set it in your .env file.")
        print("Falling back to local scraping mode...")
        return False
    
    try:
        # Run the CrewAI pipeline
        result = run_crew_pipeline(sites)
        
        # Parse the result and save to CSV
        # The result should be CSV format from the presenter agent
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            f.write(result)
        
        print(f"CrewAI pipeline completed. Results saved to {output_path}")
        return True
        
    except Exception as e:
        print(f"Error in CrewAI pipeline: {e}")
        print("Falling back to local scraping mode...")
        return False


def run_local_mode(limit: int, output_path: str, enable_rag: bool = True) -> None:
    """Run the local scraping and matching pipeline"""
    logger = get_logger(__name__)
    metrics = MetricsTracker()
    start_time = time.time()
    
    logger.info("Running local scraping and matching pipeline...")
    
    proxy = get_proxy()
    
    # Collect data using local scrapers
    collected = collect_all(limit=limit, proxy=proxy, metrics=metrics)
    logger.info(f"Total collected markets: {len(collected)}")
    
    if not collected:
        logger.warning("No markets collected. Exiting.")
        return
    
    # Match and unify products
    unified = run_pipeline(collected)
    logger.info(f"Created {len(unified)} unified product groups")
    metrics.log_metric("unified_products", len(unified))
    
    # Export to CSV
    export_csv(unified, output_path)
    logger.info(f"Wrote {sum(len(u.members) for u in unified)} rows to {output_path}")
    
    # Initialize RAG system if enabled
    if enable_rag:
        try:
            logger.info("Initializing RAG system...")
            rag_system = ProductRAG()
            rag_system.add_products(unified)
            logger.info("RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            metrics.log_error(e, "rag_initialization")
    
    # Log final metrics
    processing_time = time.time() - start_time
    metrics.log_metric("processing_time", processing_time)
    
    summary = metrics.get_summary()
    logger.info(f"Pipeline completed in {processing_time:.2f} seconds")
    logger.info(f"Final metrics: {summary}")


def main() -> None:
    parser = argparse.ArgumentParser(description="CrowdWisdomTrading AI Agent - Prediction Market Unifier")
    parser.add_argument("--output", default="data/output/unified_products.csv", help="Output CSV file path")
    parser.add_argument("--limit", type=int, default=150, help="Maximum markets to fetch per site")
    parser.add_argument("--sites", nargs="+", default=["polymarket.com", "prediction-market.com", "kalshi.com"], 
                       help="Sites to scrape")
    parser.add_argument("--mode", choices=["crewai", "local", "auto", "test"], default="auto",
                       help="Run mode: crewai (browser automation), local (API scraping), auto (try crewai first), test (sample data)")
    parser.add_argument("--log-file", default="logs/pipeline.log", help="Log file path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG system initialization")
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = get_logger(__name__)

    logger.info("=== CrowdWisdomTrading AI Agent ===")
    logger.info(f"Output: {args.output}")
    logger.info(f"Limit: {args.limit} markets per site")
    logger.info(f"Sites: {', '.join(args.sites)}")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"RAG enabled: {not args.no_rag}")

    if args.mode == "crewai":
        success = run_crewai_mode(args.sites, args.output)
        if not success:
            logger.error("CrewAI mode failed. Exiting.")
            return
    elif args.mode == "local":
        run_local_mode(args.limit, args.output, enable_rag=not args.no_rag)
    elif args.mode == "test":
        logger.info("Running in TEST MODE with sample data")
        unified_products = run_test_mode(args.output)
        if not args.no_rag:
            try:
                logger.info("Initializing RAG system with test data...")
                rag_system = ProductRAG()
                rag_system.add_products(unified_products)
                logger.info("RAG system initialized successfully with test data")
            except Exception as e:
                logger.error(f"Failed to initialize RAG system: {e}")
    else:  # auto mode
        success = run_crewai_mode(args.sites, args.output)
        if not success:
            run_local_mode(args.limit, args.output, enable_rag=not args.no_rag)


if __name__ == "__main__":
    main()
