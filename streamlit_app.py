import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd

# Page config
st.set_page_config(
    page_title="DPB Support-Tickets",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "tickets" not in st.session_state:
    st.session_state.tickets = []

# File for persistent storage
TICKETS_FILE = "tickets.json"

def load_tickets():
    """Load tickets from JSON file"""
    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_tickets(tickets):
    """Save tickets to JSON file"""
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, ensure_ascii=False, indent=2)
    st.session_state.tickets = tickets

def login_page():
    """Login page with Railcube branding"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🚆 Railcube</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #888;'>Support-Tickets System</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        password = st.text_input("🔐 Masterkennwort", type="password", key="login_password")
        
        if st.button("🔓 Anmelden", use_container_width=True):
            if password == "rail26dpb#":
                st.session_state.logged_in = True
                st.session_state.tickets = load_tickets()
                st.success("✅ Erfolgreich angemeldet!")
                st.rerun()
            else:
                st.error("❌ Falsches Kennwort!")
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #888; font-size: 12px;'>DPB Support System</p>", unsafe_allow_html=True)

def main_app():
    """Main application"""
    # Sidebar
    st.sidebar.markdown("# 🎫 Support-Tickets")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Abmelden", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.tickets = []
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Main content
    st.markdown("<h1>🎫 Support-Tickets System</h1>", unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["➕ Neues Ticket", "📋 Tickets"])
    
    # Tab 1: Add new ticket
    with tab1:
        st.markdown("### Neues Support-Ticket erstellen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Titel", placeholder="Ticket-Titel")
            priority = st.selectbox("Priorität", ["🟢 Niedrig", "🟡 Mittel", "🔴 Hoch"])
        
        with col2:
            category = st.selectbox("Kategorie", ["Bug", "Feature Request", "Support", "Dokumentation", "Sonstiges"])
            status = st.selectbox("Status", ["Offen", "In Bearbeitung", "Gelöst"])
        
        description = st.text_area("Beschreibung", placeholder="Geben Sie die Ticket-Beschreibung ein", height=150)
        
        st.markdown("#### Ticket-Erstellungsdatum und -zeit")
        col1, col2 = st.columns(2)
        
        with col1:
            created_date = st.date_input("Erstellungsdatum")
        
        with col2:
            created_time = st.time_input("Erstellungszeit")
        
        if st.button("💾 Ticket speichern", use_container_width=True):
            if title and description:
                created_datetime = datetime.combine(created_date, created_time).strftime("%Y-%m-%d %H:%M:%S")
                new_ticket = {
                    "id": len(st.session_state.tickets) + 1,
                    "title": title,
                    "description": description,
                    "category": category,
                    "priority": priority,
                    "status": status,
                    "created_at": created_datetime,
                    "support_response_at": None
                }
                st.session_state.tickets.append(new_ticket)
                save_tickets(st.session_state.tickets)
                st.success("✅ Ticket erfolgreich erstellt!")
                st.rerun()
            else:
                st.error("❌ Bitte füllen Sie alle erforderlichen Felder aus!")
    
    # Tab 2: View and manage tickets
    with tab2:
        st.markdown("### Ticket-Verwaltung")
        
        if not st.session_state.tickets:
            st.info("📭 Keine Tickets vorhanden. Erstellen Sie ein neues im Tab 'Neues Ticket'!")
        else:
            # Statistiken
            st.markdown("#### 📊 Statistiken")
            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
            
            total_tickets = len(st.session_state.tickets)
            responded_tickets = len([t for t in st.session_state.tickets if t.get("support_response_at")])
            
            with stats_col1:
                st.metric("Gesamt Tickets", total_tickets)
            
            with stats_col2:
                st.metric("Support antwortet", responded_tickets)
            
            with stats_col3:
                pending_tickets = len([t for t in st.session_state.tickets if not t.get("support_response_at")])
                st.metric("Noch ohne Antwort", pending_tickets)
            
            # Calculate average response time
            response_times = []
            for ticket in st.session_state.tickets:
                if ticket.get("support_response_at") and ticket.get("created_at"):
                    try:
                        created = datetime.strptime(ticket["created_at"], "%Y-%m-%d %H:%M:%S")
                        responded = datetime.strptime(ticket["support_response_at"], "%Y-%m-%d %H:%M:%S")
                        delta = responded - created
                        response_times.append(delta.total_seconds() / 3600)  # in hours
                    except:
                        pass
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            with stats_col4:
                st.metric("Ø Antwortzeit (Stunden)", f"{avg_response_time:.1f}")
            
            st.markdown("---")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_status = st.selectbox("Nach Status filtern", ["Alle"] + ["Offen", "In Bearbeitung", "Gelöst"])
            with col2:
                filter_priority = st.selectbox("Nach Priorität filtern", ["Alle", "🟢 Niedrig", "🟡 Mittel", "🔴 Hoch"])
            with col3:
                filter_category = st.selectbox("Nach Kategorie filtern", ["Alle"] + ["Bug", "Feature Request", "Support", "Dokumentation", "Sonstiges"])
            
            # View mode toggle
            view_mode = st.radio("Ansicht", ["📇 Kartensicht", "📋 Listensicht"], horizontal=True)
            
            # Apply filters
            filtered_tickets = st.session_state.tickets
            
            if filter_status != "Alle":
                filtered_tickets = [t for t in filtered_tickets if t["status"] == filter_status]
            if filter_priority != "Alle":
                filtered_tickets = [t for t in filtered_tickets if t["priority"] == filter_priority]
            if filter_category != "Alle":
                filtered_tickets = [t for t in filtered_tickets if t["category"] == filter_category]
            
            st.markdown(f"**Angezeigte Tickets: {len(filtered_tickets)} / {len(st.session_state.tickets)}**")
            st.markdown("---")
            
            # Display tickets based on view mode
            if view_mode == "📇 Kartensicht":
                # Card view
                for ticket in filtered_tickets:
                    with st.container(border=True):
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"### {ticket['title']}")
                            st.write(f"**Kategorie:** {ticket['category']} | **Priorität:** {ticket['priority']} | **Status:** {ticket['status']}")
                            st.write(f"*Erstellt: {ticket['created_at']}*")
                            
                            if ticket.get("support_response_at"):
                                st.write(f"*Support antwortet: {ticket['support_response_at']}*")
                                try:
                                    created = datetime.strptime(ticket["created_at"], "%Y-%m-%d %H:%M:%S")
                                    responded = datetime.strptime(ticket["support_response_at"], "%Y-%m-%d %H:%M:%S")
                                    response_hours = (responded - created).total_seconds() / 3600
                                    st.write(f"⏱️ **Antwortzeit:** {response_hours:.1f} Stunden")
                                except:
                                    pass
                            else:
                                st.write("*Support antwortet: Noch nicht gesetzt*")
                            
                            st.write(f"**Beschreibung:** {ticket['description']}")
                        
                        with col2:
                            st.write("")  # spacing
                            st.write("")  # spacing
                            if st.button("⏰ Antwort", key=f"response_{ticket['id']}", use_container_width=True):
                                st.session_state[f"edit_response_{ticket['id']}"] = True
                            
                            if st.button("🗑️ Löschen", key=f"delete_{ticket['id']}", use_container_width=True):
                                st.session_state.tickets = [t for t in st.session_state.tickets if t["id"] != ticket["id"]]
                                save_tickets(st.session_state.tickets)
                                st.success("✅ Ticket erfolgreich gelöscht!")
                                st.rerun()
                    
                    # Edit response time
                    if st.session_state.get(f"edit_response_{ticket['id']}"):
                        with st.expander(f"📝 Support-Antwort für Ticket {ticket['id']} bearbeiten", expanded=True):
                            response_date = st.date_input(f"Antwortdatum", key=f"resp_date_{ticket['id']}")
                            response_time = st.time_input(f"Antwortzeit", key=f"resp_time_{ticket['id']}")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                if st.button("💾 Speichern", key=f"save_response_{ticket['id']}", use_container_width=True):
                                    response_datetime = datetime.combine(response_date, response_time).strftime("%Y-%m-%d %H:%M:%S")
                                    for t in st.session_state.tickets:
                                        if t["id"] == ticket["id"]:
                                            t["support_response_at"] = response_datetime
                                    save_tickets(st.session_state.tickets)
                                    st.session_state[f"edit_response_{ticket['id']}"] = False
                                    st.success("✅ Antwortzeit gespeichert!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.button("✖️ Abbrechen", key=f"cancel_response_{ticket['id']}", use_container_width=True):
                                    st.session_state[f"edit_response_{ticket['id']}"] = False
                                    st.rerun()
            
            else:  # List view
                # Create DataFrame for table view
                table_data = []
                for ticket in filtered_tickets:
                    response_time = "Nicht gesetzt"
                    response_hours = ""
                    
                    if ticket.get("support_response_at"):
                        try:
                            created = datetime.strptime(ticket["created_at"], "%Y-%m-%d %H:%M:%S")
                            responded = datetime.strptime(ticket["support_response_at"], "%Y-%m-%d %H:%M:%S")
                            response_time = ticket["support_response_at"]
                            response_hours = f"{(responded - created).total_seconds() / 3600:.1f}h"
                        except:
                            response_time = ticket.get("support_response_at", "Fehler")
                    
                    table_data.append({
                        "ID": ticket["id"],
                        "Titel": ticket["title"],
                        "Kategorie": ticket["category"],
                        "Priorität": ticket["priority"],
                        "Status": ticket["status"],
                        "Erstellt": ticket["created_at"],
                        "Support antwortet": response_time,
                        "Antwortzeit": response_hours
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                
                # Edit response time for selected tickets
                st.markdown("#### Support-Antwort bearbeiten")
                ticket_to_edit = st.selectbox("Wählen Sie ein Ticket zur Bearbeitung", 
                                              [f"ID: {t['id']} - {t['title']}" for t in filtered_tickets] + [""])
                
                if ticket_to_edit:
                    ticket_id = int(ticket_to_edit.split(" - ")[0].split(": ")[1])
                    ticket = next((t for t in st.session_state.tickets if t["id"] == ticket_id), None)
                    
                    if ticket:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            response_date = st.date_input("Antwortdatum", key=f"resp_date_list_{ticket_id}")
                        
                        with col2:
                            response_time = st.time_input("Antwortzeit", key=f"resp_time_list_{ticket_id}")
                        
                        if st.button("💾 Antwortzeit speichern", use_container_width=True):
                            response_datetime = datetime.combine(response_date, response_time).strftime("%Y-%m-%d %H:%M:%S")
                            for t in st.session_state.tickets:
                                if t["id"] == ticket_id:
                                    t["support_response_at"] = response_datetime
                            save_tickets(st.session_state.tickets)
                            st.success("✅ Antwortzeit gespeichert!")
                            st.rerun()

# Main logic
if st.session_state.logged_in:
    main_app()
else:
    login_page()
