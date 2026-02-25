# -*- coding: utf-8 -*-
"""Generiert Grafiken aus dem Swissvotes-Datensatz."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Deutsche Schrift
plt.rcParams['font.family'] = 'DejaVu Sans'

df = pd.read_excel('DATASET XLSX 11-02-2026.xlsx', sheet_name='DATA')

HAUPTGRUPPEN = {
    1: 'Staatsordnung',
    2: 'Aussenpolitik',
    3: 'Sicherheitspolitik',
    4: 'Wirtschaft',
    5: 'Landwirtschaft',
    6: 'Öffentliche Finanzen',
    7: 'Energie',
    8: 'Verkehr und Infrastruktur',
    9: 'Umwelt und Lebensraum',
    10: 'Sozial- und Gesellschaftspolitik',
    11: 'Bildung und Forschung',
    12: 'Kultur, Religion, Medien'
}

RECHTSFORM = {
    1: 'Obligatorisches Referendum',
    2: 'Fakultatives Referendum',
    3: 'Volksinitiative',
    4: 'Direkter Gegenentwurf',
    5: 'Stichfrage'
}

def get_hg(val):
    if pd.isna(val) or val == '.' or val == '':
        return None
    try:
        num = int(float(val))
        return num if 1 <= num <= 12 else None
    except:
        return None

# 1. Haeufigkeit Hauptgruppen
counts = {i: 0 for i in range(1, 13)}
for _, row in df.iterrows():
    seen = set()
    for col in ['d1e1', 'd2e1', 'd3e1']:
        if col in df.columns:
            hg = get_hg(row[col])
            if hg and hg not in seen:
                counts[hg] += 1
                seen.add(hg)

fig, ax = plt.subplots(figsize=(12, 6))
labels = [HAUPTGRUPPEN[i] for i in range(1, 13)]
values = [counts[i] for i in range(1, 13)]
colors = plt.cm.Blues([0.3 + 0.6 * (v/max(values)) for v in values])
bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1])
ax.set_xlabel('Anzahl Abstimmungen')
ax.set_title('Haeufigkeit der Hauptgruppen (Politikbereiche)\nSwissvotes 1848-2026, n=708')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('chart_hauptgruppen.png', dpi=150, bbox_inches='tight')
plt.close()
print('Gespeichert: chart_hauptgruppen.png')

# 2. Annahme-Statistik
annahme = df['annahme'].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
v_abgelehnt = annahme.get(0, 0) + annahme.get(0.0, 0)
v_angenommen = annahme.get(1, 0) + annahme.get(1.0, 0)
v_rest = len(df) - v_abgelehnt - v_angenommen
vals = [v_abgelehnt, v_angenommen, max(0, v_rest)]
labels = ['Abgelehnt', 'Angenommen', 'Ohne Ergebnis']
colors = ['#e74c3c', '#27ae60', '#95a5a6']
ax.pie(vals, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
ax.set_title('Abstimmungsergebnisse (Annahme vs. Ablehnung)\nSwissvotes 1848-2026')
plt.tight_layout()
plt.savefig('chart_annahme.png', dpi=150, bbox_inches='tight')
plt.close()
print('Gespeichert: chart_annahme.png')

# 3. Rechtsform
rechtsform = df['rechtsform'].value_counts()
fig, ax = plt.subplots(figsize=(10, 5))
labels = [RECHTSFORM.get(int(k), str(k)) for k in rechtsform.index]
ax.bar(labels, rechtsform.values, color=plt.cm.viridis([0.2, 0.4, 0.6, 0.8, 1.0][:len(labels)]))
ax.set_ylabel('Anzahl')
ax.set_title('Verteilung nach Rechtsform\nSwissvotes 1848-2026')
plt.xticks(rotation=25, ha='right')
plt.tight_layout()
plt.savefig('chart_rechtsform.png', dpi=150, bbox_inches='tight')
plt.close()
print('Gespeichert: chart_rechtsform.png')

# 4. Bundesrat-Uebereinstimmung nach Hauptgruppen
# br-pos: 1=Befuerwortend, 2=Ablehnend, 3=Keine, 8=Gegenentwurf, 9=Initiative
# annahme: 0=Abgelehnt, 1=Angenommen, 8=Gegenentwurf, 9=Initiative
def get_br_val(val):
    if pd.isna(val) or val == '.' or val == '':
        return None
    try:
        return int(float(val))
    except:
        return None

def uebereinstimmung_br(br_pos, annahme):
    """True wenn Volk der Bundesratsempfehlung gefolgt ist."""
    br = get_br_val(br_pos)
    an = get_br_val(annahme)
    if br is None or an is None:
        return None
    if br == 3:  # Keine Empfehlung
        return None
    if br == 1 and an == 1: return True   # BR befuerwortete, angenommen
    if br == 2 and an == 0: return True   # BR lehnte ab, abgelehnt
    if br == 8 and an == 8: return True   # BR Gegenentwurf, Gegenentwurf gewann
    if br == 9 and an == 9: return True   # BR Initiative, Initiative gewann
    if br in (1, 2, 8, 9):
        return False
    return None

df['uebereinstimmung_br'] = df.apply(
    lambda r: uebereinstimmung_br(r.get('br-pos'), r.get('annahme')), axis=1
)
df_br = df[df['uebereinstimmung_br'].notna()].copy()

# Nach Hauptgruppe (d1e1 = primaerer Politikbereich)
hg_ueber = {i: {'ja': 0, 'nein': 0} for i in range(1, 13)}
for _, row in df_br.iterrows():
    hg = get_hg(row.get('d1e1'))
    if hg:
        if row['uebereinstimmung_br']:
            hg_ueber[hg]['ja'] += 1
        else:
            hg_ueber[hg]['nein'] += 1

# Tabelle und Grafik
rows_table = []
for i in range(1, 13):
    ja, nein = hg_ueber[i]['ja'], hg_ueber[i]['nein']
    total = ja + nein
    if total > 0:
        pct = round(100 * ja / total, 1)
    else:
        pct = 0
    rows_table.append((HAUPTGRUPPEN[i], ja, nein, total, pct))

# Sortieren nach Gesamtzahl (absteigend)
rows_table.sort(key=lambda x: x[3], reverse=True)

# Grafik: Gestapeltes Balkendiagramm
fig, ax = plt.subplots(figsize=(12, 7))
labels = [r[0] for r in rows_table]
ja_vals = [r[1] for r in rows_table]
nein_vals = [r[2] for r in rows_table]
x = range(len(labels))
ax.barh(x, ja_vals, label='Volk folgte Bundesrat', color='#27ae60')
ax.barh(x, nein_vals, left=ja_vals, label='Volk folgte nicht', color='#e74c3c')
ax.set_yticks(x)
ax.set_yticklabels(labels, fontsize=9)
ax.set_xlabel('Anzahl Abstimmungen')
ax.set_title('Übereinstimmung Volk – Bundesratsempfehlung nach Hauptgruppe\n(Swissvotes 1848–2026, nur Vorlagen mit klarer BR-Position)')
ax.legend(loc='lower right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('chart_bundesrat_uebereinstimmung.png', dpi=150, bbox_inches='tight')
plt.close()
print('Gespeichert: chart_bundesrat_uebereinstimmung.png')

# CSV-Tabelle speichern fuer HTML-Integration
with open('bundesrat_uebereinstimmung.csv', 'w', encoding='utf-8') as f:
    f.write('Hauptgruppe;Gefolgt;Nicht gefolgt;Total;Anteil gefolgt (%)\n')
    for r in rows_table:
        f.write(f'{r[0]};{r[1]};{r[2]};{r[3]};{r[4]}\n')
print('Gespeichert: bundesrat_uebereinstimmung.csv')

# 5. Liniendiagramm: Anteil angenommen in % pro 4-Jahresperiode, pro Hauptgruppe
df['datum_parsed'] = pd.to_datetime(df['datum'], errors='coerce')
df['jahr'] = df['datum_parsed'].dt.year

def is_angenommen(val):
    if pd.isna(val) or val == '.' or val == '':
        return None
    try:
        v = int(float(val))
        return v in (1, 8, 9)  # 1=Angenommen, 8/9=Stichfrage (Gewinner)
    except:
        return None

for hg_id, hg_name in HAUPTGRUPPEN.items():
    rows_hg = []
    for _, row in df.iterrows():
        if get_hg(row.get('d1e1')) != hg_id:
            continue
        jahr = row.get('jahr')
        if pd.isna(jahr) or jahr < 1848 or jahr > 2030:
            continue
        an = is_angenommen(row.get('annahme'))
        if an is not None:
            jahr_4 = int(jahr) // 4 * 4  # 4-Jahresperiode: 1848, 1852, 1856, ...
            rows_hg.append({'jahr_4': jahr_4, 'angenommen': an})

    if not rows_hg:
        continue
    df_hg = pd.DataFrame(rows_hg)
    by_period = df_hg.groupby('jahr_4').agg(
        total=('angenommen', 'count'),
        angenommen=('angenommen', 'sum')
    ).reset_index()
    by_period['pct'] = 100 * by_period['angenommen'] / by_period['total']
    by_period['label'] = by_period['jahr_4'].astype(str) + '–' + (by_period['jahr_4'] + 3).astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(by_period['jahr_4'], by_period['pct'], 'o-', color='#2874a6', linewidth=2, markersize=4)
    ax.set_xticks(by_period['jahr_4'])
    ax.set_xticklabels(by_period['label'], rotation=45, ha='right')
    ax.set_xlabel('4-Jahresperiode')
    ax.set_ylabel('Anteil angenommen (%)')
    ax.set_title(f'Anteil angenommener Vorlagen nach 4-Jahresperiode\n{hg_name} (Swissvotes 1848–2026)')
    ax.set_ylim(0, 100)
    ax.axhline(y=50, color='#bdc3c7', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fname = f'chart_annahme_hg{hg_id:02d}.png'
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Gespeichert: {fname}')

# 5b. Gestapeltes Balkendiagramm: Bundesrat-Uebereinstimmung pro 4-Jahresperiode, pro Hauptgruppe
for hg_id, hg_name in HAUPTGRUPPEN.items():
    rows_br = []
    for _, row in df.iterrows():
        if get_hg(row.get('d1e1')) != hg_id:
            continue
        if row.get('uebereinstimmung_br') is None or pd.isna(row.get('uebereinstimmung_br')):
            continue
        jahr = row.get('jahr')
        if pd.isna(jahr) or jahr < 1848 or jahr > 2030:
            continue
        jahr_4 = int(jahr) // 4 * 4
        gefolgt = 1 if row['uebereinstimmung_br'] else 0
        rows_br.append({'jahr_4': jahr_4, 'gefolgt': gefolgt})

    if not rows_br:
        continue
    df_br_hg = pd.DataFrame(rows_br)
    by_period = df_br_hg.groupby('jahr_4').agg(
        gefolgt=('gefolgt', 'sum'),
        total=('gefolgt', 'count')
    ).reset_index()
    by_period['nicht_gefolgt'] = by_period['total'] - by_period['gefolgt']
    by_period['gefolgt_pct'] = 100 * by_period['gefolgt'] / by_period['total']
    by_period['nicht_gefolgt_pct'] = 100 * by_period['nicht_gefolgt'] / by_period['total']
    by_period['label'] = by_period['jahr_4'].astype(str) + '–' + (by_period['jahr_4'] + 3).astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = range(len(by_period))
    ax.bar(x_pos, by_period['gefolgt_pct'], label='Gefolgt', color='#27ae60')
    ax.bar(x_pos, by_period['nicht_gefolgt_pct'], bottom=by_period['gefolgt_pct'], label='Nicht gefolgt', color='#e74c3c')
    # n-Beschriftung pro Balken
    for i, (_, row) in enumerate(by_period.iterrows()):
        ax.text(i, 102, f"n={int(row['total'])}", ha='center', va='bottom', fontsize=8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(by_period['label'], rotation=45, ha='right')
    ax.set_xlabel('4-Jahresperiode')
    ax.set_ylabel('Anteil (%)')
    ax.set_ylim(0, 115)
    ax.set_title(f'Bundesratsempfehlung: Gefolgt vs. nicht gefolgt nach 4-Jahresperiode\n{hg_name} (Swissvotes 1848–2026)')
    ax.legend(loc='upper right')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    fname = f'chart_bundesrat_hg{hg_id:02d}.png'
    plt.savefig(fname, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Gespeichert: {fname}')

# 6. Abstimmungen pro Jahrzehnt
df_clean = df[df['jahr'].notna() & (df['jahr'] >= 1848) & (df['jahr'] <= 2025)].copy()
df_clean['jahrzehnt'] = (df_clean['jahr'] // 10) * 10
decade_counts = df_clean.groupby('jahrzehnt').size()

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(decade_counts.index.astype(int), decade_counts.values, color='#3498db', edgecolor='white')
ax.set_xlabel('Jahrzehnt')
ax.set_ylabel('Anzahl Abstimmungen')
ax.set_title('Eidgenoessische Abstimmungen pro Jahrzehnt\nSwissvotes 1848-2025')
ax.set_xticks(decade_counts.index.astype(int))
plt.tight_layout()
plt.savefig('chart_jahrzehnt.png', dpi=150, bbox_inches='tight')
plt.close()
print('Gespeichert: chart_jahrzehnt.png')

# 7. Wortanalyse (titel_kurz_d + stichwort)
import re
from collections import Counter

STOPWORDS = {'der', 'die', 'das', 'und', 'den', 'dem', 'des', 'ein', 'eine', 'einer', 'eines',
             'für', 'von', 'zu', 'mit', 'auf', 'bei', 'nach', 'aus', 'im', 'in', 'an', 'am',
             'als', 'oder', 'bis', 'durch', 'gegen', 'ohne', 'um', 'über', 'unter', 'vor',
             'sich', 'ist', 'sind', 'war', 'waren', 'wird', 'werden', 'hat', 'haben', 'had',
             'kann', 'können', 'soll', 'sollen', 'muss', 'müssen', 'wird', 'werden',
             'des', 'dem', 'den', 'einem', 'einen', 'einer', 'dieser', 'diese', 'dieses',
             'jeder', 'jede', 'jedem', 'allen', 'alle', 'allem', 'beim', 'zum', 'zur',
             'art', 'abs', 'bzw', 'bge', 'bv', 'nr', 'zgb', 'stgb', 'etc', 'ev', 'uvm'}

def extract_words(text):
    if pd.isna(text) or text == '.' or str(text).strip() == '':
        return []
    s = str(text).lower()
    words = re.findall(r'[a-zA-ZäöüÄÖÜß]+', s)
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]

all_words = []
for _, row in df.iterrows():
    for col in ['titel_kurz_d', 'stichwort']:
        if col in df.columns:
            all_words.extend(extract_words(row.get(col)))

word_freq = Counter(all_words)
top_words = word_freq.most_common(30)

# Grafik: Top 20 Woerter
fig, ax = plt.subplots(figsize=(10, 7))
words_plot = [w[0] for w in top_words[:20]]
counts_plot = [w[1] for w in top_words[:20]]
colors = plt.cm.Blues([0.4 + 0.5 * (c / max(counts_plot)) for c in counts_plot])
ax.barh(range(len(words_plot)), counts_plot[::-1], color=colors[::-1])
ax.set_yticks(range(len(words_plot)))
ax.set_yticklabels(words_plot[::-1], fontsize=9)
ax.set_xlabel('Haeufigkeit')
ax.set_title('Wortanalyse: Haeufigste Woerter in Titeln und Stichwoertern\n(titel_kurz_d + stichwort, Swissvotes 1848–2026)')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('chart_wortanalyse.png', dpi=150, bbox_inches='tight')
plt.close()
print('Gespeichert: chart_wortanalyse.png')

# CSV fuer HTML-Tabelle
with open('wortanalyse.csv', 'w', encoding='utf-8') as f:
    f.write('Rang;Wort;Haeufigkeit\n')
    for i, (word, count) in enumerate(top_words, 1):
        f.write(f'{i};{word};{count}\n')
print('Gespeichert: wortanalyse.csv')

# 8. Querschnittsthemen: Zuordnung + Abstimmungsanzahl
def row_matches_theme(row, codes_with_e3=None):
    """codes_with_e3: list of (e1, e2, e3_optional). e2/e3 None = any. e3 can be prefix like '1.66'."""
    if codes_with_e3 is None:
        return False
    for d in ['d1', 'd2', 'd3']:
        e1, e2, e3 = row.get(d + 'e1'), row.get(d + 'e2'), row.get(d + 'e3')
        if pd.isna(e1) or e1 == '.' or str(e1).strip() == '':
            continue
        try:
            c1 = int(float(e1))
            c2 = float(e2) if not (pd.isna(e2) or e2 == '.' or str(e2).strip() == '') else None
            c3 = str(e3).strip() if not (pd.isna(e3) or e3 == '.' or str(e3).strip() == '') else None
            for code in codes_with_e3:
                if len(code) == 2:
                    ce1, ce2 = code[0], code[1]
                    if c1 == ce1 and (ce2 is None or c2 == ce2):
                        return True
                else:
                    ce1, ce2, ce3 = code[0], code[1], code[2] if len(code) > 2 else None
                    if c1 != ce1:
                        continue
                    if ce2 is not None and c2 != ce2:
                        continue
                    if ce3 is not None and (c3 is None or not str(c3).startswith(str(ce3))):
                        continue
                    return True
        except Exception:
            pass
    return False

THEMEN = [
    ('Gesundheit', [(10, 10.1)], 1),
    ('Digitalisierung', [(8, 8.7), (12, 12.5), (1, 1.6, 1.66), (1, 1.4, 1.43), (1, 1.3, 1.31)], 3),
    ('Migration', [(10, 10.3)], 1),
    ('Klima & Umwelt', [(7, None), (9, None), (8, None), (5, None)], 4),
    ('EU & Aussenpolitik', [(2, None)], 1),
    ('Soziale Sicherheit', [(10, 10.2)], 1),
    ('Armee & Sicherheit', [(3, None)], 1),
    ('Finanzen & Steuern', [(6, None), (4, 4.3)], 2),
]

themen_counts = []
for name, codes, n_hg in THEMEN:
    n_abst = sum(1 for _, row in df.iterrows() if row_matches_theme(row, codes))
    themen_counts.append((name, n_hg, n_abst))

with open('themen_querschnitt.csv', 'w', encoding='utf-8') as f:
    f.write('Thema;Anzahl Hauptgruppen;Anzahl Abstimmungen\n')
    for name, n_hg, n_abst in themen_counts:
        f.write(f'{name};{n_hg};{n_abst}\n')
print('Gespeichert: themen_querschnitt.csv')

# HTML-Tabelle fuer Themen generieren
with open('themen_querschnitt_html.txt', 'w', encoding='utf-8') as f:
    for name, n_hg, n_abst in themen_counts:
        f.write(f'        <tr><td>{name}</td><td>{n_hg}</td><td>{n_abst}</td></tr>\n')
print('Gespeichert: themen_querschnitt_html.txt')

print('\nAlle Grafiken erstellt.')
