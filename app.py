from __future__ import annotations

from datetime import date
import pandas as pd
import streamlit as st

from database import initialize_database
from services import (
    EXPENSE_TYPE_OPTIONS,
    SPLIT_TYPE_OPTIONS,
    add_category,
    apply_filters,
    apply_income_filters,
    authenticate_user,
    build_category_summary,
    build_dashboard_metrics,
    build_income_vs_expense_summary,
    create_expense,
    create_income,
    delete_category,
    delete_expense,
    export_expenses_to_csv,
    export_expenses_to_pdf,
    format_currency,
    get_categories,
    get_expense_by_id,
    get_expenses,
    get_incomes,
    get_user_by_id,
    get_usernames,
    get_visible_expenses,
    get_month_options,
    update_expense,
    update_user_profile,
    validate_expense_data,
    validate_income_data,
    REPORTLAB_AVAILABLE,
)
from ui_helpers import close_section, open_section, render_topbar, require_authentication


st.set_page_config(page_title="Monitor Spese", page_icon="€", layout="wide")


MONTH_NAMES = {
    "01": "Gennaio",
    "02": "Febbraio",
    "03": "Marzo",
    "04": "Aprile",
    "05": "Maggio",
    "06": "Giugno",
    "07": "Luglio",
    "08": "Agosto",
    "09": "Settembre",
    "10": "Ottobre",
    "11": "Novembre",
    "12": "Dicembre",
}


