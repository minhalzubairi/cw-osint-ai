"""
AI Analyzer using DigitalOcean's Gradient AI Platform
"""

import httpx
import time
import logging
from typing import Dict, Any, List
from datetime import datetime

from backend.core.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered analyzer using Gradient AI"""
    
    def __init__(self):
        """Initialize AI analyzer with Gradient AI configuration"""
        self.endpoint = settings.GRADIENT_AI_ENDPOINT
        self.api_key = settings.GRADIENT_AI_API_KEY
        self.model = settings.AI_MODEL
        self.max_tokens = settings.AI_MAX_TOKENS
        self.temperature = settings.AI_TEMPERATURE
    
    async def analyze(
        self,
        content: str,
        analysis_type: str = "comprehensive",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Perform AI analysis on content
        
        Args:
            content: Text content to analyze
            analysis_type: Type of analysis (sentiment, trend, summary, comprehensive)
            metadata: Additional metadata for context
            
        Returns:
            Analysis results dictionary
        """
        start_time = time.time()
        
        try:
            # Build prompt based on analysis type
            prompt = self._build_prompt(content, analysis_type, metadata)
            
            # Call Gradient AI API
            result = await self._call_gradient_ai(prompt)
            
            processing_time = time.time() - start_time
            
            # Parse and structure the result
            structured_result = self._structure_result(result, analysis_type)
            structured_result['processing_time'] = processing_time
            structured_result['model'] = self.model
            
            return structured_result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                'error': str(e),
                'processing_time': time.time() - start_time,
                'model': self.model
            }
    
    def _build_prompt(
        self,
        content: str,
        analysis_type: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Build appropriate prompt for analysis type"""
        
        base_context = "You are an expert OSINT analyst specializing in analyzing open-source intelligence data."
        
        if metadata:
            context_info = f"\n\nContext: {metadata}"
        else:
            context_info = ""
        
        prompts = {
            "sentiment": f"""{base_context}
            
Analyze the sentiment of the following content and provide a detailed assessment.
{context_info}

Content:
{content}

Provide your analysis in the following JSON format:
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "explanation": "detailed explanation",
    "key_phrases": ["phrase1", "phrase2"],
    "emotions": ["emotion1", "emotion2"]
}}""",
            
            "trend": f"""{base_context}
            
Identify trends, patterns, and significant topics in the following content.
{context_info}

Content:
{content}

Provide your analysis in the following JSON format:
{{
    "trends": [
        {{
            "topic": "topic name",
            "mentions": number,
            "sentiment": "positive/negative/neutral",
            "confidence": 0.0-1.0
        }}
    ],
    "emerging_topics": ["topic1", "topic2"],
    "key_themes": ["theme1", "theme2"]
}}""",
            
            "summary": f"""{base_context}
            
Provide a concise summary of the following content, highlighting the most important points.
{context_info}

Content:
{content}

Provide your analysis in the following JSON format:
{{
    "summary": "concise summary (2-3 sentences)",
    "key_points": ["point1", "point2", "point3"],
    "entities": ["entity1", "entity2"],
    "action_items": ["action1", "action2"]
}}""",
            
            "comprehensive": f"""{base_context}
            
Perform a comprehensive analysis of the following content including sentiment, trends, and key insights.
{context_info}

Content:
{content}

Provide your analysis in the following JSON format:
{{
    "summary": "brief summary",
    "sentiment": {{
        "overall": "positive/negative/neutral",
        "confidence": 0.0-1.0,
        "explanation": "explanation"
    }},
    "trends": [
        {{
            "topic": "topic name",
            "mentions": number,
            "sentiment": "positive/negative/neutral"
        }}
    ],
    "key_insights": ["insight1", "insight2", "insight3"],
    "entities": ["entity1", "entity2"],
    "recommendations": ["recommendation1", "recommendation2"]
}}"""
        }
        
        return prompts.get(analysis_type, prompts["comprehensive"])
    
    async def _call_gradient_ai(self, prompt: str) -> str:
        """
        Call DigitalOcean Gradient AI API
        
        Note: This is a placeholder implementation.
        You'll need to update this with actual Gradient AI API calls
        based on DigitalOcean's documentation.
        """
        
        # For now, this is a mock implementation
        # Replace with actual Gradient AI API call
        
        try:
            # Example structure (update based on actual API)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.endpoint}/inference",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": self.max_tokens,
                        "temperature": self.temperature
                    },
                    timeout=60.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract the response content
                # This structure may vary based on actual API
                return result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling Gradient AI: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling Gradient AI: {e}")
            raise
    
    def _structure_result(self, ai_response: str, analysis_type: str) -> Dict[str, Any]:
        """
        Parse and structure the AI response
        
        Args:
            ai_response: Raw response from AI
            analysis_type: Type of analysis performed
            
        Returns:
            Structured result dictionary
        """
        import json
        
        try:
            # Try to parse JSON response
            parsed = json.loads(ai_response)
            parsed['analysis_type'] = analysis_type
            parsed['timestamp'] = datetime.utcnow().isoformat()
            return parsed
        except json.JSONDecodeError:
            # If not JSON, return as text
            logger.warning("AI response not in JSON format, returning as text")
            return {
                'analysis_type': analysis_type,
                'raw_response': ai_response,
                'timestamp': datetime.utcnow().isoformat(),
                'parsed': False
            }
    
    async def batch_analyze(
        self,
        items: List[Dict[str, Any]],
        analysis_type: str = "comprehensive"
    ) -> List[Dict[str, Any]]:
        """
        Perform batch analysis on multiple items
        
        Args:
            items: List of items to analyze (each with 'content' key)
            analysis_type: Type of analysis to perform
            
        Returns:
            List of analysis results
        """
        results = []
        
        for item in items:
            result = await self.analyze(
                content=item.get('content', ''),
                analysis_type=analysis_type,
                metadata=item.get('metadata')
            )
            results.append(result)
        
        return results
