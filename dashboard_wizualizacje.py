import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, List, Any, Tuple

def utworz_wizualizacje_portfela(stan_spolki: Dict[str, Any]) -> List[go.Figure]:
    """
    Tworzy zestaw interaktywnych wizualizacji dla portfela
    """
    wykresy = []
    print("\n🔄 Generuję wykresy dla dashboardu...")
    
    # 1. Wykres alokacji aktywów (donut chart)
    print("💰 Generuję wykres alokacji aktywów...")
    # Pobieramy kurs USD
    kurs_usd = stan_spolki.get('Kurs_USD_PLN', 1)
    
    # Pobieramy wartości w PLN z odpowiednich miejsc w strukturze
    podsumowanie = stan_spolki.get('PODSUMOWANIE', {})
    
    akcje_pln = stan_spolki['PORTFEL_AKCJI'].get('Suma_PLN', 0)
    krypto_total_usd = stan_spolki.get('PORTFEL_KRYPTO', {}).get('Suma_USD', 0)
    gotowka_pln = podsumowanie.get('Gotowka_PLN', 0)
    
    # Konwertujemy wszystko na USD dla spójności
    akcje_usd = akcje_pln / kurs_usd
    krypto_usd = krypto_total_usd
    gotowka_usd = gotowka_pln / kurs_usd
    
    # Dodajemy wartości do opisu dla lepszej czytelności
    labels = [
        f'Akcje (${akcje_usd:,.2f})',
        f'Krypto (${krypto_usd:,.2f})',
        f'Gotówka (${gotowka_usd:,.2f})'
    ]
    
    values = [akcje_usd, krypto_usd, gotowka_usd]
    total_usd = sum(values)
    
    # Obliczamy procenty dla każdej kategorii
    percentages = [f"{(v/total_usd*100):.1f}%" if total_usd > 0 else "0%" for v in values]
    
    # Łączymy etykiety z procentami
    labels = [f"{l} ({p})" for l, p in zip(labels, percentages)]
    print("✅ Dane alokacji aktywów przetworzone")
    
    # Kolory dla różnych typów aktywów
    colors = ['#2ecc71', '#f1c40f', '#3498db']
    
    fig_alokacja = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker=dict(colors=colors),
        textinfo='label',
        textposition='outside',
        title='Alokacja Aktywów'
    )])
    
    # Dodajemy całkowitą wartość portfela w środku wykresu
    fig_alokacja.update_layout(
        title=dict(
            text='Struktura Portfela',
            x=0.5,
            y=0.95,
            xanchor='center',
            yanchor='top',
            font=dict(size=24)
        ),
        annotations=[dict(
            text=f'Suma\n${total_usd:,.2f}',
            x=0.5,
            y=0.5,
            font=dict(size=20),
            showarrow=False
        )],
        showlegend=True,
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    wykresy.append(fig_alokacja)
    print("✅ Wykres alokacji aktywów wygenerowany")
    
    # 2. Wykres top 10 pozycji (treemap)
    try:
        if stan_spolki['PORTFEL_AKCJI'].get('Pozycje'):
            print("📊 Generuję mapę drzewa top 10 pozycji...")
            df_pozycje = pd.DataFrame(stan_spolki['PORTFEL_AKCJI']['Pozycje'])
            # Konwertujemy wartości na USD
            kurs_usd = stan_spolki.get('Kurs_USD_PLN', 1)
            if 'Wartosc_PLN' in df_pozycje.columns:
                df_pozycje['Wartosc_USD'] = df_pozycje['Wartosc_PLN'] / kurs_usd
            else:
                df_pozycje['Wartosc_USD'] = df_pozycje['Wartosc_total_USD']
            
            df_pozycje = df_pozycje.sort_values('Wartosc_USD', ascending=False).head(10)
            
            fig_top10 = px.treemap(
                df_pozycje,
                path=[px.Constant("Portfolio"), df_pozycje.get('Sektor', 'Ticker'), 'Ticker'],
                values='Wartosc_USD',
                title='Top 10 Pozycji w Portfelu (USD)'
            )
            wykresy.append(fig_top10)
            print("✅ Mapa drzewa wygenerowana")
    except Exception as e:
        print(f"⚠️ Nie udało się wygenerować mapy drzewa: {e}")
    
    # 3. Porównanie z benchmarkiem (linia)
    print("📈 Generuję wykres porównawczy z benchmarkiem...")
    try:
        fig_benchmark = go.Figure()
        
        # Generujemy przykładowe dane benchmarkowe
        dates = pd.date_range(end=pd.Timestamp.now(), periods=252, freq='B')
        benchmark_return = pd.Series(index=dates, data=[100 * (1 + 0.0003 * i + np.random.normal(0, 0.01)) for i in range(252)])
        
        fig_benchmark.add_trace(go.Scatter(
            x=dates,
            y=benchmark_return,
            name='S&P 500 (symulowane)',
            line=dict(color='blue', dash='dash')
        ))
        
        # Dodaj symulowaną linię portfela dla porównania
        portfolio_return = pd.Series(index=dates, data=[100 * (1 + 0.0004 * i + np.random.normal(0, 0.015)) for i in range(252)])
        
        fig_benchmark.add_trace(go.Scatter(
            x=dates,
            y=portfolio_return,
            name='Nasz Portfel (symulowane)',
            line=dict(color='green')
        ))
        
        fig_benchmark.update_layout(
            title='Symulowane Porównanie z Benchmarkiem',
            xaxis_title='Data',
            yaxis_title='Wartość Zindeksowana (100 = początek)',
            hovermode='x unified',
            showlegend=True
        )
        wykresy.append(fig_benchmark)
        print("✅ Wykres porównawczy wygenerowany")
    except Exception as e:
        print(f"⚠️ Nie udało się wygenerować wykresu porównawczego: {e}")
    
    # 4. Analiza sektorowa (wykres słupkowy + pie chart)
    print("📊 Generuję analizę sektorową...")
    
    # Pobierz dane akcji z arkusza (dostępne w szczegółach tabeli)
    szczegoly_tabela = stan_spolki['PORTFEL_AKCJI'].get('Szczegoly_tabela', [])
    
    if szczegoly_tabela:
        # Utwórz DataFrame z danych
        headers = szczegoly_tabela[0]
        data = szczegoly_tabela[1:]
        df = pd.DataFrame(data, columns=headers)
        
        # Znajdź kolumny z sektorem i wartością
        sektor_col = next((col for col in df.columns if 'sektor' in col.lower()), None)
        wartosc_col = next((col for col in df.columns if 'wartość' in col.lower() or 'wartosc' in col.lower()), None)
        
        if sektor_col and wartosc_col:
            # Konwertuj wartości na liczby
            df[wartosc_col] = pd.to_numeric(df[wartosc_col].str.replace(',', '.'), errors='coerce')
            
            # Grupuj po sektorach
            df_sektory = df.groupby(sektor_col)[wartosc_col].sum().reset_index()
            df_sektory = df_sektory.sort_values(wartosc_col, ascending=True)  # Sortuj rosnąco
            
            # Konwertuj na USD
            kurs_usd = stan_spolki.get('Kurs_USD_PLN', 1)
            df_sektory['Wartosc_USD'] = df_sektory[wartosc_col] / kurs_usd
            
            # Oblicz procenty
            total = df_sektory['Wartosc_USD'].sum()
            df_sektory['Procent'] = (df_sektory['Wartosc_USD'] / total * 100).round(1)
            
            # Stwórz wykres
            fig_sektory = sp.make_subplots(
                rows=1, cols=2,
                subplot_titles=(
                    'Alokacja Sektorowa (USD)',
                    'Alokacja Sektorowa (%)'
                ),
                specs=[[{"type": "bar"}, {"type": "pie"}]],
                horizontal_spacing=0.1
            )
            
            # Wykres słupkowy
            fig_sektory.add_trace(
                go.Bar(
                    y=df_sektory[sektor_col],
                    x=df_sektory['Wartosc_USD'],
                    orientation='h',
                    text=[f'${x:,.0f}' for x in df_sektory['Wartosc_USD']],
                    textposition='auto',
                    marker_color='#2ecc71'
                ),
                row=1, col=1
            )
            
            # Wykres kołowy
            fig_sektory.add_trace(
                go.Pie(
                    labels=df_sektory[sektor_col],
                    values=df_sektory['Wartosc_USD'],
                    textinfo='label+percent',
                    hole=.3,
                    marker=dict(
                        colors=px.colors.qualitative.Set3
                    )
                ),
                row=1, col=2
            )
            
            # Aktualizuj layout
            fig_sektory.update_layout(
                height=700,
                title={
                    'text': "Analiza Sektorowa Portfela",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=24)
                },
                showlegend=False,
                annotations=[
                    dict(
                        text=f'Suma: ${total:,.2f}',
                        x=0.5,
                        y=-0.15,
                        showarrow=False,
                        xref='paper',
                        yref='paper',
                        font=dict(size=16)
                    )
                ]
            )
            
            # Aktualizuj osie wykresu słupkowego
            fig_sektory.update_xaxes(title_text="Wartość (USD)", row=1, col=1)
            
            wykresy.append(fig_sektory)
            print("✅ Analiza sektorowa wygenerowana")
        else:
            print("⚠️ Nie znaleziono kolumn z sektorem lub wartością w danych")
    
    # 5. Wykres zmian wartości portfela w czasie
    try:
        print("📈 Generuję wykres wartości portfela w czasie...")
        # Generujemy przykładowe dane historyczne
        dates = pd.date_range(end=pd.Timestamp.now(), periods=365, freq='D')
        initial_value = stan_spolki['PODSUMOWANIE']['Wartosc_netto_USD']
        
        # Symulujemy historyczne wartości z trendem wzrostowym i zmiennością
        trend = np.linspace(0.8 * initial_value, initial_value, len(dates))
        noise = np.random.normal(0, initial_value * 0.02, len(dates))
        values = trend + noise
        
        df_historia = pd.DataFrame({
            'data': dates,
            'wartosc': values
        }).set_index('data')
        
        fig_trendy = go.Figure()
        
        # Główna linia wartości
        fig_trendy.add_trace(go.Scatter(
            x=df_historia.index,
            y=df_historia['wartosc'],
            name='Wartość Portfela',
            line=dict(color='blue'),
            fill='tonexty'  # Dodaje wypełnienie pod linią
        ))
        
        # Linia trendu
        z = np.polyfit(range(len(df_historia)), df_historia['wartosc'], 1)
        p = np.poly1d(z)
        fig_trendy.add_trace(go.Scatter(
            x=df_historia.index,
            y=p(range(len(df_historia))),
            name='Trend',
            line=dict(color='red', dash='dash')
        ))
        
        # Formatowanie wykresu
        fig_trendy.update_layout(
            title='Symulowana Historia Wartości Portfela',
            xaxis_title='Data',
            yaxis_title='Wartość (USD)',
            hovermode='x unified',
            showlegend=True,
            height=500
        )
        
        wykresy.append(fig_trendy)
        print("✅ Wykres wartości portfela wygenerowany")
    except Exception as e:
        print(f"⚠️ Nie udało się wygenerować wykresu wartości portfela: {e}")
    
    return wykresy

