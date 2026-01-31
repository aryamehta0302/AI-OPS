"""
GENAI EXPLANATION ENGINE (OLLAMA)
==================================
Converts structured agent reasoning into human-readable explanations.

CRITICAL RULES:
- LLM NEVER decides - only explains
- LLM NEVER sees raw metrics
- LLM ONLY receives structured reasoning
- System works WITHOUT this module (graceful fallback)

Uses local Ollama with phi3:mini
Endpoint: http://localhost:11434
NO API keys required
NO cloud calls
"""

import httpx
import asyncio
from typing import Dict, Optional
from dataclasses import dataclass
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExplanationRequest:
    """Structured input for explanation generation"""
    decision: str
    root_cause: Optional[str]
    health_trend: str
    persistence: int
    action_taken: Optional[str]
    confidence: float
    contributing_factors: list


@dataclass 
class ExplanationResponse:
    """Structured output from explanation engine"""
    explanation: str
    generated_by: str  # "ollama" or "fallback"
    model: str
    latency_ms: float
    success: bool


class ExplanationEngine:
    """
    GenAI Explanation Layer using Ollama
    
    This module:
    1. Receives STRUCTURED agent decisions (not raw metrics)
    2. Generates human-readable explanations
    3. Falls back gracefully if Ollama unavailable
    
    The agent system works INDEPENDENTLY of this module.
    """
    
    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "phi3:mini",
        timeout_seconds: float = 5.0,  # Balance between responsiveness and giving Ollama time
        enabled: bool = True
    ):
        """
        Initialize explanation engine
        
        Args:
            ollama_url: Base URL for Ollama API
            model: Model to use (phi3:mini recommended)
            timeout_seconds: Request timeout
            enabled: Whether to attempt LLM explanations
        """
        self.ollama_url = ollama_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled
        self.available = False  # Set after health check
        
        # Large cache for repeated explanations (avoid redundant LLM calls)
        # Most decisions repeat, so caching is very effective
        self.explanation_cache: Dict[str, str] = {}
        self.cache_max_size = 200  # Increased cache size
    
    async def check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:  # Fast check
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    self.available = True
                    logger.info(f"Ollama available at {self.ollama_url}")
                    return True
        except Exception as e:
            logger.warning(f"Ollama not available (using fallback): {e}")
            self.available = False
        return False
    
    def check_availability_sync(self) -> bool:
        """Synchronous version of availability check"""
        try:
            import requests
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2.0)  # Fast check
            if response.status_code == 200:
                self.available = True
                logger.info(f"Ollama available at {self.ollama_url}")
                return True
        except Exception as e:
            logger.warning(f"Ollama not available (using fallback): {e}")
            self.available = False
        return False
    
    def _build_prompt(self, request: ExplanationRequest) -> str:
        """
        Build a SHORT prompt for the LLM - optimized for speed
        
        IMPORTANT: Only structured data, no raw metrics
        """
        # Shorter prompt = faster response
        prompt = f"""AIOps analyst. Explain this agent decision in ONE sentence (max 30 words).

Decision: {request.decision}
Trend: {request.health_trend}
Cycles: {request.persistence}
Cause: {request.root_cause or "none"}
Confidence: {request.confidence:.0%}

Response:"""
        return prompt
    
    def _generate_fallback(self, request: ExplanationRequest) -> str:
        """
        Generate a deterministic fallback explanation
        Used when Ollama is unavailable or disabled
        These templates provide good, context-aware explanations
        """
        decision = request.decision
        trend = request.health_trend
        persistence = request.persistence
        root_cause = request.root_cause or "system load"
        confidence = request.confidence
        factors = request.contributing_factors or []
        
        # Build factor string
        factor_str = ", ".join(factors[:3]) if factors else "general metrics"
        
        templates = {
            "NO_ACTION": f"System operating normally. Health trend: {trend.lower()}. Confidence: {confidence:.0%}. Monitoring continues.",
            
            "ESCALATE": f"[ALERT] Escalated. {trend.replace('_', ' ').title()} trend detected for {persistence} cycles. Root cause: {root_cause}. Contributing factors: {factor_str}. Confidence: {confidence:.0%}.",
            
            "DE_ESCALATE": f"[RESOLVED] Recovery confirmed. Health improving after {persistence} cycles. Trend: {trend.lower()}. Alert level reduced.",
            
            "PREDICT_FAILURE": f"[CRITICAL] Failure predicted. {trend.replace('_', ' ').title()} for {persistence} cycles. Root cause: {root_cause}. Immediate attention required. Confidence: {confidence:.0%}.",
            
            "AUTO_HEAL": f"[REMEDIATION] Auto-healing initiated. Degradation detected: {root_cause}. Trend: {trend.lower()} for {persistence} cycles. Applying corrective actions. Confidence: {confidence:.0%}.",
            
            "INVESTIGATE": f"[REVIEW] Investigation recommended. Anomaly detected in {root_cause}. Trend: {trend.lower()}. Factors: {factor_str}. Confidence: {confidence:.0%}."
        }
        
        return templates.get(
            decision,
            f"Agent decision: {decision}. Health trend: {trend}. Persistence: {persistence} cycles. Root cause: {root_cause}. Confidence: {confidence:.0%}."
        )
    
    async def explain_async(self, request: ExplanationRequest) -> ExplanationResponse:
        """
        Generate explanation asynchronously
        
        Args:
            request: Structured explanation request
            
        Returns:
            ExplanationResponse with explanation and metadata
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{request.decision}:{request.health_trend}:{request.persistence}:{request.root_cause}"
        if cache_key in self.explanation_cache:
            return ExplanationResponse(
                explanation=self.explanation_cache[cache_key],
                generated_by="cache",
                model=self.model,
                latency_ms=0,
                success=True
            )
        
        # If disabled or unavailable, use fallback
        if not self.enabled or not self.available:
            fallback = self._generate_fallback(request)
            return ExplanationResponse(
                explanation=fallback,
                generated_by="fallback",
                model="none",
                latency_ms=(time.time() - start_time) * 1000,
                success=True
            )
        
        # Try Ollama
        try:
            prompt = self._build_prompt(request)
            
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,  # Low temperature for consistency
                            "num_predict": 50    # Short response = fast
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    explanation = result.get("response", "").strip()
                    
                    # Clean up the response
                    explanation = explanation.replace("\n\n", " ").strip()
                    if not explanation:
                        explanation = self._generate_fallback(request)
                    
                    # Cache the result
                    if len(self.explanation_cache) >= self.cache_max_size:
                        # Remove oldest entry
                        oldest_key = next(iter(self.explanation_cache))
                        del self.explanation_cache[oldest_key]
                    self.explanation_cache[cache_key] = explanation
                    
                    return ExplanationResponse(
                        explanation=explanation,
                        generated_by="ollama",
                        model=self.model,
                        latency_ms=(time.time() - start_time) * 1000,
                        success=True
                    )
                else:
                    logger.warning(f"Ollama returned {response.status_code}")
                    
        except Exception as e:
            logger.warning(f"Ollama request failed: {e}")
        
        # Fallback on any error
        fallback = self._generate_fallback(request)
        return ExplanationResponse(
            explanation=fallback,
            generated_by="fallback",
            model="none",
            latency_ms=(time.time() - start_time) * 1000,
            success=True
        )
    
    def explain_sync(self, request: ExplanationRequest) -> ExplanationResponse:
        """
        Generate explanation synchronously (for non-async contexts)
        
        Args:
            request: Structured explanation request
            
        Returns:
            ExplanationResponse with explanation and metadata
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{request.decision}:{request.health_trend}:{request.persistence}:{request.root_cause}"
        if cache_key in self.explanation_cache:
            return ExplanationResponse(
                explanation=self.explanation_cache[cache_key],
                generated_by="cache",
                model=self.model,
                latency_ms=0,
                success=True
            )
        
        # If disabled or unavailable, use fallback
        if not self.enabled or not self.available:
            fallback = self._generate_fallback(request)
            return ExplanationResponse(
                explanation=fallback,
                generated_by="fallback",
                model="none",
                latency_ms=(time.time() - start_time) * 1000,
                success=True
            )
        
        # Try Ollama synchronously
        try:
            import requests
            prompt = self._build_prompt(request)
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 50  # Short response = fast
                    }
                },
                timeout=self.timeout_seconds
            )
            
            if response.status_code == 200:
                result = response.json()
                explanation = result.get("response", "").strip()
                
                # Clean up
                explanation = explanation.replace("\n\n", " ").strip()
                if not explanation:
                    explanation = self._generate_fallback(request)
                
                # Cache
                if len(self.explanation_cache) >= self.cache_max_size:
                    oldest_key = next(iter(self.explanation_cache))
                    del self.explanation_cache[oldest_key]
                self.explanation_cache[cache_key] = explanation
                
                return ExplanationResponse(
                    explanation=explanation,
                    generated_by="ollama",
                    model=self.model,
                    latency_ms=(time.time() - start_time) * 1000,
                    success=True
                )
                
        except Exception as e:
            logger.warning(f"Ollama sync request failed: {e}")
        
        # Fallback
        fallback = self._generate_fallback(request)
        return ExplanationResponse(
            explanation=fallback,
            generated_by="fallback",
            model="none",
            latency_ms=(time.time() - start_time) * 1000,
            success=True
        )
    
    def explain_decision(
        self,
        decision: str,
        root_cause: Optional[str],
        health_trend: str,
        persistence: int,
        action_taken: Optional[str] = None,
        confidence: float = 0.8,
        contributing_factors: list = None,
        use_fallback: bool = False  # Force fast fallback (skip Ollama)
    ) -> Dict:
        """
        Convenience method to explain a decision
        
        Args:
            use_fallback: If True, skip Ollama and use fast template-based explanation
        
        Returns dict with explanation and metadata
        """
        request = ExplanationRequest(
            decision=decision,
            root_cause=root_cause,
            health_trend=health_trend,
            persistence=persistence,
            action_taken=action_taken,
            confidence=confidence,
            contributing_factors=contributing_factors or []
        )
        
        # If use_fallback is True, bypass Ollama entirely
        if use_fallback:
            fallback = self._generate_fallback(request)
            return {
                "explanation": fallback,
                "generated_by": "fallback",
                "model": "none",
                "latency_ms": 0
            }
        
        response = self.explain_sync(request)
        
        return {
            "explanation": response.explanation,
            "generated_by": response.generated_by,
            "model": response.model,
            "latency_ms": response.latency_ms
        }
    
    def get_status(self) -> Dict:
        """Get explanation engine status"""
        return {
            "enabled": self.enabled,
            "available": self.available,
            "ollama_url": self.ollama_url,
            "model": self.model,
            "cache_size": len(self.explanation_cache)
        }
