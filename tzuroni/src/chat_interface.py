import argparse
import sys
from typing import Optional
from .rag_system import ProductRAG
from .logging_config import get_logger, setup_logging

logger = get_logger(__name__)


class PredictionMarketChat:
    """Interactive chat interface for prediction markets"""
    
    def __init__(self, rag_system: ProductRAG):
        self.rag = rag_system
        self.conversation_history = []
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("🤖 Welcome to the Prediction Market Chat Assistant!")
        print("Ask me about prediction markets, prices, or specific topics.")
        print("Type 'help' for commands, 'stats' for system info, or 'quit' to exit.")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye! Thanks for chatting about prediction markets!")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'stats':
                    self._show_stats()
                    continue
                
                if user_input.lower() == 'history':
                    self._show_history()
                    continue
                
                # Process the query
                response = self._process_query(user_input)
                print(f"\n🤖 Assistant: {response}")
                
                # Store in history
                self.conversation_history.append({
                    'user': user_input,
                    'assistant': response,
                    'timestamp': self._get_timestamp()
                })
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error in chat: {e}")
                print(f"\n❌ Sorry, I encountered an error: {e}")
    
    def _process_query(self, query: str) -> str:
        """Process a user query and return a response"""
        logger.info(f"Processing query: {query}")
        
        # Use RAG system to get response
        response = self.rag.chat_about_products(query)
        
        # Add some personality and context
        if "couldn't find" in response.lower():
            response += "\n\n💡 Tip: Try asking about specific topics like elections, crypto, sports, or current events!"
        
        return response
    
    def _show_help(self):
        """Show help information"""
        help_text = """
📋 Available Commands:
• help - Show this help message
• stats - Show system statistics
• history - Show conversation history
• quit/exit/q - Exit the chat

💡 Example Questions:
• "What are the current prices for Trump election markets?"
• "Show me crypto prediction markets"
• "What sports markets are available?"
• "Which markets have the highest confidence scores?"
• "Tell me about election prediction markets"

🔍 The system searches across multiple prediction market platforms including:
• Polymarket
• Manifold
• PredictIt
• And more!
        """
        print(help_text)
    
    def _show_stats(self):
        """Show system statistics"""
        stats = self.rag.get_product_stats()
        
        stats_text = f"""
📊 System Statistics:
• Total Products: {stats.get('total_products', 0)}
• Total Markets: {stats.get('total_markets', 0)}
• Sites Covered: {', '.join(stats.get('sites_covered', []))}
• Average Confidence: {stats.get('average_confidence', 0):.1%}
• Conversation History: {len(self.conversation_history)} exchanges
        """
        print(stats_text)
    
    def _show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print("📝 No conversation history yet.")
            return
        
        print("\n📝 Conversation History:")
        print("-" * 60)
        
        for i, exchange in enumerate(self.conversation_history, 1):
            print(f"\n{i}. {exchange['timestamp']}")
            print(f"   💬 You: {exchange['user']}")
            print(f"   🤖 Assistant: {exchange['assistant'][:100]}...")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


def main():
    """Main entry point for the chat interface"""
    parser = argparse.ArgumentParser(description="Prediction Market Chat Assistant")
    parser.add_argument("--log-file", default="logs/chat.log", help="Log file path")
    parser.add_argument("--log-level", default="INFO", help="Logging level")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger.info("Starting Prediction Market Chat Assistant")
    
    try:
        # Initialize RAG system
        print("🔄 Initializing RAG system...")
        rag_system = ProductRAG()
        
        # Check if we have products loaded
        stats = rag_system.get_product_stats()
        if stats['total_products'] == 0:
            print("⚠️  No products found in RAG system.")
            print("Please run the main data collection first:")
            print("   python -m src.main --mode local --limit 50")
            print("Then restart the chat interface.")
            return
        
        print(f"✅ Loaded {stats['total_products']} products from {len(stats['sites_covered'])} sites")
        
        # Start chat
        chat = PredictionMarketChat(rag_system)
        chat.start_chat()
        
    except Exception as e:
        logger.error(f"Failed to start chat: {e}")
        print(f"❌ Failed to start chat: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
