import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer
from .types import UnifiedProduct, SiteMarket
from .logging_config import get_logger

logger = get_logger(__name__)


class ProductRAG:
    """RAG system for chatting about prediction market products"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the RAG system with embedding model"""
        self.model = SentenceTransformer(model_name)
        self.embeddings = []
        self.products = []
        self.embedding_cache_file = "data/embeddings_cache.json"
        
        # Load existing embeddings if available
        self._load_embeddings()
    
    def _load_embeddings(self):
        """Load cached embeddings from file"""
        if os.path.exists(self.embedding_cache_file):
            try:
                with open(self.embedding_cache_file, 'r') as f:
                    data = json.load(f)
                    self.embeddings = [np.array(emb) for emb in data.get('embeddings', [])]
                    self.products = data.get('products', [])
                logger.info(f"Loaded {len(self.products)} cached product embeddings")
            except Exception as e:
                logger.warning(f"Failed to load embeddings cache: {e}")
    
    def _save_embeddings(self):
        """Save embeddings to cache file"""
        try:
            os.makedirs(os.path.dirname(self.embedding_cache_file), exist_ok=True)
            data = {
                'embeddings': [emb.tolist() for emb in self.embeddings],
                'products': self.products,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.embedding_cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.products)} product embeddings to cache")
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
    
    def add_products(self, unified_products: List[UnifiedProduct]):
        """Add products to the RAG system and generate embeddings"""
        logger.info(f"Adding {len(unified_products)} unified products to RAG system")
        
        for product in unified_products:
            # Create product document for embedding
            product_text = self._create_product_text(product)
            
            # Generate embedding
            embedding = self.model.encode(product_text)
            
            # Store product and embedding
            self.products.append({
                'unified_title': product.unified_title,
                'members': [member.dict() for member in product.members],
                'confidence_scores': product.confidence_scores,
                'text': product_text
            })
            self.embeddings.append(embedding)
        
        # Save to cache
        self._save_embeddings()
        logger.info(f"RAG system now contains {len(self.products)} products")
    
    def _create_product_text(self, product: UnifiedProduct) -> str:
        """Create text representation of product for embedding"""
        text_parts = [f"Product: {product.unified_title}"]
        
        for member, confidence in zip(product.members, product.confidence_scores):
            text_parts.append(f"Available on {member.site}: {member.title}")
            if member.price is not None:
                text_parts.append(f"Price: {member.price:.4f}")
            text_parts.append(f"Confidence: {confidence:.3f}")
        
        return " | ".join(text_parts)
    
    def search_products(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for products similar to the query"""
        if not self.embeddings:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode(query)
        
        # Calculate similarities
        similarities = []
        for i, embedding in enumerate(self.embeddings):
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((similarity, i))
        
        # Sort by similarity and return top results
        similarities.sort(reverse=True)
        results = []
        
        for similarity, idx in similarities[:top_k]:
            product = self.products[idx].copy()
            product['similarity_score'] = float(similarity)
            results.append(product)
        
        logger.info(f"Search for '{query}' returned {len(results)} results")
        return results
    
    def chat_about_products(self, user_message: str) -> str:
        """Chat interface for querying products"""
        logger.info(f"Chat query: {user_message}")
        
        # Search for relevant products
        relevant_products = self.search_products(user_message, top_k=3)
        
        if not relevant_products:
            return "I couldn't find any prediction markets related to your query. Try asking about specific topics like 'elections', 'crypto prices', or 'sports outcomes'."
        
        # Generate response
        response_parts = ["Here are some relevant prediction markets:"]
        
        for i, product in enumerate(relevant_products, 1):
            response_parts.append(f"\n{i}. **{product['unified_title']}**")
            
            # Add price information
            prices = []
            for member in product['members']:
                if member.get('price') is not None:
                    prices.append(f"{member['site']}: {member['price']:.1%}")
            
            if prices:
                response_parts.append(f"   Current prices: {', '.join(prices)}")
            
            # Add confidence info
            avg_confidence = np.mean(product['confidence_scores'])
            response_parts.append(f"   Match confidence: {avg_confidence:.1%}")
        
        response_parts.append(f"\n\nSimilarity score: {relevant_products[0]['similarity_score']:.2f}")
        
        return "\n".join(response_parts)
    
    def get_product_stats(self) -> Dict[str, Any]:
        """Get statistics about the products in the RAG system"""
        if not self.products:
            return {"total_products": 0}
        
        total_markets = sum(len(p['members']) for p in self.products)
        sites = set()
        for product in self.products:
            for member in product['members']:
                sites.add(member['site'])
        
        avg_confidence = np.mean([
            np.mean(p['confidence_scores']) for p in self.products
        ])
        
        return {
            "total_products": len(self.products),
            "total_markets": total_markets,
            "sites_covered": list(sites),
            "average_confidence": float(avg_confidence)
        }


def create_rag_agent() -> 'Agent':
    """Create a CrewAI agent for RAG-based product chat"""
    from crewai import Agent
    from .config import get_litellm_model
    
    return Agent(
        role="Product Chat Assistant",
        goal="Help users find and understand prediction markets using RAG-powered search",
        backstory="""You are an expert assistant who helps users discover and understand 
        prediction markets. You use advanced search capabilities to find relevant markets 
        and provide detailed information about prices, confidence scores, and market details.""",
        verbose=True,
        llm_model=get_litellm_model(),
        allow_delegation=False
    )


def create_rag_task(agent: 'Agent', rag_system: ProductRAG, user_query: str) -> 'Task':
    """Create a task for the RAG agent"""
    from crewai import Task
    
    return Task(
        description=f"""A user is asking about prediction markets: "{user_query}"
        
        Use the RAG system to search for relevant products and provide a helpful response.
        Include information about:
        - Relevant prediction markets
        - Current prices across different sites
        - Confidence scores for product matches
        - Any additional context that might be helpful
        
        Make your response conversational and informative.
        """,
        agent=agent,
        expected_output="A helpful response about prediction markets related to the user's query"
    )
