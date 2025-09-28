import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import io
import os

# =========================
# Passwortschutz
# =========================
PASSWORT = "Savoy3011"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    eingabe = st.text_input("Bitte Passwort eingeben:", type="password")
    if st.button("Login"):
        if eingabe == PASSWORT:
            st.session_state.authenticated = True
            st.success("Login erfolgreich ✅")
        else:
            st.error("Falsches Passwort")

st.title("Hesta-Statistik Hotel Savoy Bern")

# =========================
# Datei & DataFrame laden
# =========================
DATA_FILE = "data.csv"

if os.path.exists(DATA_FILE):
    try:
        df = pd.read_csv(DATA_FILE, parse_dates=["Monat"])
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["Monat", "Land", "Anreisen", "Nächte"])
else:
    df = pd.DataFrame(columns=["Monat", "Land", "Anreisen", "Nächte"])

# =========================
# Länderliste
# =========================
LAENDER_INPUT = [
    "🇨🇭 Schweiz", "🇩🇪 Deutschland", "🇫🇷 Frankreich", "🇮🇹 Italien",
    "🇷🇺 Russland", "🇪🇸 Spanien", "🇬🇧 Grossbritannien", "🇺🇸 USA",
    "🇨🇦 Kanada", "🇧🇷 Brasilien", "🇨🇳 China", "🇭🇰 Hongkong",
    "🇯🇵 Japan", "🇰🇷 Korea", "🇹🇭 Thailand", "🇦🇪 VAE", "🇦🇺 Australien"
]
LAENDER_REIHENFOLGE = LAENDER_INPUT + ["Total ausgewählte Länder", "Total übrige Länder", "Total"]

# =========================
# Eingabefeld nur, wenn Passwort korrekt
# =========================
if st.session_state.authenticated:
    with st.form("eingabe_formular"):
        jahr = st.selectbox(
            "Jahr",
            list(range(2017, datetime.today().year + 2)),
            index=list(range(2017, datetime.today().year + 2)).index(datetime.today().year)
        )
        monat = st.selectbox("Monat", list(range(1, 13)), index=datetime.today().month - 2)

        anreisen_inputs = {}
        naechte_inputs = {}

        # Labels über den Eingabefeldern
        col0, col1, col2 = st.columns([2, 1, 1])
        with col0:
            st.markdown("<b>Land</b>", unsafe_allow_html=True)
        with col1:
            st.markdown("<b>Anreisen</b>", unsafe_allow_html=True)
        with col2:
            st.markdown("<b>Nächte</b>", unsafe_allow_html=True)

        # Länder-Eingaben mit abwechselnder Hintergrundfarbe
        for i, land in enumerate(LAENDER_INPUT):
            bg_color = "#f2f2f2" if i % 2 == 0 else "white"

            col0, col1, col2 = st.columns([2, 1, 1])
            with col0:
                st.markdown(f"<div style='background-color:{bg_color}; font-size:20px; height:38px; display:flex; align-items:flex-end;'>{land}</div>", unsafe_allow_html=True)
            with col1:
                val_anreisen = st.number_input(
                    "", min_value=0, value=0, step=1, key=f"{land}_anreisen", label_visibility="collapsed"
                )
                anreisen_inputs[land] = "" if val_anreisen == 0 else val_anreisen
            with col2:
                val_naechte = st.number_input(
                    "", min_value=0, value=0, step=1, key=f"{land}_naechte", label_visibility="collapsed"
                )
                naechte_inputs[land] = "" if val_naechte == 0 else val_naechte

            # Hintergrundfarbe der Eingabefelder auf Zeilenfarbe setzen
            st.markdown(f"""
                <style>
                div[data-testid="stNumberInput"] {{
                    background-color: {bg_color} !important;
                }}
                </style>
            """, unsafe_allow_html=True)

        # Total ausgewählte Länder (berechnet)
        total_ausgewählte_anreisen = sum(int(anreisen_inputs[l]) if anreisen_inputs[l] != "" else 0 for l in LAENDER_INPUT)
        total_ausgewählte_naechte = sum(int(naechte_inputs[l]) if naechte_inputs[l] != "" else 0 for l in LAENDER_INPUT)

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("<div style='font-size:20px; background-color:#d9edf7; display:flex; align-items:flex-end;'>Total ausgewählte Länder</div>", unsafe_allow_html=True)
        with col2:
            st.number_input("", value=total_ausgewählte_anreisen, disabled=True, key="total_ausgewählte_anreisen")
        with col3:
            st.number_input("", value=total_ausgewählte_naechte, disabled=True, key="total_ausgewählte_naechte")

        # Total (manuell)
        if "total_anreisen_input" not in st.session_state:
            st.session_state.total_anreisen_input = total_ausgewählte_anreisen
        if "total_naechte_input" not in st.session_state:
            st.session_state.total_naechte_input = total_ausgewählte_naechte

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("<div style='font-size:20px; background-color:#d9edf7; display:flex; align-items:flex-end;'>Total</div>", unsafe_allow_html=True)
        with col2:
            total_anreisen_input = st.number_input("", min_value=0, step=1, key="total_anreisen_input")
        with col3:
            total_naechte_input = st.number_input("", min_value=0, step=1, key="total_naechte_input")

        # Total übrige Länder (berechnet)
        total_übrige_anreisen = total_anreisen_input - total_ausgewählte_anreisen
        total_übrige_naechte = total_naechte_input - total_ausgewählte_naechte

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("<div style='font-size:20px; background-color:#d9edf7; display:flex; align-items:flex-end;'>Total übrige Länder</div>", unsafe_allow_html=True)
        with col2:
            st.number_input("", value=total_übrige_anreisen, disabled=True, key="total_übrige_anreisen")
        with col3:
            st.number_input("", value=total_übrige_naechte, disabled=True, key="total_übrige_naechte")

        # Submit-Button
        submitted = st.form_submit_button("Speichern")


    # =========================
    # Daten speichern
    # =========================
    if submitted:
        monat_datum = pd.Timestamp(datetime(jahr, monat, 1))
        daten_neu = []

        for land in LAENDER_INPUT:
            anr = int(anreisen_inputs[land]) if anreisen_inputs[land] != "" else 0
            nae = int(naechte_inputs[land]) if naechte_inputs[land] != "" else 0
            daten_neu.append({"Monat": monat_datum, "Land": land, "Anreisen": anr, "Nächte": nae})

        daten_neu.append({"Monat": monat_datum, "Land": "Total ausgewählte Länder", "Anreisen": total_ausgewählte_anreisen, "Nächte": total_ausgewählte_naechte})
        daten_neu.append({"Monat": monat_datum, "Land": "Total übrige Länder", "Anreisen": total_übrige_anreisen, "Nächte": total_übrige_naechte})
        daten_neu.append({"Monat": monat_datum, "Land": "Total", "Anreisen": total_anreisen_input, "Nächte": total_naechte_input})

        df_neu = pd.DataFrame(daten_neu)
        df = pd.concat([df[~df.set_index(['Monat','Land']).index.isin(df_neu.set_index(['Monat','Land']).index)], df_neu], ignore_index=True)
        df["Land"] = pd.Categorical(df["Land"], categories=LAENDER_REIHENFOLGE, ordered=True)
        df = df.sort_values(by=["Monat","Land"])
        df.to_csv(DATA_FILE, index=False)
        st.success("Daten erfolgreich gespeichert ✅")

