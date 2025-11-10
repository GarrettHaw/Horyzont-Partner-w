"""
Autonomous Conversation Engine - Silnik autonomicznych rozmów Rady Partnerów
Partnerzy rozmawiają ze sobą nawet gdy Zarządzającego nie ma
"""

import json
import os
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from api_usage_tracker import get_tracker
import anthropic
import google.generativeai as genai
from openai import OpenAI

# Import Nexus AI Engine
try:
    from nexus_ai_engine import get_nexus_engine
    NEXUS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Nexus AI Engine niedostępny: {e}")
    NEXUS_AVAILABLE = False

# Import konfiguracji z głównego pliku
try:
    from streamlit_app import (
        PERSONAS,
        wczytaj_kodeks, wczytaj_cele, wczytaj_stan_spolki
    )
    IMPORT_OK = True
except Exception as e:
    print(f"⚠️ Nie można zaimportować z streamlit_app.py: {e}")
    IMPORT_OK = False
    PERSONAS = {}

# API Keys zawsze z .env (bezpieczniej niż import z streamlit_app)
from dotenv import load_dotenv
load_dotenv()
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

# Jeśli PERSONAS nie załadowano z streamlit_app, spróbuj z gra_rpg
if not PERSONAS:
    try:
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from gra_rpg import PERSONAS as PERSONAS_FROM_RPG
        PERSONAS = PERSONAS_FROM_RPG
        print("✅ Załadowano PERSONAS z gra_rpg.py")
    except:
        print("⚠️ Nie można załadować PERSONAS")

# Pliki danych
CONVERSATIONS_FILE = "autonomous_conversations.json"
TOPICS_FILE = "autonomous_topics_config.json"

# Domyślne tematy rozmów
DEFAULT_TOPICS = {
    "portfolio_analysis": {
        "name": "Analiza Portfela",
        "description": "Przegląd aktualnego stanu portfela i jego alokacji",
        "priority": "MEDIUM",
        "frequency": "daily",
        "prompt_template": "Przeanalizujmy aktualny stan portfela. Wartość akcji: {stocks_value} PLN, Krypto: {crypto_value} USD, Długi: {debt_value} PLN. Jak oceniacie obecną alokację?"
    },
    "market_trends": {
        "name": "Trendy Rynkowe",
        "description": "Dyskusja o aktualnych trendach na rynkach",
        "priority": "LOW",
        "frequency": "weekly",
        "prompt_template": "Co sądzicie o aktualnych trendach rynkowych? Bitcoin ostatnio {btc_trend}, rynek akcji {stock_trend}."
    },
    "risk_assessment": {
        "name": "Ocena Ryzyka",
        "description": "Analiza ryzyka w portfelu",
        "priority": "HIGH",
        "frequency": "daily",
        "prompt_template": "Przeanalizujmy poziom ryzyka w portfelu. Czy jesteśmy odpowiednio zdywersyfikowani? Jakie są największe zagrożenia?"
    },
    "goals_review": {
        "name": "Przegląd Celów",
        "description": "Dyskusja o postępach w realizacji celów",
        "priority": "MEDIUM",
        "frequency": "weekly",
        "prompt_template": "Sprawdźmy postępy w realizacji naszych celów finansowych. Czy jesteśmy na dobrej drodze?"
    },
    "strategy_debate": {
        "name": "Debata Strategiczna",
        "description": "Dyskusja o długoterminowej strategii",
        "priority": "HIGH",
        "frequency": "weekly",
        "prompt_template": "Porozmawiajmy o naszej długoterminowej strategii inwestycyjnej. Czy powinna się zmienić? Co dostosować?"
    },
    "nexus_meta_discussion": {
        "name": "Meta-Dyskusja o Radzie",
        "description": "Nexus moderuje dyskusję o efektywności współpracy Rady",
        "priority": "MEDIUM",
        "frequency": "monthly",
        "prompt_template": "Nexus zaprasza do refleksji: Jak oceniacie naszą współpracę jako Rada? Co działa dobrze? Co moglibyśmy poprawić w naszych dyskusjach?"
    },
    "ai_voting_weights": {
        "name": "Przegląd Wag Głosów",
        "description": "Dyskusja o systemie scoring i wagach głosów partnerów",
        "priority": "LOW",
        "frequency": "monthly",
        "prompt_template": "Porozmawiajmy o systemie dynamicznych wag głosów. Czy obecny system scoring dobrze odzwierciedla wartość waszych porad? Jak go ulepszyć?"
    },
    "knowledge_gaps": {
        "name": "Luki Wiedzy",
        "description": "Identyfikacja obszarów gdzie Rada potrzebuje więcej expertise",
        "priority": "MEDIUM",
        "frequency": "monthly",
        "prompt_template": "Jakie są nasze największe luki wiedzy? W jakich obszarach potrzebujemy lepszych analiz lub dodatkowych źródeł informacji?"
    }
}


