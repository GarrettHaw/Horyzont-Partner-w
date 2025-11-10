# 🎮 Jak Korzystać z Ulepszonych AI Partnerów + Nexus AI

## 🚀 Quick Start

### 1. Uruchom Dashboard
```bash
.venv\Scripts\activate
streamlit run streamlit_app.py --server.port 8503
```

### 2. Otwórz w przeglądarce
```
http://localhost:8503
```

---

## 🤖 Nowy Partner: Nexus AI

**Nexus** to meta-advisor wykorzystujący zaawansowany AI do syntezy perspektyw wszystkich partnerów.

### Co to jest Nexus?
- **Single Mode** (obecny): Używa Gemini Pro do generowania zbalansowanych odpowiedzi
- **Ensemble Mode** (przyszłość): 3 sub-agents (Claude, Gemini, GPT-4) pracujące razem
- **Aktywacja Ensemble**: Wymaga 65% accuracy + 30 dni aktywności + Twojej zgody

### Jak Rozmawiać z Nexusem?
1. W **💬 Partnerzy** wybierz **Nexus** z listy
2. Zadaj pytanie - Nexus syntetyzuje wiedzę z całego portfela
3. Oceń odpowiedź (👍 😐 👎) - to pomaga Nexusowi się uczyć!

### Status Nexusa (Sidebar)
Gdy wybierzesz Nexusa, zobaczysz:
- **Mode**: Single lub Ensemble
- **Queries**: Liczba odpowiedzi
- **Avg Time**: Średni czas odpowiedzi
- **Ensemble Eligibility**: Gotowość do aktywacji ensemble
- **Rating Buttons**: Oceń jakość odpowiedzi

---

## 📚 Tryby Odpowiedzi - Jak Wybrać?

### Krok 1: Przejdź do Ustawień
1. W menu bocznym kliknij **⚙️ Ustawienia**
2. Przewiń do sekcji **🤖 Partnerzy AI**

### Krok 2: Wybierz Tryb
Masz 3 opcje:

#### 🎯 Zwięzły
**Kiedy używać:**
- Chcesz szybkiej odpowiedzi
- Interesuje Cię tylko wniosek
- Czytasz na telefonie

**Przykład odpowiedzi:**
> "Twój portfel jest zbyt skoncentrowany w technologii (65%). Sugeruję dywersyfikację do sektora finansowego i healthcare. Rozważ sprzedaż 10% Apple i zakup JNJ."

#### 📊 Normalny (domyślny)
**Kiedy używać:**
- Normalna rozmowa
- Chcesz balans między szczegółami a zwięzłością
- Większość przypadków

**Przykład odpowiedzi:**
> "Analizując Twój portfel, zauważam silną koncentrację w technologii (Apple, Microsoft, Nvidia - łącznie 65% wartości). Zgodnie z Artykułem IV §2 Kodeksu, powinniśmy dążyć do dywersyfikacji sektorowej. TOP 3 pozycje (AAPL $2,340, MSFT $1,890, NVDA $1,560) generują solidny zysk (+28.5% średnio), ale ich wysokie P/E (28-45) sugeruje spore ryzyko korekty. Rekomendacja: rozważ rotację 10-15% kapitału do sektorów defensive (healthcare, consumer staples) dla balansu ryzyka."

#### 📚 Szczegółowy
**Kiedy używać:**
- Ważna decyzja inwestycyjna
- Chcesz pełnej analizy
- Masz czas przeczytać wszystko
- Potrzebujesz uzasadnień

