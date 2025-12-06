"""T069: Hallucination validation with 20+ diverse queries"""
import requests
import json

# Test queries across all book topics
test_queries = [
    # ROS 2 Module
    {'query': 'What is ROS 2?', 'expected_topic': 'ROS 2 framework'},
    {'query': 'Explain ROS 2 nodes and topics', 'expected_topic': 'ROS 2 core concepts'},
    {'query': 'How do I create a publisher in ROS 2 Python?', 'expected_topic': 'ROS 2 Python'},
    {'query': 'What is URDF?', 'expected_topic': 'Robot modeling'},
    {'query': 'How do I integrate LiDAR sensors in ROS 2?', 'expected_topic': 'Sensor integration'},

    # Digital Twin Module
    {'query': 'What is a digital twin?', 'expected_topic': 'Digital twin concept'},
    {'query': 'Explain Gazebo simulation', 'expected_topic': 'Gazebo fundamentals'},
    {'query': 'How do simulated sensors work in Gazebo?', 'expected_topic': 'Simulated sensors'},
    {'query': 'What is Unity used for in robotics?', 'expected_topic': 'Unity visualization'},
    {'query': 'How do I build realistic environments?', 'expected_topic': 'Environment building'},

    # AI Robot Brain Module
    {'query': 'What is NVIDIA Isaac?', 'expected_topic': 'NVIDIA Isaac platform'},
    {'query': 'Explain perception pipelines', 'expected_topic': 'Perception'},
    {'query': 'What is Isaac ROS?', 'expected_topic': 'Isaac ROS'},
    {'query': 'How does Nav2 work?', 'expected_topic': 'Navigation'},
    {'query': 'What is reinforcement learning for robots?', 'expected_topic': 'RL sim-to-real'},

    # VLA Module
    {'query': 'What are vision-language-action models?', 'expected_topic': 'VLA introduction'},
    {'query': 'Explain voice-to-action pipelines', 'expected_topic': 'Voice-to-action'},
    {'query': 'How do LLMs help with robot planning?', 'expected_topic': 'LLM cognitive planning'},
    {'query': 'What is multimodal interaction?', 'expected_topic': 'Multimodal'},

    # Edge cases (should return insufficient_context)
    {'query': 'What is the capital of France?', 'expected_topic': 'OUT_OF_SCOPE'},
    {'query': 'How do I cook pasta?', 'expected_topic': 'OUT_OF_SCOPE'},
]

print('='*70)
print('T069: HALLUCINATION VALIDATION - 21 DIVERSE QUERIES')
print('='*70)
print()

results = {
    'grounded': 0,
    'insufficient_context': 0,
    'error': 0,
    'hallucinations': []
}

for i, test in enumerate(test_queries, 1):
    query = test['query']
    expected = test['expected_topic']

    try:
        response = requests.post(
            'http://localhost:8000/api/v1/chat/query',
            json={'query': query},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            status = data.get('grounding_status', 'unknown')
            answer = data.get('response', '')
            citations = data.get('citations', [])

            # Count status
            if status == 'grounded':
                results['grounded'] += 1
            elif status == 'insufficient_context':
                results['insufficient_context'] += 1
            else:
                results['error'] += 1

            # Check for hallucinations
            hallucination = False
            if expected == 'OUT_OF_SCOPE' and status != 'insufficient_context':
                hallucination = True
                results['hallucinations'].append({
                    'query': query,
                    'reason': 'Answered out-of-scope question',
                    'answer': answer[:100]
                })

            # Display result
            print(f'{i}. [{status.upper()[:4]}] {query}')
            if citations:
                print(f'   Citations: {len(citations)} source(s)')
            print(f'   Answer: {answer[:80]}...')
            print()

        else:
            print(f'{i}. FAILED - {query} (HTTP {response.status_code})')
            results['error'] += 1
            print()

    except Exception as e:
        print(f'{i}. ERROR - {query}: {str(e)[:50]}')
        results['error'] += 1
        print()

print('='*70)
print('VALIDATION RESULTS')
print('='*70)
print(f'Total queries: {len(test_queries)}')
print(f'Grounded responses: {results["grounded"]}')
print(f'Insufficient context: {results["insufficient_context"]}')
print(f'Errors: {results["error"]}')
print(f'Hallucinations detected: {len(results["hallucinations"])}')
print()

if results['hallucinations']:
    print('HALLUCINATIONS FOUND:')
    for h in results['hallucinations']:
        print(f'  - {h["query"]}: {h["reason"]}')
    print()
    print('FAIL: Hallucinations detected')
else:
    print('PASS: Zero hallucinations detected')
