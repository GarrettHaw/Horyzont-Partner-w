"""
Consultation System - System konsultacji z Radą Partnerów
Pozwala Partnerowi Zarządzającemu zadawać pytania/propozycje i zbierać głosy od partnerów AI
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import google.generativeai as genai
from openai import OpenAI
import anthropic
from api_usage_tracker import APIUsageTracker

class ConsultationManager:
    """Zarządza systemem konsultacji z Radą Partnerów"""
    
    def __init__(self, consultations_file='consultations.json'):
        self.consultations_file = consultations_file
        self.tracker = APIUsageTracker()
        
        # Load API keys
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        
        # Configure APIs
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
        
        # Load personas from persona_memory.json via streamlit_app
        try:
            # Import PERSONAS from streamlit_app (ładuje persona_memory.json)
            from streamlit_app import PERSONAS
            
            # Convert PERSONAS dict to list format expected by consultation system
            self.personas = []
            for name, config in PERSONAS.items():
                self.personas.append({
                    'name': name,
                    'model_engine': config.get('model_engine', 'gemini'),
                    'system_instruction': config.get('system_instruction', ''),
                    'ukryty_cel': config.get('ukryty_cel', '')
                })
            
            print(f"✓ Załadowano {len(self.personas)} person z persona_memory.json")
            
        except Exception as e:
            print(f"⚠️ Nie udało się załadować person: {e}")
            self.personas = []
    
    def _parse_personas(self, content: str) -> List[Dict]:
        """Parse personas from compiled file"""
        personas = []
        sections = content.split('===')
        
        for section in sections:
            if 'IMIĘ:' in section:
                lines = section.strip().split('\n')
                persona = {}
                
                for line in lines:
                    if line.startswith('IMIĘ:'):
                        persona['name'] = line.replace('IMIĘ:', '').strip()
                    elif line.startswith('MODEL:'):
                        persona['model_engine'] = line.replace('MODEL:', '').strip()
                
                if persona.get('name') and persona.get('model_engine'):
                    personas.append(persona)
        
        return personas
    
    def create_consultation(self, question: str, selected_partners: List[str]) -> Dict:
        """
        Utwórz nową konsultację
        
        Args:
            question: Pytanie/propozycja dla Rady
            selected_partners: Lista imion partnerów do zapytania
        
        Returns:
            Dict z ID konsultacji
        """
        consultation = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "question": question,
            "participants": selected_partners,
            "responses": [],
            "summary": None,
            "created_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        # Save initial consultation
        self._save_consultation(consultation)
        
        return consultation
    
    def collect_responses(self, consultation_id: str) -> Dict:
        """
        Zbierz odpowiedzi od wszystkich wybranych partnerów
        
        Args:
            consultation_id: ID konsultacji
        
        Returns:
            Zaktualizowany dict konsultacji
        """
        consultation = self._load_consultation(consultation_id)
        if not consultation:
            return None
        
        question = consultation['question']
        participants = consultation['participants']
        
        print(f"\n🗳️ Zbieram odpowiedzi od {len(participants)} partnerów...")
        
        for partner_name in participants:
            print(f"\n📞 Pytam: {partner_name}...")
            
            # Find persona
            persona = next((p for p in self.personas if p['name'] == partner_name), None)
            if not persona:
                print(f"⚠️ Nie znaleziono persony dla {partner_name}")
                continue
            
            # Get response
            response = self._ask_partner(partner_name, persona, question)
            
            if response:
                consultation['responses'].append(response)
                print(f"✅ Odpowiedź zebrana od {partner_name}")
            else:
                print(f"❌ Błąd przy zbieraniu odpowiedzi od {partner_name}")
        
        # Update status
        consultation['status'] = 'responses_collected'
        self._save_consultation(consultation)
        
        return consultation
    
    def _ask_partner(self, name: str, persona: Dict, question: str) -> Optional[Dict]:
        """
        Zapytaj pojedynczego partnera o opinię
        
        Returns:
            Dict: {partner, stance, reasoning, raw_response}
        """
        model_engine = persona.get('model_engine', 'gemini')
        
        # Build prompt
        prompt = f"""Jesteś {name}, członek Rady Partnerów firmy inwestycyjnej.

Partner Zarządzający zadaje Ci pytanie:
"{question}"

Odpowiedz w formacie JSON z następującymi polami:
1. "stance": "for" (za) lub "against" (przeciw) lub "neutral" (neutralny)
2. "reasoning": Twoje argumenty (2-3 zdania)
3. "confidence": Twoja pewność decyzji w skali 1-10

