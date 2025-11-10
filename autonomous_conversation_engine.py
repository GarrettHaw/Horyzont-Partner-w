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
                self._save_conversation(conversation)  # Zapisz ze summary
                print(f"✅ Summary wygenerowane")
        
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


def main():
    """Główna funkcja - uruchom autonomiczną rozmowę"""
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
    else:
        print("\n❌ Nie udało się przeprowadzić rozmowy (brak budżetu API?)")
    
    # Wyświetl status API po rozmowie
    print("\n📊 Status API po rozmowie:")
    engine.tracker.print_status()


if __name__ == "__main__":
    main()
