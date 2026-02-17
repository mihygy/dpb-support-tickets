import datetime
import random
from PIL import Image
from io import BytesIO
import requests

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="RailCube Support-Tickets", page_icon="🚂")

# Layout für Logo und Titel
col1, col2 = st.columns([1, 4])
with col1:
    st.image("RAILCUBE-LOGO.png", width=100)
with col2:
    st.title("RailCube Support-Tickets")

st.write(
    """
    RailCube-Anwendung Support-Ticket-Manager. Hier können Sie Support-Anfragen 
    für RailCube verwalten, bestehende Tickets bearbeiten und Statistiken anzeigen.
    """
)

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Create empty dataframe with column structure
    data = {
        "ID": [],
        "Issue": [],
        "Status": [],
        "Priority": [],
        "Date Submitted": [],
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across
    # page runs). This ensures our data is persisted when the app updates.
    st.session_state.df = df


# Show a section to add a new ticket.
st.header("Neues Support-Ticket hinzufügen")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("Beschreiben Sie das RailCube-Problem")
    priority = st.selectbox("Priorität", ["Hoch", "Mittel", "Niedrig"])
    submitted = st.form_submit_button("Absenden")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    if len(st.session_state.df) > 0:
        recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    else:
        recent_ticket_number = 0
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Offen",
                "Priority": priority,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Ticket erfolgreich eingereicht! Ticket-Details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing tickets in a table.
st.header("Bestehende Tickets")
st.write(f"Anzahl der Tickets: `{len(st.session_state.df)}`")

st.info(
    "Sie können Tickets durch Doppelklick auf eine Zelle bearbeiten. Beobachten Sie, wie sich die "
    "Diagramme unten automatisch aktualisieren! Sie können die Tabelle durch Klick auf die Spaltenüberschriften sortieren.",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket-Status",
            options=["Offen", "In Bearbeitung", "Geschlossen"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priorität",
            help="Priorität",
            options=["Hoch", "Mittel", "Niedrig"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

# Show some metrics and charts about the ticket.
st.header("Statistiken")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Offen"])
col1.metric(label="Anzahl offener Tickets", value=num_open_tickets, delta=10)
col2.metric(label="Erste Antwortzeit (Stunden)", value=5.2, delta=-1.5)
col3.metric(label="Durchschnittliche Lösungszeit (Stunden)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Ticket-Status pro Monat")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Aktuelle Ticket-Prioritäten")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
