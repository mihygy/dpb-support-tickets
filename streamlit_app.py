import streamlit as st
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import altair as alt
import io
import csv

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

if "settings" not in st.session_state:
    st.session_state.settings = {
        "priorities": ["🟢 Niedrig", "🟡 Mittel", "🔴 Hoch"],
        "categories": ["Bug", "Feature Request", "Support", "Dokumentation", "Sonstiges"],
        "statuses": ["Offen", "In Bearbeitung", "Gelöst"]
    }

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
        
        if st.button("🔓 Anmelden", width='stretch'):
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
    
    if st.sidebar.button("🚪 Abmelden", width='stretch'):
        st.session_state.logged_in = False
        st.session_state.tickets = []
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Main content
    st.markdown("<h1>🎫 Support-Tickets System</h1>", unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Neues Ticket", "📋 Tickets", "📊 Erweiterte Stats", "⚙️ Einstellungen"])
    
    # Tab 1: Add new ticket
    with tab1:
        st.markdown("### Neues Support-Ticket erstellen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Titel", placeholder="Ticket-Titel")
            priority = st.selectbox("Priorität", st.session_state.settings["priorities"])
        
        with col2:
            category = st.selectbox("Kategorie", st.session_state.settings["categories"])
            status = st.selectbox("Status", st.session_state.settings["statuses"])
        
        description = st.text_area("Beschreibung", placeholder="Geben Sie die Ticket-Beschreibung ein", height=150)
        
        tags_input = st.text_input("🏷️ Tags", placeholder="Tags durch Komma trennen (z.B. urgent, client, feature)")
        
        st.markdown("#### Ticket-Erstellungsdatum und -zeit")
        col1, col2 = st.columns(2)
        
        with col1:
            created_date = st.date_input("Erstellungsdatum")
        
        with col2:
            created_time = st.time_input("Erstellungszeit")
        
        if st.button("💾 Ticket speichern", width='stretch'):
            if title and description:
                created_datetime = datetime.combine(created_date, created_time).strftime("%Y-%m-%d %H:%M:%S")
                tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                
                new_ticket = {
                    "id": len(st.session_state.tickets) + 1,
                    "title": title,
                    "description": description,
                    "category": category,
                    "priority": priority,
                    "status": status,
                    "created_at": created_datetime,
                    "support_response_at": None,
                    "tags": tags,
                    "comments": []
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
            
            # Charts
            st.markdown("#### 📈 Visualisierungen")
            
            chart_col1, chart_col2 = st.columns(2)
            
            # Chart 1: Response Status (Pie Chart)
            with chart_col1:
                response_data = pd.DataFrame({
                    "Status": ["Mit Antwort", "Ohne Antwort"],
                    "Anzahl": [responded_tickets, pending_tickets]
                })
                
                pie_chart = alt.Chart(response_data).mark_arc().encode(
                    theta="Anzahl",
                    color=alt.Color("Status:N", scale=alt.Scale(
                        domain=["Mit Antwort", "Ohne Antwort"],
                        range=["#4CAF50", "#FF9800"]
                    )),
                    tooltip=["Status", "Anzahl"]
                ).properties(
                    title="Support-Antworten Status",
                    height=300
                )
                st.altair_chart(pie_chart, use_container_width=True)
            
            # Chart 2: Tickets by Priority (Bar Chart)
            with chart_col2:
                priority_counts = {}
                for ticket in st.session_state.tickets:
                    priority = ticket["priority"]
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                
                priority_data = pd.DataFrame({
                    "Priorität": list(priority_counts.keys()),
                    "Anzahl": list(priority_counts.values())
                })
                
                priority_chart = alt.Chart(priority_data).mark_bar().encode(
                    x=alt.X("Priorität:N"),
                    y=alt.Y("Anzahl:Q"),
                    color=alt.Color("Priorität:N", scale=alt.Scale(
                        domain=["🟢 Niedrig", "🟡 Mittel", "🔴 Hoch"],
                        range=["#4CAF50", "#FFC107", "#F44336"]
                    )),
                    tooltip=["Priorität", "Anzahl"]
                ).properties(
                    title="Tickets nach Priorität",
                    height=300
                )
                st.altair_chart(priority_chart, use_container_width=True)
            
            # Chart 3: Tickets by Status (Bar Chart)
            chart_col3, chart_col4 = st.columns(2)
            
            with chart_col3:
                status_counts = {}
                for ticket in st.session_state.tickets:
                    status = ticket["status"]
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                status_data = pd.DataFrame({
                    "Status": list(status_counts.keys()),
                    "Anzahl": list(status_counts.values())
                })
                
                status_chart = alt.Chart(status_data).mark_bar().encode(
                    x=alt.X("Status:N"),
                    y=alt.Y("Anzahl:Q"),
                    color=alt.Color("Status:N", scale=alt.Scale(
                        domain=["Offen", "In Bearbeitung", "Gelöst"],
                        range=["#FF5722", "#2196F3", "#4CAF50"]
                    )),
                    tooltip=["Status", "Anzahl"]
                ).properties(
                    title="Tickets nach Status",
                    height=300
                )
                st.altair_chart(status_chart, use_container_width=True)
            
            # Chart 4: Tickets by Category (Bar Chart)
            with chart_col4:
                category_counts = {}
                for ticket in st.session_state.tickets:
                    category = ticket["category"]
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                category_data = pd.DataFrame({
                    "Kategorie": list(category_counts.keys()),
                    "Anzahl": list(category_counts.values())
                })
                
                category_chart = alt.Chart(category_data).mark_bar().encode(
                    x=alt.X("Anzahl:Q"),
                    y=alt.Y("Kategorie:N"),
                    color=alt.Color("Kategorie:N"),
                    tooltip=["Kategorie", "Anzahl"]
                ).properties(
                    title="Tickets nach Kategorie",
                    height=300
                )
                st.altair_chart(category_chart, use_container_width=True)
            
            # Chart 5: Response Time Distribution
            if response_times:
                st.markdown("---")
                
                response_time_data = pd.DataFrame({
                    "Antwortzeit (Stunden)": response_times
                })
                
                histogram = alt.Chart(response_time_data).mark_bar().encode(
                    alt.X("Antwortzeit (Stunden):Q", bin=alt.Bin(maxbins=10)),
                    y="count()",
                    color="count()",
                    tooltip=["count()"]
                ).properties(
                    title="Verteilung der Support-Antwortzeiten",
                    height=300
                )
                
                st.altair_chart(histogram, use_container_width=True)
            
            st.markdown("---")
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_status = st.selectbox("Nach Status filtern", ["Alle"] + st.session_state.settings["statuses"])
            with col2:
                filter_priority = st.selectbox("Nach Priorität filtern", ["Alle"] + st.session_state.settings["priorities"])
            with col3:
                filter_category = st.selectbox("Nach Kategorie filtern", ["Alle"] + st.session_state.settings["categories"])
            
            # Search and date filters
            col4, col5, col6 = st.columns(3)
            
            with col4:
                search_text = st.text_input("🔍 Suchen (Titel/Beschreibung)", placeholder="Suchtext eingeben")
            
            with col5:
                date_filter_from = st.date_input("Von Datum", value=datetime.now() - timedelta(days=30))
            
            with col6:
                date_filter_to = st.date_input("Bis Datum", value=datetime.now())
            
            # View mode toggle
            view_mode = st.radio("Ansicht", ["📇 Kartensicht", "📋 Listensicht"], horizontal=True)
            
            # Export options
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                if st.button("📥 Als CSV exportieren", width='stretch'):
                    csv_buffer = io.StringIO()
                    csv_writer = csv.writer(csv_buffer)
                    csv_writer.writerow(["ID", "Titel", "Kategorie", "Priorität", "Status", "Erstellt", "Support antwortet", "Tags"])
                    
                    for ticket in filtered_tickets:
                        csv_writer.writerow([
                            ticket["id"],
                            ticket["title"],
                            ticket["category"],
                            ticket["priority"],
                            ticket["status"],
                            ticket["created_at"],
                            ticket.get("support_response_at", ""),
                            ", ".join(ticket.get("tags", []))
                        ])
                    
                    st.download_button(
                        label="⬇️ CSV herunterladen",
                        data=csv_buffer.getvalue(),
                        file_name=f"tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            with col_exp2:
                if st.button("📋 Als Pandas DataFrame", width='stretch'):
                    csv_buffer = io.StringIO()
                    csv_writer = csv.writer(csv_buffer)
                    csv_writer.writerow(["ID", "Titel", "Kategorie", "Priorität", "Status", "Erstellt", "Support antwortet", "Antwortzeit"])
                    
                    for ticket in filtered_tickets:
                        response_time = ""
                        if ticket.get("support_response_at"):
                            try:
                                created = datetime.strptime(ticket["created_at"], "%Y-%m-%d %H:%M:%S")
                                responded = datetime.strptime(ticket["support_response_at"], "%Y-%m-%d %H:%M:%S")
                                response_time = f"{(responded - created).total_seconds() / 3600:.2f}h"
                            except:
                                pass
                        
                        csv_writer.writerow([
                            ticket["id"],
                            ticket["title"],
                            ticket["category"],
                            ticket["priority"],
                            ticket["status"],
                            ticket["created_at"],
                            ticket.get("support_response_at", ""),
                            response_time
                        ])
                    
                    st.download_button(
                        label="⬇️ Detaillierter Report",
                        data=csv_buffer.getvalue(),
                        file_name=f"tickets_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            
            # Apply filters
            filtered_tickets = st.session_state.tickets
            
            if filter_status != "Alle":
                filtered_tickets = [t for t in filtered_tickets if t["status"] == filter_status]
            if filter_priority != "Alle":
                filtered_tickets = [t for t in filtered_tickets if t["priority"] == filter_priority]
            if filter_category != "Alle":
                filtered_tickets = [t for t in filtered_tickets if t["category"] == filter_category]
            
            # Date filter
            if date_filter_from and date_filter_to:
                filtered_tickets = [t for t in filtered_tickets 
                                  if date_filter_from.isoformat() <= t["created_at"][:10] <= date_filter_to.isoformat()]
            
            # Search filter
            if search_text:
                filtered_tickets = [t for t in filtered_tickets 
                                  if search_text.lower() in t["title"].lower() or search_text.lower() in t["description"].lower()]
            
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
                            
                            if ticket.get("tags"):
                                tags_str = " ".join([f"🏷️ {tag}" for tag in ticket["tags"]])
                                st.write(tags_str)
                            
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
                            
                            # Comments section
                            if ticket.get("comments"):
                                st.markdown("**💬 Kommentare:**")
                                for comment in ticket["comments"]:
                                    st.write(f"- {comment}")
                        
                        with col2:
                            st.write("")  # spacing
                            st.write("")  # spacing
                            if st.button("⏰ Antwort", key=f"response_{ticket['id']}", width='stretch'):
                                st.session_state[f"edit_response_{ticket['id']}"] = True
                            
                            if st.button("🗑️ Löschen", key=f"delete_{ticket['id']}", width='stretch'):
                                st.session_state.tickets = [t for t in st.session_state.tickets if t["id"] != ticket["id"]]
                                save_tickets(st.session_state.tickets)
                                st.success("✅ Ticket erfolgreich gelöscht!")
                                st.rerun()
                    
                    # Edit response time
                    if st.session_state.get(f"edit_response_{ticket['id']}"):
                        with st.expander(f"📝 Support-Antwort für Ticket {ticket['id']} bearbeiten", expanded=True):
                            response_date = st.date_input(f"Antwortdatum", key=f"resp_date_{ticket['id']}")
                            response_time = st.time_input(f"Antwortzeit", key=f"resp_time_{ticket['id']}")
                            
                            comment_text = st.text_area(f"💬 Kommentar hinzufügen", key=f"comment_{ticket['id']}")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                if st.button("💾 Speichern", key=f"save_response_{ticket['id']}", width='stretch'):
                                    response_datetime = datetime.combine(response_date, response_time).strftime("%Y-%m-%d %H:%M:%S")
                                    for t in st.session_state.tickets:
                                        if t["id"] == ticket["id"]:
                                            t["support_response_at"] = response_datetime
                                            if comment_text and comment_text.strip():
                                                if "comments" not in t:
                                                    t["comments"] = []
                                                t["comments"].append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {comment_text}")
                                    save_tickets(st.session_state.tickets)
                                    st.session_state[f"edit_response_{ticket['id']}"] = False
                                    st.success("✅ Antwortzeit gespeichert!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.button("✖️ Abbrechen", key=f"cancel_response_{ticket['id']}", width='stretch'):
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
                        
                        if st.button("💾 Antwortzeit speichern", width='stretch'):
                            response_datetime = datetime.combine(response_date, response_time).strftime("%Y-%m-%d %H:%M:%S")
                            for t in st.session_state.tickets:
                                if t["id"] == ticket_id:
                                    t["support_response_at"] = response_datetime
                            save_tickets(st.session_state.tickets)
                            st.success("✅ Antwortzeit gespeichert!")
                            st.rerun()
        
        # Tab 3: Advanced Statistics
        with tab3:
            st.markdown("### 📊 Erweiterte Statistiken")
            
            if not st.session_state.tickets:
                st.info("Keine Daten für Statistiken verfügbar.")
            else:
                # Daily trends
                st.markdown("#### 📈 Tägliche Trends")
                
                daily_data = {}
                for ticket in st.session_state.tickets:
                    date = ticket["created_at"][:10]
                    daily_data[date] = daily_data.get(date, 0) + 1
                
                daily_df = pd.DataFrame({
                    "Datum": list(daily_data.keys()),
                    "Tickets": list(daily_data.values())
                })
                
                if not daily_df.empty:
                    line_chart = alt.Chart(daily_df).mark_line(point=True).encode(
                        x="Datum:T",
                        y="Tickets:Q",
                        tooltip=["Datum", "Tickets"]
                    ).properties(
                        title="Tickets pro Tag",
                        height=300
                    )
                    st.altair_chart(line_chart, use_container_width=True)
                
                # Response rate by priority
                st.markdown("#### ⏱️ Durchschnittliche Antwortzeit pro Priorität")
                
                priority_response_times = {}
                priority_counts = {}
                
                for ticket in st.session_state.tickets:
                    if ticket.get("support_response_at") and ticket.get("created_at"):
                        try:
                            created = datetime.strptime(ticket["created_at"], "%Y-%m-%d %H:%M:%S")
                            responded = datetime.strptime(ticket["support_response_at"], "%Y-%m-%d %H:%M:%S")
                            response_hours = (responded - created).total_seconds() / 3600
                            priority = ticket["priority"]
                            
                            if priority not in priority_response_times:
                                priority_response_times[priority] = []
                                priority_counts[priority] = 0
                            
                            priority_response_times[priority].append(response_hours)
                            priority_counts[priority] += 1
                        except:
                            pass
                
                priority_avg_data = []
                for priority, times in priority_response_times.items():
                    avg_time = sum(times) / len(times) if times else 0
                    priority_avg_data.append({
                        "Priorität": priority,
                        "Ø Antwortzeit (h)": avg_time
                    })
                
                if priority_avg_data:
                    priority_df = pd.DataFrame(priority_avg_data)
                    priority_bar = alt.Chart(priority_df).mark_bar().encode(
                        x="Priorität",
                        y="Ø Antwortzeit (h)",
                        color=alt.Color("Priorität", scale=alt.Scale(
                            domain=st.session_state.settings["priorities"],
                            range=["#4CAF50", "#FFC107", "#F44336"]
                        ))
                    ).properties(
                        height=300
                    )
                    st.altair_chart(priority_bar, use_container_width=True)
                
                # Response rate by category
                st.markdown("#### 📂 Response Rate nach Kategorie")
                
                category_stats = {}
                for category in st.session_state.settings["categories"]:
                    total = len([t for t in st.session_state.tickets if t["category"] == category])
                    responded = len([t for t in st.session_state.tickets if t["category"] == category and t.get("support_response_at")])
                    if total > 0:
                        category_stats[category] = (responded / total) * 100
                
                if category_stats:
                    category_df = pd.DataFrame({
                        "Kategorie": list(category_stats.keys()),
                        "Response Rate (%)": list(category_stats.values())
                    })
                    
                    category_bar = alt.Chart(category_df).mark_bar().encode(
                        x="Response Rate (%)",
                        y="Kategorie",
                        color="Response Rate (%)"
                    ).properties(
                        height=300
                    )
                    st.altair_chart(category_bar, use_container_width=True)
        
        # Tab 4: Settings
        with tab4:
            st.markdown("### ⚙️ Systemeinstellungen")
            
            st.markdown("#### Prioritäten verwalten")
            priorities_str = ", ".join(st.session_state.settings["priorities"])
            new_priorities = st.text_area("Prioritäten (durch Komma trennen)", value=priorities_str, height=100)
            
            st.markdown("#### Kategorien verwalten")
            categories_str = ", ".join(st.session_state.settings["categories"])
            new_categories = st.text_area("Kategorien (durch Komma trennen)", value=categories_str, height=100)
            
            st.markdown("#### Status verwalten")
            statuses_str = ", ".join(st.session_state.settings["statuses"])
            new_statuses = st.text_area("Status (durch Komma trennen)", value=statuses_str, height=100)
            
            if st.button("💾 Einstellungen speichern", width='stretch'):
                st.session_state.settings["priorities"] = [p.strip() for p in new_priorities.split(",")]
                st.session_state.settings["categories"] = [c.strip() for c in new_categories.split(",")]
                st.session_state.settings["statuses"] = [s.strip() for s in new_statuses.split(",")]
                
                st.success("✅ Einstellungen gespeichert!")
            
            st.markdown("---")
            st.markdown("#### 📊 Datenexport & Backup")
            
            if st.button("💾 Alle Tickets als JSON exportieren", width='stretch'):
                json_data = json.dumps(st.session_state.tickets, ensure_ascii=False, indent=2)
                st.download_button(
                    label="⬇️ JSON herunterladen",
                    data=json_data,
                    file_name=f"tickets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

# Main logic

# Main logic
if st.session_state.logged_in:
    main_app()
else:
    login_page()