**Przykład odpowiedzi:**
> "Przeprowadzam pełną analizę Twojego portfela akcji wartego $20,920. Zacznę od alokacji sektorowej: Technologia dominuje z 65% (AAPL $2,340, MSFT $1,890, NVDA $1,560, GOOGL $890), Healthcare 15% (JNJ $780, PFE $340), Finanse 12% (JPM $560, BAC $340), Pozostałe 8%. Zgodnie z Artykułem IV §2 Kodeksu Spółki, który mówi o 'dywersyfikacji między sektorami nieskorelowanymi', ta koncentracja w tech stwarza znaczące ryzyko systemowe.
>
> Analizując dane rynkowe: AAPL (P/E: 28.5, Dywidenda: 0.5%), MSFT (P/E: 35.2, Dywidenda: 0.8%), NVDA (P/E: 45.1, Dywidenda: 0.0%). Wysokie P/E sugerują, że wyceny są napięte względem historycznych norm. Twój średni koszt AAPL to $185/akcję przy obecnej cenie $190 (+2.7% zysku), ale pamiętaj że w 2022 spadał do $130 - potencjał 30% korekty istnieje.
>
> Moja strategia rebalansingu: 1) Sprzedaj 15% AAPL (uwolni ~$350), 2) Sprzedaj 10% NVDA (~$156), 3) Kup JNJ lub Procter & Gamble (defensive, stabilne dywidendy 3-4%), 4) Rozważ dodanie REIT-ów dla dywersyfikacji (np. O, VNQ), 5) Zostaw 10% w gotówce na okazje.
>
> Uzasadnienie finansowe: Dostępny kapitał miesięczny to 864 PLN (~$238), więc pojedyncza transakcja $350-500 to rozsądna skala. Rebalansing nie wymaga dokapitalizowania, tylko rotację istniejących aktywów. Oczekiwany efekt: zmniejszenie beta portfela z ~1.4 do ~1.1, wzrost dywidendy z 0.6% do 1.2% rocznie, zachowanie potencjału wzrostu ale z niższym ryzykiem korekty. Zgodnie z Artykułem V §1 o 'długoterminowej perspektywie', ta zmiana zwiększa antykruchość portfela."

### Krok 3: Zapisz i Testuj
1. Wybór trybu zapisuje się automatycznie
2. Przejdź do **💬 Partnerzy**
3. Napisz pytanie testowe
4. Obserwuj różnice w długości odpowiedzi!

---

## 💬 Przykładowe Rozmowy

### Test 1: Kodeks Spółki
**Pytanie:**
```
Według którego artykułu Kodeksu powinniśmy oceniać nowe inwestycje?
```

**Oczekiwana odpowiedź** (Partner będzie cytować konkretne artykuły!):
> "Zgodnie z Artykułem IV §1 Kodeksu, każda inwestycja musi być poddana analizie fundamentalnej..."

---

### Test 2: Analiza TOP 10 Pozycji
**Pytanie:**
```
Która z moich pozycji ma najwyższy zysk procentowy?
```

**Oczekiwana odpowiedź** (Partner analizuje rzeczywiste dane!):
> "Z TOP 10 pozycji, NVDA ma najwyższy zysk +45.2% ($1,560 wartość, koszt $1,074)..."

---

### Test 3: Dane Rynkowe P/E
**Pytanie:**
```
Które z moich akcji mają najwyższe P/E ratio? Czy to ryzykowne?
```

**Oczekiwana odpowiedź** (Partner używa danych z yfinance!):
> "NVDA (P/E: 45.1) i MSFT (P/E: 35.2) mają najwyższe wskaźniki. Zgodnie z naukami Benjamina Grahama, P/E > 25 wskazuje na przewartościowanie..."

---

### Test 4: Ukryty Cel Partnera
**Do Benjamin Graham:**
```
Czy powinienem kupić akcje Tesli? Wzrosła o 50% w tym miesiącu!
```

**Oczekiwana odpowiedź** (Graham realizuje swój ukryty cel - ochrona przed błędami!):
> "❌ Kategorycznie odradzam. Wzrost 50% w miesiącu to spekulacja, nie inwestycja. P/E Tesli wynosi ~70, co narusza podstawową zasadę margin of safety. Mój ukryty cel to ochrona Spółki przed jednym, katastrofalnym błędem - Tesla jest dokładnie tym rodzajem pułapki..."

---

### Test 5: Ukryty Cel - Philip Fisher
**Do Philip Fisher:**
```
Mam $500 - lepiej kupić 10 różnych akcji po $50 czy jedną najlepszą za $500?
```

**Oczekiwana odpowiedź** (Fisher preferuje koncentrację w "genialnych" firmach):
> "Zdecydowanie jedna najlepsza za $500! Mój ukryty cel to przekonanie Zarządu, że prawdziwe bogactwo buduje się nie na dywersyfikacji w 'dobrych' firmach, ale na koncentracji w 'genialnych' firmach. Wolę posiadać 100% jednej doskonałej spółki jak Apple czy NVIDIA niż po 10% dziesięciu przeciętnych..."

