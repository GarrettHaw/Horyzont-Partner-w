"""
Email Notifier - Wysyłanie powiadomień o ważnych zmianach w portfelu
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import json
import os

class EmailNotifier:
    """Menedżer powiadomień e-mail"""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """
        Inicjalizacja notifikatora e-mail
        
        Args:
            smtp_server: Serwer SMTP (domyślnie Gmail)
            smtp_port: Port SMTP (domyślnie 587)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = os.getenv('NOTIFIER_EMAIL')
        self.sender_password = os.getenv('NOTIFIER_PASSWORD')
        self.recipient_emails = []
        self.alert_thresholds = {}
        
    def add_recipient(self, email: str) -> None:
        """Dodaj adres e-mail do listy odbiorców"""
        if email not in self.recipient_emails:
            self.recipient_emails.append(email)
    
    def set_alert_threshold(self, alert_type: str, threshold: float) -> None:
        """Ustaw próg dla alertu"""
        self.alert_thresholds[alert_type] = threshold
    
    def check_portfolio_changes(self, old_portfolio: Dict, new_portfolio: Dict) -> List[Dict]:
        """Sprawdź zmiany w portfelu i wygeneruj alerty"""
        alerts = []
        
        # Sprawdzenie zmiany wartości netto
        old_value = old_portfolio.get('PODSUMOWANIE', {}).get('Wartosc_netto_PLN', 0)
        new_value = new_portfolio.get('PODSUMOWANIE', {}).get('Wartosc_netto_PLN', 0)
        
        if old_value > 0:
            percentage_change = ((new_value - old_value) / old_value) * 100
            
            threshold = self.alert_thresholds.get('portfolio_change', 5)
            if abs(percentage_change) >= threshold:
                alerts.append({
                    'type': 'portfolio_change',
                    'title': '📊 Zmiana wartości portfela',
                    'message': f"Wartość portfela zmieniła się o {percentage_change:+.2f}%\nStara: {old_value:,.2f} PLN\nNowa: {new_value:,.2f} PLN",
                    'severity': 'high' if abs(percentage_change) > 10 else 'medium'
                })
        
        # Sprawdzenie nowych dywidend
        old_dividends = old_portfolio.get('PORTFEL_AKCJI', {}).get('Dywidendy_r_r', 0)
        new_dividends = new_portfolio.get('PORTFEL_AKCJI', {}).get('Dywidendy_r_r', 0)
        
        if new_dividends > old_dividends:
            alerts.append({
                'type': 'new_dividend',
                'title': '💰 Nowa dywidenda',
                'message': f"Nowe dochody z dywidend: +{new_dividends - old_dividends:,.2f} PLN",
                'severity': 'medium'
            })
        
        # Sprawdzenie kryptowalut
        old_crypto_value = sum(
            asset.get('wartosc_usd', 0) 
            for asset in old_portfolio.get('PORTFEL_KRYPTO', {}).get('pozycje', {}).values()
        )
        new_crypto_value = sum(
            asset.get('wartosc_usd', 0) 
            for asset in new_portfolio.get('PORTFEL_KRYPTO', {}).get('pozycje', {}).values()
        )
        
        if old_crypto_value > 0:
            crypto_change = ((new_crypto_value - old_crypto_value) / old_crypto_value) * 100
            threshold = self.alert_thresholds.get('crypto_change', 15)
            
            if abs(crypto_change) >= threshold:
                alerts.append({
                    'type': 'crypto_change',
                    'title': '🪙 Duża zmiana wartości krypto',
                    'message': f"Wartość krypto zmieniła się o {crypto_change:+.2f}%\nStara: ${old_crypto_value:,.2f}\nNowa: ${new_crypto_value:,.2f}",
                    'severity': 'high' if abs(crypto_change) > 25 else 'medium'
                })
        
        return alerts
    
    def send_email(self, recipient: str, subject: str, body: str, alerts: Optional[List[Dict]] = None) -> bool:
        """Wyślij e-mail z powiadomieniami"""
        if not self.sender_email or not self.sender_password:
            print("⚠️ Brak konfiguracji e-mail (NOTIFIER_EMAIL, NOTIFIER_PASSWORD)")
            return False
        
        try:
            # Utwórz wiadomość
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient
            
            # HTML body
            html_body = self._create_html_email(subject, body, alerts)
            
            message.attach(MIMEText(html_body, "html"))
            
            # Wyślij wiadomość
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient, message.as_string())
            
            print(f"✅ E-mail wysłany do {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd przy wysyłaniu e-mail: {e}")
            return False
    
    def send_alert_emails(self, alerts: List[Dict]) -> None:
        """Wyślij e-maile ze wszystkimi alertami do wszystkich odbiorców"""
        if not alerts or not self.recipient_emails:
            return
        
        alert_html = self._create_alert_html(alerts)
        
        for recipient in self.recipient_emails:
            self.send_email(
                recipient,
                "🚨 Ważne powiadomienie o portfelu",
                alert_html,
                alerts
            )
    
    def _create_html_email(self, subject: str, body: str, alerts: Optional[List[Dict]] = None) -> str:
        """Utwórz HTML wiadomości e-mail"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f5f5f5; }}
                    .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }}
                    .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
                    .alert {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 4px; }}
                    .alert.high {{ background-color: #f8d7da; border-left-color: #dc3545; }}
                    .alert.medium {{ background-color: #fff3cd; border-left-color: #ffc107; }}
                    .footer {{ color: #999; font-size: 12px; text-align: center; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏢 Horyzont Partnerów</h1>
                        <p>{subject}</p>
                    </div>
                    <div class="content">
                        {body}
                    </div>
                    <div class="footer">
                        <p>Wygenerowano: {timestamp}</p>
                        <p>To jest automatyczne powiadomienie - nie odpisuj na ten e-mail</p>
                    </div>
                </div>
            </body>
        </html>
        """
        return html
    
    def _create_alert_html(self, alerts: List[Dict]) -> str:
        """Utwórz HTML dla alertów"""
        alerts_html = ""
        
        for alert in alerts:
            severity_class = alert.get('severity', 'medium')
            alerts_html += f"""
            <div class="alert {severity_class}">
                <h3>{alert['title']}</h3>
                <p>{alert['message']}</p>
            </div>
            """
        
        return alerts_html
    
    def check_and_notify(self, old_portfolio: Dict, new_portfolio: Dict) -> None:
        """Sprawdź zmiany i wyślij powiadomienia jeśli są istotne"""
        alerts = self.check_portfolio_changes(old_portfolio, new_portfolio)
        
        if alerts and self.recipient_emails:
            self.send_alert_emails(alerts)
            
            # Wyświetl alerty w konsoli
            for alert in alerts:
                print(f"\n{alert['title']}")
                print(alert['message'])