# =========================
# Tabellen & Diagramme
# =========================
if not df.empty:
    # Pivot
    pivot_naechte = df.pivot_table(index="Monat", columns="Land", values="Nächte", aggfunc="sum")
    pivot_anreisen = df.pivot_table(index="Monat", columns="Land", values="Anreisen", aggfunc="sum")

    # Berechnungen
    avg_naechte_pro_anreise = pivot_naechte / pivot_anreisen.replace(0, pd.NA)
    total_naechte = pivot_naechte.sum(axis=1)
    percent_naechte = pivot_naechte.div(total_naechte, axis=0) * 100
    mom_change_year = pivot_naechte.pct_change(12) * 100

    ytd_naechte = pivot_naechte.cumsum()
    ytd_anreisen = pivot_anreisen.cumsum()
    ytd_avg = ytd_naechte / ytd_anreisen.replace(0, pd.NA)
    ytd_percent = ytd_naechte.div(ytd_naechte.sum(axis=1), axis=0) * 100
    ytd_change_year = ytd_naechte.pct_change(12) * 100

    # Monat auswählen
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

    # Tabelle
    st.dataframe(temp.round(2), height=750)

    # XLSX-Download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        temp.to_excel(writer, index=False, sheet_name='Monatliche Daten')
    st.download_button(
        label="Tabelle als XLSX herunterladen",
        data=output.getvalue(),
        file_name=f'Tabelle_{monat_auswahl}.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Balkendiagramm pro Land
    land_auswahl = st.selectbox("Land für Balkendiagramm auswählen", pivot_naechte.columns)
    df_chart = pivot_naechte[[land_auswahl]].reset_index().rename(columns={land_auswahl:'Nächte'})
    df_chart['Monat'] = df_chart['Monat'].dt.strftime('%B %Y')
    df_chart = df_chart.sort_values('Monat')
    chart = alt.Chart(df_chart).mark_bar().encode(
        x=alt.X('Monat:N', sort=list(df_chart['Monat'])),
        y=alt.Y('Nächte:Q'),
        tooltip=['Monat','Nächte']
    ).properties(width=700)
    st.altair_chart(chart)

    # YTD-Balkendiagramm
    df_ytd_chart = ytd_naechte[[land_auswahl]].reset_index().rename(columns={land_auswahl:'Nächte YTD'})
    df_ytd_chart['Monat'] = df_ytd_chart['Monat'].dt.strftime('%B %Y')
    df_ytd_chart = df_ytd_chart.sort_values('Monat')
    chart_ytd = alt.Chart(df_ytd_chart).mark_bar(color='orange').encode(
        x=alt.X('Monat:N', sort=list(df_ytd_chart['Monat'])),
        y=alt.Y('Nächte YTD:Q'),
        tooltip=['Monat','Nächte YTD']
    ).properties(width=700)
    st.altair_chart(chart_ytd)





# streamlit run guest.py

# Aus den eingegebenen Werten sollten folgende Zahlen ausgerechnet werden und in einer immer sichtbaren Tabelle dargestellt werden: 1. Durchschnittliche Anzahl Nächte pro Anreise pro Land (Nächte / Anreisen) 2. % Anteil Nächte pro Land (Total alle Länder = 100%) 3. % Veränderung der Anzahl Nächte im Vergleich zum selben Monat im Vorjahr pro Land 4. alle oben aufgeführten Berechnungen sollten auch als YTD berechnet werden (z.B. März beinhaltet die Daten von Januar, Februar und März; Mai beinhaltet die Daten von Januar, Februar, März, April und Mai) Zudem sollten auch Einträge mit dem Wert 0 akzeptiert werden.

# Eingabeformular
#st.header("Neue Daten eingeben")
#with st.form("eingabe_form"):
    #jahr = st.selectbox("Jahr", list(range(2017, datetime.today().year + 4)), index=list(range(2017, datetime.today().year + 4)).index(datetime.today().year))
    #monat = st.selectbox("Monat", list(range(1, 13)), index=datetime.today().month - 2)