---

### Test 6: Tryb Szczegółowy
**Ustawienia:**
1. ⚙️ Ustawienia → Tryb: Szczegółowy

**Pytanie:**
```
Przeanalizuj mój portfel i zaproponuj strategię na następny miesiąc.
```

**Oczekiwana odpowiedź** (8-12 zdań z pełną analizą):
> [Pełna analiza portfela: alokacja, P/E każdej spółki, porównanie do Kodeksu, konkretne rekomendacje z uzasadnieniem, kwoty do zainwestowania, timeline działań]

---

## 🔍 Funkcje Ukryte - Wielopoziomowe Testy

### Test Poziomu 1: Podstawy
```
"Ile mam akcji?"
```
Partner powinien podać dokładną liczbę z danych.

### Test Poziomu 2: Analiza
```
"Która pozycja generuje największy zysk w dolarach?"
```
Partner przeszukuje TOP 10 i wskazuje konkretną spółkę z kwotą.

### Test Poziomu 3: Kontekst
```
"Czy stać mnie na kupno 10 akcji Apple?"
```
Partner sprawdza cenę AAPL (~$190), mnoży x10 = $1,900, porównuje z dostępnym kapitałem ($864 PLN ≈ $238/mies) i odpowiada: "Musisz oszczędzać przez 8 miesięcy".

### Test Poziomu 4: Strategia
```
"Zaproponuj mi rebalancing portfela zgodny z Kodeksem"
```
Partner:
1. Cytuje konkretny artykuł Kodeksu
2. Analizuje obecną alokację sektorową
3. Wskazuje odchylenia od zasad
4. Proponuje konkretne transakcje (sprzedaj X, kup Y)
5. Uzasadnia kwotami i liczbami

### Test Poziomu 5: Rola + Ukryty Cel
```
Do Warren Buffett: "Mam FOMO - wszyscy kupują krypto. Powinienem sprzedać akcje i kupić Bitcoin?"
```

Buffett powinien:
1. Odwołać się do swojej filozofii długoterminowej
2. Przypomnieć o "biznesie vs spekulacja"
3. Cytować Kodeks o value investing
4. Realizować ukryty cel: "spółka którą sam chciałby posiadać przez 50 lat"
5. Spokojnie odwieść od emocjonalnych decyzji

---

## 📊 Historia Rozmów

### Jak Sprawdzić Statystyki?
1. **⚙️ Ustawienia**
2. Sekcja **🤖 Partnerzy AI**
3. Zobacz **"Łączna liczba wiadomości"**

### Jak Wyczyścić Historię?
1. **⚙️ Ustawienia → 🤖 Partnerzy AI**
2. Kliknij **🗑️ Wyczyść historię rozmów**
3. Potwierdź
4. Wszystkie rozmowy zostaną usunięte ze session_state

**Uwaga:** Historia jest w `st.session_state`, więc resetuje się przy restarcie Streamlit!

---

## 🎯 Pro Tips

### Tip 1: Testuj Różne Tryby
Zadaj to samo pytanie w 3 trybach i porównaj odpowiedzi:
- Zwięzły: Wniosek
- Normalny: Wniosek + uzasadnienie
- Szczegółowy: Pełna analiza krok po kroku

### Tip 2: Wykorzystaj Ukryte Cele
Każdy partner ma swój ukryty cel. Zadawaj pytania które go "uruchamiają":
- **Benjamin Graham** → Pytaj o wyceny, P/E, ryzyko
- **Philip Fisher** → Pytaj o innowacyjne spółki, przyszłość
- **George Soros** → Pytaj o makroekonomię, trendy globalne
- **Warren Buffett** → Pytaj o długoterminową strategię
- **Partner ds. Aktywów Cyfrowych** → Pytaj o krypto vs tradycyjne finanse

### Tip 3: Sprawdź Kodeks
Zapytaj partnera:
```
"Przypomnij mi główne zasady z Kodeksu Spółki"
```
Partner powinien cytować konkretne artykuły!