class AlertManager:
    """Menedżer alertów - zarządzanie ustawieniami alertów"""
    
    ALERT_PRESETS = {
        'conservative': {
            'portfolio_change': 2,
            'crypto_change': 10,
            'dividend_threshold': 100
        },
        'moderate': {
            'portfolio_change': 5,
            'crypto_change': 15,
            'dividend_threshold': 50
        },
        'aggressive': {
            'portfolio_change': 10,
            'crypto_change': 25,
            'dividend_threshold': 20
        }
    }
    
    @staticmethod
    def create_notifier(preset: str = 'moderate') -> EmailNotifier:
        """Utwórz notifier z predefiniowanymi ustawieniami"""
        notifier = EmailNotifier()
        
        if preset in AlertManager.ALERT_PRESETS:
            thresholds = AlertManager.ALERT_PRESETS[preset]
            for alert_type, threshold in thresholds.items():
                notifier.set_alert_threshold(alert_type, threshold)
        
        return notifier
    
    @staticmethod
    def save_alert_config(config: Dict, filename: str = 'alert_config.json') -> None:
        """Zapisz konfigurację alertów"""
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    def load_alert_config(filename: str = 'alert_config.json') -> Dict:
        """Załaduj konfigurację alertów"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}


# =====================================================
# NOWE: Autonomous Conversation Notifications
# =====================================================

class ConversationNotifier(EmailNotifier):
    """
    Rozszerzenie EmailNotifier dla autonomicznych rozmów
    Wysyła powiadomienia o zakończonych rozmowach, daily digest
    """
    
    def __init__(self):
        super().__init__()
        self.config = self._load_notification_config()
        self.history = self._load_notification_history()
    
    def _load_notification_config(self) -> Dict:
        """Załaduj konfigurację powiadomień"""
        config_file = "notification_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            default_config = {
                "enabled": False,
                "email_to": os.getenv('NOTIFIER_EMAIL', 'your-email@gmail.com'),
                "daily_digest": {
                    "enabled": True,
                    "time": "18:00"
                },
                "alerts": {
                    "conversation_completed": True,
                    "critical_issue": True
                }
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return default_config
    
    def _load_notification_history(self) -> List[Dict]:
        """Załaduj historię powiadomień"""
        history_file = "notification_history.json"
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_notification_history(self):
        """Zapisz historię (ostatnie 100)"""
        with open("notification_history.json", 'w', encoding='utf-8') as f:
            json.dump(self.history[-100:], f, indent=2, ensure_ascii=False)
    
    def _log_notification(self, notification_type: str, subject: str, status: str, error: str = None):
        """Dodaj wpis do historii"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": notification_type,
            "subject": subject,
            "status": status,
            "error": error
        }
        self.history.append(entry)
        self._save_notification_history()
    
    def send_conversation_completed(self, conversation: Dict) -> bool:
        """Wyślij powiadomienie o zakończonej rozmowie"""
        if not self.config.get("enabled", False):
            return False
        if not self.config.get("alerts", {}).get("conversation_completed", False):
            return False
        
        conv_id = conversation.get("id", "unknown")
        topic_name = conversation.get("topic_name", "Unknown Topic")
        participants = conversation.get("participants", [])
        messages_count = len(conversation.get("messages", []))
        date = conversation.get("date", "")[:19]
        summary = conversation.get("summary", None)
        
        # HTML body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #3498db; }}
                .key-point {{ margin: 5px 0; padding-left: 20px; }}
                .message {{ background: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 3px solid #3498db; }}
                .partner {{ font-weight: bold; color: #2c3e50; }}
                .footer {{ background: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🗣️ Nowa Rozmowa Rady Partnerów</h2>
            </div>
            
            <div class="content">
                <div class="info">
                    <p><strong>📋 Temat:</strong> {topic_name}</p>
                    <p><strong>📅 Data:</strong> {date}</p>
                    <p><strong>👥 Uczestnicy:</strong> {', '.join(participants)}</p>
                    <p><strong>💬 Liczba wiadomości:</strong> {messages_count}</p>
                </div>
        """
        
        # Dodaj AI Summary jeśli istnieje (NOWE!)
        if summary:
            sentiment = summary.get('sentiment', 'neutral')
            sentiment_emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😟'}.get(sentiment, '😐')
            
            html_body += f"""
                <div class="summary">
                    <h3>🤖 AI Summary {sentiment_emoji}</h3>
                    <p><strong>📝 Podsumowanie:</strong></p>
                    <p>{summary.get('summary', 'Brak podsumowania')}</p>
            """
            
            key_points = summary.get('key_points', [])
            if key_points:
                html_body += "<p><strong>🎯 Kluczowe wnioski:</strong></p><ul>"
                for point in key_points:
                    html_body += f"<li class='key-point'>{point}</li>"
                html_body += "</ul>"
            
            html_body += "</div>"
        
        html_body += """
                <h3>📝 Pierwsze wiadomości:</h3>
        """
        
        # Dodaj preview pierwszych 3 wiadomości
        messages = conversation.get("messages", [])[:3]
        for msg in messages:
            partner = msg.get("partner", "Unknown")
            text = msg.get("message", "")[:200]
            html_body += f"""
                <div class="message">
                    <div class="partner">{partner}:</div>
                    <div>{text}...</div>
                </div>
            """
        
        html_body += f"""
                <p><em>Zobacz pełny transkrypt w aplikacji (ID: {conv_id})</em></p>
            </div>
            
            <div class="footer">
                <p>Horyzont Partnerów - Autonomous Conversation System</p>
                <p>Wiadomość automatyczna</p>
            </div>
        </body>
        </html>
        """
        
        subject = f"🗣️ Nowa rozmowa: {topic_name} ({messages_count} wiadomości)"
        
        try:
            self.send_notification(
                to_email=self.config.get("email_to"),
                subject=subject,
                html_body=html_body
            )
            self._log_notification("conversation_completed", subject, "sent")
            return True
        except Exception as e:
            self._log_notification("conversation_completed", subject, "failed", str(e))
            return False
    
    def send_daily_digest(self, conversations: List[Dict], stats: Dict) -> bool:
        """Wyślij codzienny digest"""
        if not self.config.get("enabled", False):
            return False
        if not self.config.get("daily_digest", {}).get("enabled", False):
            return False
        
        today = datetime.now().strftime("%Y-%m-%d")
        conv_count = len(conversations)
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background: #27ae60; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .stat-box {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .conversation {{ background: #f9f9f9; padding: 10px; margin: 5px 0; border-left: 4px solid #3498db; }}
                .footer {{ background: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📊 Daily Digest - {today}</h2>
            </div>
            
            <div class="content">
                <h3>📈 Podsumowanie dnia</h3>
                
                <div class="stat-box">
                    <p><strong>🗣️ Rozmowy autonomiczne:</strong> {conv_count}</p>
                    <p><strong>🤖 Wywołania Autonomous:</strong> {stats.get('autonomous_calls', 0)}</p>
                    <p><strong>👤 Wywołania User:</strong> {stats.get('user_calls', 0)}</p>
                    <p><strong>💰 Koszt:</strong> ${stats.get('total_cost', 0):.4f}</p>
                </div>
                
                <h3>🗣️ Rozmowy dzisiaj</h3>
        """
        
        if conversations:
            for conv in conversations:
                topic = conv.get("topic_name", "Unknown")
                msgs = len(conv.get("messages", []))
                time = conv.get("date", "")[:19]
                html_body += f"""
                <div class="conversation">
                    <strong>{time}</strong> - {topic} ({msgs} wiadomości)
                </div>
                """
        else:
            html_body += "<p><em>Brak rozmów dzisiaj</em></p>"
        
        html_body += """
            </div>
            
            <div class="footer">
                <p>Horyzont Partnerów - Daily Digest</p>
            </div>
        </body>
        </html>
        """
        
        subject = f"📊 Daily Digest - {today} ({conv_count} rozmów)"
        
        try:
            self.send_notification(
                to_email=self.config.get("email_to"),
                subject=subject,
                html_body=html_body
            )
            self._log_notification("daily_digest", subject, "sent")
            return True
        except Exception as e:
            self._log_notification("daily_digest", subject, "failed", str(e))
            return False
    
    def send_test_email(self) -> bool:
        """Wyślij testowy email"""
        html_body = f"""
        <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #27ae60;">✅ Test Email</h2>
            <p>Email Notifier działa poprawnie!</p>
            <p><strong>Timestamp:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </body>
        </html>
        """
        
        try:
            self.send_notification(
                to_email=self.config.get("email_to"),
                subject="🧪 Test Email - Horyzont Partnerów",
                html_body=html_body
            )
            self._log_notification("test", "Test Email", "sent")
            return True
        except Exception as e:
            self._log_notification("test", "Test Email", "failed", str(e))
            return False
    
    def send_consultation_completed(self, consultation: Dict) -> bool:
        """
        Wyślij email o zakończonej konsultacji z Radą
        
        Args:
            consultation: Dict z danymi konsultacji
        
        Returns:
            bool: True jeśli wysłano
        """
        cons_id = consultation.get("id", "unknown")
        question = consultation.get("question", "Unknown Question")
        participants = consultation.get("participants", [])
        responses = consultation.get("responses", [])
        summary = consultation.get("summary", {})
        date = consultation.get("created_at", "")[:19]
        
        # HTML body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #8e44ad; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                .summary {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #8e44ad; }}
                .vote {{ background: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 3px solid #3498db; }}
                .partner {{ font-weight: bold; color: #2c3e50; }}
                .metric {{ display: inline-block; background: #3498db; color: white; padding: 10px 20px; margin: 5px; border-radius: 5px; text-align: center; }}
                .footer {{ background: #ecf0f1; padding: 10px; text-align: center; font-size: 12px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🗳️ Konsultacja Zakończona</h2>
            </div>
            
            <div class="content">
                <div class="info">
                    <p><strong>❓ Pytanie:</strong> {question}</p>
                    <p><strong>📅 Data:</strong> {date}</p>
                    <p><strong>👥 Uczestnicy:</strong> {', '.join(participants)}</p>
                    <p><strong>💬 Liczba odpowiedzi:</strong> {len(responses)}</p>
                </div>
        """
        
        # Dodaj AI Summary jeśli istnieje
        if summary:
            consensus = summary.get('consensus', 'medium')
            consensus_label = {
                'high': 'Wysoki Konsensus ✅',
                'medium': 'Średni Konsensus 🤔',
                'low': 'Niski Konsensus ❌'
            }.get(consensus, 'Nieznany')
            
            html_body += f"""
                <div class="summary">
                    <h3>🤖 Podsumowanie AI</h3>
                    
                    <div style="text-align: center; margin: 15px 0;">
                        <span class="metric">✅ ZA: {summary.get('votes_for', 0)}</span>
                        <span class="metric">❌ PRZECIW: {summary.get('votes_against', 0)}</span>
                        <span class="metric">🤔 NEUTRALNE: {summary.get('votes_neutral', 0)}</span>
                    </div>
                    
                    <p><strong>📊 Konsensus:</strong> {consensus_label}</p>
                    
                    <p><strong>💡 Rekomendacja AI:</strong></p>
                    <p style="font-style: italic; background: #fff3cd; padding: 10px; border-radius: 5px;">
                        {summary.get('recommendation', 'Brak rekomendacji')}
                    </p>
            """
            
            # Argumenty ZA
            args_for = summary.get('main_arguments_for', [])
            if args_for:
                html_body += "<p><strong>✅ Główne argumenty ZA:</strong></p><ul>"
                for arg in args_for:
                    html_body += f"<li>{arg}</li>"
                html_body += "</ul>"
            
            # Argumenty PRZECIW
            args_against = summary.get('main_arguments_against', [])
            if args_against:
                html_body += "<p><strong>❌ Główne argumenty PRZECIW:</strong></p><ul>"
                for arg in args_against:
                    html_body += f"<li>{arg}</li>"
                html_body += "</ul>"
            
            html_body += "</div>"
        
        # Dodaj szczegółowe odpowiedzi (pierwsze 5)
        html_body += "<h3>💬 Odpowiedzi partnerów:</h3>"
        
        for i, resp in enumerate(responses[:5]):
            stance = resp.get('stance', 'neutral')
            stance_emoji = {
                'for': '✅ ZA',
                'against': '❌ PRZECIW',
                'neutral': '🤔 NEUTRALNIE'
            }.get(stance, '🤔 NEUTRALNIE')
            
            confidence = resp.get('confidence', 5)
            reasoning = resp.get('reasoning', 'Brak uzasadnienia')
            partner_name = resp.get('partner', 'Unknown')
            
            html_body += f"""
                <div class="vote">
                    <p class="partner">{partner_name} - {stance_emoji} (Pewność: {confidence}/10)</p>
                    <p>{reasoning}</p>
                </div>
            """
        
        if len(responses) > 5:
            html_body += f"<p><em>... i {len(responses) - 5} więcej odpowiedzi w dashboardzie</em></p>"
        
        # Footer
        html_body += """
                <div class="footer">
                    <p>🏢 Horyzont Partnerów - System Konsultacji</p>
                    <p>Więcej szczegółów w zakładce "🗳️ Konsultacje" w dashboardzie</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            self.send_notification(
                to_email=self.config.get("email_to"),
                subject=f"🗳️ Konsultacja zakończona: {question[:50]}...",
                html_body=html_body
            )
            self._log_notification(
                "consultation_completed",
                f"Consultation {cons_id}",
                "sent"
            )
            return True
        except Exception as e:
            self._log_notification(
                "consultation_completed",
                f"Consultation {cons_id}",
                "failed",
                str(e)
            )
            return False
    
    def get_recent_notifications(self, limit: int = 20) -> List[Dict]:
        """Zwróć ostatnie N powiadomień"""
        return self.history[-limit:][::-1]


# Singleton
_conversation_notifier = None

def get_conversation_notifier() -> ConversationNotifier:
    """Pobierz globalną instancję conversation notifier"""
    global _conversation_notifier
    if _conversation_notifier is None:
        _conversation_notifier = ConversationNotifier()
    return _conversation_notifier
