"""
Analyst - Analyzes results and extracts insights
"""
import logging
from typing import Dict, Any, List
from llm_interface import LLMInterface
from cognition_base import CognitionBase

logger = logging.getLogger("ASI-GO.Analyst")

class Analyst:
    """Analyzes execution results and provides insights"""
    
    def __init__(self, llm: LLMInterface, cognition_base: CognitionBase):
        self.llm = llm
        self.cognition_base = cognition_base
        self.analyses = []
        
    def analyze_results(self, proposal: Dict[str, Any], test_result: Dict[str, Any], 
                       validation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the results of a solution attempt"""
        logger.info("Analyzing solution results")
        
        # Handle case where test_result might have None values
        output_preview = "None"
        if test_result.get('output'):
            output_preview = test_result['output'][:500] + "..." if len(test_result['output']) > 500 else test_result['output']
        
        system_prompt = """You are an expert at analyzing code execution results and providing insights.
        Focus on identifying what worked, what didn't, and why.
        Provide actionable recommendations for improvement."""
        
        prompt = f"""Goal: {proposal['goal']}
        
        Solution Summary:
        - Iteration: {proposal.get('iteration', 1)}
        - Strategies used: {proposal.get('strategies_used', [])}
        
        Execution Results:
        - Success: {test_result['success']}
        - Output: {output_preview}
        - Error: {test_result.get('error', 'None')}
        - Issues: {test_result.get('issues', [])}
        
        Validation:
        - Meets goal: {validation.get('meets_goal', False)}
        - Confidence: {validation.get('confidence', 0)}
        - Notes: {validation.get('notes', [])}
        
        Please provide:
        1. Analysis of what happened
        2. Why the solution succeeded or failed
        3. Specific improvements needed
        4. Lessons learned for future attempts
        5. A success probability score (0-1)"""
        
        try:
            response = self.llm.query(prompt, system_prompt)
            
            analysis = {
                "iteration": proposal.get('iteration', 1),
                "success": test_result['success'],
                "analysis": response,
                "test_result": test_result,
                "validation": validation
            }
            
            self.analyses.append(analysis)
            
            # Extract insights for cognition base
            self._extract_insights(analysis, proposal)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze results: {e}")
            # Return a basic analysis even if LLM fails
            basic_analysis = {
                "iteration": proposal.get('iteration', 1),
                "success": test_result['success'],
                "analysis": f"Analysis failed: {str(e)}. Test result: {'Success' if test_result['success'] else 'Failed'}",
                "test_result": test_result,
                "validation": validation
            }
            self.analyses.append(basic_analysis)
            return basic_analysis
    
    def _extract_insights(self, analysis: Dict[str, Any], proposal: Dict[str, Any]):
        """Extract insights from analysis for the cognition base"""
        try:
            insight = {
                "goal": proposal['goal'],
                "strategy": proposal.get('strategies_used', []),
                "success": analysis['success'],
                "key_learning": analysis.get('analysis', '')[:200] if analysis.get('analysis') else "No analysis available",
                "significance": 0.5 if analysis['success'] else 0.3
            }
            
            self.cognition_base.add_insight(insight)
        except Exception as e:
            logger.warning(f"Failed to extract insights: {e}")
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of all analyses"""
        if not self.analyses:
            return "No analyses performed yet."
        
        successful = sum(1 for a in self.analyses if a['success'])
        total = len(self.analyses)
        
        report = f"""
ASI-GO Analysis Summary
======================
Total Attempts: {total}
Successful: {successful}
Success Rate: {successful/total*100:.1f}%

Iterations:
"""
        for analysis in self.analyses:
            report += f"\n  Iteration {analysis['iteration']}: "
            report += "✓ Success" if analysis['success'] else "✗ Failed"
            if not analysis['success'] and analysis['test_result'].get('error'):
                error_msg = analysis['test_result']['error']
                # Truncate long error messages
                if len(error_msg) > 50:
                    error_msg = error_msg[:50] + "..."
                report += f" - {error_msg}"
        
        # Add session insights
        try:
            session_summary = self.cognition_base.get_session_summary()
            if session_summary['total_insights'] > 0:
                report += f"\n\nInsights Generated: {session_summary['total_insights']}"
                if session_summary['strategies_used']:
                    report += f"\nStrategies Used: {', '.join(str(s) for s in session_summary['strategies_used'] if s)}"
        except Exception as e:
            logger.warning(f"Failed to add session summary: {e}")
        
        return report
    
    def recommend_next_action(self) -> str:
        """Recommend the next action based on analysis history"""
        if not self.analyses:
            return "No data available. Start with a new proposal."
        
        last_analysis = self.analyses[-1]
        
        if last_analysis['success'] and last_analysis['validation'].get('meets_goal'):
            return "Goal achieved! Consider optimizing the solution or trying a more complex goal."
        elif last_analysis['success']:
            return "Solution runs but doesn't fully meet the goal. Refine the logic."
        elif len(self.analyses) >= 5:
            return "Multiple attempts failed. Consider revising the goal or approach fundamentally."
        else:
            return "Refine the current approach based on the error feedback."