class AutonomousConversationEngine:
    """Silnik autonomicznych rozmów"""
    
    def __init__(self):
        self.tracker = get_tracker()
        self.topics_config = self._load_topics_config()
        self.conversations_db = self._load_conversations()
        
        # Konfiguruj AI clients
        self.claude_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY) if ANTHROPIC_KEY else None
        if GEMINI_KEY:
            genai.configure(api_key=GEMINI_KEY)
        
        # OpenRouter client (NIE standardowy OpenAI!)
        if OPENROUTER_KEY:
            self.openai_client = OpenAI(
                api_key=OPENROUTER_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
        else:
            self.openai_client = None
        
        print("✅ Autonomous Conversation Engine initialized")
    
    def _load_topics_config(self) -> Dict:
        """Załaduj konfigurację tematów"""
        if os.path.exists(TOPICS_FILE):
            with open(TOPICS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            self._save_topics_config(DEFAULT_TOPICS)
            return DEFAULT_TOPICS
    
    def _save_topics_config(self, config: Dict):
        """Zapisz konfigurację tematów"""
        with open(TOPICS_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def _load_conversations(self) -> List[Dict]:
        """Załaduj historię rozmów"""
        if os.path.exists(CONVERSATIONS_FILE):
            with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return []
    
    def _save_conversation(self, conversation: Dict):
        """Zapisz rozmowę do bazy"""
        self.conversations_db.append(conversation)
        
        # Zachowaj ostatnie 100 rozmów
        if len(self.conversations_db) > 100:
            self.conversations_db = self.conversations_db[-100:]
        
        with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.conversations_db, f, indent=2, ensure_ascii=False)
    
    def check_api_budget(self) -> Tuple[bool, str]:
        """
        Sprawdź czy jest dostępny budżet API dla autonomicznej rozmowy
        
        Returns:
            (can_proceed, message)
        """
        budgets = self.tracker.get_all_budgets()
        
        # Sprawdź czy którekolwiek API ma dostępny budżet
        available_apis = []
        for api_name, budget in budgets.items():
            if budget["autonomous"]["remaining"] > 8:  # Min 8 wywołań na rozmowę (4 partnerów x 2)
                available_apis.append(api_name)
        
        if not available_apis:
            return False, "🚫 Brak dostępnego budżetu API dla autonomicznych rozmów dzisiaj"
        
        return True, f"✅ Dostępne API: {', '.join(available_apis)}"
    
    def select_topic(self) -> Tuple[str, Dict]:
        """
        Wybierz temat do dyskusji
        
        Returns:
            (topic_id, topic_config)
        """
        # Możesz dodać bardziej zaawansowaną logikę (np. AI decyduje)
        # Na razie: losowy temat z HIGH priority
        
        high_priority = {k: v for k, v in self.topics_config.items() if v.get("priority") == "HIGH"}
        
        if high_priority:
            topic_id = random.choice(list(high_priority.keys()))
        else:
            topic_id = random.choice(list(self.topics_config.keys()))
        
        return topic_id, self.topics_config[topic_id]
    
    def generate_opening_prompt(self, topic: Dict) -> str:
        """Wygeneruj początkowy prompt rozmowy"""
        template = topic.get("prompt_template", "Porozmawiajmy o {topic_name}")
        
        # Podstaw rzeczywiste dane (jeśli IMPORT_OK)
        try:
            stan_spolki = wczytaj_stan_spolki() if IMPORT_OK else {}
            
            prompt = template.format(
                stocks_value=stan_spolki.get('akcje_wartosc', 0),
                crypto_value=stan_spolki.get('krypto_wartosc', 0),
                debt_value=stan_spolki.get('dlugi_laczne', 0),
                btc_trend="rośnie" if random.random() > 0.5 else "spada",
                stock_trend="stabilny" if random.random() > 0.5 else "zmniejsza się",
                topic_name=topic.get("name", "temat")
            )
        except:
            prompt = f"Porozmawiajmy o: {topic.get('name', 'strategii')}"
        
        return prompt
    
    def select_participants(self, topic: Dict) -> List[str]:
        """
        Wybierz uczestników rozmowy (4 partnerów)
        
        WAŻNE: Wykluczamy "Partner Zarządzający (JA)" - to fizyczna osoba!
        Autonomiczne rozmowy = tylko AI partners bez użytkownika
        """
        if not PERSONAS:
            return ["Nexus", "Warren Buffett", "George Soros", "Changpeng Zhao (CZ)"]
        
        all_partners = list(PERSONAS.keys())
        
        # ❌ WYKLUCZAMY "Partner Zarządzający (JA)" z autonomicznych rozmów!
        ai_only_partners = [p for p in all_partners if p != "Partner Zarządzający (JA)"]
        
        # Wybierz 4 AI partnerów (Nexus, Warren, Soros, CZ)
        # Możesz dodać logikę: risk topics = Soros first, value = Buffett first, crypto = CZ first
        participants = ai_only_partners[:4] if len(ai_only_partners) >= 4 else ai_only_partners
        
        return participants
    
    def call_ai_partner(self, partner_name: str, prompt: str, context: List[Dict]) -> Optional[str]:
        """
        Wyślij prompt do AI partnera
        
        Args:
            partner_name: Nazwa partnera
            prompt: Główny prompt
            context: Lista poprzednich wiadomości [{"partner": "...", "message": "..."}]
        
        Returns:
            Odpowiedź AI lub None jeśli błąd
        """
        if not PERSONAS or partner_name not in PERSONAS:
            return None
        
        persona = PERSONAS[partner_name]
        model_engine = persona.get("model_engine", "gemini")
        
        # ✨ NEXUS HANDLING - używa nexus_ai_engine.py
        if model_engine == "nexus" and NEXUS_AVAILABLE:
            try:
                nexus = get_nexus_engine()
                
                # Przygotuj kontekst dla Nexusa
                nexus_context = {
                    'conversation_type': 'autonomous',
                    'topic': prompt,
                    'previous_messages': context[-3:] if context else [],
                    'participant_count': len(set([msg.get('partner') for msg in context])) if context else 0
                }
                
                # Nexus prompt - jest moderatorem rozmowy
                nexus_prompt = f"""Jesteś Nexus - meta-advisor koordynujący Radę Partnerów.

To jest AUTONOMICZNA rozmowa (Zarządzającego nie ma). 
Rozmawiasz z {', '.join([msg.get('partner', '?') for msg in context[-3:]])} o temacie: {prompt}

Twoja rola:
- Syntetyzuj różne perspektywy
- Wskazuj consensus lub główne różnice
- Zadawaj pytania prowokujące głębszą dyskusję
- Bądź zwięzły (3-4 zdania max)

POPRZEDNIE WYPOWIEDZI:
{chr(10).join([f"{msg['partner']}: {msg['message']}" for msg in context[-3:]]) if context else "Brak poprzednich wypowiedzi"}

Twoja odpowiedź (jako moderator, zwięźle):"""
                
                result = nexus.generate_response(nexus_prompt, context=nexus_context)
                
                if result.get('success'):
                    answer = result.get('response', '')
                    
                    # Oczyść odpowiedź
                    answer = answer.strip()
                    for token in ['<s>', '</s>', '<|endoftext|>', '<|im_end|>', '�']:
                        answer = answer.replace(token, '')
                    answer = answer.strip()
                    
                    # Track API call (Nexus używa Gemini w single mode)
                    self.tracker.track_call('gemini', is_autonomous=True)
                    
                    return answer
                else:
                    print(f"⚠️ Nexus zwrócił błąd: {result.get('error')}")
                    return None
                    
            except Exception as e:
                print(f"❌ Błąd wywołania Nexus: {e}")
                return None
        
        # Mapuj model_engine na api_type dla trackera
        if model_engine.startswith("openrouter"):
            api_type = "openai"  # OpenRouter używa OpenAI API
        else:
            api_type = model_engine  # "gemini" lub "claude"
        
        # Sprawdź budżet przed wywołaniem
        if not self.tracker.can_make_autonomous_call(api_type):
            print(f"⚠️ Brak budżetu {api_type} dla {partner_name}")
            return None
        
        # Przygotuj pełny prompt z kontekstem
        full_prompt = f"""Jesteś {partner_name}.

{persona.get('opis', '')}

WAŻNE: To jest autonomiczna rozmowa Rady Partnerów (Zarządzającego nie ma).
Rozmawiasz z kolegami z Rady. Bądź zwięzły (max 3-4 zdania).
"""
        
        # Dodaj kontekst poprzednich wypowiedzi
        if context:
            full_prompt += "\n\n💬 POPRZEDNIE WYPOWIEDZI:\n"
            for msg in context[-3:]:  # Ostatnie 3 wiadomości
                full_prompt += f"{msg['partner']}: {msg['message']}\n"
        
        full_prompt += f"\n\nTemat dyskusji: {prompt}\n\nTwoja odpowiedź (zwięźle, 3-4 zdania):"
        
        # Wywołaj odpowiednie API na podstawie model_engine
        try:
            # OPENROUTER (wszystkie modele openrouter_*)
            if model_engine.startswith("openrouter") and self.openai_client:
                # Mapuj model_engine na konkretny model OpenRouter (z :free!)
                model_map = {
                    "openrouter_mistral": "mistralai/mistral-7b-instruct:free",
                    "openrouter_llama": "meta-llama/llama-4-maverick:free",
                    "openrouter_mixtral": "meta-llama/llama-4-scout:free",
                    "openrouter_glm": "z-ai/glm-4.5-air:free"
                }
                model_name = model_map.get(model_engine, "mistralai/mistral-7b-instruct:free")
                
                response = self.openai_client.chat.completions.create(
                    model=model_name,
                    max_tokens=300,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                answer = response.choices[0].message.content
                
            # GEMINI
            elif model_engine == "gemini":
                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                response = model.generate_content(full_prompt)
                answer = response.text
                
            # CLAUDE
            elif model_engine == "claude" and self.claude_client:
                response = self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,
                    messages=[{"role": "user", "content": full_prompt}]
                )
                answer = response.content[0].text
            else:
                print(f"❌ Nieznany model_engine: {model_engine}")
                return None
            
            # Oczyść odpowiedź z tokenów specjalnych
            answer = answer.strip()
            # Usuń tokeny: <s>, </s>, <|endoftext|>, itp.
            for token in ['<s>', '</s>', '<|endoftext|>', '<|im_end|>', '�']:
                answer = answer.replace(token, '')
            answer = answer.strip()
            
            # Zarejestruj wywołanie
            self.tracker.track_call(api_type, is_autonomous=True)
            
            return answer
            
        except Exception as e:
            print(f"❌ Błąd wywołania {api_type} dla {partner_name}: {e}")
            return None
    
    def run_conversation(self, max_messages: int = 12) -> Optional[Dict]:
        """
        Uruchom autonomiczną rozmowę
        
        Args:
            max_messages: Maksymalna liczba wiadomości (domyślnie 12)
        
        Returns:
            Dict z rozmową lub None jeśli błąd
        """
        print("\n" + "="*60)
        print("🤖 AUTONOMOUS CONVERSATION ENGINE - START")
        print("="*60)
        
        # 1. Sprawdź budżet API
        can_proceed, budget_msg = self.check_api_budget()
        print(budget_msg)
        
        if not can_proceed:
            return None
        
        # 2. Wybierz temat
        topic_id, topic = self.select_topic()
        print(f"📋 Temat: {topic['name']} (Priority: {topic['priority']})")
        
        # 3. Wybierz uczestników
        participants = self.select_participants(topic)
        print(f"👥 Uczestnicy: {', '.join(participants)}")
        
        # 4. Wygeneruj opening prompt
        opening_prompt = self.generate_opening_prompt(topic)
        print(f"💬 Opening: {opening_prompt[:100]}...")
        
        # 5. Rozpocznij rozmowę
        conversation = {
            "id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "date": datetime.now().isoformat(),
            "topic_id": topic_id,
            "topic_name": topic['name'],
            "opening_prompt": opening_prompt,  # ✅ DODANE: Pełny tekst opening
            "participants": participants,
            "messages": [],
            "status": "in_progress",
            "api_calls_used": 0
        }
        
        context = []
        
        for i in range(max_messages):
            # Rotuj uczestników
            current_partner = participants[i % len(participants)]
            
            print(f"\n[{i+1}/{max_messages}] 🗣️ {current_partner} odpowiada...")
            
            # Wywołaj AI
            response = self.call_ai_partner(current_partner, opening_prompt, context)
            
            if response:
                message = {
                    "partner": current_partner,
                    "message": response,
                    "timestamp": datetime.now().isoformat(),
                    "message_number": i + 1
                }
                
                conversation["messages"].append(message)
                context.append({"partner": current_partner, "message": response})
                conversation["api_calls_used"] += 1
                
                print(f"   ✅ {response[:150]}...")
            else:
                print(f"   ⚠️ Brak odpowiedzi (limit API?)")
                # Jeśli 3 kolejne błędy, przerwij
                if i > 0 and all(m is None for m in conversation["messages"][-3:]):
                    print("   🚫 Zbyt wiele błędów, przerywam rozmowę")
                    break
        
        # 6. Zakończ rozmowę
        conversation["status"] = "completed"
        conversation["completed_at"] = datetime.now().isoformat()
        
        # 7. Zapisz do bazy
        self._save_conversation(conversation)
        self.tracker.increment_autonomous_conversation()
        
        print(f"\n✅ Rozmowa zakończona: {len(conversation['messages'])} wiadomości")
        print(f"💾 Zapisano jako: {conversation['id']}")
        
        # 8. Wygeneruj AI Summary (jeśli są wiadomości)
        if len(conversation['messages']) > 0:
            print(f"🤖 Generuję AI Summary...")
            summary = self._generate_summary(conversation)
            if summary:
                conversation['summary'] = summary
                print(f"✅ Summary wygenerowane")
        
        # 8b. ✨ NEXUS META-ANALYSIS (jeśli dostępny)
        if NEXUS_AVAILABLE and len(conversation['messages']) >= 3:
            print(f"🤖 Nexus przeprowadza meta-analizę...")
            meta_analysis = self.nexus_meta_analysis(conversation)
            if meta_analysis:
                conversation['nexus_meta_analysis'] = meta_analysis
                print(f"✅ Nexus meta-analysis ukończona")
                print(f"   Jakość rozmowy: {meta_analysis.get('overall_quality', 0):.0%}")
        
        # Zapisz ze wszystkimi analizami
        self._save_conversation(conversation)
        
        # 9. Wyślij email notification (jeśli włączone)
        try:
            from email_notifier import get_conversation_notifier
            notifier = get_conversation_notifier()
            if notifier.config.get("enabled", False):
                notifier.send_conversation_completed(conversation)
                print(f"📧 Email notification wysłany")
        except Exception as e:
            print(f"⚠️ Nie można wysłać email notification: {e}")
        
        print("="*60 + "\n")
        
        return conversation
    
    def _generate_summary(self, conversation: Dict) -> Optional[Dict]:
        """
        Wygeneruj AI summary rozmowy używając Gemini
        
        Returns:
            Dict z polami: summary, key_points, sentiment
            None jeśli błąd
        """
        try:
            messages = conversation.get("messages", [])
            if not messages:
                return None
            
            # Zbuduj transkrypt
            transcript = "\n".join([
                f"{msg.get('partner', 'Unknown')}: {msg.get('message', '')[:300]}"  # Max 300 znaków na msg
                for msg in messages
            ])
            
            topic_name = conversation.get("topic_name", "Unknown Topic")
            
            prompt = f"""Przeanalizuj tę rozmowę Rady Partnerów i wygeneruj zwięzłe podsumowanie.

TEMAT ROZMOWY: {topic_name}

TRANSKRYPT:
{transcript}

Wygeneruj odpowiedź w formacie JSON z następującymi polami:
1. "summary": Krótkie podsumowanie rozmowy (2-3 zdania max)
2. "key_points": Lista 3 najważniejszych wniosków (krótkie zdania)
3. "sentiment": "positive" lub "neutral" lub "negative" (ogólny ton rozmowy)

Odpowiedź TYLKO w formacie JSON, bez dodatkowego tekstu:
"""
            
            # Wywołaj Gemini
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            # Parse JSON
            response_text = response.text.strip()
            
            # Usuń markdown code blocks jeśli są
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            summary_data = json.loads(response_text)
            
            # Track API call
            self.tracker.track_call('gemini', is_autonomous=True)
            
            return summary_data
            
        except Exception as e:
            print(f"❌ Błąd generowania summary: {e}")
            return None
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Zwróć ostatnie N rozmów"""
        return sorted(self.conversations_db, key=lambda x: x.get("date", ""), reverse=True)[:limit]
    
    def get_conversation_by_id(self, conv_id: str) -> Optional[Dict]:
        """Zwróć konkretną rozmowę po ID"""
        for conv in self.conversations_db:
            if conv.get("id") == conv_id:
                return conv
        return None
    
    # ============================================================================
    # NEXUS ENHANCED FEATURES - Meta-analysis, Voting Simulation, Knowledge Synthesis
    # ============================================================================
    
    def nexus_meta_analysis(self, conversation: Dict) -> Optional[Dict]:
        """
        🤖 Nexus przeprowadza meta-analizę rozmowy
        
        Analizuje:
        - Główne trendy w dyskusji
        - Punkty zgody i sporu
        - Quality score wypowiedzi każdego partnera
        - Rekomendacje dla przyszłych dyskusji
        
        Args:
            conversation: Dict z zakończoną rozmową
        
        Returns:
            Dict z meta-analizą lub None
        """
        if not NEXUS_AVAILABLE:
            print("⚠️ Nexus niedostępny - meta-analysis pomięta")
            return None
        
        messages = conversation.get("messages", [])
        if len(messages) < 3:
            print("⚠️ Za mało wiadomości do meta-analizy (min 3)")
            return None
        
        try:
            nexus = get_nexus_engine()
            
            # Zbuduj transkrypt
            transcript = "\n".join([
                f"[{msg.get('message_number', '?')}] {msg.get('partner', 'Unknown')}: {msg.get('message', '')}"
                for msg in messages
            ])
            
            topic_name = conversation.get("topic_name", "Unknown")
            opening_prompt = conversation.get("opening_prompt", "")
            
            analysis_prompt = f"""Przeprowadź META-ANALIZĘ tej autonomicznej rozmowy Rady Partnerów.

TEMAT: {topic_name}
OPENING: {opening_prompt}
LICZBA WYPOWIEDZI: {len(messages)}
UCZESTNICY: {', '.join(conversation.get('participants', []))}

TRANSKRYPT ROZMOWY:
{transcript}

Przeanalizuj i zwróć TYLKO JSON z następującymi polami:
{{
    "main_themes": ["temat1", "temat2", "temat3"],
    "consensus_points": ["punkt zgody 1", "punkt zgody 2"],
    "disagreement_points": ["punkt sporu 1", "punkt sporu 2"],
    "partner_quality_scores": {{
        "Partner1": {{"score": 0.8, "reason": "dlaczego"}},
        "Partner2": {{"score": 0.6, "reason": "dlaczego"}}
    }},
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommendations": ["rekomendacja 1", "rekomendacja 2"],
    "overall_quality": 0.75
}}

JSON (bez dodatkowego tekstu):"""
            
            context = {'conversation_analysis': True}
            result = nexus.generate_response(analysis_prompt, context=context)
            
            if result.get('success'):
                # Parse JSON z odpowiedzi
                response_text = result.get('response', '').strip()
                
                # Usuń markdown blocks
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                    response_text = response_text.strip()
                
                meta_analysis = json.loads(response_text)
                
                print(f"✅ Nexus Meta-Analysis completed")
                print(f"   Main themes: {len(meta_analysis.get('main_themes', []))}")
                print(f"   Overall quality: {meta_analysis.get('overall_quality', 0)}")
                
                return meta_analysis
            else:
                print(f"❌ Nexus meta-analysis failed: {result.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ Błąd meta-analysis: {e}")
            return None
    
    def nexus_voting_simulation(self, conversation: Dict, decision_question: str) -> Optional[Dict]:
        """
        🗳️ Nexus symuluje głosowanie na podstawie rozmowy
        
        Na podstawie analizy wypowiedzi partnerów w rozmowie,
        Nexus przewiduje jak zagłosowaliby na konkretną decyzję.
        
        Args:
            conversation: Dict z zakończoną rozmową
            decision_question: Pytanie decyzyjne (np. "Czy zwiększyć alokację w krypto do 30%?")
        
        Returns:
            Dict z symulacją głosowania lub None
        """
        if not NEXUS_AVAILABLE:
            print("⚠️ Nexus niedostępny - voting simulation pomięta")
            return None
        
        messages = conversation.get("messages", [])
        if len(messages) < 3:
            print("⚠️ Za mało wiadomości do voting simulation")
            return None
        
        try:
            nexus = get_nexus_engine()
            
            # Grupuj wiadomości po partnerach
            partner_statements = {}
            for msg in messages:
                partner = msg.get('partner', 'Unknown')
                if partner not in partner_statements:
                    partner_statements[partner] = []
                partner_statements[partner].append(msg.get('message', ''))
            
            # Zbuduj summary wypowiedzi każdego partnera
            partner_summaries = "\n".join([
                f"{partner}: {'; '.join(statements[:3])}"  # Pierwsze 3 wypowiedzi
                for partner, statements in partner_statements.items()
            ])
            
            voting_prompt = f"""Na podstawie autonomicznej rozmowy, zasymuluj jak partnerzy zagłosowaliby na poniższą decyzję.

PYTANIE DECYZYJNE: {decision_question}

WYPOWIEDZI PARTNERÓW W ROZMOWIE:
{partner_summaries}

Przeanalizuj stanowiska i zwróć TYLKO JSON:
{{
    "votes": {{
        "Partner1": {{"vote": "ZA", "confidence": 0.8, "reasoning": "dlaczego"}},
        "Partner2": {{"vote": "PRZECIW", "confidence": 0.6, "reasoning": "dlaczego"}},
        "Partner3": {{"vote": "WSTRZYMUJĘ SIĘ", "confidence": 0.5, "reasoning": "dlaczego"}}
    }},
    "predicted_outcome": "ZA" lub "PRZECIW" lub "REMIS",
    "vote_tally": {{"ZA": 2, "PRZECIW": 1, "WSTRZYMUJĘ SIĘ": 1}},
    "confidence_overall": 0.7,
    "key_arguments_for": ["argument 1", "argument 2"],
    "key_arguments_against": ["argument 1", "argument 2"],
    "nexus_recommendation": "Twoja rekomendacja jako meta-advisor"
}}

Możliwe głosy: "ZA", "PRZECIW", "WSTRZYMUJĘ SIĘ"
JSON (bez dodatkowego tekstu):"""
            
            context = {'voting_simulation': True}
            result = nexus.generate_response(voting_prompt, context=context)
            
            if result.get('success'):
                response_text = result.get('response', '').strip()
                
                # Usuń markdown blocks
                if response_text.startswith('```'):
                    response_text = response_text.split('```')[1]
                    if response_text.startswith('json'):
                        response_text = response_text[4:]
                    response_text = response_text.strip()
                
                voting_result = json.loads(response_text)
                
                print(f"✅ Nexus Voting Simulation completed")
                print(f"   Predicted outcome: {voting_result.get('predicted_outcome')}")
                print(f"   Confidence: {voting_result.get('confidence_overall', 0)}")
                
                return voting_result
            else:
                print(f"❌ Nexus voting simulation failed: {result.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ Błąd voting simulation: {e}")
            return None
    
    def nexus_knowledge_synthesis(self, recent_conversations: List[Dict], query: str) -> Optional[str]:
        """
        📚 Nexus syntetyzuje wiedzę z wielu rozmów
        
        Analizuje wiele ostatnich rozmów i odpowiada na pytanie
        bazując na zgromadzonej wiedzy.
        
        Args:
            recent_conversations: Lista ostatnich rozmów (max 5)
            query: Pytanie do Nexusa
        
        Returns:
            Odpowiedź Nexusa lub None
        """
        if not NEXUS_AVAILABLE:
            print("⚠️ Nexus niedostępny - knowledge synthesis pomięta")
            return None
        
        if not recent_conversations:
            return "Brak rozmów do analizy."
        
        try:
            nexus = get_nexus_engine()
            
            # Zbuduj knowledge base z rozmów
            knowledge_base = []
            
            for conv in recent_conversations[:5]:  # Max 5 ostatnich
                topic = conv.get('topic_name', 'Unknown')
                date = conv.get('date', 'Unknown')
                
                # Dodaj summary jeśli istnieje
                if 'summary' in conv:
                    summary_text = conv['summary'].get('summary', '')
                    key_points = conv['summary'].get('key_points', [])
                    knowledge_base.append(f"[{date}] {topic}: {summary_text} | Kluczowe wnioski: {', '.join(key_points)}")
                else:
                    # Fallback - pierwsze 3 wiadomości
                    messages = conv.get('messages', [])[:3]
                    msgs_text = '; '.join([f"{m.get('partner')}: {m.get('message', '')[:100]}" for m in messages])
                    knowledge_base.append(f"[{date}] {topic}: {msgs_text}")
            
            knowledge_text = "\n".join(knowledge_base)
            
            synthesis_prompt = f"""Jesteś Nexus - meta-advisor z dostępem do historii autonomicznych rozmów Rady Partnerów.

PYTANIE: {query}

BAZA WIEDZY Z OSTATNICH ROZMÓW:
{knowledge_text}

Na podstawie powyższej wiedzy, udziel zwięzłej odpowiedzi (max 5-6 zdań):
- Syntetyzuj insights z różnych rozmów
- Wskaż trendy i wzorce
- Podaj konkretne rekomendacje
- Cytuj konkretne rozmowy jeśli relevantne

Odpowiedź:"""
            
            context = {'knowledge_synthesis': True, 'conversations_count': len(recent_conversations)}
            result = nexus.generate_response(synthesis_prompt, context=context)
            
            if result.get('success'):
                answer = result.get('response', '').strip()
                print(f"✅ Nexus Knowledge Synthesis completed ({len(recent_conversations)} rozmów)")
                return answer
            else:
                print(f"❌ Nexus knowledge synthesis failed: {result.get('error')}")
                return None
                
        except Exception as e:
            print(f"❌ Błąd knowledge synthesis: {e}")
            return None


def main():
    """Główna funkcja - uruchom autonomiczną rozmowę z Nexus enhancements"""
    engine = AutonomousConversationEngine()
    
    # Wyświetl status API przed rozmową
    print("\n📊 Status API przed rozmową:")
    engine.tracker.print_status()
    
    # Uruchom rozmowę
    conversation = engine.run_conversation(max_messages=12)
    
    if conversation:
        print(f"\n✅ Sukces! ID rozmowy: {conversation['id']}")
        print(f"📝 Liczba wiadomości: {len(conversation['messages'])}")
        print(f"🔢 Użyto API calls: {conversation['api_calls_used']}")
        
        # ✨ NEXUS ENHANCED FEATURES DEMO
        if NEXUS_AVAILABLE:
            print("\n" + "="*60)
            print("🤖 NEXUS ENHANCED FEATURES - DEMO")
            print("="*60)
            
            # 1. Meta-analysis już została wykonana w run_conversation()
            if 'nexus_meta_analysis' in conversation:
                meta = conversation['nexus_meta_analysis']
                print(f"\n📊 Meta-Analysis Results:")
                print(f"   Overall Quality: {meta.get('overall_quality', 0):.0%}")
                print(f"   Main Themes: {', '.join(meta.get('main_themes', []))}")
                print(f"   Consensus: {len(meta.get('consensus_points', []))} punktów")
                print(f"   Disagreements: {len(meta.get('disagreement_points', []))} punktów")
            
            # 2. Voting Simulation - przykładowe pytanie
            print(f"\n🗳️ Voting Simulation Example:")
            decision_q = "Czy zwiększyć alokację w krypto do 30% portfela?"
            voting_result = engine.nexus_voting_simulation(conversation, decision_q)
            
            if voting_result:
                print(f"   Pytanie: {decision_q}")
                print(f"   Predicted Outcome: {voting_result.get('predicted_outcome')}")
                print(f"   Vote Tally: {voting_result.get('vote_tally')}")
                print(f"   Confidence: {voting_result.get('confidence_overall', 0):.0%}")
                print(f"   Nexus Recommendation: {voting_result.get('nexus_recommendation', 'N/A')[:100]}...")
            
            # 3. Knowledge Synthesis - pytanie bazujące na historii
            recent = engine.get_recent_conversations(limit=5)
            if len(recent) > 0:
                print(f"\n📚 Knowledge Synthesis Example:")
                query = "Jakie są najważniejsze obawy Rady dotyczące naszego portfela w ostatnich dyskusjach?"
                synthesis = engine.nexus_knowledge_synthesis(recent, query)
                
                if synthesis:
                    print(f"   Pytanie: {query}")
                    print(f"   Nexus Answer:\n   {synthesis[:300]}...")
        
    else:
        print("\n❌ Nie udało się przeprowadzić rozmowy (brak budżetu API?)")
    
    # Wyświetl status API po rozmowie
    print("\n📊 Status API po rozmowie:")
    engine.tracker.print_status()


if __name__ == "__main__":
    main()