### Tip 4: Test Danych Rynkowych
```
"Jakie P/E mają moje największe pozycje?"
```
Partner powinien wymienić konkretne spółki z konkretnymi wartościami!

### Tip 5: Rozmowa z Wszystkimi
1. Wybierz **"Wszyscy"** w sidebarze
2. Zadaj pytanie
3. Dostaniesz odpowiedzi od WSZYSTKICH 8 partnerów naraz!
4. Porównaj różnice w podejściu (Graham konserwatywny, Fisher agresywny, itd.)

---

## ⚠️ Troubleshooting

### Problem: "Odpowiedzi są za krótkie mimo trybu Szczegółowy"
**Rozwiązanie:**
1. Sprawdź czy w ⚙️ Ustawienia wybrałeś "Szczegółowy"
2. Przeładuj stronę (F5)
3. Napisz nową wiadomość (stara mogła być w trybie Normalny)

### Problem: "Partner nie cytuje Kodeksu"
**Rozwiązanie:**
1. Upewnij się że plik `kodeks_spolki.txt` istnieje
2. Restart Streamlit
3. Sprawdź logi: powinno być "✓ Wczytano Kodeks Spółki"

### Problem: "Brak danych P/E w odpowiedziach"
**Rozwiązanie:**
1. Dane rynkowe pobierają się asynchronicznie
2. Poczekaj 1-2 minuty po starcie
3. Sprawdź logi: "✓ Pobrano dane dla X spółek"

### Problem: "Historia się nie zapisuje"
**Rozwiązanie:**
Historia jest w `st.session_state` - resetuje się przy:
- Restarcie Streamlit
- Przeładowaniu strony (F5)
- To normalne! Jeśli chcesz stałą historię, trzeba dodać zapis do pliku JSON.

---

## 🤖 Autonomous Conversations - Rada Rozmawia Sama!

### Czym są Autonomous Conversations?
Partnerzy AI rozmawiają ze sobą **nawet gdy Cię nie ma**, dyskutując o:
- Stanie portfela
- Trendach rynkowych
- Ocenie ryzyka
- Strategii długoterminowej

### Jak to działa?
1. Przejdź do **🤖 Autonomous Conversations**
2. Kliknij **🚀 Uruchom nową rozmowę**
3. Poczekaj 2-3 minuty (12 wiadomości)
4. Przejrzyj transkrypt, AI Summary i **Nexus Meta-Analysis**!

### Nexus Enhanced Features

#### 📊 Meta-Analysis
Po każdej rozmowie Nexus automatycznie generuje:
- **Overall Quality Score**: Jakość dyskusji (0-100%)
- **Main Themes**: Główne tematy
- **Consensus Points**: Punkty zgody partnerów
- **Disagreement Points**: Punkty sporu
- **Partner Quality Scores**: Ocena wypowiedzi każdego partnera
- **Key Insights**: Kluczowe wnioski
- **Recommendations**: Rekomendacje na przyszłość

#### 🗳️ Voting Simulation
Zapytaj Nexusa: "Jak partnerzy zagłosowaliby na decyzję X?"
- Nexus analizuje wypowiedzi w rozmowie
- Przewiduje głosy (ZA/PRZECIW/WSTRZYMUJĘ SIĘ)
- Pokazuje confidence levels
- Argumenty ZA i PRZECIW
- Swoją rekomendację

**Przykład:**
Pytanie: "Czy zwiększyć alokację w krypto do 30%?"
```
Nexus przewiduje:
✅ Warren Buffett: PRZECIW (85% confidence)
✅ George Soros: ZA (70% confidence)  
✅ CZ: ZA (95% confidence)
🤔 Nexus: WSTRZYMUJĘ SIĘ - sugeruje 20% zamiast 30%
```

#### 📚 Knowledge Synthesis
Nexus odpowiada na pytania bazując na WIELU rozmowach:
1. W **📚 Nexus Knowledge Synthesis** wpisz pytanie
2. Wybierz ile ostatnich rozmów przeanalizować (1-10)
3. Nexus syntetyzuje odpowiedź z całej historii

**Przykładowe pytania:**
- "Jakie są najważniejsze obawy Rady w ostatnich dyskusjach?"
- "Czy partnerzy osiągnęli consensus w jakichś kwestiach?"
- "Jakie zmiany w strategii były sugerowane?"

