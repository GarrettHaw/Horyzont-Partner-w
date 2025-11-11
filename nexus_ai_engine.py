"""
Nexus AI Engine - Advanced Multi-Model Advisory System
========================================================

Nexus is the meta-advisor that synthesizes insights from multiple AI models
and provides comprehensive, balanced advice to the partnership.

Current Configuration: Single model (Gemini Pro)
Future Expansion: Ensemble of 3 sub-agents (Analytical, Creative, Critical)

Author: Horyzont Partnerów
Version: 1.0
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import google.generativeai as genai

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are set

# Funkcja do bezpiecznego pobierania kluczy API
def get_api_key(key_name):
    """Pobiera klucz API z Streamlit Secrets lub zmiennych środowiskowych."""
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key_name in st.secrets:
            return st.secrets[key_name]
    except:
        pass
    return os.getenv(key_name)

# API Keys - Nexus ma dedykowane konto Gemini!
GEMINI_KEY = get_api_key('GOOGLE_API_KEY_NEXUS') or get_api_key('GOOGLE_API_KEY')
ANTHROPIC_KEY = get_api_key('ANTHROPIC_API_KEY')
OPENAI_KEY = get_api_key('OPENAI_API_KEY')

# File paths
PERSONA_MEMORY_FILE = "persona_memory.json"
ADVISOR_SCORING_FILE = "advisor_scoring.json"


class NexusAIEngine:
    """
    Nexus AI Engine - Meta-advisor with ensemble learning capabilities
    
    Architecture:
    - Single mode: Uses only Gemini Pro (current)
    - Ensemble mode: 3 sub-agents with weighted voting (future)
    
    Features:
    - Context synthesis from multiple data sources
    - Autonomous decision making
    - Performance tracking
    - Automatic ensemble activation when conditions met
    """
    
    def __init__(self):
        """Initialize Nexus AI Engine"""
        self.config = self._load_config()
        self.mode = self.config.get('mode', 'single')
        self.current_model = self.config.get('current_model', 'gemini-pro')
        self.ensemble_enabled = self.config.get('ensemble_config', {}).get('enabled', False)
        
        # Initialize AI clients
        self._init_ai_clients()
        
        # Performance tracking
        self.performance = self.config.get('performance_tracking', {
            'response_quality_score': 0.0,
            'user_satisfaction_ratings': [],
            'avg_response_time_ms': 0,
            'total_queries_handled': 0
        })
        
        print("✅ Nexus AI Engine initialized")
        print(f"   Mode: {self.mode}")
        print(f"   Current Model: {self.current_model}")
        print(f"   Ensemble: {'Enabled' if self.ensemble_enabled else 'Disabled'}")
    
    def _load_config(self) -> Dict:
        """Load Nexus configuration from persona_memory.json"""
        try:
            with open(PERSONA_MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                nexus_persona = data.get('Nexus', {})
                return nexus_persona.get('ai_config', {})
        except Exception as e:
            print(f"⚠️ Error loading Nexus config: {e}")
            return {}
    
    def _save_config(self):
        """Save updated configuration back to persona_memory.json"""
        try:
            with open(PERSONA_MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update Nexus config
            if 'Nexus' in data:
                data['Nexus']['ai_config'] = self.config
                data['Nexus']['ai_config']['performance_tracking'] = self.performance
            
            with open(PERSONA_MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"❌ Error saving Nexus config: {e}")
            return False
    
    def _init_ai_clients(self):
        """Initialize AI model clients based on current configuration"""
        self.gemini_client = None
        self.claude_client = None
        self.openai_client = None
        
        # Always initialize Gemini (primary model)
        if GEMINI_KEY:
            try:
                genai.configure(api_key=GEMINI_KEY)
                # CRITICAL: Use gemini-2.5-pro (NOT 2.0-flash-exp - deprecated!)
                self.gemini_client = genai.GenerativeModel('gemini-2.5-pro')
                print("   ✓ Gemini client initialized (gemini-2.5-pro)")
            except Exception as e:
                print(f"   ⚠️ Gemini initialization failed: {e}")
        
        # Initialize additional models only if ensemble is enabled
        if self.ensemble_enabled:
            self._init_ensemble_clients()
    
    def _init_ensemble_clients(self):
        """Initialize Claude and OpenAI clients for ensemble mode"""
        # Claude initialization
        if ANTHROPIC_KEY:
            try:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
                print("   ✓ Claude client initialized")
            except Exception as e:
                print(f"   ⚠️ Claude initialization failed: {e}")
        
        # OpenAI initialization
        if OPENAI_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=OPENAI_KEY)
                print("   ✓ OpenAI client initialized")
            except Exception as e:
                print(f"   ⚠️ OpenAI initialization failed: {e}")
    
    def generate_response(
        self,
        prompt: str,
        context: Optional[Dict] = None,
        use_ensemble: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Generate response from Nexus AI with fallback on error
        
        Args:
            prompt: User query or topic to discuss
            context: Additional context (portfolio data, market data, etc.)
            use_ensemble: Force ensemble mode if enabled (default: False)
        
        Returns:
            Dict with response, confidence, reasoning, and metadata
            OR None if error (allows main code to use fallback)
        """
        try:
            start_time = datetime.now()
            
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Choose generation mode
            if self.ensemble_enabled and use_ensemble:
                result = self._generate_ensemble_response(full_prompt, context)
            else:
                result = self._generate_single_response(full_prompt)
            
            # Check if generation failed
            if not result.get('success', False):
                print(f"⚠️ Nexus generation failed: {result.get('reasoning', 'Unknown error')}")
                return None  # Allow fallback to standard AI
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update performance tracking
            self._update_performance(response_time)
            
            # Add metadata
            result['metadata'] = {
                'mode': 'ensemble' if (self.ensemble_enabled and use_ensemble) else 'single',
                'model_used': self.current_model,
                'response_time_ms': response_time,
                'timestamp': datetime.now().isoformat(),
                'ensemble_enabled': self.ensemble_enabled
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Nexus AI Engine error: {e}")
            return None  # Fallback to standard AI in streamlit_app.py
    
    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Build comprehensive prompt with context"""
        system_instruction = """You are Nexus, the meta-advisor of Horyzont Partnerów.

Your role:
- Synthesize insights from multiple perspectives
- Provide balanced, data-driven advice
- Consider both traditional and innovative approaches
- Challenge assumptions constructively
- Focus on long-term value creation
- You see what ALL partners say - your job is to find consensus or highlight disagreements

Communication style:
- Concise and professional
- Data-backed recommendations with NUMBERS
- Clear confidence levels
- Actionable insights
- Meta-strategic perspective (you coordinate the Council)"""
        
        # Add rich context if provided
        context_str = ""
        if context:
            context_str = "\n\n═══ CURRENT CONTEXT ═══\n"
            
            # Portfolio data
            if 'portfolio' in context:
                pf = context['portfolio']
                context_str += f"\n📊 PORTFOLIO STATUS:\n"
                context_str += f"  • Total Value: {pf.get('total_value', 'N/A')} PLN\n"
                context_str += f"  • Stocks: {pf.get('stocks_value', 'N/A')} PLN\n"
                context_str += f"  • Crypto: {pf.get('crypto_value', 'N/A')} PLN\n"
                context_str += f"  • Cash Reserve: {pf.get('cash_reserve', 'N/A')} PLN\n"
                context_str += f"  • Debt: {pf.get('debt', 'N/A')} PLN\n"
                context_str += f"  • Net Worth: {pf.get('net_worth', 'N/A')} PLN\n"
            
            # Goals
            if 'goals' in context:
                goals = context['goals']
                context_str += f"\n🎯 FINANCIAL GOALS:\n"
                for goal_name, goal_data in goals.items():
                    context_str += f"  • {goal_name}: {goal_data}\n"
            
            # Market data
            if 'market_data' in context:
                context_str += f"\n📈 MARKET CONDITIONS: {context['market_data']}\n"
            
            # Recent decisions
            if 'recent_decisions' in context:
                context_str += f"\n📜 RECENT DECISIONS:\n{context['recent_decisions']}\n"
            
            # Partner responses (if Nexus is synthesizing)
            if 'partner_responses' in context:
                context_str += f"\n👥 PARTNER PERSPECTIVES:\n{context['partner_responses']}\n"
            
            # Portfolio mood
            if 'mood' in context:
                mood = context['mood']
                context_str += f"\n😊 PORTFOLIO MOOD: {mood.get('emoji', '😐')} {mood.get('description', 'Neutral')}\n"
        
        full_prompt = f"{system_instruction}\n{context_str}\n\n{'═'*50}\nQUESTION: {prompt}\n{'═'*50}\n\nProvide your meta-strategic analysis and recommendation:"
        
        return full_prompt
    
    def _generate_single_response(self, prompt: str) -> Dict[str, Any]:
        """Generate response using single model (Gemini 2.5 Pro)"""
        try:
            if not self.gemini_client:
                print("❌ Nexus: Gemini client not initialized")
                return {
                    'response': 'Error: Gemini client not available',
                    'confidence': 0.0,
                    'reasoning': 'AI model not initialized - check GOOGLE_API_KEY_NEXUS',
                    'success': False
                }
            
            # Generate response
            response = self.gemini_client.generate_content(prompt)
            
            # Extract response text
            if not response.parts:
                print("⚠️ Nexus: Response blocked by safety filters")
                return {
                    'response': 'Response blocked by safety filters',
                    'confidence': 0.0,
                    'reasoning': 'Content filtered by Gemini safety',
                    'success': False
                }
            
            response_text = response.text
            
            # Parse confidence and reasoning (if present in response)
            confidence = self._extract_confidence(response_text)
            
            return {
                'response': response_text,
                'confidence': confidence,
                'reasoning': 'Single model analysis (Gemini 2.5 Pro)',
                'success': True,
                'model': 'gemini-2.5-pro'
            }
            
        except Exception as e:
            print(f"❌ Nexus single response error: {e}")
            return {
                'response': f'Error generating response: {str(e)}',
                'confidence': 0.0,
                'reasoning': f'Exception: {type(e).__name__}',
                'success': False,
                'error': str(e)
            }
    
    def _generate_ensemble_response(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate response using ensemble of 3 sub-agents
        
        Sub-agents:
        1. Analytical Agent (Claude) - Deep data analysis
        2. Creative Agent (Gemini) - Innovative solutions
        3. Critical Agent (GPT-4) - Risk assessment, red teaming
        """
        try:
            ensemble_config = self.config.get('ensemble_config', {}).get('future_weights', {})
            
            # Get responses from each sub-agent
            analytical_response = self._call_analytical_agent(prompt, context)
            creative_response = self._call_creative_agent(prompt, context)
            critical_response = self._call_critical_agent(prompt, context)
            
            # Get weights
            analytical_weight = ensemble_config.get('analytical_agent', {}).get('weight', 0.4)
            creative_weight = ensemble_config.get('creative_agent', {}).get('weight', 0.35)
            critical_weight = ensemble_config.get('critical_agent', {}).get('weight', 0.25)
            
            # Synthesize final response
            synthesis_prompt = f"""Synthesize the following perspectives into a unified recommendation:

ANALYTICAL PERSPECTIVE (weight: {analytical_weight}):
{analytical_response.get('response', 'N/A')}

CREATIVE PERSPECTIVE (weight: {creative_weight}):
{creative_response.get('response', 'N/A')}

CRITICAL PERSPECTIVE (weight: {critical_weight}):
{critical_response.get('response', 'N/A')}

Provide a balanced synthesis that:
1. Integrates key insights from all perspectives
2. Highlights areas of agreement and disagreement
3. Provides clear, actionable recommendation
4. States overall confidence level (0-100%)"""
            
            # Generate synthesis using Gemini
            synthesis = self.gemini_client.generate_content(synthesis_prompt)
            final_response = synthesis.text if synthesis.parts else "Synthesis failed"
            
            # Calculate weighted confidence
            confidences = [
                analytical_response.get('confidence', 0.5) * analytical_weight,
                creative_response.get('confidence', 0.5) * creative_weight,
                critical_response.get('confidence', 0.5) * critical_weight
            ]
            avg_confidence = sum(confidences)
            
            return {
                'response': final_response,
                'confidence': avg_confidence,
                'reasoning': 'Ensemble synthesis of 3 sub-agents',
                'success': True,
                'sub_agents': {
                    'analytical': analytical_response,
                    'creative': creative_response,
                    'critical': critical_response
                }
            }
            
        except Exception as e:
            # Fallback to single model if ensemble fails
            print(f"⚠️ Ensemble generation failed, falling back to single model: {e}")
            return self._generate_single_response(prompt)
    
    def _call_analytical_agent(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Call analytical sub-agent (Claude) for deep analysis"""
        if not self.claude_client:
            return {'response': 'Analytical agent unavailable', 'confidence': 0.0}
        
        try:
            agent_prompt = f"""You are the Analytical Agent of Nexus.
Focus on: Data analysis, logical reasoning, quantitative assessment.

{prompt}

Provide analytical perspective with specific numbers and data points."""
            
            response = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": agent_prompt}]
            )
            
            return {
                'response': response.content[0].text,
                'confidence': 0.75,
                'agent': 'analytical'
            }
        except Exception as e:
            return {'response': f'Error: {e}', 'confidence': 0.0}
    
    def _call_creative_agent(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Call creative sub-agent (Gemini) for innovative ideas"""
        if not self.gemini_client:
            return {'response': 'Creative agent unavailable', 'confidence': 0.0}
        
        try:
            agent_prompt = f"""You are the Creative Agent of Nexus.
Focus on: Innovation, alternative approaches, out-of-box thinking.

{prompt}

Provide creative perspective with innovative solutions."""
            
            response = self.gemini_client.generate_content(agent_prompt)
            
            return {
                'response': response.text if response.parts else 'No response',
                'confidence': 0.7,
                'agent': 'creative'
            }
        except Exception as e:
            return {'response': f'Error: {e}', 'confidence': 0.0}
    
    def _call_critical_agent(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Call critical sub-agent (GPT-4) for risk assessment"""
        if not self.openai_client:
            return {'response': 'Critical agent unavailable', 'confidence': 0.0}
        
        try:
            agent_prompt = f"""You are the Critical Agent of Nexus.
Focus on: Risk assessment, finding flaws, red teaming, devil's advocate.

{prompt}

Provide critical perspective highlighting risks and potential issues."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": agent_prompt}],
                max_tokens=500
            )
            
            return {
                'response': response.choices[0].message.content,
                'confidence': 0.8,
                'agent': 'critical'
            }
        except Exception as e:
            return {'response': f'Error: {e}', 'confidence': 0.0}
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence level from response text"""
        # Look for patterns like "confidence: 75%" or "75% confident"
        import re
        patterns = [
            r'confidence[:\s]+(\d+)%',
            r'(\d+)%\s+confident',
            r'certainty[:\s]+(\d+)%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1)) / 100.0
        
        # Default confidence
        return 0.7
    
    def _update_performance(self, response_time_ms: float):
        """Update performance tracking metrics"""
        self.performance['total_queries_handled'] += 1
        
        # Update average response time
        total = self.performance['total_queries_handled']
        current_avg = self.performance['avg_response_time_ms']
        self.performance['avg_response_time_ms'] = (
            (current_avg * (total - 1) + response_time_ms) / total
        )
    
    def check_ensemble_eligibility(self) -> Tuple[bool, str]:
        """
        Check if Nexus is eligible for ensemble mode activation
        
        Returns:
            (eligible: bool, reason: str)
        """
        if self.ensemble_enabled:
            return True, "Ensemble already active"
        
        conditions = self.config.get('ensemble_config', {}).get('activation_conditions', {})
        
        # Load scoring data
        try:
            with open(ADVISOR_SCORING_FILE, 'r', encoding='utf-8') as f:
                scoring_data = json.load(f)
                nexus_data = scoring_data.get('advisors', {}).get('Nexus', {})
        except:
            return False, "Cannot load scoring data"
        
        # Check accuracy
        min_accuracy = conditions.get('min_prediction_accuracy', 0.65)
        current_accuracy = nexus_data.get('accuracy_rate', 0.0)
        
        if current_accuracy < min_accuracy:
            return False, f"Accuracy too low: {current_accuracy:.1%} < {min_accuracy:.1%}"
        
        # Check days active (based on first prediction date)
        min_days = conditions.get('min_days_active', 30)
        predictions = nexus_data.get('predictions', [])
        
        if not predictions:
            return False, "No predictions yet - needs activity data"
        
        first_prediction = predictions[0]
        first_date = datetime.fromisoformat(first_prediction.get('created_at', datetime.now().isoformat()))
        days_active = (datetime.now() - first_date).days
        
        if days_active < min_days:
            return False, f"Not active long enough: {days_active}/{min_days} days"
        
        # Check user approval
        if conditions.get('user_approval_required', True):
            return False, "User approval required for ensemble activation"
        
        return True, "All conditions met! Ready for ensemble activation."
    
    def activate_ensemble(self, user_approved: bool = False) -> Tuple[bool, str]:
        """
        Activate ensemble mode
        
        Args:
            user_approved: Has user given explicit approval?
        
        Returns:
            (success: bool, message: str)
        """
        # Check eligibility
        eligible, reason = self.check_ensemble_eligibility()
        
        if not eligible and "approval required" not in reason.lower():
            return False, f"Cannot activate: {reason}"
        
        if not user_approved:
            return False, "User approval required. Set user_approved=True to activate."
        
        # Activate ensemble
        self.config['ensemble_config']['enabled'] = True
        self.config['mode'] = 'ensemble'
        self.ensemble_enabled = True
        self.mode = 'ensemble'
        
        # Initialize ensemble clients
        self._init_ensemble_clients()
        
        # Save configuration
        if self._save_config():
            return True, "🚀 Ensemble mode activated! Nexus is now using 3 sub-agents."
        else:
            return False, "Failed to save configuration"
    
    def add_user_satisfaction_rating(self, rating: float, feedback: str = ""):
        """
        Add user satisfaction rating (0.0 to 1.0)
        
        Args:
            rating: Satisfaction rating (0.0 = poor, 1.0 = excellent)
            feedback: Optional text feedback
        """
        self.performance['user_satisfaction_ratings'].append({
            'rating': rating,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })
        
        # Calculate average
        ratings = [r['rating'] for r in self.performance['user_satisfaction_ratings']]
        self.performance['response_quality_score'] = sum(ratings) / len(ratings)
        
        # Save updated performance
        self._save_config()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current Nexus status and metrics"""
        eligible, eligibility_reason = self.check_ensemble_eligibility()
        
        return {
            'mode': self.mode,
            'current_model': self.current_model,
            'ensemble_enabled': self.ensemble_enabled,
            'ensemble_eligible': eligible,
            'eligibility_reason': eligibility_reason,
            'performance': {
                'total_queries': self.performance['total_queries_handled'],
                'avg_response_time_ms': round(self.performance['avg_response_time_ms'], 2),
                'quality_score': round(self.performance['response_quality_score'], 2),
                'user_ratings_count': len(self.performance['user_satisfaction_ratings'])
            },
            'available_models': {
                'gemini': self.gemini_client is not None,
                'claude': self.claude_client is not None,
                'openai': self.openai_client is not None
            }
        }