CATEGORY_ICONS = {
    "Spesa": "🛒",
    "Casa": "🏠",
    "Trasporti": "🚗",
    "Ristoranti": "🍽️",
    "Svago": "🎟️",
    "Salute": "💊",
    "Abbonamenti": "💳",
    "Viaggi": "✈️",
    "Regali": "🎁",
    "Altro": "●",
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #f5f1ea;
                --panel: rgba(255, 252, 247, 0.88);
                --panel-strong: #fffdfa;
                --border: #e4d7c5;
                --text: #2f2419;
                --muted: #776556;
                --accent: #b45d34;
                --accent-dark: #8b4323;
                --green: #4f7a5c;
                --shadow: 0 18px 40px rgba(70, 43, 22, 0.08);
            }
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(197, 133, 86, 0.14), transparent 28%),
                    radial-gradient(circle at top right, rgba(79, 122, 92, 0.16), transparent 24%),
                    linear-gradient(180deg, #fbf7f2 0%, #f3ede4 100%);
                color: var(--text);
            }
            .block-container {
                padding-top: 0.85rem;
                padding-bottom: 2.5rem;
                max-width: 1320px;
            }
            .hero-card {
                padding: 1.65rem 1.8rem;
                border-radius: 28px;
                background:
                    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 28%),
                    radial-gradient(circle at bottom left, rgba(242, 203, 170, 0.14), transparent 22%),
                    linear-gradient(135deg, #2d2218 0%, #5d3724 50%, #9b5734 100%);
                color: white;
                box-shadow: 0 24px 60px rgba(65, 32, 16, 0.16);
                margin-bottom: 1.5rem;
            }
            div[data-testid="stMetric"] {
                background: var(--panel-strong);
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 1rem 1rem 0.9rem 1rem;
                box-shadow: var(--shadow);
                min-height: 132px;
            }
            div[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #fcf7f0 0%, #f2e7d8 100%);
                border-right: 1px solid rgba(171, 133, 99, 0.18);
            }
            div[data-testid="stMetricLabel"] p {
                color: var(--muted);
                font-weight: 600;
                font-size: 0.93rem;
            }
            div[data-testid="stMetricValue"] {
                color: var(--text);
                font-size: 1.45rem;
            }
            div[data-testid="stMetricDelta"] {
                color: var(--green);
            }
            .small-note {
                color: var(--muted);
                font-size: 0.92rem;
            }
            .topbar-text {
                color: var(--muted);
                font-size: 0.9rem;
                padding-top: 0.15rem;
            }
            .topbar-row {
                padding-top: 0.45rem;
                margin-bottom: 0.2rem;
            }
            .section-card {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 1rem 1.1rem 1.15rem 1.1rem;
                box-shadow: var(--shadow);
                backdrop-filter: blur(10px);
            }
            .section-title {
                font-size: 1.05rem;
                font-weight: 700;
                color: var(--text);
                margin-bottom: 0.25rem;
            }
            .section-subtitle {
                color: var(--muted);
                font-size: 0.93rem;
                margin-bottom: 0.9rem;
            }
            .balance-chip {
                display: inline-block;
                margin-top: 0.6rem;
                padding: 0.45rem 0.7rem;
                border-radius: 999px;
                background: rgba(255, 255, 255, 0.15);
                font-size: 0.9rem;
            }
            div[data-baseweb="select"] > div,
            div[data-baseweb="input"] > div,
            div[data-baseweb="textarea"] > div,
            div[data-baseweb="base-input"] {
                border-radius: 16px !important;
                border-color: #dbcab6 !important;
            }
            div.stButton > button,
            div.stDownloadButton > button,
            div[data-testid="stFormSubmitButton"] button {
                border-radius: 16px !important;
                border: 1px solid transparent !important;
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%) !important;
                color: white !important;
                font-weight: 600 !important;
                box-shadow: 0 10px 24px rgba(139, 67, 35, 0.18);
            }
            div.stButton > button:hover,
            div.stDownloadButton > button:hover,
            div[data-testid="stFormSubmitButton"] button:hover {
                transform: translateY(-1px);
            }
            div.stButton > button[kind="tertiary"] {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: var(--text) !important;
                padding: 0 !important;
                min-height: auto !important;
                height: auto !important;
                border-radius: 0 !important;
                font-size: 0.92rem !important;
                font-weight: 500 !important;
            }
            div.stButton > button[kind="tertiary"]:hover {
                background: transparent !important;
                color: var(--accent-dark) !important;
                transform: none !important;
            }
            section[data-testid="stSidebar"] div.stButton > button[kind="tertiary"] {
                justify-content: flex-start !important;
                text-align: left !important;
                width: auto !important;
                min-height: auto !important;
                padding: 0.1rem 0 !important;
                font-size: 0.9rem !important;
            }
            div.stButton > button[kind="secondary"],
            div[data-testid="stFormSubmitButton"] button[kind="secondary"] {
                background: linear-gradient(180deg, rgba(255, 251, 246, 0.99) 0%, rgba(246, 238, 228, 0.98) 100%) !important;
                color: var(--text) !important;
                border: 1px solid var(--border) !important;
                box-shadow: 0 16px 30px rgba(70, 43, 22, 0.07) !important;
            }
            div.stButton > button[kind="secondary"] {
                min-height: 176px !important;
                white-space: pre-line !important;
                text-align: left !important;
                line-height: 1.28 !important;
                padding: 1.15rem 1.15rem !important;
                border-radius: 24px !important;
                letter-spacing: 0.01em;
                position: relative;
                background: rgba(255, 251, 246, 0.98) !important;
                box-shadow: none !important;
                border: 1px solid var(--border) !important;
            }
            div.stButton > button[kind="secondary"] p {
                font-size: 1.25rem !important;
                font-weight: 500 !important;
                line-height: 1.15 !important;
            }
            div.stButton > button[kind="secondary"]:hover {
                border-color: #cfad8d !important;
                box-shadow: none !important;
                background: rgba(255, 252, 249, 1) !important;
            }
            div[data-testid="stDataFrame"] {
                border-radius: 20px;
                overflow: hidden;
                border: 1px solid var(--border);
            }
            div[data-testid="stRadio"] > div {
                background: rgba(255, 250, 244, 0.85);
                border: 1px solid var(--border);
                border-radius: 999px;
                padding: 0.32rem;
                box-shadow: 0 10px 26px rgba(70, 43, 22, 0.06);
                display: inline-flex;
            }
            div[data-testid="stRadio"] label {
                margin-right: 0.35rem;
            }
            div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
                display: none !important;
            }
            div[data-testid="stRadio"] label[data-baseweb="radio"] {
                background: transparent;
                border-radius: 999px;
                padding: 0.5rem 0.95rem;
                min-width: 130px;
                justify-content: center;
                transition: all 0.18s ease;
            }
            div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
                box-shadow: 0 8px 18px rgba(139, 67, 35, 0.18);
            }
            div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {
                color: white !important;
            }
            div[data-testid="stRadio"] p {
                color: var(--text);
                font-weight: 600;
                font-size: 0.95rem;
            }
            .legend-row {
                display: flex;
                gap: 0.5rem;
                flex-wrap: wrap;
                margin-top: 0.8rem;
            }
            .legend-badge {
                background: rgba(255,255,255,0.16);
                border: 1px solid rgba(255,255,255,0.14);
                padding: 0.35rem 0.65rem;
                border-radius: 999px;
                font-size: 0.86rem;
            }
            .category-name {
                font-size: 1rem;
                font-weight: 700;
                color: var(--text);
                margin-bottom: 0.35rem;
            }
            .category-total {
                font-size: 1.35rem;
                font-weight: 800;
                color: var(--accent-dark);
                margin-bottom: 0.65rem;
            }
            .category-meta {
                color: var(--muted);
                font-size: 0.92rem;
                line-height: 1.55;
            }
            .expense-detail-card {
                background:
                    linear-gradient(180deg, rgba(255, 253, 249, 0.98) 0%, rgba(248, 241, 233, 0.98) 100%);
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 1rem 1.05rem;
                margin-bottom: 0.85rem;
                box-shadow: 0 14px 28px rgba(70, 43, 22, 0.06);
            }
            .expense-detail-title {
                font-size: 1.02rem;
                font-weight: 800;
                color: var(--text);
                margin-bottom: 0.3rem;
            }
            .expense-detail-meta {
                color: var(--muted);
                font-size: 0.93rem;
                line-height: 1.6;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_back_circle_button(key: str) -> bool:
    st.markdown(
        """
        <style>
            div.stButton > button[kind="secondary"]:has(p:only-child) {
                width: 34px !important;
                min-width: 34px !important;
                height: 34px !important;
                min-height: 34px !important;
                border-radius: 999px !important;
                padding: 0 !important;
                background: rgba(255, 251, 246, 0.98) !important;
                color: #2f2419 !important;
                border: 1px solid #e4d7c5 !important;
                box-shadow: none !important;
                font-size: 0.95rem !important;
                line-height: 1 !important;
            }
            div.stButton > button[kind="secondary"]:has(p:only-child):hover {
                background: rgba(255, 252, 249, 1) !important;
                border-color: #cfad8d !important;
            }
            div.stButton > button[kind="secondary"]:has(p:only-child) p {
                font-size: 0.95rem !important;
                font-weight: 600 !important;
                line-height: 1 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    return st.button("←", key=key, type="secondary", use_container_width=False)


def main() -> None:
    initialize_database()
    if not require_authentication():
        return
    inject_styles()

    all_expenses = get_expenses()
    current_user = st.session_state.current_user or {}
    current_username = current_user.get("username", "")
    all_expenses = get_visible_expenses(all_expenses, current_username)
    all_incomes = get_incomes()

    render_topbar()
    filtered_expenses, selected_month = render_sidebar_filters(all_expenses)
    filtered_incomes = apply_income_filters(all_incomes, selected_month)
    current_section = st.session_state.get("current_section", "Home")
    if st.session_state.get("current_view") == "dashboard_detail":
        render_dashboard_detail_page(all_expenses, all_incomes, selected_month)
        return
    if st.session_state.get("current_view") == "category_detail":
        render_category_detail_page(filtered_expenses)
        return
    if st.session_state.get("current_view") == "profile":
        render_profile_page()
        return
    if st.session_state.get("current_view") != "home":
        render_operation_detail_page(filtered_expenses, filtered_incomes)
        return

    if current_section == "Home":
        render_hero(all_expenses)
        render_dashboard(all_expenses, all_incomes, selected_month)
    render_main_content(filtered_expenses, filtered_incomes, all_expenses, all_incomes)


def initialize_session_state() -> None:
    if "selected_expense_id" not in st.session_state:
        st.session_state.selected_expense_id = None
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None


def render_login_page() -> None:
    spacer_left, center, spacer_right = st.columns([1, 1.15, 1])
    with center:
        st.markdown(
            """
            <div class="hero-card" style="margin-top: 3rem;">
                <div style="letter-spacing:0.08em; text-transform:uppercase; font-size:0.82rem; opacity:0.78; margin-bottom:0.45rem;">
                    Accesso riservato
                </div>
                <h1 style="margin:0; font-size:2rem;">Accedi al tuo monitor spese</h1>
                <p style="margin:0.8rem 0 0 0; opacity:0.92;">
                    Inserisci username e password per entrare nell'app. Le credenziali demo sono pronte per i test.
                </p>
                <div class="legend-row">
                    <span class="legend-badge">Utente demo: io / demo123</span>
                    <span class="legend-badge">Utente demo: compagna / demo123</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        open_section("Login", "Accesso locale semplice con utenti salvati in SQLite.")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Accedi", use_container_width=True)

            if submitted:
                user = authenticate_user(username, password)
                if user is None:
                    st.error("Credenziali non valide. Controlla username e password.")
                else:
                    st.session_state.is_authenticated = True
                    st.session_state.current_user = user
                    st.success("Accesso effettuato.")
                    st.rerun()
        close_section()


def render_topbar() -> None:
    user = st.session_state.current_user or {}
    st.markdown('<div class="topbar-row">', unsafe_allow_html=True)
    left, right = st.columns([1, 0.08])
    with left:
        st.markdown(
            f'<div class="topbar-text">Connesso come: {user.get("full_name", "Utente")} ({user.get("username", "-")})</div>',
            unsafe_allow_html=True,
        )
    with right:
        if st.button("Logout", key="logout_small", use_container_width=False, type="tertiary"):
            st.session_state.is_authenticated = False
            st.session_state.current_user = None
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_hero(dataframe: pd.DataFrame) -> None:
    total_expenses = len(dataframe)
    total_amount = format_currency(float(dataframe["amount"].sum())) if not dataframe.empty else format_currency(0)

    st.markdown(
        f"""
        <div class="hero-card">
            <div style="display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; align-items:flex-start;">
                <div style="max-width:720px;">
                    <div style="letter-spacing:0.08em; text-transform:uppercase; font-size:0.82rem; opacity:0.78; margin-bottom:0.45rem;">
                        Finanze personali
                    </div>
                    <h1 style="margin:0; font-size:2.1rem; line-height:1.08;">Monitor spese personali e di coppia</h1>
                    <p style="margin:0.8rem 0 0 0; max-width:620px; opacity:0.92; font-size:1rem;">
                        Un cruscotto semplice ma piu curato per registrare le spese, capire chi ha anticipato cosa
                        e tenere d'occhio il saldo di coppia.
                    </p>
                    <div class="legend-row">
                        <span class="legend-badge">{total_expenses} movimenti registrati</span>
                        <span class="legend-badge">{total_amount} tracciati</span>
                        <span class="legend-badge">SQLite locale</span>
                    </div>
                </div>
                <div class="balance-chip">
                    Inserisci, filtra, modifica ed esporta in pochi clic
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_main_content(
    filtered_expenses: pd.DataFrame,
    filtered_incomes: pd.DataFrame,
    all_expenses: pd.DataFrame,
    all_incomes: pd.DataFrame,
) -> None:
    section = st.radio(
        "Sezioni",
        ["Home", "Entrate", "Uscite", "Analisi", "Riepilogo"],
        horizontal=True,
        label_visibility="collapsed",
        key="current_section",
    )

    if section == "Home":
        st.caption("Scegli una card per entrare nella schermata dedicata all'operazione che vuoi eseguire.")
        render_operation_cards(filtered_expenses)

    elif section == "Entrate":
        render_secondary_stats_line(all_expenses, all_incomes, "Entrate")
        st.caption("Le entrate del periodo selezionato, in una vista semplice e immediata.")
        render_incomes_section(filtered_incomes)

    elif section == "Uscite":
        render_secondary_stats_line(all_expenses, all_incomes, "Uscite")
        st.caption("Trova una categoria e apri il dettaglio delle spese che contiene.")
        render_category_dashboard(filtered_expenses)

    elif section == "Analisi":
        render_secondary_stats_line(all_expenses, all_incomes, "Analisi")
        st.caption("Una vista piu calma per capire come stai spendendo nel tempo.")
        render_charts(filtered_expenses)
        st.write("")
        render_income_expense_analysis(all_incomes, all_expenses)

    else:
        render_secondary_stats_line(all_expenses, all_incomes, "Riepilogo")
        st.caption("Tutte le spese filtrate in un'unica vista, con esportazione CSV.")
        render_expense_list(filtered_expenses)
        st.write("")
        render_export_section(filtered_expenses)


def render_secondary_stats_line(all_expenses: pd.DataFrame, all_incomes: pd.DataFrame, section_name: str) -> None:
    filters = st.session_state.get("filters", {})
    current_user = st.session_state.current_user or {}
    current_username = current_user.get("username", "")
    selected_month = filters.get("month_label", "Tutti")
    month_expenses = all_expenses if selected_month == "Tutti" else all_expenses[all_expenses["month_label"] == selected_month]
    month_incomes = all_incomes if selected_month == "Tutti" else all_incomes[all_incomes["month_label"] == selected_month]
    metrics = build_dashboard_metrics(month_expenses, current_username)
    total_incomes = float(month_incomes["amount"].sum()) if not month_incomes.empty else 0.0

    stats = [
        ("Entrate", format_currency(total_incomes), section_name == "Entrate"),
        ("Spese", format_currency(metrics["total_month"]), section_name == "Uscite"),
        ("Mie", format_currency(metrics["my_personal"]), False),
        ("Condivise", format_currency(metrics["shared_total"]), False),
        ("Saldo", build_balance_label(metrics["balance"]), section_name == "Analisi"),
    ]
    columns = st.columns(len(stats))
    for column, (label, value, active) in zip(columns, stats):
        with column:
            if active:
                st.markdown(f"**{label}**")
                st.markdown(f"**{value}**")
            else:
                st.caption(label)
                st.write(value)


def render_sidebar_filters(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    user = st.session_state.current_user or {}

    st.sidebar.markdown("## Profilo")
    if st.sidebar.button(user.get("full_name", "Utente"), key="profile_button", use_container_width=False, type="tertiary"):
        st.session_state.current_view = "profile"
        st.rerun()
    st.sidebar.markdown(
        f"<div class='small-note'>{user.get('username', '-')}</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.write("")

    st.sidebar.markdown("## Home")
    if st.sidebar.button("Vai alla home", use_container_width=False, type="tertiary"):
        st.session_state.current_view = "home"
        st.session_state.current_section = "Home"
        st.rerun()

    st.sidebar.write("")
    st.sidebar.markdown("## Filtri")
    toggle_label = "Nascondi filtri" if st.session_state.show_filters else "Mostra filtri"
    if st.sidebar.button(toggle_label, use_container_width=False, type="tertiary"):
        st.session_state.show_filters = not st.session_state.show_filters
        st.rerun()

    month_options = get_month_options(dataframe)
    category_options = ["Tutte"] + get_categories()
    payer_values = sorted(dataframe["payer"].dropna().unique().tolist()) if not dataframe.empty else []
    payer_options = ["Tutti"] + payer_values
    type_options = ["Tutte"] + EXPENSE_TYPE_OPTIONS

    available_months = [month for month in month_options if month != "Tutti"]
    year_options = sorted({month.split("-")[0] for month in available_months}, reverse=True)
    previous_filters = st.session_state.get(
        "filters",
        {"month_label": "Tutti", "category": "Tutte", "payer": "Tutti", "expense_type": "Tutte"},
    )
    selected_month = previous_filters.get("month_label", "Tutti")
    selected_category = previous_filters.get("category", "Tutte")
    selected_payer = previous_filters.get("payer", "Tutti")
    selected_type = previous_filters.get("expense_type", "Tutte")

    if not st.session_state.show_filters:
        st.sidebar.caption("Filtri nascosti.")
    else:
        st.sidebar.caption("Riduci il dataset e aggiorna l'app.")

    if st.session_state.show_filters and year_options:
        selected_year = selected_month.split("-")[0] if selected_month != "Tutti" else year_options[0]
        selected_year = st.sidebar.selectbox("Anno", year_options, index=year_options.index(selected_year))
        month_map = {
            MONTH_NAMES.get(month.split("-")[1], month): month
            for month in available_months
            if month.startswith(selected_year)
        }
        month_labels = list(month_map.keys())
        default_month_label = None
        if selected_month != "Tutti" and selected_month.startswith(selected_year):
            default_month_label = MONTH_NAMES.get(selected_month.split("-")[1], selected_month)
        default_index = month_labels.index(default_month_label) if default_month_label in month_labels else 0
        selected_month_label = st.sidebar.selectbox("Mese", month_labels, index=default_index) if month_labels else None
        selected_month = month_map[selected_month_label] if selected_month_label else "Tutti"

        selected_category = st.sidebar.selectbox(
            "Categoria",
            category_options,
            index=category_options.index(selected_category) if selected_category in category_options else 0,
        )
        selected_payer = st.sidebar.selectbox(
            "Persona",
            payer_options,
            index=payer_options.index(selected_payer) if selected_payer in payer_options else 0,
        )
        selected_type = st.sidebar.selectbox(
            "Tipo spesa",
            type_options,
            index=type_options.index(selected_type) if selected_type in type_options else 0,
        )

    filtered = apply_filters(
        dataframe=dataframe,
        month_label=selected_month,
        category=selected_category,
        payer=selected_payer,
        expense_type=selected_type,
    )

    st.sidebar.markdown(
        f"<div class='small-note'>Spese mostrate: <strong>{len(filtered)}</strong></div>",
        unsafe_allow_html=True,
    )
    st.session_state.filters = {
        "month_label": selected_month,
        "category": selected_category,
        "payer": selected_payer,
        "expense_type": selected_type,
    }

    return filtered, selected_month


def render_dashboard(all_expenses: pd.DataFrame, all_incomes: pd.DataFrame, selected_month: str) -> None:
    current_user = st.session_state.current_user or {}
    current_username = current_user.get("username", "")
    month_data = all_expenses if selected_month == "Tutti" else all_expenses[all_expenses["month_label"] == selected_month]
    month_incomes = all_incomes if selected_month == "Tutti" else all_incomes[all_incomes["month_label"] == selected_month]
    metrics = build_dashboard_metrics(month_data, current_username)
    total_incomes = float(month_incomes["amount"].sum()) if not month_incomes.empty else 0.0

    st.subheader("Dashboard")
    col1, col2, col3, col4, col5 = st.columns(5)
    render_dashboard_card(
        col1,
        "Totale entrate",
        format_currency(total_incomes),
        "total_incomes",
    )
    render_dashboard_card(
        col2,
        "Totale spese mese",
        format_currency(metrics["total_month"]),
        "total_month",
    )
    render_dashboard_card(
        col3,
        "Mie spese personali",
        format_currency(metrics["my_personal"]),
        "my_personal",
    )
    render_dashboard_card(
        col4,
        "Spese condivise",
        format_currency(metrics["shared_total"]),
        "shared_total",
    )
    render_dashboard_card(
        col5,
        "Saldo coppia",
        build_balance_label(metrics["balance"]),
        "balance",
    )

    st.caption(
        "Saldo coppia: valore positivo = l'altra persona deve soldi a me; valore negativo = io devo soldi all'altra persona."
    )


def render_dashboard_card(column, title: str, value: str, metric_key: str) -> None:
    label = f"{title}\n{value}"
    with column:
        if st.button(
            label,
            key=f"dashboard_{metric_key}",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state.dashboard_metric = metric_key
            st.session_state.current_view = "dashboard_detail"
            st.rerun()


def render_create_form() -> None:
    category_options = get_categories()
    payer_usernames = get_usernames()
    if st.session_state.pop("reset_new_expense_form", False):
        for key in [
            "new_expense_name",
            "new_expense_amount",
            "new_expense_date",
            "new_expense_description",
            "new_expense_category",
            "new_expense_payer",
            "new_expense_type",
            "new_expense_split_type",
            "new_expense_share_percentage",
        ]:
            st.session_state.pop(key, None)

    col1, col2, col3 = st.columns([1.35, 0.85, 0.8])
    name = col1.text_input("Nome", placeholder="Spesa, bolletta, cena...", key="new_expense_name")
    amount = col2.number_input(
        "Importo",
        min_value=0.0,
        step=0.5,
        format="%.2f",
        key="new_expense_amount",
    )
    expense_date = col3.date_input(
        "Data",
        value=st.session_state.get("new_expense_date", date.today()),
        format="YYYY-MM-DD",
        key="new_expense_date",
    )

    category = st.selectbox("Categoria", category_options, key="new_expense_category")
    description = st.text_area(
        "Descrizione",
        placeholder="Facoltativa",
        help="Puoi lasciarla vuota se non ti serve.",
        key="new_expense_description",
    )

    col4, col5 = st.columns(2)
    payer = col4.selectbox("Persona che ha pagato", payer_usernames, key="new_expense_payer")
    expense_type = col5.selectbox("Tipo spesa", EXPENSE_TYPE_OPTIONS, key="new_expense_type")

    split_type = None
    my_share_percentage = None

    if expense_type == "Condivisa":
        split_type = st.selectbox("Divisione", SPLIT_TYPE_OPTIONS, key="new_expense_split_type")
        if split_type == "50/50":
            my_share_percentage = 50.0
        else:
            my_share_percentage = st.slider(
                "Percentuale della mia quota",
                min_value=0,
                max_value=100,
                value=int(st.session_state.get("new_expense_share_percentage", 50)),
                key="new_expense_share_percentage",
                help="La quota dell'altra persona viene calcolata automaticamente come complemento a 100.",
            )
    else:
        st.caption("Per le spese personali non serve impostare una divisione.")

    if st.button("Salva spesa", use_container_width=True, key="save_new_expense"):
        payload = {
            "amount": amount,
            "name": name,
            "description": description,
            "expense_type": expense_type,
            "my_share_percentage": my_share_percentage,
        }
        errors = validate_expense_data(payload)
        if errors:
            for error in errors:
                st.error(error)
        else:
            create_expense(
                expense_date=expense_date,
                amount=amount,
                name=name,
                category=category,
                description=description,
                payer=payer,
                expense_type=expense_type,
                split_type=split_type,
                my_share_percentage=my_share_percentage,
            )
            st.success("Spesa salvata con successo.")
            st.session_state.reset_new_expense_form = True
            st.rerun()


def render_expense_list(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        st.info("Nessuna spesa trovata con i filtri selezionati.")
        return

    display_frame = dataframe[
        [
            "id",
            "expense_date",
            "amount",
            "name",
            "category",
            "description",
            "payer",
            "expense_type",
            "split_type",
            "my_share_amount",
            "partner_share_amount",
        ]
    ].copy()
    display_frame["expense_date"] = display_frame["expense_date"].dt.strftime("%Y-%m-%d")
    display_frame["amount"] = display_frame["amount"].map(format_currency)
    display_frame["my_share_amount"] = display_frame["my_share_amount"].map(format_currency)
    display_frame["partner_share_amount"] = display_frame["partner_share_amount"].map(format_currency)
    display_frame["split_type"] = display_frame["split_type"].fillna("-")
    display_frame = display_frame.rename(
        columns={
            "id": "ID",
            "expense_date": "Data",
            "amount": "Importo",
            "name": "Nome",
            "category": "Categoria",
            "description": "Descrizione",
            "payer": "Pagato da",
            "expense_type": "Tipo spesa",
            "split_type": "Divisione",
            "my_share_amount": "Quota mia",
            "partner_share_amount": "Quota compagna",
        }
    )

    st.dataframe(
        display_frame,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID": st.column_config.NumberColumn(width="small"),
            "Data": st.column_config.TextColumn(width="small"),
            "Importo": st.column_config.TextColumn(width="small"),
            "Nome": st.column_config.TextColumn(width="medium"),
            "Categoria": st.column_config.TextColumn(width="small"),
            "Descrizione": st.column_config.TextColumn(width="medium"),
            "Pagato da": st.column_config.TextColumn(width="small"),
            "Tipo spesa": st.column_config.TextColumn(width="small"),
            "Divisione": st.column_config.TextColumn(width="small"),
            "Quota mia": st.column_config.TextColumn(width="small"),
            "Quota compagna": st.column_config.TextColumn(width="small"),
        },
    )


def render_edit_section(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        st.info("Seleziona un filtro diverso o aggiungi una spesa per modificarla.")
        return

    category_options = get_categories()
    payer_usernames = get_usernames()

    options = {
        build_expense_option_label(row): int(row["id"])
        for _, row in dataframe.iterrows()
    }

    option_labels = list(options.keys())
    preselected_expense_id = st.session_state.pop("preselected_expense_id", None)
    default_index = 0
    if preselected_expense_id is not None:
        for index, label in enumerate(option_labels):
            if options[label] == preselected_expense_id:
                default_index = index
                break

    selected_label = st.selectbox("Scegli una spesa", option_labels, index=default_index)
    selected_expense_id = options[selected_label]
    expense = get_expense_by_id(selected_expense_id)

    if expense is None:
        st.warning("La spesa selezionata non esiste piu.")
        return

    with st.form("edit_expense_form"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Nome modifica", value=expense.get("name", expense["description"]))
        expense_date = col2.date_input("Data modifica", value=expense["expense_date"], format="YYYY-MM-DD")

        col3, col4 = st.columns(2)
        category = col3.selectbox(
            "Categoria modifica",
            category_options,
            index=category_options.index(expense["category"]) if expense["category"] in category_options else 0,
        )
        amount = col4.number_input("Importo modifica", min_value=0.0, value=float(expense["amount"]), step=0.5)

        description = st.text_area("Descrizione modifica", value=expense["description"])

        col5, col6 = st.columns(2)
        payer = col5.selectbox(
            "Persona che ha pagato",
            payer_usernames,
            index=payer_usernames.index(expense["payer"]) if expense["payer"] in payer_usernames else 0,
        )
        expense_type = col6.selectbox(
            "Tipo spesa modifica",
            EXPENSE_TYPE_OPTIONS,
            index=EXPENSE_TYPE_OPTIONS.index(expense["expense_type"]),
        )

        split_type = None
        my_share_percentage = None

        if expense_type == "Condivisa":
            default_split = expense["split_type"] or "50/50"
            split_type = st.selectbox(
                "Divisione modifica",
                SPLIT_TYPE_OPTIONS,
                index=SPLIT_TYPE_OPTIONS.index(default_split),
            )
            if split_type == "50/50":
                my_share_percentage = 50.0
            else:
                default_share = int(expense["my_share_percentage"] or 50)
                my_share_percentage = st.slider(
                    "Percentuale della mia quota modifica",
                    min_value=0,
                    max_value=100,
                    value=default_share,
                )
        else:
            st.caption("Per le spese personali non serve impostare una divisione.")

        save_col, delete_col = st.columns(2)
        save_clicked = save_col.form_submit_button("Aggiorna spesa", use_container_width=True)
        delete_clicked = delete_col.form_submit_button("Elimina spesa", use_container_width=True)

        if save_clicked:
            payload = {
                "amount": amount,
                "name": name,
                "description": description,
                "expense_type": expense_type,
                "my_share_percentage": my_share_percentage,
            }
            errors = validate_expense_data(payload)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                update_expense(
                    expense_id=selected_expense_id,
                    expense_date=expense_date,
                    amount=amount,
                    name=name,
                    category=category,
                    description=description,
                    payer=payer,
                    expense_type=expense_type,
                    split_type=split_type,
                    my_share_percentage=my_share_percentage,
                )
                st.success("Spesa aggiornata con successo.")
                st.rerun()

        if delete_clicked:
            delete_expense(selected_expense_id)
            st.success("Spesa eliminata con successo.")
            st.rerun()


def render_charts(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        st.info("Non ci sono dati da visualizzare nei grafici.")
        return

    category_chart = dataframe.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    monthly_chart = (
        dataframe.groupby("month_label", as_index=False)["amount"].sum().sort_values("month_label")
    )
    monthly_chart = monthly_chart.rename(columns={"month_label": "Mese", "amount": "Totale"})

    left_chart, right_chart = st.columns(2)
    with left_chart:
        st.caption("Spese per categoria")
        st.bar_chart(category_chart.set_index("category"), color="#b45d34")

    with right_chart:
        st.caption("Andamento mensile")
        st.line_chart(monthly_chart.set_index("Mese"), color="#4f7a5c")


def render_export_section(dataframe: pd.DataFrame) -> None:
    csv_data = export_expenses_to_csv(dataframe)
    if not csv_data:
        st.info("Non ci sono dati da esportare con i filtri attuali.")
        return

    st.caption("Esporta le spese filtrate")
    csv_col, pdf_col = st.columns(2)
    csv_col.download_button(
        label="Scarica CSV",
        data=csv_data,
        file_name="spese_filtrate.csv",
        mime="text/csv",
        use_container_width=True,
    )
    if REPORTLAB_AVAILABLE:
        pdf_data = export_expenses_to_pdf(dataframe)
        pdf_col.download_button(
            label="Scarica PDF",
            data=pdf_data,
            file_name="spese_filtrate.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        pdf_col.button(
            "Scarica PDF",
            disabled=True,
            use_container_width=True,
            help="Installa reportlab per attivare l'esportazione PDF.",
        )


def render_category_dashboard(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        st.info("Non ci sono spese da analizzare nelle categorie con i filtri attuali.")
        return

    summary = build_category_summary(dataframe)
    if summary.empty:
        st.info("Non ci sono categorie da mostrare.")
        return

    search_term = st.text_input(
        "Cerca categoria",
        placeholder="Scrivi una categoria, ad esempio Casa o Spesa",
        help="Filtra le categorie visibili e apri il dettaglio cliccando sulla card.",
    ).strip()

    filtered_summary = summary.copy()
    if search_term:
        filtered_summary = filtered_summary[
            filtered_summary["category"].str.contains(search_term, case=False, na=False)
        ]

    if filtered_summary.empty:
        st.info("Nessuna categoria trovata con questa ricerca.")
        return

    with st.expander("Panoramica categorie", expanded=False):
        columns = st.columns(3, gap="medium")
        for index, (_, row) in enumerate(filtered_summary.iterrows()):
            category_name = str(row["category"])
            icon = CATEGORY_ICONS.get(category_name, "●")
            label = (
                f"{icon}\n"
                f"{category_name}\n"
                f"{format_currency(float(row['totale']))}"
            )
            with columns[index % 3]:
                if st.button(
                    label,
                    key=f"open_category_{category_name}",
                    use_container_width=True,
                    type="secondary",
                ):
                    st.session_state.selected_category = category_name
                    st.session_state.current_view = "category_detail"
                    st.rerun()

    render_recent_expenses_expander(dataframe)


def render_recent_expenses_expander(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        return

    cutoff_date = pd.Timestamp(date.today()) - pd.Timedelta(days=9)
    recent_expenses = dataframe[dataframe["expense_date"] >= cutoff_date].copy()
    recent_expenses = recent_expenses.sort_values(by=["expense_date", "id"], ascending=[False, False]).head(10)

    with st.expander("Spese recenti", expanded=False):
        if recent_expenses.empty:
            st.info("Nessuna spesa negli ultimi 10 giorni con i filtri attivi.")
            return

        for _, row in recent_expenses.iterrows():
            title = str(row.get("name") or row.get("description") or "Spesa")
            details = (
                f"{row['expense_date'].strftime('%Y-%m-%d')}  |  "
                f"{row['category']}  |  "
                f"{format_currency(float(row['amount']))}"
            )
            extra = f"{row['payer']}  |  {row['expense_type']}"

            content_col, action_col = st.columns([0.92, 0.08], vertical_alignment="center")
            with content_col:
                st.markdown(f"**{title}**")
                st.caption(details)
                st.caption(extra)
            with action_col:
                if st.button("✎", key=f"edit_recent_{int(row['id'])}", help="Modifica spesa"):
                    st.session_state.preselected_expense_id = int(row["id"])
                    st.session_state.current_view = "edit_expense"
                    st.rerun()
            st.divider()




def render_operation_cards(dataframe: pd.DataFrame) -> None:
    cards = [
        {
            "title": "Nuova spesa",
            "subtitle": "Inserisci una nuova spesa personale o condivisa.",
            "view": "new_expense",
        },
        {
            "title": "Nuova entrata",
            "subtitle": "Registra una nuova entrata mensile.",
            "view": "new_income",
        },
        {
            "title": "Modifica spesa",
            "subtitle": "Apri la schermata per aggiornare o eliminare un movimento.",
            "view": "edit_expense",
        },
        {
            "title": "Aggiungi categoria",
            "subtitle": "Crea una nuova categoria da usare nei prossimi inserimenti.",
            "view": "add_category",
        },
    ]

    columns = st.columns(2, gap="large")
    for index, card in enumerate(cards):
        with columns[index % 2]:
            st.markdown(
                """
                <style>
                    div.stButton > button[kind="secondary"] {
                        min-height: 116px !important;
                        padding-top: 0.95rem !important;
                        padding-bottom: 0.95rem !important;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )
            label = card["title"]
            if st.button(
                label.upper(),
                key=f"operation_card_{card['view']}",
                use_container_width=True,
                type="secondary",
            ):
                st.session_state.current_view = card["view"]
                st.rerun()


def render_operation_detail_page(filtered_expenses: pd.DataFrame, filtered_incomes: pd.DataFrame) -> None:
    current_view = st.session_state.get("current_view", "home")
    view_config = {
        "new_expense": (
            "Nuova spesa",
            "Compila il form qui sotto per registrare una nuova spesa.",
        ),
        "new_income": (
            "Nuova entrata",
            "Compila il form qui sotto per registrare una nuova entrata.",
        ),
        "edit_expense": (
            "Modifica spesa",
            "Seleziona una spesa esistente e aggiorna i campi necessari.",
        ),
        "add_category": (
            "Aggiungi categoria",
            "Crea una nuova categoria personalizzata per organizzare meglio le spese.",
        ),
    }

    if current_view not in view_config:
        st.session_state.current_view = "home"
        st.session_state.current_section = "Home"
        st.rerun()

    title, subtitle = view_config[current_view]
    st.markdown(
        f"""
        <div class="hero-card">
            <div style="letter-spacing:0.08em; text-transform:uppercase; font-size:0.82rem; opacity:0.78; margin-bottom:0.45rem;">
                Operazioni
            </div>
            <h1 style="margin:0; font-size:2rem;">{title}</h1>
            <p style="margin:0.8rem 0 0 0; max-width:780px; opacity:0.92; font-size:1rem;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, info_col = st.columns([0.08, 0.92])
    with back_col:
        back_clicked = render_back_circle_button("back_to_operations")
    if back_clicked:
        st.session_state.current_view = "home"
        st.session_state.current_section = "Home"
        st.rerun()
    info_col.caption("Usa la sidebar per mantenere i filtri attivi anche nelle schermate operative.")

    if current_view == "new_expense":
        render_create_form()
    elif current_view == "new_income":
        open_section("Nuova entrata", "Inserimento rapido di una nuova entrata.")
        render_create_income_form()
        close_section()
    elif current_view == "edit_expense":
        open_section("Modifica spesa", "Aggiorna o elimina una spesa esistente.")
        render_edit_section(filtered_expenses)
        close_section()
    elif current_view == "add_category":
        open_section("Aggiungi categoria", "Una nuova categoria sara disponibile nei form delle spese.")
        render_add_category_form()
        close_section()


def render_add_category_form() -> None:
    with st.form("add_category_form", clear_on_submit=True):
        category_name = st.text_input("Nome nuova categoria")
        submitted = st.form_submit_button("Salva categoria", use_container_width=True)
        if submitted:
            success, message = add_category(category_name)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    existing_categories = get_categories()
    st.caption("Categorie disponibili")
    if not existing_categories:
        st.info("Non ci sono categorie disponibili.")
        return

    for category_name in existing_categories:
        name_col, action_col = st.columns([0.9, 0.1], vertical_alignment="center")
        with name_col:
            st.write(category_name)
        with action_col:
            if st.button("✕", key=f"delete_category_{category_name}", help="Elimina categoria"):
                success, message = delete_category(category_name)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)


def render_create_income_form() -> None:
    with st.form("create_income_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        income_date = col1.date_input("Data entrata", value=date.today(), format="YYYY-MM-DD")
        amount = col2.number_input("Importo entrata", min_value=0.0, step=50.0, format="%.2f")

        source = st.text_input("Fonte entrata", placeholder="Stipendio, freelance, rimborso...")
        description = st.text_input("Descrizione entrata")
        submitted = st.form_submit_button("Salva entrata", use_container_width=True)
        if submitted:
            payload = {"amount": amount, "source": source, "description": description}
            errors = validate_income_data(payload)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                create_income(
                    income_date=income_date,
                    amount=amount,
                    source=source,
                    description=description,
                )
                st.success("Entrata salvata con successo.")
                st.rerun()


def render_incomes_section(dataframe: pd.DataFrame) -> None:
    if dataframe.empty:
        st.info("Nessuna entrata trovata per il periodo selezionato.")
        return

    left, right = st.columns(2)
    left.metric("Totale entrate", format_currency(float(dataframe["amount"].sum())))
    right.metric("Numero entrate", int(len(dataframe)))

    for _, row in dataframe.iterrows():
        st.markdown(
            f"""
            <div class="expense-detail-card">
                <div class="expense-detail-title">{format_currency(float(row['amount']))} · {row['source']}</div>
                <div class="expense-detail-meta">
                    {row['income_date'].strftime("%Y-%m-%d")} · {row['description']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_income_expense_analysis(all_incomes: pd.DataFrame, all_expenses: pd.DataFrame) -> None:
    st.caption("Confronto mensile tra entrate e uscite")
    summary = build_income_vs_expense_summary(all_incomes, all_expenses)
    if summary.empty:
        st.info("Non ci sono abbastanza dati per confrontare entrate e uscite.")
        return

    latest = summary.iloc[-1]
    col1, col2, col3 = st.columns(3)
    col1.metric("Entrate ultimo mese", format_currency(float(latest["Entrate"])))
    col2.metric("Uscite ultimo mese", format_currency(float(latest["Uscite"])))
    col3.metric("Saldo ultimo mese", format_currency(float(latest["Saldo"])))

    chart_data = summary.rename(columns={"month_label": "Mese"}).set_index("Mese")
    st.line_chart(chart_data[["Entrate", "Uscite", "Saldo"]])


def render_dashboard_detail_page(all_expenses: pd.DataFrame, all_incomes: pd.DataFrame, selected_month: str) -> None:
    metric_key = st.session_state.get("dashboard_metric")
    current_user = st.session_state.current_user or {}
    current_username = current_user.get("username", "")
    month_data = all_expenses if selected_month == "Tutti" else all_expenses[all_expenses["month_label"] == selected_month]
    month_incomes = all_incomes if selected_month == "Tutti" else all_incomes[all_incomes["month_label"] == selected_month]

    view_map = {
        "total_incomes": (
            "Totale entrate",
            "Tutte le entrate del periodo selezionato.",
            month_incomes,
            "income",
        ),
        "total_month": (
            "Totale spese mese",
            "Tutte le spese del periodo selezionato.",
            month_data,
            "expense",
        ),
        "my_personal": (
            "Mie spese personali",
            "Solo le spese personali pagate da me.",
            month_data[(month_data["expense_type"] == "Personale") & (month_data["payer"] == current_username)],
            "expense",
        ),
        "shared_total": (
            "Spese condivise",
            "Tutte le spese condivise del periodo selezionato.",
            month_data[month_data["expense_type"] == "Condivisa"],
            "expense",
        ),
        "balance": (
            "Saldo coppia",
            "Dettaglio delle spese condivise che compongono il saldo tra voi due.",
            month_data[month_data["expense_type"] == "Condivisa"],
            "expense",
        ),
    }

    if metric_key not in view_map:
        st.session_state.current_view = "home"
        st.rerun()

    title, subtitle, detail_frame, detail_type = view_map[metric_key]
    st.markdown(
        f"""
        <div class="hero-card">
            <div style="letter-spacing:0.08em; text-transform:uppercase; font-size:0.82rem; opacity:0.78; margin-bottom:0.45rem;">
                Dashboard
            </div>
            <h1 style="margin:0; font-size:2rem;">{title}</h1>
            <p style="margin:0.8rem 0 0 0; max-width:780px; opacity:0.92; font-size:1rem;">
                {subtitle}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, info_col = st.columns([0.08, 0.92])
    with back_col:
        back_clicked = render_back_circle_button("back_to_dashboard")
    if back_clicked:
        st.session_state.current_view = "home"
        st.rerun()
    info_col.caption(f"Mese attivo nella dashboard: {selected_month}")

    open_section(title, "Elenco delle spese che compongono la voce selezionata.")
    if detail_frame.empty:
        st.info("Nessuna spesa trovata per questa voce della dashboard.")
    else:
        if detail_type == "income":
            render_incomes_section(detail_frame)
        else:
            render_expense_list(detail_frame)
    close_section()


def render_profile_page() -> None:
    current_user = st.session_state.get("current_user") or {}
    user_id = current_user.get("id")
    user = get_user_by_id(user_id) if user_id else None

    if user is None:
        st.session_state.current_view = "home"
        st.rerun()

    st.markdown(
        """
        <div class="hero-card">
            <div style="letter-spacing:0.08em; text-transform:uppercase; font-size:0.82rem; opacity:0.78; margin-bottom:0.45rem;">
                Profilo
            </div>
            <h1 style="margin:0; font-size:2rem;">Dati utente</h1>
            <p style="margin:0.8rem 0 0 0; max-width:780px; opacity:0.92; font-size:1rem;">
                Qui puoi modificare i dati personali salvati per il tuo accesso.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, info_col = st.columns([0.08, 0.92])
    with back_col:
        back_clicked = render_back_circle_button("back_to_home_from_profile")
    if back_clicked:
        st.session_state.current_view = "home"
        st.rerun()
    info_col.caption("I dati salvati qui vengono riutilizzati per il login e per il profilo.")

    open_section("Profilo utente", "Aggiorna i dati salvati per questo account.")
    with st.form("profile_form"):
        full_name = st.text_input("Nome completo", value=user.get("full_name", ""))
        username = st.text_input("Username", value=user.get("username", ""))
        email = st.text_input("Email", value=user.get("email", ""))
        new_password = st.text_input("Nuova password", type="password", help="Lascia vuoto per non cambiarla.")
        submitted = st.form_submit_button("Salva modifiche", use_container_width=True)

        if submitted:
            success, message, updated_user = update_user_profile(
                user_id=user["id"],
                full_name=full_name,
                username=username,
                email=email,
                new_password=new_password,
            )
            if success and updated_user is not None:
                st.session_state.current_user = updated_user
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    close_section()


def render_category_detail_page(filtered_expenses: pd.DataFrame) -> None:
    selected_category = st.session_state.get("selected_category")
    if not selected_category:
        st.session_state.current_view = "home"
        st.session_state.current_section = "Uscite"
        st.rerun()

    category_expenses = filtered_expenses[filtered_expenses["category"] == selected_category].copy()

    st.markdown(
        f"""
        <div class="hero-card">
            <div style="letter-spacing:0.08em; text-transform:uppercase; font-size:0.82rem; opacity:0.78; margin-bottom:0.45rem;">
                Dettaglio categoria
            </div>
            <h1 style="margin:0; font-size:2rem;">{selected_category}</h1>
            <p style="margin:0.8rem 0 0 0; max-width:780px; opacity:0.92; font-size:1rem;">
                Vista dedicata della categoria selezionata. Qui trovi solo le spese di questa categoria
                con i filtri attivi della sidebar gia applicati.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, info_col = st.columns([0.08, 0.92])
    with back_col:
        back_clicked = render_back_circle_button("back_to_categories")
    if back_clicked:
        st.session_state.current_view = "home"
        st.session_state.current_section = "Uscite"
        st.rerun()
    info_col.caption("La sidebar continua a controllare mese, persona e tipo spesa.")

    if category_expenses.empty:
        st.info("Nessuna spesa trovata per questa categoria con i filtri correnti.")
        return

    summary = build_category_summary(category_expenses)
    category_row = summary.iloc[0]

    stat1, stat2, stat3, stat4 = st.columns(4)
    stat1.metric("Totale categoria", format_currency(float(category_row["totale"])))
    stat2.metric("Numero spese", int(category_row["numero_spese"]))
    stat3.metric("Quota mia", format_currency(float(category_row["quota_mia"])))
    stat4.metric("Quota compagna", format_currency(float(category_row["quota_compagna"])))

    open_section("Spese della categoria", "Elenco dettagliato dei movimenti appartenenti a questa categoria.")
    for _, row in category_expenses.iterrows():
        split_label = row["split_type"] if pd.notna(row["split_type"]) else "-"
        expense_name = str(row.get("name") or row.get("description") or "Spesa")
        description = str(row.get("description") or "").strip()
        with st.container(border=True):
            st.markdown(f"**{expense_name}**")
            meta_line = (
                f"Data: {row['expense_date'].strftime('%Y-%m-%d')}  |  "
                f"Importo: {format_currency(float(row['amount']))}  |  "
                f"Pagato da: {row['payer']}"
            )
            st.caption(meta_line)
            details_line = (
                f"Tipo: {row['expense_type']}  |  "
                f"Divisione: {split_label}  |  "
                f"Quota mia: {format_currency(float(row['my_share_amount']))}  |  "
                f"Quota compagna: {format_currency(float(row['partner_share_amount']))}"
            )
            st.caption(details_line)
            if description:
                st.caption(f"Note: {description}")
    close_section()


def build_expense_option_label(row: pd.Series) -> str:
    date_label = row["expense_date"].strftime("%Y-%m-%d")
    name_label = row.get("name", row["description"])
    return f"#{int(row['id'])} | {date_label} | {name_label} | {format_currency(float(row['amount']))}"


def build_balance_label(balance: float) -> str:
    if balance > 0:
        return f"L'altra persona deve {format_currency(balance)}"
    if balance < 0:
        return f"Io devo {format_currency(abs(balance))}"
    return "In pari"


def open_section(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def close_section() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
