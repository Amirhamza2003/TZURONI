#!/usr/bin/env python3
"""
Demo script for the Prediction Market Chat Assistant
Shows how to use the RAG system to chat about products
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.rag_system import ProductRAG
from src.logging_config import setup_logging, get_logger


def demo_rag_queries():
    """Demonstrate RAG system with sample queries"""
    
    # Setup logging
    setup_logging("INFO", "logs/demo.log")
    logger = get_logger(__name__)
    
    print("🤖 Prediction Market Chat Demo")
    print("=" * 50)
    
    # Initialize RAG system
    print("🔄 Initializing RAG system...")
    rag_system = ProductRAG()
    
    # Check if we have products
    stats = rag_system.get_product_stats()
    if stats['total_products'] == 0:
        print("❌ No products found in RAG system.")
        print("Please run the main pipeline first:")
        print("   python -m src.main --mode local --limit 50")
        return
    
    print(f"✅ Loaded {stats['total_products']} products from {len(stats['sites_covered'])} sites")
    print()
    
    # Sample queries to demonstrate
    demo_queries = [
        "What are the current prices for Trump election markets?",
        "Show me crypto prediction markets",
        "What sports markets are available?",
        "Which markets have the highest confidence scores?",
        "Tell me about election prediction markets",
        "What are the latest technology prediction markets?",
        "Show me markets about current events"
    ]
    
    # Run demo queries
    for i, query in enumerate(demo_queries, 1):
        print(f"\n🔍 Demo Query {i}: {query}")
        print("-" * 40)
        
        try:
            response = rag_system.chat_about_products(query)
            print(response)
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"❌ Error: {e}")
        
        print()
    
    # Show system stats
    print("📊 Final System Statistics:")
    print("-" * 40)
    final_stats = rag_system.get_product_stats()
    for key, value in final_stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("\n🎉 Demo completed! You can now run the interactive chat:")
    print("   python -m src.chat_interface")


if __name__ == "__main__":
    demo_rag_queries()