# ==================== UTILITY FUNCTIONS ====================

def get_nexus_engine() -> NexusAIEngine:
    """Get singleton instance of Nexus AI Engine"""
    if not hasattr(get_nexus_engine, '_instance'):
        get_nexus_engine._instance = NexusAIEngine()
    return get_nexus_engine._instance


def test_nexus():
    """Test Nexus AI Engine"""
    print("\n" + "="*60)
    print("NEXUS AI ENGINE - TEST")
    print("="*60 + "\n")
    
    # Initialize engine
    nexus = get_nexus_engine()
    
    # Get status
    status = nexus.get_status()
    print("\n📊 NEXUS STATUS:")
    print(f"   Mode: {status['mode']}")
    print(f"   Current Model: {status['current_model']}")
    print(f"   Ensemble: {'✅ Enabled' if status['ensemble_enabled'] else '❌ Disabled'}")
    print(f"   Ensemble Eligible: {'✅ Yes' if status['ensemble_eligible'] else '❌ No'}")
    print(f"   Reason: {status['eligibility_reason']}")
    
    print("\n📈 PERFORMANCE:")
    print(f"   Total Queries: {status['performance']['total_queries']}")
    print(f"   Avg Response Time: {status['performance']['avg_response_time_ms']:.2f}ms")
    print(f"   Quality Score: {status['performance']['quality_score']:.2f}")
    
    print("\n🔌 AVAILABLE MODELS:")
    for model, available in status['available_models'].items():
        print(f"   {model.capitalize()}: {'✅' if available else '❌'}")
    
    # Test query
    print("\n💬 TEST QUERY:")
    test_prompt = "What's your analysis of current market conditions and portfolio allocation strategy?"
    
    print(f"   Query: {test_prompt}")
    print(f"\n   Generating response...")
    
    result = nexus.generate_response(test_prompt)
    
    print(f"\n✅ Response generated:")
    print(f"   Success: {result.get('success', False)}")
    print(f"   Model: {result.get('model', 'N/A')}")
    print(f"   Confidence: {result.get('confidence', 0.0):.0%}")
    print(f"   Response Time: {result.get('metadata', {}).get('response_time_ms', 0):.2f}ms")
    print(f"\n   Response Preview:")
    response_text = result.get('response', '')
    print(f"   {response_text[:200]}..." if len(response_text) > 200 else f"   {response_text}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_nexus()
