import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import io
import os

st.title("Hesta-Statistik: Anreisen und Nächte pro Nationalität")

DATA_FILE = "data.csv"

try:
    df = pd.read_csv(DATA_FILE, parse_dates=["Monat"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["Monat", "Nationalität", "Anreisen", "Nächte"])

LAENDER_INPUT = ["🇨🇭 Schweiz", "🇩🇪 Deutschland", "🇫🇷 Frankreich", "🇮🇹 Italien", "🇷🇺 Russland", "🇪🇸 Spanien", "🇬🇧 Grossbritannien", "🇺🇸 USA", "🇨🇦 Kanada", "🇧🇷 Brasilien", "🇨🇳 China", "🇭🇰 Hongkong", "🇯🇵 Japan", "🇰🇷 Korea", "🇹🇭 Thailand", "🇦🇪 VAE", "🇦🇺 Australien"]
LAENDER_REIHENFOLGE = LAENDER_INPUT + ["Total ausgewählte Länder", "Total übrige Länder", "Total"]


# CSV laden oder leeres DataFrame erstellen
if os.path.exists(DATA_FILE) and os.path.getsize(DATA_FILE) > 0:
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["Monat"])
    except Exception:
        df = pd.DataFrame(columns=["Monat", "Land", "Anreisen", "Nächte"])
else:
    df = pd.DataFrame(columns=["Monat", "Land", "Anreisen", "Nächte"])

st.title("Tourismus-Statistik")

# Auswahl Monat/Jahr
with st.form("eingabe_formular"):
    jahr = st.selectbox(
        "Jahr",
        list(range(2020, datetime.today().year + 2)),
        index=list(range(2020, datetime.today().year + 2)).index(datetime.today().year)
    )
    monat = st.selectbox("Monat", list(range(1, 13)), index=datetime.today().month - 1)

    anreisen_inputs = {}
    naechte_inputs = {}

    # Länder-Eingaben
    for land in LAENDER_INPUT:
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            st.markdown(
                f"<div style='font-size:20px; height:38px; display:flex; align-items:flex-end;'>{land}</div>",
                unsafe_allow_html=True
            )
        with col2:
            val = st.number_input(
                "Anreisen", min_value=0, value=0, step=1, key=f"{land}_anreisen"
            )
            anreisen_inputs[land] = "" if val == 0 else val
        with col3:
            val = st.number_input(
                "Nächte", min_value=0, value=0, step=1, key=f"{land}_naechte"
            )
            naechte_inputs[land] = "" if val == 0 else val

    # Total ausgewählte Länder (live)
    total_ausgewählte_anreisen = sum(int(anreisen_inputs[l]) if anreisen_inputs[l] != "" else 0 for l in LAENDER_INPUT)
    total_ausgewählte_naechte = sum(int(naechte_inputs[l]) if naechte_inputs[l] != "" else 0 for l in LAENDER_INPUT)

    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.markdown("<div style='font-size:20px; display:flex; align-items:flex-end;'>Total ausgewählte Länder</div>", unsafe_allow_html=True)
    with col2:
        st.number_input("Anreisen Total ausgewählte Länder", value=total_ausgewählte_anreisen, disabled=True)
    with col3:
        st.number_input("Nächte Total ausgewählte Länder", value=total_ausgewählte_naechte, disabled=True)

    # Total (manuell, Session-State)
    if "total_anreisen_input" not in st.session_state:
        st.session_state.total_anreisen_input = total_ausgewählte_anreisen
    if "total_naechte_input" not in st.session_state:
        st.session_state.total_naechte_input = total_ausgewählte_naechte

    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.markdown("<div style='font-size:20px; display:flex; align-items:flex-end;'>Total</div>", unsafe_allow_html=True)
    with col2:
        total_anreisen_input = st.number_input(
            "Anreisen Total", min_value=0, step=1, key="total_anreisen_input"
        )
    with col3:
        total_naechte_input = st.number_input(
            "Nächte Total", min_value=0, step=1, key="total_naechte_input"
        )

    # Total übrige Länder (live)
    total_übrige_anreisen = total_anreisen_input - total_ausgewählte_anreisen
    total_übrige_naechte = total_naechte_input - total_ausgewählte_naechte

    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.markdown("<div style='font-size:20px; display:flex; align-items:flex-end;'>Total übrige Länder</div>", unsafe_allow_html=True)
    with col2:
        st.number_input("Anreisen Total übrige Länder", value=total_übrige_anreisen, disabled=True)
    with col3:
        st.number_input("Nächte Total übrige Länder", value=total_übrige_naechte, disabled=True)

    # Submit-Button
    submitted = st.form_submit_button("Speichern")

