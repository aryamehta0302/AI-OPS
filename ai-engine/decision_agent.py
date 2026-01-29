"""
AGENTIC AI DECISION ENGINE
===========================
A true autonomous agent that:
- Perceives system state via metrics
- Maintains memory of past behavior
- Reasons over trends and persistence
- Decides actions autonomously (NO LLM)
- Outputs structured reasoning for every decision

This is NOT a chatbot. This is a decision-making agent.
"""

import time
from collections import deque, defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum


class AgentDecision(Enum):
    """Possible autonomous decisions the agent can make"""
    NO_ACTION = "NO_ACTION"
    ESCALATE = "ESCALATE"
    DE_ESCALATE = "DE_ESCALATE"
    PREDICT_FAILURE = "PREDICT_FAILURE"
    AUTO_HEAL = "AUTO_HEAL"


class HealthTrend(Enum):
    """Health trajectory over time"""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DEGRADING = "DEGRADING"
    CRITICAL_DECLINE = "CRITICAL_DECLINE"


@dataclass
class AgentMemory:
    """Memory state for a single node"""
    node_id: str
    health_history: deque  # Sliding window of (timestamp, health_score)
    anomaly_history: deque  # Sliding window of anomaly scores
    degradation_counter: int  # How many consecutive cycles of degradation
    recovery_counter: int  # How many consecutive cycles of recovery
    last_decision: Optional[str] = None
    last_decision_time: Optional[float] = None
    last_healing_attempt: Optional[float] = None
    healing_outcome: Optional[str] = None
    incident_state: Optional[str] = None
    # NEW: Track actual agent state from PC agents
    agent_state: Optional[dict] = None
    connection_state: str = "CONNECTED"
    last_heartbeat_time: Optional[float] = None
    # CPU tracking for sustained high usage warning
    cpu_high_start_time: Optional[float] = None  # When CPU first went high
    cpu_warning_issued: bool = False  # Prevent repeated warnings


@dataclass
class AgentReasoning:
    """Structured output of agent's decision process"""
    node_id: str
    decision: str
    confidence: float
    contributing_factors: List[str]
    persistence: int
    health_trend: str
    health_score: float
    anomaly_score: float
    trend_velocity: float
    timestamp: float
    reasoning_chain: List[str]  # Step-by-step reasoning
    # NEW: Include agent state awareness
    agent_status: str = "ACTIVE"
    connection_state: str = "CONNECTED"


