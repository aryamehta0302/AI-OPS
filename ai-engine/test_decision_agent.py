"""
TEST SCRIPT FOR DECISION AGENT
Simulates various system states to verify agent behavior
"""

import sys
import time
from decision_agent import DecisionAgent, AgentDecision, HealthTrend


def print_decision(reasoning, cycle):
    """Pretty print agent decision"""
    print(f"\n{'='*60}")
    print(f"CYCLE {cycle} - Node: {reasoning.node_id}")
    print(f"{'='*60}")
    print(f"Health Score: {reasoning.health_score:.1f}")
    print(f"Anomaly Score: {reasoning.anomaly_score:.2f}")
    print(f"Trend: {reasoning.health_trend} (velocity: {reasoning.trend_velocity:.2f})")
    print(f"Persistence: {reasoning.persistence} cycles")
    print(f"\n🤖 AGENT DECISION: {reasoning.decision}")
    print(f"   Confidence: {reasoning.confidence:.2%}")
    print(f"   Factors: {', '.join(reasoning.contributing_factors)}")
    print(f"\n📋 Reasoning Chain:")
    for i, step in enumerate(reasoning.reasoning_chain, 1):
        print(f"   {i}. {step}")


def test_scenario_1_normal_operation():
    """Test: Stable system with normal health"""
    print("\n" + "="*60)
    print("SCENARIO 1: Normal Operation")
    print("="*60)
    
    agent = DecisionAgent()
    node_id = "TEST-NODE-1"
    
    for cycle in range(5):
        health = 85.0 + (cycle * 0.5)  # Slight improvement
        anomaly = 0.15
        
        reasoning = agent.perceive(
            node_id=node_id,
            health_score=health,
            anomaly_score=anomaly,
            root_cause=None
        )
        
        print_decision(reasoning, cycle + 1)
        time.sleep(0.5)
    
    # Verify: Should be NO_ACTION with high confidence
    assert reasoning.decision == "NO_ACTION"
    assert reasoning.confidence >= 0.80
    print("\n✅ SCENARIO 1 PASSED: Agent correctly maintains NO_ACTION for stable system")


def test_scenario_2_gradual_degradation():
    """Test: Gradual health decline triggering ESCALATE"""
    print("\n" + "="*60)
    print("SCENARIO 2: Gradual Degradation")
    print("="*60)
    
    agent = DecisionAgent()
    node_id = "TEST-NODE-2"
    
    health_scores = [85, 80, 75, 68, 65, 62, 60]  # Declining
    
    for cycle, health in enumerate(health_scores):
        anomaly = 0.3 + (cycle * 0.05)  # Increasing anomalies
        
        reasoning = agent.perceive(
            node_id=node_id,
            health_score=health,
            anomaly_score=anomaly,
            root_cause="CPU"
        )
        
        print_decision(reasoning, cycle + 1)
        time.sleep(0.5)
    
    # Verify: Should ESCALATE after persistence threshold
    assert reasoning.decision == "ESCALATE"
    assert reasoning.persistence >= 3
    print("\n✅ SCENARIO 2 PASSED: Agent correctly escalated after persistent degradation")


def test_scenario_3_critical_failure():
    """Test: Rapid decline to critical state"""
    print("\n" + "="*60)
    print("SCENARIO 3: Critical Failure")
    print("="*60)
    
    agent = DecisionAgent()
    node_id = "TEST-NODE-3"
    
    health_scores = [80, 70, 55, 45, 40, 38]  # Rapid decline
    
    for cycle, health in enumerate(health_scores):
        anomaly = 0.6 + (cycle * 0.1)
        
        reasoning = agent.perceive(
            node_id=node_id,
            health_score=health,
            anomaly_score=anomaly,
            root_cause="MEMORY"
        )
        
        print_decision(reasoning, cycle + 1)
        time.sleep(0.5)
    
    # Verify: Should predict failure or auto-heal
    assert reasoning.decision in ["PREDICT_FAILURE", "AUTO_HEAL"]
    assert reasoning.health_score < 50
    print("\n✅ SCENARIO 3 PASSED: Agent correctly detected critical state")