# Daten speichern
if submitted:
    monat_datum = pd.Timestamp(datetime(jahr, monat, 1))
    daten_neu = []

    # Länder
    for land in LAENDER_INPUT:
        anr = int(anreisen_inputs[land]) if anreisen_inputs[land] != "" else 0
        nae = int(naechte_inputs[land]) if naechte_inputs[land] != "" else 0
        daten_neu.append({"Monat": monat_datum, "Land": land, "Anreisen": anr, "Nächte": nae})

    # Totals
    # Total ausgewählte Länder (berechnet aus Eingaben der Länder)
    daten_neu.append({
        "Monat": monat_datum,
        "Land": "Total ausgewählte Länder",
        "Anreisen": total_ausgewählte_anreisen,
        "Nächte": total_ausgewählte_naechte
    })

    # Total übrige Länder (berechnet aus Total-Eingabe minus Total ausgewählte Länder)
    daten_neu.append({
        "Monat": monat_datum,
        "Land": "Total übrige Länder",
        "Anreisen": total_anreisen_input - total_ausgewählte_anreisen,
        "Nächte": total_naechte_input - total_ausgewählte_naechte
    })

    # Total (direkt aus den Eingabefeldern)
    daten_neu.append({
        "Monat": monat_datum,
        "Land": "Total",
        "Anreisen": total_anreisen_input,
        "Nächte": total_naechte_input
    })

    # Neues DataFrame erstellen
    df_neu = pd.DataFrame(daten_neu)

    # Alte Daten für diesen Monat/Land überschreiben
    df = pd.concat([
        df[~df.set_index(['Monat','Land']).index.isin(df_neu.set_index(['Monat','Land']).index)],
        df_neu
    ], ignore_index=True)

    # Reihenfolge für Anzeige festlegen
    df["Land"] = pd.Categorical(df["Land"], categories=LAENDER_INPUT + ["Total ausgewählte Länder", "Total übrige Länder", "Total"], ordered=True)
    df = df.sort_values(by=["Monat","Land"])
    df.to_csv(DATA_FILE, index=False)

    st.success("Daten erfolgreich gespeichert ✅")