class DecisionAgent:
    """
    CORE AGENTIC AI ENGINE
    
    Responsibilities:
    1. PERCEIVE: Ingest real-time metrics per node
    2. REMEMBER: Maintain sliding window memory
    3. REASON: Analyze trends, persistence, patterns
    4. DECIDE: Choose action autonomously
    5. EXPLAIN: Provide structured reasoning
    """
    
    def __init__(
        self,
        memory_window_size: int = 20,
        degradation_threshold: float = 70.0,
        critical_threshold: float = 50.0,
        anomaly_threshold: float = 0.6,
        persistence_threshold: int = 3
    ):
        """
        Initialize the decision agent with configurable thresholds
        
        Args:
            memory_window_size: How many data points to remember
            degradation_threshold: Health score below which indicates degradation
            critical_threshold: Health score indicating critical state
            anomaly_threshold: Anomaly score above which triggers concern
            persistence_threshold: How many cycles before action is taken
        """
        self.memory_window_size = memory_window_size
        self.degradation_threshold = degradation_threshold
        self.critical_threshold = critical_threshold
        self.anomaly_threshold = anomaly_threshold
        self.persistence_threshold = persistence_threshold
        
        # Memory storage per node
        self.node_memories: Dict[str, AgentMemory] = {}
        
        # Decision history for feedback loops
        self.decision_history: deque = deque(maxlen=100)
    
    def _get_or_create_memory(self, node_id: str) -> AgentMemory:
        """Get existing memory or create new memory for a node"""
        if node_id not in self.node_memories:
            self.node_memories[node_id] = AgentMemory(
                node_id=node_id,
                health_history=deque(maxlen=self.memory_window_size),
                anomaly_history=deque(maxlen=self.memory_window_size),
                degradation_counter=0,
                recovery_counter=0,
                agent_state=None,
                connection_state="CONNECTED",
                last_heartbeat_time=None,
                cpu_high_start_time=None,
                cpu_warning_issued=False
            )
        return self.node_memories[node_id]
    
    def perceive(
        self,
        node_id: str,
        health_score: float,
        anomaly_score: float,
        root_cause: Optional[str] = None,
        incident_state: Optional[str] = None,
        agent_state: Optional[dict] = None,
        metrics: Optional[dict] = None  # Raw metrics for CPU tracking
    ) -> AgentReasoning:
        """
        PERCEPTION PHASE
        Ingest new metrics and update memory
        
        Args:
            node_id: Unique identifier for the node
            health_score: Current health (0-100)
            anomaly_score: Current anomaly level (0-1)
            root_cause: Detected root cause if any
            incident_state: Current incident state
            agent_state: PC agent internal state (DEGRADED/HEALTHY/etc)
            metrics: Raw system metrics (for CPU tracking)
            
        Returns:
            AgentReasoning with decision and explanation
        """
        timestamp = time.time()
        memory = self._get_or_create_memory(node_id)
        
        # Update memory with new observations
        memory.health_history.append((timestamp, health_score))
        memory.anomaly_history.append((timestamp, anomaly_score))
        memory.incident_state = incident_state
        memory.last_heartbeat_time = timestamp
        memory.connection_state = "CONNECTED"
        
        # NEW: Update agent state from PC agent
        if agent_state:
            memory.agent_state = agent_state
        
        # NEW: Track CPU sustained high usage (>= 95% for 20+ seconds)
        cpu_warning = None
        if metrics and metrics.get("cpu"):
            cpu_usage = metrics["cpu"].get("usage_percent", 0)
            CPU_HIGH_THRESHOLD = 95.0  # Consider >= 95% as "high"
            CPU_WARNING_DURATION = 20.0  # Warn after 20 seconds
            
            if cpu_usage >= CPU_HIGH_THRESHOLD:
                if memory.cpu_high_start_time is None:
                    # CPU just went high
                    memory.cpu_high_start_time = timestamp
                    memory.cpu_warning_issued = False
                else:
                    # CPU has been high - check duration
                    duration = timestamp - memory.cpu_high_start_time
                    if duration >= CPU_WARNING_DURATION and not memory.cpu_warning_issued:
                        cpu_warning = f"⚠️ CPU at {cpu_usage:.1f}% for {duration:.0f}s"
                        memory.cpu_warning_issued = True
            else:
                # CPU is normal - reset tracking
                memory.cpu_high_start_time = None
                memory.cpu_warning_issued = False
        
        # Determine agent status from agent_state
        agent_status = "ACTIVE"
        if agent_state:
            if agent_state.get("health_state") in ["DEGRADED", "DEGRADING"]:
                agent_status = "DEGRADED"
            elif agent_state.get("health_state") == "RECOVERING":
                agent_status = "RECOVERING"
        
        # REASONING PHASE
        reasoning = self._reason(memory, health_score, anomaly_score, root_cause, agent_state, cpu_warning)
        
        # DECISION PHASE
        decision, confidence, factors = self._decide(memory, reasoning, agent_state)
        
        # Update memory with decision
        memory.last_decision = decision.value
        memory.last_decision_time = timestamp
        
        # Create structured reasoning output
        agent_reasoning = AgentReasoning(
            node_id=node_id,
            decision=decision.value,
            confidence=confidence,
            contributing_factors=factors,
            persistence=memory.degradation_counter,
            health_trend=reasoning['trend'].value,
            health_score=health_score,
            anomaly_score=anomaly_score,
            trend_velocity=reasoning['velocity'],
            timestamp=timestamp,
            reasoning_chain=reasoning['reasoning_chain'],
            agent_status=agent_status,
            connection_state=memory.connection_state
        )
        
        # Store in decision history for feedback
        self.decision_history.append(agent_reasoning)
        
        return agent_reasoning
    
    def _reason(
        self,
        memory: AgentMemory,
        health_score: float,
        anomaly_score: float,
        root_cause: Optional[str],
        agent_state: Optional[dict] = None,
        cpu_warning: Optional[str] = None  # CPU sustained high warning
    ) -> Dict:
        """
        REASONING PHASE
        Analyze trends, persistence, and patterns
        
        Returns:
            Dictionary with trend analysis and reasoning steps
        """
        reasoning_chain = []
        
        # 0. CPU WARNING (NEW: Sustained high CPU alert)
        if cpu_warning:
            reasoning_chain.append(cpu_warning)
        
        # 0b. AGENT STATE ANALYSIS (Use real PC agent state)
        if agent_state:
            agent_health_state = agent_state.get("health_state", "UNKNOWN")
            degradation_type = agent_state.get("degradation_type", "NONE")
            degradation_level = agent_state.get("degradation_level", 0)
            
            if agent_health_state in ["DEGRADED", "DEGRADING"]:
                reasoning_chain.append(f"PC Agent reports: {agent_health_state} ({degradation_type}, level: {degradation_level:.2f})")
            elif agent_health_state == "RECOVERING":
                reasoning_chain.append(f"PC Agent reports: RECOVERING from {degradation_type}")
            else:
                reasoning_chain.append(f"PC Agent reports: {agent_health_state}")
        
        # 1. TREND ANALYSIS
        trend, velocity = self._analyze_trend(memory.health_history)
        reasoning_chain.append(f"Health trend: {trend.value} (velocity: {velocity:.2f})")
        
        # 2. PERSISTENCE ANALYSIS
        if health_score < self.degradation_threshold:
            memory.degradation_counter += 1
            memory.recovery_counter = 0
            reasoning_chain.append(f"Degradation persists for {memory.degradation_counter} cycles")
        elif health_score >= self.degradation_threshold and memory.degradation_counter > 0:
            memory.recovery_counter += 1
            reasoning_chain.append(f"Recovery detected for {memory.recovery_counter} cycles")
            if memory.recovery_counter >= 2:
                memory.degradation_counter = max(0, memory.degradation_counter - 1)
        else:
            memory.degradation_counter = 0
            memory.recovery_counter = 0
            reasoning_chain.append("System stable")
        
        # 3. ANOMALY ANALYSIS
        anomaly_pattern = self._analyze_anomaly_pattern(memory.anomaly_history)
        reasoning_chain.append(f"Anomaly pattern: {anomaly_pattern}")
        
        # 4. CRITICAL STATE DETECTION
        is_critical = health_score < self.critical_threshold
        if is_critical:
            reasoning_chain.append("CRITICAL: Health below critical threshold")
        
        # 5. ROOT CAUSE CONTEXT
        if root_cause:
            reasoning_chain.append(f"Root cause identified: {root_cause}")
        
        # 6. AGENT STATE CORRELATION (NEW)
        agent_degraded = False
        if agent_state:
            if agent_state.get("health_state") in ["DEGRADED", "DEGRADING"]:
                agent_degraded = True
                reasoning_chain.append("CONFIRMED: Agent self-reports degradation")
        
        return {
            'trend': trend,
            'velocity': velocity,
            'anomaly_pattern': anomaly_pattern,
            'is_critical': is_critical,
            'reasoning_chain': reasoning_chain,
            'agent_degraded': agent_degraded
        }
    
    def _analyze_trend(self, health_history: deque) -> Tuple[HealthTrend, float]:
        """
        Calculate health trend and velocity
        
        Returns:
            (HealthTrend, velocity) where velocity is points per observation
        """
        if len(health_history) < 3:
            return HealthTrend.STABLE, 0.0
        
        # Calculate linear trend over recent history
        recent_window = 5
        recent = list(health_history)[-recent_window:]
        
        if len(recent) < 2:
            return HealthTrend.STABLE, 0.0
        
        # Simple velocity: change per time step
        first_health = recent[0][1]
        last_health = recent[-1][1]
        velocity = (last_health - first_health) / len(recent)
        
        # Classify trend
        if velocity < -3.0:
            return HealthTrend.CRITICAL_DECLINE, velocity
        elif velocity < -1.0:
            return HealthTrend.DEGRADING, velocity
        elif velocity > 1.0:
            return HealthTrend.IMPROVING, velocity
        else:
            return HealthTrend.STABLE, velocity
    
    def _analyze_anomaly_pattern(self, anomaly_history: deque) -> str:
        """
        Detect patterns in anomaly behavior
        
        Returns:
            Pattern description
        """
        if len(anomaly_history) < 3:
            return "insufficient_data"
        
        recent = [score for _, score in list(anomaly_history)[-5:]]
        avg_anomaly = sum(recent) / len(recent)
        
        if avg_anomaly > self.anomaly_threshold:
            # Check if increasing
            if len(recent) >= 2 and recent[-1] > recent[0]:
                return "escalating_anomalies"
            else:
                return "sustained_anomalies"
        elif avg_anomaly > self.anomaly_threshold / 2:
            return "moderate_anomalies"
        else:
            return "normal"
    
    def _decide(
        self,
        memory: AgentMemory,
        reasoning: Dict,
        agent_state: Optional[dict] = None
    ) -> Tuple[AgentDecision, float, List[str]]:
        """
        DECISION PHASE
        Autonomous decision-making based on reasoning
        
        Returns:
            (decision, confidence, contributing_factors)
        """
        factors = []
        confidence = 0.0
        
        trend = reasoning['trend']
        velocity = reasoning['velocity']
        is_critical = reasoning['is_critical']
        anomaly_pattern = reasoning['anomaly_pattern']
        agent_degraded = reasoning.get('agent_degraded', False)
        
        # DECISION LOGIC (Rule-based, deterministic)
        
        # 0. AGENT-CONFIRMED DEGRADATION → Higher confidence decisions
        if agent_degraded and agent_state:
            degradation_level = agent_state.get("degradation_level", 0)
            factors.append(f"agent_confirmed_degradation_{agent_state.get('degradation_type', 'UNKNOWN')}")
            
            # If agent reports severe degradation, fast-track to AUTO_HEAL
            if degradation_level >= 0.7:
                factors.append(f"severe_degradation_level_{degradation_level:.2f}")
                return AgentDecision.AUTO_HEAL, 0.90, factors
            elif degradation_level >= 0.4:
                factors.append(f"moderate_degradation_level_{degradation_level:.2f}")
                return AgentDecision.ESCALATE, 0.85, factors
        
        # 1. CRITICAL STATE → AUTO_HEAL or PREDICT_FAILURE
        if is_critical and memory.degradation_counter >= self.persistence_threshold:
            factors.append("critical_health_persistent")
            factors.append(f"degradation_count_{memory.degradation_counter}")
            
            if trend == HealthTrend.CRITICAL_DECLINE:
                factors.append("accelerating_decline")
                return AgentDecision.PREDICT_FAILURE, 0.95, factors
            else:
                factors.append("critical_but_stable")
                return AgentDecision.AUTO_HEAL, 0.85, factors
        
        # 2. DEGRADING WITH PERSISTENCE → ESCALATE
        if trend in [HealthTrend.DEGRADING, HealthTrend.CRITICAL_DECLINE]:
            if memory.degradation_counter >= self.persistence_threshold:
                factors.append("persistent_degradation")
                factors.append(f"velocity_{velocity:.2f}")
                return AgentDecision.ESCALATE, 0.80, factors
        
        # 3. IMPROVING AFTER DEGRADATION → DE_ESCALATE
        if trend == HealthTrend.IMPROVING and memory.degradation_counter > 0:
            factors.append("recovery_detected")
            factors.append(f"recovery_count_{memory.recovery_counter}")
            
            if memory.recovery_counter >= 2:
                factors.append("sustained_recovery")
                return AgentDecision.DE_ESCALATE, 0.75, factors
        
        # 4. ESCALATING ANOMALIES → ESCALATE
        if anomaly_pattern == "escalating_anomalies":
            factors.append("anomaly_escalation")
            return AgentDecision.ESCALATE, 0.70, factors
        
        # 5. EARLY WARNING: DEGRADING BUT NOT YET PERSISTENT
        if trend == HealthTrend.DEGRADING and memory.degradation_counter < self.persistence_threshold:
            factors.append("early_degradation_signal")
            # If agent confirms degradation, give more weight
            if agent_degraded:
                factors.append("agent_confirms_early_degradation")
                return AgentDecision.ESCALATE, 0.70, factors
            return AgentDecision.NO_ACTION, 0.60, factors
        
        # 6. AGENT RECOVERING → DE_ESCALATE with confidence
        if agent_state and agent_state.get("health_state") == "RECOVERING":
            factors.append("agent_self_recovering")
            return AgentDecision.DE_ESCALATE, 0.75, factors
        
        # 7. DEFAULT: STABLE SYSTEM
        factors.append("system_stable")
        return AgentDecision.NO_ACTION, 0.90, factors
    
    def get_node_memory_summary(self, node_id: str) -> Optional[Dict]:
        """Get current memory state for a node (for debugging/visibility)"""
        if node_id not in self.node_memories:
            return None
        
        memory = self.node_memories[node_id]
        return {
            'node_id': node_id,
            'health_history_size': len(memory.health_history),
            'degradation_counter': memory.degradation_counter,
            'recovery_counter': memory.recovery_counter,
            'last_decision': memory.last_decision,
            'last_decision_time': memory.last_decision_time,
            'incident_state': memory.incident_state,
            # NEW: Include agent state info
            'agent_state': memory.agent_state,
            'connection_state': memory.connection_state,
            'last_heartbeat_time': memory.last_heartbeat_time
        }
    
    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Get recent decision history across all nodes"""
        return [asdict(decision) for decision in list(self.decision_history)[-limit:]]
    
    def clear_node_memory(self, node_id: str):
        """Clear memory when node disconnects"""
        if node_id in self.node_memories:
            del self.node_memories[node_id]
