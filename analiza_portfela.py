from typing import Dict, Any, List, Tuple
import datetime
from collections import defaultdict

def oblicz_statystyki_portfela(stan_spolki: Dict[str, Any]) -> Dict[str, Any]:
    """
    Oblicza szczegółowe statystyki portfela
    """
    portfel = stan_spolki['PORTFEL_AKCJI']
    
    # Podstawowe metryki
    total_value = portfel.get('Wartosc_total_USD', 0)
    invested_value = portfel.get('Zainwestowane_USD', 0)
    total_gain_loss = total_value - invested_value
    
    # Analiza sektorowa
    sektory = defaultdict(float)
    for pozycja in portfel.get('Pozycje', []):
        sektor = pozycja.get('Sektor', 'Nieznany')
        wartosc = pozycja.get('Wartosc_total_USD', 0)
        sektory[sektor] += wartosc
    
    # Obliczanie koncentracji
    pozycje = portfel.get('Pozycje', [])
    sorted_pozycje = sorted(pozycje, key=lambda x: x.get('Wartosc_total_USD', 0), reverse=True)
    top_5_koncentracja = sum(p.get('Wartosc_total_USD', 0) for p in sorted_pozycje[:5]) / total_value if total_value else 0
    
    # Ryzyko
    ryzyko = {
        'Koncentracja_top_5': top_5_koncentracja,
        'Liczba_pozycji': len(pozycje),
        'Srednia_wartosc_pozycji': total_value / len(pozycje) if pozycje else 0
    }
    
    return {
        'Statystyki_podstawowe': {
            'Wartosc_calkowita_USD': total_value,
            'Zainwestowane_USD': invested_value,
            'Zysk_strata_USD': total_gain_loss,
            'Zwrot_procentowy': (total_gain_loss / invested_value * 100) if invested_value else 0
        },
        'Analiza_sektorowa': dict(sektory),
        'Ryzyko': ryzyko,
        'Data_analizy': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generuj_rekomendacje(statystyki: Dict[str, Any]) -> List[str]:
    """
    Generuje rekomendacje na podstawie analizy portfela
    """
    rekomendacje = []
    
    # 1. Dywersyfikacja sektorowa
    sektory = statystyki['Analiza_sektorowa']
    max_sektor = max(sektory.items(), key=lambda x: x[1])
    if max_sektor[1] / statystyki['Statystyki_podstawowe']['Wartosc_calkowita_USD'] > 0.3:
        rekomendacje.append(
            f"⚠️ Wysoka koncentracja w sektorze {max_sektor[0]} ({max_sektor[1]:.1f}%). "
            "Rozważ dywersyfikację do innych sektorów."
        )
    
    # 2. Koncentracja pozycji
    if statystyki['Ryzyko']['Koncentracja_top_5'] > 0.5:
        rekomendacje.append(
            "⚠️ Wysoka koncentracja w top 5 pozycjach (>50% portfela). "
            "Rozważ redystrybucję kapitału dla lepszej dywersyfikacji."
        )
    
    # 3. Liczba pozycji
    if statystyki['Ryzyko']['Liczba_pozycji'] < 10:
        rekomendacje.append(
            "💡 Mała liczba pozycji w portfelu. "
            "Rozważ dodanie więcej pozycji dla lepszej dywersyfikacji."
        )
    elif statystyki['Ryzyko']['Liczba_pozycji'] > 30:
        rekomendacje.append(
            "💡 Duża liczba pozycji w portfelu. "
            "Rozważ konsolidację mniejszych pozycji dla lepszej efektywności zarządzania."
        )
    
    # 4. Zwrot z inwestycji
    roi = statystyki['Statystyki_podstawowe']['Zwrot_procentowy']
    if roi < -10:
        rekomendacje.append(
            "⚠️ Znacząca strata w portfelu. "
            "Przeanalizuj przyczyny strat i rozważ rebalancing portfela."
        )
    elif roi > 20:
        rekomendacje.append(
            "💡 Wysoki zwrot z inwestycji. "
            "Rozważ częściową realizację zysków lub rebalancing dla zachowania proporcji."
        )
    
    return rekomendacje

def przeprowadz_analize_portfela(stan_spolki: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Przeprowadza pełną analizę portfela i generuje rekomendacje
    """
    statystyki = oblicz_statystyki_portfela(stan_spolki)
    rekomendacje = generuj_rekomendacje(statystyki)
    
    return statystyki, rekomendacje

def wyswietl_raport_analizy(statystyki: Dict[str, Any], rekomendacje: List[str]) -> None:
    """
    Wyświetla sformatowany raport z analizy portfela
    """
    print("\n" + "="*80)
    print("📊 RAPORT ANALIZY PORTFELA")
    print("="*80)
    
    # 1. Podstawowe statystyki
    print("\n📈 STATYSTYKI PODSTAWOWE:")
    podstawowe = statystyki['Statystyki_podstawowe']
    print(f"- Wartość całkowita: ${podstawowe['Wartosc_calkowita_USD']:,.2f}")
    print(f"- Zainwestowane: ${podstawowe['Zainwestowane_USD']:,.2f}")
    print(f"- Zysk/Strata: ${podstawowe['Zysk_strata_USD']:,.2f} ({podstawowe['Zwrot_procentowy']:.1f}%)")
    
    # 2. Analiza sektorowa
    print("\n📊 ANALIZA SEKTOROWA:")
    for sektor, wartosc in sorted(statystyki['Analiza_sektorowa'].items(), key=lambda x: x[1], reverse=True):
        procent = (wartosc / podstawowe['Wartosc_calkowita_USD'] * 100)
        print(f"- {sektor}: ${wartosc:,.2f} ({procent:.1f}%)")
    
    # 3. Metryki ryzyka
    print("\n⚠️ METRYKI RYZYKA:")
    ryzyko = statystyki['Ryzyko']
    print(f"- Koncentracja top 5: {ryzyko['Koncentracja_top_5']*100:.1f}%")
    print(f"- Liczba pozycji: {ryzyko['Liczba_pozycji']}")
    print(f"- Średnia wartość pozycji: ${ryzyko['Srednia_wartosc_pozycji']:,.2f}")
    
    # 4. Rekomendacje
    if rekomendacje:
        print("\n💡 REKOMENDACJE:")
        for rek in rekomendacje:
            print(f"- {rek}")
    
    print("\n" + "="*80)
    print(f"🕒 Data analizy: {statystyki['Data_analizy']}")
    print("="*80 + "\n")