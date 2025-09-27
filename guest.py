import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import io

st.title("Tourismus-Statistik: Anreisen und Nächte pro Nationalität")

DATA_FILE = "overnight_data.csv"

try:
    df = pd.read_csv(DATA_FILE, parse_dates=["Monat"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["Monat", "Nationalität", "Anreisen", "Nächte"])

LAENDER_INPUT = ["🇨🇭 Schweiz", "🇩🇪 Deutschland", "🇫🇷 Frankreich", "🇮🇹 Italien", "🇷🇺 Russland", "🇪🇸 Spanien", "🇬🇧 Grossbritannien", "🇺🇸 USA", "🇨🇦 Kanada", "🇧🇷 Brasilien", "🇨🇳 China", "🇭🇰 Hongkong", "🇯🇵 Japan", "🇰🇷 Korea", "🇹🇭 Thailand", "🇦🇪 VAE", "🇦🇺 Australien"]
LAENDER_REIHENFOLGE = LAENDER_INPUT + ["Total ausgewählte Länder", "Total übrige Länder", "🌍 Total"]

st.header("Neue Daten eingeben")
with st.form("eingabe_form"):
    jahr = st.selectbox("Jahr", list(range(2020, datetime.today().year + 2)), index=list(range(2020, datetime.today().year + 2)).index(datetime.today().year))
    monat = st.selectbox("Monat", list(range(1, 13)), index=datetime.today().month - 1)

    anreisen_inputs, naechte_inputs = {}, {}

    for land in LAENDER_INPUT:
        col1, col2, col3 = st.columns([2,2,2])
        with col1:
            st.markdown(f"<div style='font-size:16px; height:38px; display:flex; align-items:flex-end;'>{land}</div>", unsafe_allow_html=True)
        with col2:
            anreisen_inputs[land] = st.number_input(f"Anreisen {land}", min_value=0, value=0, key=f"{land}_anreisen")
        with col3:
            naechte_inputs[land] = st.number_input(f"Nächte {land}", min_value=0, value=0, key=f"{land}_naechte")

    total_ausgewählte_anreisen = sum(anreisen_inputs.values())
    total_ausgewählte_naechte = sum(naechte_inputs.values())

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        st.markdown(f"<div style='font-size:16px; height:38px; display:flex; align-items:flex-end;'>Total ausgewählte Länder</div>", unsafe_allow_html=True)
    with col2:
        st.number_input("Anreisen total ausgewählte Länder", value=total_ausgewählte_anreisen, disabled=True)
    with col3:
        st.number_input("Nächte total ausgewählte Länder", value=total_ausgewählte_naechte, disabled=True)

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        st.markdown(f"<div style='font-size:16px; height:38px; display:flex; align-items:flex-end;'>Total</div>", unsafe_allow_html=True)
    with col2:
        total_anreisen_input = st.number_input("Anreisen Total", min_value=0, value=0, key="total_anreisen")
    with col3:
        total_naechte_input = st.number_input("Nächte Total", min_value=0, value=0, key="total_naechte")

    total_übrige_anreisen = total_anreisen_input - total_ausgewählte_anreisen
    total_übrige_naechte = total_naechte_input - total_ausgewählte_naechte

    col1, col2, col3 = st.columns([2,2,2])
    with col1:
        st.markdown(f"<div style='font-size:16px; height:38px; display:flex; align-items:flex-end;'>Total übrige Länder</div>", unsafe_allow_html=True)
    with col2:
        st.number_input("Anreisen total übrige Länder", value=total_übrige_anreisen, disabled=True)
    with col3:
        st.number_input("Nächte total übrige Länder", value=total_übrige_naechte, disabled=True)

    submitted = st.form_submit_button("Speichern")

if submitted:
    monat_datum = datetime(jahr, monat, 1)
    daten_neu = []

    for land in LAENDER_INPUT:
        anreisen = anreisen_inputs[land]
        naechte = naechte_inputs[land]
        daten_neu.append({"Monat": monat_datum, "Nationalität": land, "Anreisen": anreisen, "Nächte": naechte})

    daten_neu.append({"Monat": monat_datum, "Nationalität": "Total ausgewählte Länder",
                      "Anreisen": total_ausgewählte_anreisen, "Nächte": total_ausgewählte_naechte})
    daten_neu.append({"Monat": monat_datum, "Nationalität": "Total übrige Länder",
                      "Anreisen": total_übrige_anreisen, "Nächte": total_übrige_naechte})
    daten_neu.append({"Monat": monat_datum, "Nationalität": "Total",
                      "Anreisen": total_anreisen_input, "Nächte": total_naechte_input})

    df_neu = pd.DataFrame(daten_neu)
    df = pd.concat([df[~df.set_index(['Monat','Nationalität']).index.isin(df_neu.set_index(['Monat','Nationalität']).index)], df_neu], ignore_index=True)
    df = df.sort_values(by=["Monat"])
    df.to_csv(DATA_FILE, index=False)
    st.success("Alle eingegebenen Daten gespeichert!")

# Tabellen und Diagramme
if not df.empty:
    df = df.sort_values(by=["Monat", "Nationalität"])
    pivot_naechte = df.pivot_table(index="Monat", columns="Nationalität", values="Nächte", aggfunc="sum")
    pivot_anreisen = df.pivot_table(index="Monat", columns="Nationalität", values="Anreisen", aggfunc="sum")

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
