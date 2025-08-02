"""
Researcher - Proposes solutions based on goals and knowledge
"""
import logging
from typing import Dict, Any, Optional
from llm_interface import LLMInterface
from cognition_base import CognitionBase

logger = logging.getLogger("ASI-GO.Researcher")

class Researcher:
    """Generates solution proposals for given problems"""
    
    def __init__(self, llm: LLMInterface, cognition_base: CognitionBase):
        self.llm = llm
        self.cognition_base = cognition_base
        self.proposal_history = []
        
    def propose_solution(self, goal: str, previous_attempt: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Propose a solution for the given goal"""
        logger.info(f"Proposing solution for goal: {goal}")
        
        # Get relevant strategies from cognition base
        strategies = self.cognition_base.get_relevant_strategies(goal)
        
        # Build the prompt
        system_prompt = """You are an expert problem solver and programmer. 
        Your task is to propose a complete, working solution for the given problem.
        Include clear, well-commented code with error handling.
        Explain your approach and why it should work."""
        
        prompt = f"Goal: {goal}\n\n"
        
        if strategies:
            prompt += "Relevant problem-solving strategies:\n"
            for strategy in strategies:
                prompt += f"- {strategy['name']}: {strategy['description']}\n"
            prompt += "\n"
        
        if previous_attempt:
            prompt += f"Previous attempt failed with: {previous_attempt.get('error', 'Unknown error')}\n"
            prompt += "Please provide an improved solution.\n\n"
        
        prompt += """Please provide:
        1. A clear explanation of your approach
        2. Complete, working Python code
        3. Expected output or results
        4. Time and space complexity analysis if applicable"""
        
        try:
            response = self.llm.query(prompt, system_prompt)
            
            proposal = {
                "goal": goal,
                "solution": response,
                "strategies_used": [s['name'] for s in strategies],
                "iteration": len(self.proposal_history) + 1
            }
            
            self.proposal_history.append(proposal)
            logger.info("Solution proposal generated successfully")
            
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to generate proposal: {e}")
            raise
    
    def refine_proposal(self, proposal: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Refine a proposal based on feedback"""
        logger.info("Refining proposal based on feedback")
        
        system_prompt = "You are an expert at improving and debugging code based on feedback."
        
        prompt = f"""Original Goal: {proposal['goal']}
        
        Previous Solution:
        {proposal['solution']}
        
        Feedback from testing:
        - Success: {feedback.get('success', False)}
        - Error: {feedback.get('error', 'None')}
        - Output: {feedback.get('output', 'None')}
        - Issues: {feedback.get('issues', [])}
        
        Please provide an improved solution that addresses the feedback.
        Keep what works and fix what doesn't."""
        
        try:
            response = self.llm.query(prompt, system_prompt)
            
            refined_proposal = {
                "goal": proposal['goal'],
                "solution": response,
                "strategies_used": proposal.get('strategies_used', []),
                "iteration": proposal['iteration'] + 1,
                "refined_from": proposal['iteration']
            }
            
            self.proposal_history.append(refined_proposal)
            return refined_proposal
            
        except Exception as e:
            logger.error(f"Failed to refine proposal: {e}")
            raise