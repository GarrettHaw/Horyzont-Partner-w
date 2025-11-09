"""
Animated Timeline - Wizualizacja ewolucji portfela w czasie
Wykorzystuje Plotly do tworzenia interaktywnych animowanych wykresów
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import webbrowser
import os


class AnimatedTimeline:
    """Generator animowanych wizualizacji timeline portfela"""
    
    def __init__(self, history_data: List[Dict[str, Any]]):
        """
        Inicjalizacja generatora timeline
        
        Args:
            history_data: Lista snapshots portfela
        """
        self.history = history_data
        self.df = self._prepare_dataframe()
    
    def _prepare_dataframe(self) -> pd.DataFrame:
        """Przygotuj DataFrame z danych historycznych"""
        if not self.history:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.history)
        
        # Konwertuj timestamp na datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        return df
    
    def create_animated_value_chart(self) -> go.Figure:
        """
        Utwórz animowany wykres wartości portfela
        
        Returns:
            Plotly Figure z animacją
        """
        if self.df.empty:
            return go.Figure()
        
        # Przygotuj dane dla animacji
        df = self.df.copy()
        df['cumulative_idx'] = range(len(df))
        
        fig = go.Figure()
        
        # Dodaj ślady dla każdego kroku animacji
        for i in range(1, len(df) + 1):
            visible = [False] * (len(df))
            visible[i-1] = True
            
            fig.add_trace(go.Scatter(
                x=df['timestamp'][:i],
                y=df['value'][:i],
                mode='lines+markers',
                name='Wartość Portfela (PLN)',
                line=dict(color='#2E86DE', width=3),
                marker=dict(size=8, color='#54A0FF'),
                fill='tozeroy',
                fillcolor='rgba(46, 134, 222, 0.1)',
                visible=(i == len(df))  # Tylko ostatni widoczny na start
            ))
        
        # Konfiguracja animacji
        steps = []
        for i in range(len(df)):
            step = dict(
                method="update",
                args=[{"visible": [False] * len(df)},
                      {"title": f"Wartość Portfela - {df.iloc[i]['date']}"}],
                label=str(df.iloc[i]['date'])
            )
            step["args"][0]["visible"][i] = True
            steps.append(step)
        
        sliders = [dict(
            active=len(df) - 1,
            yanchor="top",
            y=0.9,
            xanchor="left",
            x=0.1,
            currentvalue={
                "prefix": "Data: ",
                "visible": True,
                "xanchor": "center"
            },
            pad={"b": 10, "t": 50},
            len=0.9,
            steps=steps
        )]
        
        fig.update_layout(
            title="📈 Timeline Wartości Portfela",
            xaxis_title="Data",
            yaxis_title="Wartość (PLN)",
            sliders=sliders,
            hovermode='x unified',
            template='plotly_white',
            height=600,
            font=dict(size=12)
        )
        
        return fig
    
    def create_multi_metric_timeline(self) -> go.Figure:
        """
        Utwórz interaktywny timeline z wieloma metrykami
        
        Returns:
            Plotly Figure z subplots
        """
        if self.df.empty:
            return go.Figure()
        
        # Utwórz subplot z 3 wykresami
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('💰 Wartość Portfela', '📊 Dźwignia', '📈 Liczba Pozycji'),
            vertical_spacing=0.1,
            row_heights=[0.5, 0.25, 0.25]
        )
        
        # Wykres 1: Wartość portfela
        fig.add_trace(
            go.Scatter(
                x=self.df['timestamp'],
                y=self.df['value'],
                mode='lines+markers',
                name='Wartość (PLN)',
                line=dict(color='#2E86DE', width=2),
                fill='tozeroy',
                fillcolor='rgba(46, 134, 222, 0.1)'
            ),
            row=1, col=1
        )
        
        # Wykres 2: Dźwignia
        fig.add_trace(
            go.Scatter(
                x=self.df['timestamp'],
                y=self.df['leverage'],
                mode='lines+markers',
                name='Leverage %',
                line=dict(color='#FF6348', width=2),
                marker=dict(size=6)
            ),
            row=2, col=1
        )
        
        # Dodaj linię ostrzegawczą dla leverage (50%)
        fig.add_hline(y=50, line_dash="dash", line_color="red", 
                      annotation_text="⚠️ Limit", row=2, col=1)
        
        # Wykres 3: Liczba pozycji
        fig.add_trace(
            go.Bar(
                x=self.df['timestamp'],
                y=self.df['stocks_count'],
                name='Akcje',
                marker_color='#10AC84'
            ),
            row=3, col=1
        )
        
        if 'crypto_count' in self.df.columns:
            fig.add_trace(
                go.Bar(
                    x=self.df['timestamp'],
                    y=self.df['crypto_count'],
                    name='Krypto',
                    marker_color='#FFA502'
                ),
                row=3, col=1
            )
        
        # Layout
        fig.update_layout(
            title_text="🕐 Multi-Metric Timeline",
            showlegend=True,
            hovermode='x unified',
            template='plotly_white',
            height=900,
            font=dict(size=11)
        )
        
        fig.update_xaxes(title_text="Data", row=3, col=1)
        fig.update_yaxes(title_text="PLN", row=1, col=1)
        fig.update_yaxes(title_text="%", row=2, col=1)
        fig.update_yaxes(title_text="Liczba", row=3, col=1)
        
        return fig
    
    def create_growth_animation(self) -> go.Figure:
        """
        Utwórz animowany wykres wzrostu z efektem "wyrastania"
        
        Returns:
            Plotly Figure z animacją wzrostu
        """
        if self.df.empty:
            return go.Figure()
        
        # Oblicz procent zmiany
        if self.df['value'].iloc[0] != 0:
            self.df['growth_percent'] = ((self.df['value'] - self.df['value'].iloc[0]) / 
                                         self.df['value'].iloc[0] * 100)
        else:
            self.df['growth_percent'] = 0
        
        # Utwórz figure
        fig = px.line(
            self.df,
            x='timestamp',
            y='growth_percent',
            title='🚀 Wzrost Portfela od Początku (%)',
            labels={'growth_percent': 'Wzrost (%)', 'timestamp': 'Data'}
        )
        
        # Dostosuj wygląd
        fig.update_traces(
            line_color='#27AE60',
            line_width=3,
            mode='lines+markers'
        )
        
        # Dodaj linię 0%
        fig.add_hline(y=0, line_dash="dash", line_color="gray", 
                      annotation_text="Punkt startowy")
        
        # Koloruj obszar w zależności od zysku/straty
        fig.add_trace(go.Scatter(
            x=self.df['timestamp'],
            y=self.df['growth_percent'],
            fill='tozeroy',
            fillcolor='rgba(39, 174, 96, 0.2)',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def create_comparison_chart(self, benchmark_data: List[float] = None) -> go.Figure:
        """
        Porównaj portfel z benchmarkiem (np. S&P 500)
        
        Args:
            benchmark_data: Lista wartości benchmarku
        
        Returns:
            Plotly Figure z porównaniem
        """
        if self.df.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Normalizuj do 100 na początku
        portfolio_norm = (self.df['value'] / self.df['value'].iloc[0] * 100)
        
        fig.add_trace(go.Scatter(
            x=self.df['timestamp'],
            y=portfolio_norm,
            mode='lines',
            name='Twój Portfel',
            line=dict(color='#2E86DE', width=3)
        ))
        
        if benchmark_data and len(benchmark_data) == len(self.df):
            benchmark_norm = [b / benchmark_data[0] * 100 for b in benchmark_data]
            fig.add_trace(go.Scatter(
                x=self.df['timestamp'],
                y=benchmark_norm,
                mode='lines',
                name='Benchmark (S&P 500)',
                line=dict(color='#95A5A6', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title='📊 Portfel vs Benchmark (znormalizowane do 100)',
            xaxis_title='Data',
            yaxis_title='Wartość względna (100 = start)',
            template='plotly_white',
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def save_and_open(self, fig: go.Figure, filename: str = 'timeline.html') -> str:
        """
        Zapisz wykres do HTML i otwórz w przeglądarce
        
        Args:
            fig: Plotly Figure
            filename: Nazwa pliku wyjściowego
        
        Returns:
            Ścieżka do zapisanego pliku
        """
        filepath = os.path.abspath(filename)
        fig.write_html(filepath)
        
        # Otwórz w przeglądarce
        webbrowser.open('file://' + filepath)
        
        return filepath
    
    def generate_full_timeline_report(self) -> List[go.Figure]:
        """
        Wygeneruj kompletny raport timeline ze wszystkimi wykresami
        
        Returns:
            Lista wszystkich wykresów
        """
        figures = []
        
        if not self.df.empty:
            # Wykres 1: Multi-metric timeline
            figures.append(self.create_multi_metric_timeline())
            
            # Wykres 2: Wzrost procentowy
            figures.append(self.create_growth_animation())
            
            # Wykres 3: Animowany timeline wartości
            # figures.append(self.create_animated_value_chart())
        
        return figures


def display_timeline(history_data: List[Dict], open_browser: bool = True) -> None:
    """
    Wyświetl timeline dla użytkownika
    
    Args:
        history_data: Historia portfela
        open_browser: Czy otworzyć w przeglądarce
    """
    if not history_data:
        print("⚠️ Brak danych historycznych. Uruchom program kilka razy aby zgromadzić dane.")
        return
    
    print(f"📊 Generuję timeline z {len(history_data)} punktów danych...")
    
    timeline = AnimatedTimeline(history_data)
    figures = timeline.generate_full_timeline_report()
    
    if not figures:
        print("❌ Nie udało się wygenerować wykresów")
        return
    
    # Zapisz główny wykres
    filepath = timeline.save_and_open(figures[0], 'portfolio_timeline.html')
    print(f"✅ Timeline zapisany: {filepath}")
    
    # Zapisz wykres wzrostu
    if len(figures) > 1:
        growth_path = timeline.save_and_open(figures[1], 'portfolio_growth.html')
        print(f"✅ Wykres wzrostu zapisany: {growth_path}")
