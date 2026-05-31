import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging
from typing import Any

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


class ChatManager:
    def __init__(self, user_id: int, conversation_id: int = None):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.memory: Any = []
        self.client: Any = None

        try:
            from google import genai
            from google.genai import types

            self.client = genai.Client(api_key=GEMINI_API_KEY)
            self.types = types
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {e}")
            self.client = None
            self.types = None

    def add_to_memory(self, role: str, content: str):
        """Add message to memory"""
        if self.types:
            if role == "user":
                self.memory.append(self.types.UserContent(content))
            else:
                self.memory.append(self.types.ModelContent(content))
        else:
            self.memory.append({
                "role": "user" if role == "user" else "model",
                "parts": [content],
            })

    def get_memory(self) -> str:
        """Get conversation memory"""
        if not self.memory:
            return ""
        lines = []
        for msg in self.memory:
            if self.types and hasattr(msg, 'role'):
                role = msg.role
                text = "".join(part.text for part in msg.parts if part.text)
            else:
                role = msg.get("role", "user")
                text = "".join(msg.get("parts", []))
            lines.append(f"{role.capitalize()}: {text}")
        return "\n".join(lines)

    def load_history(self, messages: List[Dict]):
        """Load chat history into memory"""
        self.memory = []
        for msg in messages:
            role = msg["sender"]
            self.add_to_memory(role, msg["content"])

    async def chat_with_rag(
        self,
        query: str,
        rag_context: Optional[str] = None,
    ) -> str:
        if not self.client:
            return "Error: Chat dependencies not available. Ensure GOOGLE_API_KEY and google-genai are configured."

        try:
            if rag_context:
                user_content = (
                    "You are a helpful customer support AI assistant.\n\n"
                    "Use the following context from uploaded documents to answer questions:\n"
                    f"{rag_context}\n\n"
                    "If the context doesn't contain relevant information, use your general knowledge to help the user.\n\n"
                    f"User question: {query}"
                )
            else:
                user_content = query

            generation_config = None
            if self.types is not None:
                generation_config = self.types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=2048,
                )

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_content,
                config=generation_config,
            )

            assistant_response = response.text or ""

            return assistant_response
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"Error: {str(e)}"

    def clear_memory(self):
        """Clear conversation memory"""
        self.memory = []


def analyze_sentiment(text: str) -> str:
    """Simple sentiment analysis"""
    positive_words = ['good', 'great', 'excellent', 'amazing', 'love', 'perfect', 'happy', 'satisfied']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'frustrated', 'disappointed', 'sad']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def categorize_query(query: str) -> str:
    """Categorize user query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['help', 'support', 'issue', 'problem', 'error']):
        return "support"
    elif any(word in query_lower for word in ['price', 'cost', 'payment', 'billing']):
        return "billing"
    elif any(word in query_lower for word in ['feature', 'how to', 'tutorial', 'guide']):
        return "feature_inquiry"
    elif any(word in query_lower for word in ['refund', 'return', 'cancel']):
        return "refund_request"
    else:
        return "general"


def detect_escalation(query: str) -> bool:
    """Detect if query needs escalation"""
    escalation_keywords = [
        'urgent', 'critical', 'emergency', 'legal', 'lawsuit',
        'complaint', 'dissatisfied', 'angry', 'furious',
        'manager', 'supervisor', 'escalate'
    ]
    
    return any(keyword in query.lower() for keyword in escalation_keywords)


def generate_faq(documents: List[str]) -> List[Dict]:
    """Generate FAQ from documents"""
    faqs = []
    
    # Simple FAQ generation - group similar documents
    for i, doc in enumerate(documents[:10]):  # Limit to first 10
        # Extract first sentence as question
        sentences = doc.split('.')
        if sentences:
            question = sentences[0].strip()
            answer = doc
            
            if len(question) > 10:
                faqs.append({
                    "id": i,
                    "question": question,
                    "answer": answer
                })
    
    return faqs
