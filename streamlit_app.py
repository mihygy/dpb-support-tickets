import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

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
        
        if st.button("💾 Ticket speichern", use_container_width=True):
            if title and description:
                new_ticket = {
                    "id": len(st.session_state.tickets) + 1,
                    "title": title,
                    "description": description,
                    "category": category,
                    "priority": priority,
                    "status": status,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.tickets.append(new_ticket)
                save_tickets(st.session_state.tickets)
                st.success("✅ Ticket erfolgreich erstellt!")
                st.rerun()
            else:
                st.error("❌ Bitte füllen Sie alle erforderlichen Felder aus!")
    
    # Tab 2: View and manage tickets
    with tab2:
        st.markdown("### Ticket-Liste")
        
        if not st.session_state.tickets:
            st.info("📭 Keine Tickets vorhanden. Erstellen Sie ein neues im Tab 'Neues Ticket'!")
        else:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_status = st.selectbox("Nach Status filtern", ["Alle"] + ["Offen", "In Bearbeitung", "Gelöst"])
            with col2:
                filter_priority = st.selectbox("Nach Priorität filtern", ["Alle", "🟢 Niedrig", "🟡 Mittel", "🔴 Hoch"])
            with col3:
                filter_category = st.selectbox("Nach Kategorie filtern", ["Alle"] + ["Bug", "Feature Request", "Support", "Dokumentation", "Sonstiges"])
            
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
            
            # Display tickets
            for ticket in filtered_tickets:
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"### {ticket['title']}")
                        st.write(f"**Kategorie:** {ticket['category']} | **Priorität:** {ticket['priority']} | **Status:** {ticket['status']}")
                        st.write(f"*Erstellt: {ticket['created_at']}*")
                        st.write(f"**Beschreibung:** {ticket['description']}")
                    
                    with col2:
                        if st.button("🗑️ Löschen", key=f"delete_{ticket['id']}", use_container_width=True):
                            st.session_state.tickets = [t for t in st.session_state.tickets if t["id"] != ticket["id"]]
                            save_tickets(st.session_state.tickets)
                            st.success("✅ Ticket erfolgreich gelöscht!")
                            st.rerun()

# Main logic
if st.session_state.logged_in:
    main_app()
else:
    login_page()
