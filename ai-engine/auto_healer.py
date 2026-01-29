"""
AGENTIC AUTO-HEALER MODULE
===========================
Policy-driven, non-destructive auto-healing system.

IMPORTANT CONSTRAINTS:
- NO OS commands
- NO process killing
- NO system modification
- ALL actions are SAFE and SIMULATED

Healing Capabilities:
1. Adaptive Monitoring - Adjust sampling rates
2. Incident Self-Resolution - Auto-close recovered incidents
3. Simulated Corrective Actions - Gradual health recovery simulation
4. Verification Loops - Confirm recovery or escalate

This module provides DEFENSIBLE auto-healing for demos and vivas.
"""

import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import deque


class HealingActionType(Enum):
    """Types of safe, non-destructive healing actions"""
    ADAPTIVE_MONITORING_INCREASE = "ADAPTIVE_MONITORING_INCREASE"
    ADAPTIVE_MONITORING_DECREASE = "ADAPTIVE_MONITORING_DECREASE"
    INCIDENT_AUTO_RESOLVE = "INCIDENT_AUTO_RESOLVE"
    SIMULATED_HEALTH_BOOST = "SIMULATED_HEALTH_BOOST"
    SIMULATED_ANOMALY_DECAY = "SIMULATED_ANOMALY_DECAY"
    VERIFICATION_CHECK = "VERIFICATION_CHECK"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class VerificationStatus(Enum):
    """Status of healing verification"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


@dataclass
class HealingAction:
    """Structured output for every healing action"""
    node_id: str
    action: str
    action_type: str  # "SIMULATED" or "REAL"
    result: str
    confidence: float
    verification_status: str
    timestamp: float
    details: Dict


@dataclass
class AdaptiveMonitoringState:
    """Tracks sampling rate adjustments per node"""
    node_id: str
    base_interval_seconds: float
    current_interval_seconds: float
    last_adjustment_time: float
    reason: str


@dataclass
class HealingMemory:
    """Memory state for healing per node"""
    node_id: str
    healing_attempts: deque  # History of healing actions
    last_healing_time: Optional[float]
    active_healing: bool
    verification_pending: bool
    verification_deadline: Optional[float]
    pre_healing_health: Optional[float]
    post_healing_health: Optional[float]
    consecutive_failures: int


class AutoHealer:
    """
    AGENTIC AUTO-HEALING ENGINE
    
    Responsibilities:
    1. Interpret DecisionAgent decisions
    2. Execute SAFE healing policies
    3. Adjust monitoring behavior adaptively
    4. Verify healing outcomes
    5. Escalate when healing fails
    
    ALL ACTIONS ARE NON-DESTRUCTIVE.
    """
    
    def __init__(
        self,
        base_sampling_interval: float = 5.0,
        min_sampling_interval: float = 1.0,
        max_sampling_interval: float = 15.0,
        verification_window_seconds: float = 30.0,
        max_healing_attempts: int = 3
    ):
        """
        Initialize the auto-healer with safety constraints
        
        Args:
            base_sampling_interval: Normal sampling rate (seconds)
            min_sampling_interval: Fastest sampling during crisis
            max_sampling_interval: Slowest sampling when stable
            verification_window_seconds: Time to verify healing
            max_healing_attempts: Max attempts before escalating
        """
        self.base_sampling_interval = base_sampling_interval
        self.min_sampling_interval = min_sampling_interval
        self.max_sampling_interval = max_sampling_interval
        self.verification_window_seconds = verification_window_seconds
        self.max_healing_attempts = max_healing_attempts
        
        # Per-node healing memory
        self.healing_memories: Dict[str, HealingMemory] = {}
        
        # Per-node adaptive monitoring state
        self.monitoring_states: Dict[str, AdaptiveMonitoringState] = {}
        
        # Global healing history for audit
        self.healing_history: deque = deque(maxlen=100)
        
        # Simulated health modifiers (for demo purposes)
        # These DON'T modify actual system - only the reported metrics
        self.health_modifiers: Dict[str, float] = {}
        self.anomaly_modifiers: Dict[str, float] = {}
    
    def _get_or_create_memory(self, node_id: str) -> HealingMemory:
        """Get or create healing memory for a node"""
        if node_id not in self.healing_memories:
            self.healing_memories[node_id] = HealingMemory(
                node_id=node_id,
                healing_attempts=deque(maxlen=10),
                last_healing_time=None,
                active_healing=False,
                verification_pending=False,
                verification_deadline=None,
                pre_healing_health=None,
                post_healing_health=None,
                consecutive_failures=0
            )
        return self.healing_memories[node_id]
    
    def _get_or_create_monitoring_state(self, node_id: str) -> AdaptiveMonitoringState:
        """Get or create monitoring state for a node"""
        if node_id not in self.monitoring_states:
            self.monitoring_states[node_id] = AdaptiveMonitoringState(
                node_id=node_id,
                base_interval_seconds=self.base_sampling_interval,
                current_interval_seconds=self.base_sampling_interval,
                last_adjustment_time=time.time(),
                reason="initialized"
            )
        return self.monitoring_states[node_id]
    
    def process_decision(
        self,
        node_id: str,
        agent_decision: str,
        health_score: float,
        anomaly_score: float,
        confidence: float
    ) -> List[HealingAction]:
        """
        Process an agent decision and execute appropriate healing actions
        
        Args:
            node_id: The node identifier
            agent_decision: Decision from DecisionAgent
            health_score: Current health score
            anomaly_score: Current anomaly score
            confidence: Decision confidence
            
        Returns:
            List of HealingAction objects describing what was done
        """
        actions = []
        timestamp = time.time()
        memory = self._get_or_create_memory(node_id)
        
        # First, check if we have pending verification
        if memory.verification_pending:
            verification_action = self._verify_healing(node_id, health_score)
            actions.append(verification_action)
        
        # Process based on decision type
        if agent_decision == "AUTO_HEAL":
            actions.extend(self._execute_auto_heal(
                node_id, health_score, anomaly_score, confidence
            ))
            
        elif agent_decision == "ESCALATE":
            actions.extend(self._execute_escalation_response(
                node_id, health_score, anomaly_score
            ))
            
        elif agent_decision == "PREDICT_FAILURE":
            actions.extend(self._execute_failure_prevention(
                node_id, health_score, anomaly_score
            ))
            
        elif agent_decision == "DE_ESCALATE":
            actions.extend(self._execute_de_escalation(
                node_id, health_score, anomaly_score
            ))
            
        elif agent_decision == "NO_ACTION":
            actions.extend(self._execute_stable_maintenance(
                node_id, health_score, anomaly_score
            ))
        
        # Record all actions in history
        for action in actions:
            self.healing_history.append(action)
            memory.healing_attempts.append(action)
        
        return actions
    
    def _execute_auto_heal(
        self,
        node_id: str,
        health_score: float,
        anomaly_score: float,
        confidence: float
    ) -> List[HealingAction]:
        """
        Execute AUTO_HEAL decision
        
        Actions:
        1. Increase monitoring frequency
        2. Apply simulated health boost
        3. Apply simulated anomaly decay
        4. Set up verification
        """
        actions = []
        timestamp = time.time()
        memory = self._get_or_create_memory(node_id)
        
        # Check if we've exceeded max attempts
        if memory.consecutive_failures >= self.max_healing_attempts:
            actions.append(HealingAction(
                node_id=node_id,
                action="ESCALATE_TO_HUMAN",
                action_type="REAL",
                result=f"Max healing attempts ({self.max_healing_attempts}) exceeded",
                confidence=0.95,
                verification_status=VerificationStatus.FAILED.value,
                timestamp=timestamp,
                details={
                    "consecutive_failures": memory.consecutive_failures,
                    "recommendation": "Manual intervention required"
                }
            ))
            return actions
        
        # Action 1: Adaptive monitoring - increase frequency
        monitoring_action = self._adjust_monitoring(
            node_id, 
            HealingActionType.ADAPTIVE_MONITORING_INCREASE,
            "auto_heal_triggered"
        )
        actions.append(monitoring_action)
        
        # Action 2: Simulated health boost (MARKED AS SIMULATED)
        health_boost = min(10.0, (100 - health_score) * 0.15)  # 15% of deficit
        self.health_modifiers[node_id] = self.health_modifiers.get(node_id, 0) + health_boost
        
        actions.append(HealingAction(
            node_id=node_id,
            action="AUTO_HEAL_HEALTH_BOOST",
            action_type="SIMULATED",  # Clearly marked
            result=f"Applied simulated health boost of {health_boost:.1f} points",
            confidence=confidence,
            verification_status=VerificationStatus.PENDING.value,
            timestamp=timestamp,
            details={
                "boost_amount": health_boost,
                "pre_health": health_score,
                "expected_post_health": min(100, health_score + health_boost),
                "note": "This is a SIMULATION - actual system unchanged"
            }
        ))
        
        # Action 3: Simulated anomaly decay
        anomaly_decay = anomaly_score * 0.2  # 20% decay
        self.anomaly_modifiers[node_id] = self.anomaly_modifiers.get(node_id, 0) - anomaly_decay
        
        actions.append(HealingAction(
            node_id=node_id,
            action="AUTO_HEAL_ANOMALY_DECAY",
            action_type="SIMULATED",
            result=f"Applied simulated anomaly decay of {anomaly_decay:.2f}",
            confidence=confidence,
            verification_status=VerificationStatus.PENDING.value,
            timestamp=timestamp,
            details={
                "decay_amount": anomaly_decay,
                "pre_anomaly": anomaly_score,
                "expected_post_anomaly": max(0, anomaly_score - anomaly_decay),
                "note": "This is a SIMULATION - actual system unchanged"
            }
        ))
        
        # Set up verification
        memory.active_healing = True
        memory.verification_pending = True
        memory.verification_deadline = timestamp + self.verification_window_seconds
        memory.pre_healing_health = health_score
        memory.last_healing_time = timestamp
        
        return actions
    
    def _execute_escalation_response(
        self,
        node_id: str,
        health_score: float,
        anomaly_score: float
    ) -> List[HealingAction]:
        """
        Respond to ESCALATE decision
        
        Actions:
        1. Increase monitoring frequency significantly
        2. Log escalation for visibility
        """
        actions = []
        timestamp = time.time()
        
        # Aggressive monitoring increase
        monitoring_action = self._adjust_monitoring(
            node_id,
            HealingActionType.ADAPTIVE_MONITORING_INCREASE,
            "escalation_detected"
        )
        actions.append(monitoring_action)
        
        actions.append(HealingAction(
            node_id=node_id,
            action="ESCALATION_ACKNOWLEDGED",
            action_type="REAL",
            result="System under close observation due to escalation",
            confidence=0.85,
            verification_status=VerificationStatus.PENDING.value,
            timestamp=timestamp,
            details={
                "health_score": health_score,
                "anomaly_score": anomaly_score,
                "action": "Increased monitoring frequency, awaiting stabilization"
            }
        ))
        
        return actions
    
    def _execute_failure_prevention(
        self,
        node_id: str,
        health_score: float,
        anomaly_score: float
    ) -> List[HealingAction]:
        """
        Respond to PREDICT_FAILURE decision
        
        Actions:
        1. Maximum monitoring frequency
        2. Log critical state
        3. Prepare for incident auto-resolution when recovery detected
        """
        actions = []
        timestamp = time.time()
        
        # Maximum monitoring frequency
        state = self._get_or_create_monitoring_state(node_id)
        state.current_interval_seconds = self.min_sampling_interval
        state.last_adjustment_time = timestamp
        state.reason = "failure_prevention"
        
        actions.append(HealingAction(
            node_id=node_id,
            action="FAILURE_PREVENTION_MODE",
            action_type="REAL",
            result=f"Maximum monitoring activated (interval: {self.min_sampling_interval}s)",
            confidence=0.95,
            verification_status=VerificationStatus.PENDING.value,
            timestamp=timestamp,
            details={
                "health_score": health_score,
                "anomaly_score": anomaly_score,
                "monitoring_interval": self.min_sampling_interval,
                "alert_level": "CRITICAL",
                "note": "System at risk - intensive monitoring enabled"
            }
        ))
        
        return actions
    
    def _execute_de_escalation(
        self,
        node_id: str,
        health_score: float,
        anomaly_score: float
    ) -> List[HealingAction]:
        """
        Respond to DE_ESCALATE decision
        
        Actions:
        1. Gradually reduce monitoring frequency
        2. Consider incident auto-resolution
        3. Clear simulated modifiers
        """
        actions = []
        timestamp = time.time()
        memory = self._get_or_create_memory(node_id)
        
        # Reduce monitoring frequency
        monitoring_action = self._adjust_monitoring(
            node_id,
            HealingActionType.ADAPTIVE_MONITORING_DECREASE,
            "de_escalation_recovery"
        )
        actions.append(monitoring_action)
        
        # Clear simulated modifiers (system recovered naturally)
        if node_id in self.health_modifiers:
            del self.health_modifiers[node_id]
        if node_id in self.anomaly_modifiers:
            del self.anomaly_modifiers[node_id]
        
        # Reset healing state
        memory.active_healing = False
        memory.consecutive_failures = 0
        
        # Auto-resolve incident if recovery confirmed
        actions.append(HealingAction(
            node_id=node_id,
            action="INCIDENT_AUTO_RESOLVE",
            action_type="REAL",
            result="Incident auto-resolved due to sustained recovery",
            confidence=0.80,
            verification_status=VerificationStatus.SUCCESS.value,
            timestamp=timestamp,
            details={
                "health_score": health_score,
                "anomaly_score": anomaly_score,
                "recovery_confirmed": True
            }
        ))
        
        return actions
    
    def _execute_stable_maintenance(
        self,
        node_id: str,
        health_score: float,
        anomaly_score: float
    ) -> List[HealingAction]:
        """
        Respond to NO_ACTION decision (stable system)
        
        Actions:
        1. Gradually return to baseline monitoring
        2. Clear any stale modifiers
        """
        actions = []
        timestamp = time.time()
        state = self._get_or_create_monitoring_state(node_id)
        
        # Only adjust if not already at baseline
        if state.current_interval_seconds != self.base_sampling_interval:
            # Gradual return to baseline
            if state.current_interval_seconds < self.base_sampling_interval:
                new_interval = min(
                    self.base_sampling_interval,
                    state.current_interval_seconds * 1.5
                )
            else:
                new_interval = self.base_sampling_interval
            
            state.current_interval_seconds = new_interval
            state.last_adjustment_time = timestamp
            state.reason = "stable_normalization"
            
            actions.append(HealingAction(
                node_id=node_id,
                action="ADAPTIVE_MONITORING_NORMALIZE",
                action_type="REAL",
                result=f"Monitoring interval adjusting to {new_interval:.1f}s",
                confidence=0.90,
                verification_status=VerificationStatus.SUCCESS.value,
                timestamp=timestamp,
                details={
                    "previous_interval": state.current_interval_seconds,
                    "new_interval": new_interval,
                    "target_interval": self.base_sampling_interval
                }
            ))
        
        # Clear stale modifiers
        if node_id in self.health_modifiers:
            del self.health_modifiers[node_id]
        if node_id in self.anomaly_modifiers:
            del self.anomaly_modifiers[node_id]
        
        return actions
    
    def _adjust_monitoring(
        self,
        node_id: str,
        action_type: HealingActionType,
        reason: str
    ) -> HealingAction:
        """Adjust monitoring frequency adaptively"""
        timestamp = time.time()
        state = self._get_or_create_monitoring_state(node_id)
        old_interval = state.current_interval_seconds
        
        if action_type == HealingActionType.ADAPTIVE_MONITORING_INCREASE:
            # Faster sampling during issues
            new_interval = max(
                self.min_sampling_interval,
                old_interval * 0.5  # Cut in half
            )
        else:
            # Slower sampling when stable
            new_interval = min(
                self.max_sampling_interval,
                old_interval * 1.5  # Increase by 50%
            )
        
        state.current_interval_seconds = new_interval
        state.last_adjustment_time = timestamp
        state.reason = reason
        
        return HealingAction(
            node_id=node_id,
            action=action_type.value,
            action_type="REAL",
            result=f"Sampling interval: {old_interval:.1f}s → {new_interval:.1f}s",
            confidence=0.90,
            verification_status=VerificationStatus.SUCCESS.value,
            timestamp=timestamp,
            details={
                "previous_interval": old_interval,
                "new_interval": new_interval,
                "reason": reason
            }
        )
    
    def _verify_healing(
        self,
        node_id: str,
        current_health: float
    ) -> HealingAction:
        """
        VERIFICATION LOOP
        Check if healing was successful
        """
        timestamp = time.time()
        memory = self._get_or_create_memory(node_id)
        
        if memory.pre_healing_health is None:
            return HealingAction(
                node_id=node_id,
                action="VERIFICATION_CHECK",
                action_type="REAL",
                result="No baseline health to verify against",
                confidence=0.5,
                verification_status=VerificationStatus.PENDING.value,
                timestamp=timestamp,
                details={}
            )
        
        health_improvement = current_health - memory.pre_healing_health
        memory.post_healing_health = current_health
        
        # Determine verification status
        if health_improvement >= 10:
            status = VerificationStatus.SUCCESS
            memory.consecutive_failures = 0
            memory.verification_pending = False
            memory.active_healing = False
            result = f"Healing SUCCESS: Health improved by {health_improvement:.1f} points"
        elif health_improvement >= 0:
            status = VerificationStatus.PARTIAL
            result = f"Healing PARTIAL: Health improved by {health_improvement:.1f} points"
        else:
            status = VerificationStatus.FAILED
            memory.consecutive_failures += 1
            result = f"Healing FAILED: Health declined by {abs(health_improvement):.1f} points"
        
        # Check if verification deadline passed
        if memory.verification_deadline and timestamp > memory.verification_deadline:
            memory.verification_pending = False
            if status != VerificationStatus.SUCCESS:
                status = VerificationStatus.FAILED
                memory.consecutive_failures += 1
        
        return HealingAction(
            node_id=node_id,
            action="VERIFICATION_CHECK",
            action_type="REAL",
            result=result,
            confidence=0.85,
            verification_status=status.value,
            timestamp=timestamp,
            details={
                "pre_healing_health": memory.pre_healing_health,
                "post_healing_health": current_health,
                "improvement": health_improvement,
                "consecutive_failures": memory.consecutive_failures
            }
        )
    
    def get_health_modifier(self, node_id: str) -> float:
        """Get current health modifier for a node (for simulated healing)"""
        return self.health_modifiers.get(node_id, 0.0)
    
    def get_anomaly_modifier(self, node_id: str) -> float:
        """Get current anomaly modifier for a node (for simulated healing)"""
        return self.anomaly_modifiers.get(node_id, 0.0)
    
    def get_monitoring_interval(self, node_id: str) -> float:
        """Get current recommended monitoring interval for a node"""
        state = self._get_or_create_monitoring_state(node_id)
        return state.current_interval_seconds
    
    def get_healing_status(self, node_id: str) -> Dict:
        """Get current healing status for a node"""
        memory = self._get_or_create_memory(node_id)
        state = self._get_or_create_monitoring_state(node_id)
        
        return {
            "node_id": node_id,
            "active_healing": memory.active_healing,
            "verification_pending": memory.verification_pending,
            "consecutive_failures": memory.consecutive_failures,
            "last_healing_time": memory.last_healing_time,
            "monitoring_interval": state.current_interval_seconds,
            "health_modifier": self.health_modifiers.get(node_id, 0),
            "anomaly_modifier": self.anomaly_modifiers.get(node_id, 0)
        }
    
    def get_healing_history(self, limit: int = 10) -> List[Dict]:
        """Get recent healing actions across all nodes"""
        return [asdict(action) for action in list(self.healing_history)[-limit:]]
    
    def clear_node_state(self, node_id: str):
        """Clear all healing state when node disconnects"""
        if node_id in self.healing_memories:
            del self.healing_memories[node_id]
        if node_id in self.monitoring_states:
            del self.monitoring_states[node_id]
        if node_id in self.health_modifiers:
            del self.health_modifiers[node_id]
        if node_id in self.anomaly_modifiers:
            del self.anomaly_modifiers[node_id]