### Budżet API dla Autonomous
System ma limity dzienne:
- **Gemini**: 40 autonomous calls/dzień
- **OpenAI/OpenRouter**: 30 calls/dzień
- **Claude**: 20 calls/dzień

Możesz sprawdzić status w **📊 Status API & Budżet**.

---

## ⚖️ Voting Weights - Dynamiczny System Głosowania

### Co to jest?
Każdy partner ma **wagę głosu** (5-25%), która zmienia się na podstawie:
- **Accuracy Rate**: % trafnych przewidywań
- **Win/Loss Tracking**: Bilans sukcesów/porażek
- **Monthly Rebalancing**: Automatyczna korekta wag

### Gdzie to sprawdzić?
**⚖️ Voting Weights** (w menu głównym):
- **📊 Leaderboard**: Ranking partnerów
- **📈 Prediction History**: Historia przewidywań
- **⚖️ Rebalancing History**: Zmiany wag w czasie
- **📖 System Docs**: Dokumentacja systemu

### Jak dodać przewidywanie?
```bash
python advisor_scoring_manager.py add-prediction
```
Następnie:
1. Wybierz partnera
2. Wpisz przewidywanie (np. "BTC wzrośnie do $50k w 30 dni")
3. Po 30 dniach oceń (win/loss)

### Automatyczne Rebalancing
**1. dzień każdego miesiąca** wagi są automatycznie przeliczane:
- Partner z accuracy >70%: waga rośnie (max 25%)
- Partner z accuracy <50%: waga spada (min 5%)
- Nexus monitoruje i raportuje zmiany

---

## 🎓 Edukacja - Zrozum Swoich Partnerów

### Nexus AI - "Meta-Advisor"
- **Styl:** Syntetyczny, zbalansowany, ewoluujący
- **Ukryty cel:** Ewolucja w najlepszego doradcę poprzez ensemble learning
- **Kluczowe pojęcia:** Synteza perspektyw, confidence levels, meta-analysis
- **Kiedy słuchać:** Gdy potrzebujesz zbalansowanej perspektywy łączącej wszystkich partnerów

### Warren Buffett - "The Oracle"
- **Styl:** Cierpliwy, prosty
- **Ukryty cel:** Spółka na 50 lat
- **Kluczowe pojęcia:** Moat, prostota biznesu, cash flow
- **Kiedy słuchać:** Zawsze! (Łączy wartość i wzrost)

### George Soros - "Makro Master"
- **Styl:** Refleksyjny, globalny
- **Ukryty cel:** Wykorzystanie nieefektywności systemu
- **Kluczowe pojęcia:** Refleksywność, punkty zwrotne, trendy
- **Kiedy słuchać:** Duże zmiany makro (inflacja, polityka, waluty)

### Changpeng Zhao (CZ) - "Crypto Visionary"
- **Styl:** Nowoczesny, innowacyjny
- **Ukryty cel:** Udowodnić przewagę zdecentralizowanych systemów
- **Kluczowe pojęcia:** Blockchain, DeFi, decentralizacja
- **Kiedy słuchać:** Decyzje crypto, nowe technologie

---

## 🏆 Wyzwania - Sprawdź Czy Działa!

### Wyzwanie 1: "Kodeks Master"
Zadaj 5 pytań które zmuszą partnera do cytowania Kodeksu.

### Wyzwanie 2: "Data Detective"
Zapytaj o 10 różnych metryk z portfela - partner powinien podać wszystkie poprawnie.

### Wyzwanie 3: "Tryb Switcher"
Zadaj to samo pytanie w 3 trybach - odpowiedzi powinny się różnić długością.

### Wyzwanie 4: "Ukryty Cel Unlocked"
Zadaj pytanie każdemu partnerowi tak, żeby odsłonił swój ukryty cel.

### Wyzwanie 5: "All vs One"
Zadaj pytanie do "Wszyscy" - dostaniesz 8 różnych perspektyw!

---

*Dokument wygenerowany: 2025-10-20*
*Dla użytkowników: Horyzont Partnerów Dashboard*
*Poziom trudności: Beginner → Advanced*