def format_currency(value: float, currency: str = 'USD') -> str:
    """Formatuje wartość waluty w czytelny sposób"""
    if abs(value) >= 1_000_000:
        return f"{currency} {value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{currency} {value/1_000:.1f}K"
    else:
        return f"{currency} {value:.2f}"

def generuj_podsumowanie_liczbowe(stan_spolki: Dict[str, Any]) -> str:
    """
    Generuje tekstowe podsumowanie najważniejszych metryk
    """
    kurs_usd = stan_spolki.get('Kurs_USD_PLN', 1)
    podsumowanie = stan_spolki.get('PODSUMOWANIE', {})
    
    wartosc_netto_pln = podsumowanie.get('Wartosc_netto_PLN', 0)
    wartosc_netto_usd = podsumowanie.get('Wartosc_netto_USD', 0)
    leverage = podsumowanie.get('Leverage_ratio', 0)
    
    portfel_akcji = stan_spolki.get('PORTFEL_AKCJI', {})
    portfel_krypto = stan_spolki.get('PORTFEL_KRYPTO', {})
    
    liczba_pozycji_akcje = len(portfel_akcji.get('Pozycje', [])) if isinstance(portfel_akcji.get('Pozycje'), list) else portfel_akcji.get('Liczba_pozycji', 0)
    liczba_pozycji_krypto = portfel_krypto.get('Liczba_pozycji', 0)
    
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: #2c3e50; margin-bottom: 20px;">📊 Podsumowanie Portfela</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="color: #34495e; margin-top: 0;">💰 Wartość Netto</h3>
                <div style="font-size: 1.2em; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                        <span>PLN:</span>
                        <strong>{format_currency(wartosc_netto_pln, 'PLN')}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                        <span>USD:</span>
                        <strong>{format_currency(wartosc_netto_usd, '$')}</strong>
                    </div>
                </div>
            </div>
            <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="color: #34495e; margin-top: 0;">📈 Metryki Portfela</h3>
                <div style="font-size: 1.2em; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                        <span>Pozycje akcyjne:</span>
                        <strong>{liczba_pozycji_akcje}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                        <span>Pozycje krypto:</span>
                        <strong>{liczba_pozycji_krypto}</strong>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                        <span>Dźwignia:</span>
                        <strong>{leverage:.1f}%</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    return html