# Tabellen und Diagramme
if not df.empty:
    df = df.sort_values(by=["Monat", "Land"])
    pivot_naechte = df.pivot_table(index="Monat", columns="Land", values="Nächte", aggfunc="sum")
    pivot_anreisen = df.pivot_table(index="Monat", columns="Land", values="Anreisen", aggfunc="sum")

    avg_naechte_pro_anreise = pivot_naechte / pivot_anreisen.replace(0, pd.NA)
    total_naechte = pivot_naechte.sum(axis=1)
    percent_naechte = pivot_naechte.div(total_naechte, axis=0) * 100
    mom_change_year = pivot_naechte.pct_change(12) * 100

    ytd_naechte = pivot_naechte.cumsum()
    ytd_anreisen = pivot_anreisen.cumsum()
    ytd_avg = ytd_naechte / ytd_anreisen.replace(0, pd.NA)
    ytd_percent = ytd_naechte.div(ytd_naechte.sum(axis=1), axis=0) * 100
    ytd_change_year = ytd_naechte.pct_change(12) * 100

    monat_auswahl = st.selectbox("Monat auswählen", [d.strftime('%Y-%m') for d in pivot_naechte.index])
    monat_date = pd.to_datetime(monat_auswahl)

    temp = pd.DataFrame({
        'Land': avg_naechte_pro_anreise.columns,
        'Durchschnittliche Nächte pro Anreise': avg_naechte_pro_anreise.loc[monat_date].values,
        '% Anteil Nächte': percent_naechte.loc[monat_date].values,
        '% Veränderung im Vergleich zum Vorjahr': mom_change_year.loc[monat_date].values,
        'YTD Durchschnittliche Nächte pro Anreise': ytd_avg.loc[monat_date].values,
        'YTD % Anteil Nächte': ytd_percent.loc[monat_date].values,
        'YTD % Veränderung im Vergleich zum Vorjahr': ytd_change_year.loc[monat_date].values
    })

    temp = temp.set_index('Land').reindex(LAENDER_REIHENFOLGE).reset_index()
    st.header(f"Berechnete Kennzahlen für {monat_auswahl}")
    # Breite der Land-Spalte anpassen
    st.markdown("""
    <style>
    /* Alle Tabellen in Streamlit */
    .dataframe-container table {
        width: 100% !important;
    }

    /* Erste Spalte (Land) breit genug */
    .dataframe-container table tr th:first-child,
    .dataframe-container table tr td:first-child {
        min-width: 200px !important;  /* passe diesen Wert an */
    }
    </style>
    """, unsafe_allow_html=True)

    # Tabelle groß genug anzeigen
    st.dataframe(temp.round(2), height=750, width=1200)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        temp.to_excel(writer, index=False, sheet_name='Monatliche Daten')
    st.download_button(
        label="Tabelle als XLSX herunterladen",
        data=output.getvalue(),
        file_name=f'Tabelle_{monat_auswahl}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    land_auswahl = st.selectbox("Land für Balkendiagramm auswählen", pivot_naechte.columns)
    st.header(f"Monatliche Anzahl Nächte für {land_auswahl}")
    df_chart = pivot_naechte[[land_auswahl]].reset_index()
    df_chart = df_chart.rename(columns={land_auswahl: 'Nächte'})
    df_chart['Monat_Label'] = df_chart['Monat'].dt.strftime('%B %Y')
    df_chart = df_chart.sort_values('Monat')

    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X('Monat_Label:N', sort=list(df_chart['Monat_Label']), title='Monat'),
        y=alt.Y('Nächte:Q', title='Anzahl Nächte'),
        tooltip=['Monat_Label', 'Nächte']
    ).properties(width=700)
    st.altair_chart(chart)

    st.header(f"YTD Anzahl Nächte für {land_auswahl}")
    df_ytd_chart = ytd_naechte[[land_auswahl]].reset_index()
    df_ytd_chart = df_ytd_chart.rename(columns={land_auswahl: 'Nächte YTD'})
    df_ytd_chart['Monat_Label'] = df_ytd_chart['Monat'].dt.strftime('%B %Y')
    df_ytd_chart = df_ytd_chart.sort_values('Monat')

    chart_ytd = alt.Chart(df_ytd_chart).mark_bar(color='orange').encode(
        x=alt.X('Monat_Label:N', sort=list(df_ytd_chart['Monat_Label']), title='Monat'),
        y=alt.Y('Nächte YTD:Q', title='Anzahl Nächte YTD'),
        tooltip=['Monat_Label', 'Nächte YTD']
    ).properties(width=700)
    st.altair_chart(chart_ytd)






# streamlit run guest.py

# Aus den eingegebenen Werten sollten folgende Zahlen ausgerechnet werden und in einer immer sichtbaren Tabelle dargestellt werden: 1. Durchschnittliche Anzahl Nächte pro Anreise pro Land (Nächte / Anreisen) 2. % Anteil Nächte pro Land (Total alle Länder = 100%) 3. % Veränderung der Anzahl Nächte im Vergleich zum selben Monat im Vorjahr pro Land 4. alle oben aufgeführten Berechnungen sollten auch als YTD berechnet werden (z.B. März beinhaltet die Daten von Januar, Februar und März; Mai beinhaltet die Daten von Januar, Februar, März, April und Mai) Zudem sollten auch Einträge mit dem Wert 0 akzeptiert werden.

# Eingabeformular
#st.header("Neue Daten eingeben")
#with st.form("eingabe_form"):
    #jahr = st.selectbox("Jahr", list(range(2017, datetime.today().year + 4)), index=list(range(2017, datetime.today().year + 4)).index(datetime.today().year))
    #monat = st.selectbox("Monat", list(range(1, 13)), index=datetime.today().month - 2)