def test_scenario_4_recovery():
    """Test: System recovery triggering DE_ESCALATE"""
    print("\n" + "="*60)
    print("SCENARIO 4: System Recovery")
    print("="*60)
    
    agent = DecisionAgent()
    node_id = "TEST-NODE-4"
    
    # First degrade
    health_scores = [85, 75, 65, 60]  # Degradation
    for cycle, health in enumerate(health_scores):
        reasoning = agent.perceive(
            node_id=node_id,
            health_score=health,
            anomaly_score=0.5,
            root_cause="CPU"
        )
        print_decision(reasoning, cycle + 1)
        time.sleep(0.3)
    
    # Now recover
    health_scores = [65, 72, 78, 82]  # Recovery
    for cycle, health in enumerate(health_scores, start=5):
        reasoning = agent.perceive(
            node_id=node_id,
            health_score=health,
            anomaly_score=0.3,
            root_cause=None
        )
        print_decision(reasoning, cycle)
        time.sleep(0.3)
    
    # Verify: Should DE_ESCALATE after sustained recovery
    assert reasoning.decision == "DE_ESCALATE"
    assert reasoning.health_trend in ["IMPROVING", "STABLE"]
    print("\n✅ SCENARIO 4 PASSED: Agent correctly de-escalated during recovery")


def test_scenario_5_multi_node():
    """Test: Multiple nodes with independent memory"""
    print("\n" + "="*60)
    print("SCENARIO 5: Multi-Node Independence")
    print("="*60)
    
    agent = DecisionAgent()
    
    # Node 1: Stable
    reasoning1 = agent.perceive("NODE-1", 85, 0.2, None)
    reasoning1 = agent.perceive("NODE-1", 86, 0.18, None)
    reasoning1 = agent.perceive("NODE-1", 84, 0.22, None)
    
    # Node 2: Degrading
    reasoning2 = agent.perceive("NODE-2", 75, 0.4, "CPU")
    reasoning2 = agent.perceive("NODE-2", 65, 0.5, "CPU")
    reasoning2 = agent.perceive("NODE-2", 60, 0.6, "CPU")
    reasoning2 = agent.perceive("NODE-2", 55, 0.65, "CPU")
    
    print("\n📊 NODE-1 Status:")
    print_decision(reasoning1, 3)
    
    print("\n📊 NODE-2 Status:")
    print_decision(reasoning2, 4)
    
    # Verify: Different decisions for different nodes
    assert reasoning1.decision == "NO_ACTION"
    assert reasoning2.decision == "ESCALATE"
    print("\n✅ SCENARIO 5 PASSED: Agent maintains independent memory per node")


def test_memory_persistence():
    """Test: Agent memory tracking"""
    print("\n" + "="*60)
    print("SCENARIO 6: Memory Persistence")
    print("="*60)
    
    agent = DecisionAgent()
    node_id = "TEST-NODE-MEM"
    
    # Cause degradation
    for i in range(5):
        agent.perceive(node_id, 60, 0.5, "CPU")
    
    # Check memory
    memory = agent.get_node_memory_summary(node_id)
    print(f"\n📝 Agent Memory State:")
    print(f"   Node: {memory['node_id']}")
    print(f"   History Size: {memory['health_history_size']}")
    print(f"   Degradation Counter: {memory['degradation_counter']}")
    print(f"   Last Decision: {memory['last_decision']}")
    
    assert memory['degradation_counter'] >= 3
    assert memory['health_history_size'] == 5
    print("\n✅ SCENARIO 6 PASSED: Agent correctly maintains memory")


def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "🧪"*30)
    print("DECISION AGENT TEST SUITE")
    print("🧪"*30)
    
    try:
        test_scenario_1_normal_operation()
        test_scenario_2_gradual_degradation()
        test_scenario_3_critical_failure()
        test_scenario_4_recovery()
        test_scenario_5_multi_node()
        test_memory_persistence()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nThe DecisionAgent is working correctly!")
        print("It demonstrates:")
        print("  ✓ Autonomous decision-making")
        print("  ✓ Memory and state tracking")
        print("  ✓ Trend analysis and reasoning")
        print("  ✓ Persistence detection")
        print("  ✓ Multi-node independence")
        print("  ✓ Structured explanations")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