def wyswietl_dashboard(stan_spolki: Dict[str, Any]) -> None:
    """
    Generuje i wyświetla interaktywny dashboard
    """
    print("\n" + "="*80)
    print("📊 ZAAWANSOWANY DASHBOARD PORTFELA")
    print("="*80)
    
    wykresy = utworz_wizualizacje_portfela(stan_spolki)
    
    # Tworzymy jeden plik HTML z wszystkimi wykresami
    html_content = """
    <html>
    <head>
        <title>Dashboard Inwestycyjny</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f0f2f5; }
            .tab { display: none; }
            .tab-active { display: block; }
            .tab-buttons { margin-bottom: 20px; }
            .tab-button {
                padding: 10px 20px;
                margin-right: 5px;
                border: none;
                background-color: #ddd;
                cursor: pointer;
                border-radius: 5px;
            }
            .tab-button.active {
                background-color: #2c3e50;
                color: white;
            }
        </style>
        <script>
            function showTab(tabName) {
                // Ukryj wszystkie taby
                var tabs = document.getElementsByClassName('tab');
                for(var i = 0; i < tabs.length; i++) {
                    tabs[i].style.display = 'none';
                }
                
                // Usuń klasę active ze wszystkich przycisków
                var buttons = document.getElementsByClassName('tab-button');
                for(var i = 0; i < buttons.length; i++) {
                    buttons[i].classList.remove('active');
                }
                
                // Pokaż wybrany tab i aktywuj przycisk
                document.getElementById(tabName).style.display = 'block';
                document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
            }
        </script>
    </head>
    <body>
    """
    
    # Dodaj podsumowanie liczbowe
    html_content += generuj_podsumowanie_liczbowe(stan_spolki)
    
    # Dodaj przyciski do przełączania między wykresami
    html_content += '<div class="tab-buttons">'
    nazwy_wykresow = ['Alokacja Aktywów', 'Porównanie z Benchmarkiem', 'Analiza Sektorowa', 'Historia Wartości']
    for i, nazwa in enumerate(nazwy_wykresow):
        active = ' active' if i == 0 else ''
        html_content += f'<button class="tab-button{active}" onclick="showTab(\'tab{i+1}\')">{nazwa}</button>'
    html_content += '</div>'
    
    # Dodaj wykresy jako taby
    for i, wykres in enumerate(wykresy):
        display = 'block' if i == 0 else 'none'
        html_content += f'<div id="tab{i+1}" class="tab" style="display: {display}">'
        html_content += wykres.to_html(full_html=False, include_plotlyjs='cdn')
        html_content += '</div>'
    
    html_content += """
    </body>
    </html>
    """
    
    # Zapisz kompletny dashboard do jednego pliku
    nazwa_pliku = 'dashboard_inwestycyjny.html'
    with open(nazwa_pliku, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✨ Wygenerowano dashboard: {nazwa_pliku}")
    
    # Automatycznie otwórz dashboard w przeglądarce
    import webbrowser
    try:
        print("\n🌐 Otwieram dashboard w przeglądarce...")
        webbrowser.open(nazwa_pliku)
    except Exception as e:
        print(f"\n⚠️ Nie udało się automatycznie otworzyć przeglądarki: {e}")
        print("💡 Otwórz plik HTML ręcznie w swojej przeglądarce")
    
    print("="*80)