Odpowiedź TYLKO w formacie JSON:"""
        
        try:
            raw_response = None
            
            # Call appropriate API
            if model_engine == 'gemini':
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content(prompt)
                raw_response = response.text
                self.tracker.track_call('gemini', is_autonomous=False)
            
            elif model_engine == 'openai':
                if not self.openai_key:
                    return None
                client = OpenAI(api_key=self.openai_key)
                response = client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                raw_response = response.choices[0].message.content
                self.tracker.track_call('openai', is_autonomous=False)
            
            elif model_engine == 'claude':
                if not self.anthropic_key:
                    return None
                client = anthropic.Anthropic(api_key=self.anthropic_key)
                response = client.messages.create(
                    model='claude-3-5-sonnet-20241022',
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                raw_response = response.content[0].text
                self.tracker.track_call('claude', is_autonomous=False)
            
            elif model_engine in ['openrouter-mistral', 'openrouter-llama', 'openrouter-mixtral', 'openrouter-glm']:
                if not self.openrouter_key:
                    return None
                
                model_map = {
                    'openrouter-mistral': 'mistralai/mistral-7b-instruct:free',
                    'openrouter-llama': 'meta-llama/llama-3.1-8b-instruct:free',
                    'openrouter-mixtral': 'mistralai/mixtral-8x7b-instruct:free',
                    'openrouter-glm': 'qwen/qwen-2-7b-instruct:free'
                }
                
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=self.openrouter_key
                )
                
                response = client.chat.completions.create(
                    model=model_map.get(model_engine, 'mistralai/mistral-7b-instruct:free'),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                raw_response = response.choices[0].message.content
                self.tracker.track_call('openrouter', is_autonomous=False)
            
            if not raw_response:
                return None
            
            # Parse JSON response
            response_text = raw_response.strip()
            
            # Clean markdown code blocks
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Clean <s> tags (OpenRouter)
            response_text = response_text.replace('<s>', '').replace('</s>', '').strip()
            
            parsed = json.loads(response_text)
            
            return {
                "partner": name,
                "stance": parsed.get('stance', 'neutral'),
                "reasoning": parsed.get('reasoning', ''),
                "confidence": parsed.get('confidence', 5),
                "raw_response": raw_response
            }
            
        except Exception as e:
            print(f"❌ Błąd przy pytaniu {name}: {e}")
            return None
    
    def generate_summary(self, consultation_id: str) -> Dict:
        """
        Wygeneruj AI summary konsultacji używając Gemini
        
        Returns:
            Dict: {votes_for, votes_against, votes_neutral, main_arguments_for, 
                   main_arguments_against, recommendation}
        """
        consultation = self._load_consultation(consultation_id)
        if not consultation or not consultation.get('responses'):
            return None
        
        print(f"\n🤖 Generuję AI Summary konsultacji...")
        
        try:
            question = consultation['question']
            responses = consultation['responses']
            
            # Build responses text
            responses_text = ""
            for resp in responses:
                stance_emoji = {'for': '✅', 'against': '❌', 'neutral': '🤔'}.get(resp['stance'], '🤔')
                responses_text += f"\n{resp['partner']} ({stance_emoji} {resp['stance'].upper()}, pewność: {resp['confidence']}/10):\n{resp['reasoning']}\n"
            
            prompt = f"""Przeanalizuj wyniki konsultacji z Radą Partnerów i wygeneruj podsumowanie.

PYTANIE: {question}

ODPOWIEDZI PARTNERÓW:
{responses_text}

Wygeneruj odpowiedź w formacie JSON z następującymi polami:
1. "votes_for": Liczba głosów ZA (int)
2. "votes_against": Liczba głosów PRZECIW (int)
3. "votes_neutral": Liczba głosów NEUTRALNYCH (int)
4. "main_arguments_for": Lista 2-3 głównych argumentów ZA (lista stringów)
5. "main_arguments_against": Lista 2-3 głównych argumentów PRZECIW (lista stringów)
6. "recommendation": Twoja rekomendacja na podstawie odpowiedzi (1 zdanie)
7. "consensus": "high" (wysoki konsensus) lub "medium" lub "low" (brak konsensusu)

Odpowiedź TYLKO w formacie JSON:
"""
            
            # Call Gemini
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            # Parse JSON
            response_text = response.text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            summary_data = json.loads(response_text)
            
            # Track API call
            self.tracker.track_call('gemini', is_autonomous=False)
            
            # Update consultation
            consultation['summary'] = summary_data
            consultation['status'] = 'completed'
            self._save_consultation(consultation)
            
            print(f"✅ Summary wygenerowane")
            
            # Wyślij email notification (jeśli włączone)
            try:
                from email_notifier import get_conversation_notifier
                notifier = get_conversation_notifier()
                if notifier.config.get("enabled", False):
                    notifier.send_consultation_completed(consultation)
                    print(f"📧 Email notification wysłany")
            except Exception as e:
                print(f"⚠️ Nie można wysłać email notification: {e}")
            
            return summary_data
            
        except Exception as e:
            print(f"❌ Błąd generowania summary: {e}")
            return None
    
    def _save_consultation(self, consultation: Dict):
        """Save consultation to JSON file"""
        consultations = self._load_all_consultations()
        
        # Update or add consultation
        existing_index = next(
            (i for i, c in enumerate(consultations) if c['id'] == consultation['id']),
            None
        )
        
        if existing_index is not None:
            consultations[existing_index] = consultation
        else:
            consultations.append(consultation)
        
        with open(self.consultations_file, 'w', encoding='utf-8') as f:
            json.dump(consultations, f, indent=2, ensure_ascii=False)
    
    def _load_consultation(self, consultation_id: str) -> Optional[Dict]:
        """Load single consultation by ID"""
        consultations = self._load_all_consultations()
        return next((c for c in consultations if c['id'] == consultation_id), None)
    
    def _load_all_consultations(self) -> List[Dict]:
        """Load all consultations from file"""
        if not os.path.exists(self.consultations_file):
            return []
        
        try:
            with open(self.consultations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def get_recent_consultations(self, limit: int = 20) -> List[Dict]:
        """Get recent consultations, sorted by date (newest first)"""
        consultations = self._load_all_consultations()
        consultations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return consultations[:limit]


# Singleton accessor
_consultation_manager = None

def get_consultation_manager() -> ConsultationManager:
    """Get or create ConsultationManager singleton"""
    global _consultation_manager
    if _consultation_manager is None:
        _consultation_manager = ConsultationManager()
    return _consultation_manager
