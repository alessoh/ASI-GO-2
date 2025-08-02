"""
Cognition Base - Repository of problem-solving knowledge
"""
import json
import os
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger("ASI-GO.CognitionBase")

class CognitionBase:
    """Stores and retrieves problem-solving patterns and strategies"""
    
    def __init__(self):
        self.knowledge_file = "cognition_knowledge.json"
        self.knowledge = self._load_knowledge()
        self.session_insights = []
        
    def _load_knowledge(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load existing knowledge from file"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load knowledge file: {e}")
        
        # Initialize with basic problem-solving patterns
        return {
            "strategies": [
                {
                    "name": "Divide and Conquer",
                    "description": "Break complex problems into smaller subproblems",
                    "applicable_to": ["optimization", "search", "mathematical problems"],
                    "example": "Finding prime numbers by checking divisibility up to sqrt(n)"
                },
                {
                    "name": "Iterative Refinement",
                    "description": "Start with a basic solution and improve it iteratively",
                    "applicable_to": ["algorithms", "numerical methods", "approximations"],
                    "example": "Newton's method for finding roots"
                },
                {
                    "name": "Pattern Recognition",
                    "description": "Identify patterns in the problem to simplify the solution",
                    "applicable_to": ["sequences", "mathematical series", "data analysis"],
                    "example": "Recognizing Fibonacci patterns in problems"
                }
            ],
            "common_errors": [
                {
                    "type": "Off-by-one errors",
                    "description": "Errors in loop boundaries or array indices",
                    "prevention": "Carefully check loop conditions and test edge cases"
                },
                {
                    "type": "Integer overflow",
                    "description": "Results exceeding data type limits",
                    "prevention": "Use appropriate data types and check for overflow conditions"
                }
            ],
            "optimization_techniques": [
                {
                    "name": "Memoization",
                    "description": "Cache results of expensive function calls",
                    "use_case": "Recursive algorithms with overlapping subproblems"
                },
                {
                    "name": "Early termination",
                    "description": "Stop computation when result is found or impossible",
                    "use_case": "Search algorithms and validation checks"
                }
            ]
        }
    
    def save_knowledge(self):
        """Persist knowledge to file"""
        try:
            with open(self.knowledge_file, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
            logger.info("Knowledge base saved successfully")
        except Exception as e:
            logger.error(f"Failed to save knowledge: {e}")
    
    def get_relevant_strategies(self, problem_description: str) -> List[Dict[str, Any]]:
        """Retrieve strategies relevant to the problem"""
        relevant_strategies = []
        
        # Simple keyword matching (could be enhanced with embeddings)
        keywords = problem_description.lower().split()
        
        for strategy in self.knowledge.get("strategies", []):
            for applicable in strategy.get("applicable_to", []):
                if any(keyword in applicable.lower() for keyword in keywords):
                    relevant_strategies.append(strategy)
                    break
        
        return relevant_strategies
    
    def add_insight(self, insight: Dict[str, Any]):
        """Add a new insight from the current session"""
        insight["timestamp"] = datetime.now().isoformat()
        self.session_insights.append(insight)
        
        # Add to permanent knowledge if significant
        if insight.get("significance", 0) > 0.7:
            if "learned_patterns" not in self.knowledge:
                self.knowledge["learned_patterns"] = []
            self.knowledge["learned_patterns"].append(insight)
            self.save_knowledge()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of insights from the current session"""
        return {
            "total_insights": len(self.session_insights),
            "insights": self.session_insights,
            "strategies_used": list(set(i.get("strategy") for i in self.session_insights if i.get("strategy")))
        }