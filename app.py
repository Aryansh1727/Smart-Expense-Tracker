
import json
from datetime import date

import pandas as pd
import plotly.express as px
import streamlit as st

from expense_manager import ExpenseManager

# CURSOR EFFECT — SUBTLE VIOLET TRAIL

st.html(
    """
    <div id="cursor-trail-root" aria-hidden="true"></div>
    <style>
      #cursor-trail-root {
        position: fixed;
        inset: 0;
        z-index: 999999;
        pointer-events: none;
        overflow: hidden;
      }
      .cursor-trail-dot {
        position: fixed;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: rgba(167, 139, 250, 0.92);
        box-shadow: 0 0 10px rgba(139, 92, 246, 0.75),
                    0 0 22px rgba(139, 92, 246, 0.32);
        pointer-events: none;
        transform: translate(-50%, -50%) scale(1);
        animation: cursor-dot-fade 520ms ease-out forwards;
        will-change: transform, opacity;
      }
      @keyframes cursor-dot-fade {
        0% { opacity: 0.92; transform: translate(-50%, -50%) scale(1); }
        100% { opacity: 0; transform: translate(-50%, -50%) scale(0.18); }
      }
      @media (prefers-reduced-motion: reduce) {
        .cursor-trail-dot { animation-duration: 1ms; }
      }
    </style>
    <script>
      (() => {
        const root = document.getElementById("cursor-trail-root");
        if (!root || root.dataset.ready === "true") return;
        root.dataset.ready = "true";
        let lastTime = 0;
        document.addEventListener("pointermove", (event) => {
          const now = performance.now();
          if (now - lastTime < 24) return;
          lastTime = now;
          const dot = document.createElement("span");
          dot.className = "cursor-trail-dot";
          dot.style.left = event.clientX + "px";
          dot.style.top = event.clientY + "px";
          root.appendChild(dot);
          window.setTimeout(() => dot.remove(), 560);
        }, { passive: true });
      })();
    </script>
    """,
    unsafe_allow_javascript=True,
)

# CURSOR EFFECT — AMBIENT BACKGROUND SPOTLIGHT

st.html(
    """
    <script>
      (() => {
        const doc = window.parent.document;
        const app = doc.querySelector('.stApp');
        if (!app || app.dataset.spotlightReady === 'true') return;
        app.dataset.spotlightReady = 'true';

        let scheduled = false;
        let lastX = -1;
        let lastY = -1;

        doc.addEventListener('pointermove', (event) => {
          lastX = event.clientX;
          lastY = event.clientY;
          if (scheduled) return;
          scheduled = true;

          window.requestAnimationFrame(() => {
            app.style.setProperty('--cursor-x', `${lastX}px`);
            app.style.setProperty('--cursor-y', `${lastY}px`);
            scheduled = false;
          });
        }, { passive: true });

        doc.addEventListener('pointerleave', () => {
          app.style.setProperty('--cursor-x', '50vw');
          app.style.setProperty('--cursor-y', '28vh');
        });
      })();
    </script>
    """,
    unsafe_allow_javascript=True,
)

# PAGE CONFIGURATION

st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CUSTOM UI THEME — PREMIUM DARK FINTECH

st.markdown("""
<style>
    html { color-scheme: dark; }
    :root {
        --bg: #0B0D12;
        --panel: #141720;
        --panel-soft: #191D29;
        --violet: #8B5CF6;
        --violet-light: #A78BFA;
        --green: #34D399;
        --red: #FB7185;
        --text: #F3F4F6;
        --muted: #9CA3AF;
        --border: #292D3A;
    }
    .stApp {
        background: radial-gradient(ellipse at top right, #1A1530 0%, #0B0D12 42%);
        color: var(--text);
    }
    [data-testid="stHeader"] {
        background: rgba(11, 13, 18, 0.92);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #11131B 0%, #171426 100%);
        border-right: 1px solid #29243A;
    }
    [data-testid="stSidebar"] * {
        color: #F3F4F6;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255,255,255,0.035);
        border: 1px solid transparent;
        border-radius: 12px;
        padding: 0.55rem 0.7rem;
        margin-bottom: 0.3rem;
        transition: background 0.15s ease, border 0.15s ease;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(139,92,246,0.13);
        border-color: rgba(167,139,250,0.25);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] [aria-checked="true"] {
        background: rgba(139,92,246,0.17);
    }
    h1, h2, h3, h4 {
        color: #F9FAFB !important;
        letter-spacing: -0.035em;
    }
    p, label, [data-testid="stMarkdownContainer"] {
        color: #D1D5DB;
    }
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #191D29 0%, #131620 100%);
        border: 1px solid #2B2F3E;
        border-radius: 18px;
        padding: 1.15rem 1.2rem;
        box-shadow: 0 8px 28px rgba(0,0,0,0.18);
    }
    [data-testid="stMetricLabel"] p {
        color: #A1A1AA !important;
        font-weight: 600;
        font-size: 0.88rem;
    }
    [data-testid="stMetricValue"] {
        color: #F9FAFB;
    }
    [data-testid="stMetricDelta"] {
        color: #34D399;
    }
    [data-testid="stForm"] {
        background: #141720;
        border: 1px solid #292D3A;
        border-radius: 18px;
        padding: 1.3rem;
    }
    input, textarea {
        background-color: #191D29 !important;
        color: #F9FAFB !important;
    }
    [data-baseweb="select"] > div {
        background-color: #191D29;
        border-color: #343849;
        color: #F9FAFB;
        border-radius: 10px;
    }
    .stButton > button, .stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
        border-radius: 11px;
        font-weight: 650;
        border: 1px solid #8B5CF6;
        transition: all 0.15s ease;
    }
    .stButton > button[kind="primary"],
    [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%);
        color: #FFFFFF;
        border: 1px solid #A78BFA;
    }
    .stButton > button:hover, .stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
        border-color: #C4B5FD;
        color: #FFFFFF;
        box-shadow: 0 0 0 3px rgba(139,92,246,0.13);
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #292D3A;
        border-radius: 14px;
        overflow: hidden;
    }
    [data-testid="stProgress"] > div {
        background: #292D3A;
        border-radius: 99px;
    }
    [data-testid="stProgress"] > div > div {
        background: linear-gradient(90deg, #8B5CF6, #A78BFA);
        border-radius: 99px;
    }
    [data-testid="stAlert"] {
        border-radius: 12px;
        background-color: #191D29;
    }
    hr {
        border-color: #292D3A;
    }
    [data-testid="stCaptionContainer"] {
        color: #9CA3AF;
    }

    /* Cursor-following ambient spotlight */
    .stApp {
        --cursor-x: 50vw;
        --cursor-y: 28vh;
        background:
            radial-gradient(
                420px circle at var(--cursor-x) var(--cursor-y),
                rgba(139, 92, 246, 0.105),
                transparent 72%
            ),
            radial-gradient(ellipse at top right, #1A1530 0%, #0B0D12 42%),
            #0B0D12;
        background-attachment: fixed;
    }

    .dashboard-topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin: 0.15rem 0 1.25rem 0;
    }
    .dashboard-brand {
        color: #A78BFA;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }
    .dashboard-heading {
        color: #F9FAFB;
        font-size: clamp(1.8rem, 3vw, 2.55rem);
        line-height: 1.1;
        font-weight: 800;
        letter-spacing: -0.045em;
        margin: 0.35rem 0 0.45rem 0;
    }
    .dashboard-subheading {
        color: #9CA3AF;
        font-size: 0.98rem;
        margin: 0;
    }
    .dashboard-month-pill {
        display: inline-block;
        padding: 0.55rem 0.85rem;
        border: 1px solid #38304F;
        border-radius: 999px;
        background: rgba(139,92,246,0.10);
        color: #D8CCFF;
        font-size: 0.82rem;
        font-weight: 650;
        white-space: nowrap;
    }
    .balance-hero {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(167,139,250,0.34);
        border-radius: 22px;
        padding: 1.45rem 1.55rem;
        background: radial-gradient(circle at 88% 8%, rgba(139,92,246,0.38), transparent 34%),
                    linear-gradient(135deg, #21183A 0%, #171827 52%, #131620 100%);
        box-shadow: 0 14px 40px rgba(0,0,0,0.22);
        min-height: 185px;
    }
    .balance-label {
        color: #C4B5FD;
        font-size: 0.86rem;
        font-weight: 650;
        letter-spacing: 0.02em;
    }
    .balance-value {
        color: #FFFFFF;
        font-size: clamp(2rem, 4vw, 3.05rem);
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -0.045em;
        margin: 0.55rem 0 0.65rem 0;
    }
    .balance-note {
        color: #C4C4D4;
        font-size: 0.88rem;
    }
    .balance-orb {
        position: absolute;
        right: -25px;
        bottom: -68px;
        width: 205px;
        height: 205px;
        border-radius: 50%;
        border: 1px solid rgba(196,181,253,0.28);
        box-shadow: 0 0 0 22px rgba(139,92,246,0.06), 0 0 0 48px rgba(139,92,246,0.04);
        pointer-events: none;
    }
    /* Subtle interactive hover effects for a premium, responsive feel */
    [data-testid="stMetric"],
    .summary-card,
    .balance-hero,
    .panel-shell,
    [data-testid="stForm"] {
        transition: transform 180ms ease, border-color 180ms ease,
                    box-shadow 180ms ease, background 180ms ease;
    }
    [data-testid="stMetric"]:hover,
    .summary-card:hover {
        transform: translateY(-3px);
        border-color: rgba(167,139,250,0.65);
        box-shadow: 0 10px 32px rgba(139,92,246,0.13),
                    0 0 0 1px rgba(139,92,246,0.08);
    }
    .balance-hero:hover {
        border-color: rgba(196,181,253,0.65);
        box-shadow: 0 16px 44px rgba(139,92,246,0.17);
    }
    .panel-shell:hover,
    [data-testid="stForm"]:hover {
        border-color: rgba(167,139,250,0.35);
    }
    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible,
    [data-testid="stFormSubmitButton"] > button:focus-visible {
        outline: 2px solid #C4B5FD;
        outline-offset: 3px;
    }
    @media (prefers-reduced-motion: reduce) {
        [data-testid="stMetric"],
        .summary-card,
        .balance-hero,
        .panel-shell,
        [data-testid="stForm"] {
            transition: none;
        }
    }

    .summary-card {
        border: 1px solid #292D3A;
        border-radius: 17px;
        padding: 1rem 1.05rem;
        background: linear-gradient(145deg, #191D29 0%, #131620 100%);
        min-height: 124px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.13);
    }
    .summary-card-label {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        color: #A1A1AA;
        font-size: 0.83rem;
        font-weight: 650;
        margin-bottom: 0.75rem;
    }
    .summary-card-value {
        color: #F9FAFB;
        font-size: clamp(1.1rem, 1.6vw, 1.55rem);
        font-weight: 780;
        letter-spacing: -0.035em;
        overflow-wrap: anywhere;
    }
    .summary-card-foot {
        color: #8B91A1;
        font-size: 0.77rem;
        margin-top: 0.35rem;
    }
    .dashboard-section-title {
        color: #F3F4F6;
        font-size: 1.08rem;
        font-weight: 750;
        margin: 0.15rem 0 0.15rem 0;
    }
    .dashboard-section-caption {
        color: #8B91A1;
        font-size: 0.83rem;
        margin-bottom: 0.8rem;
    }
    .panel-shell {
        background: #141720;
        border: 1px solid #292D3A;
        border-radius: 18px;
        padding: 1rem 1.05rem 0.65rem 1.05rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    .transaction-chip {
        display: inline-block;
        border-radius: 999px;
        padding: 0.25rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 700;
    }
    @media (max-width: 768px) {
        .dashboard-topline { align-items: flex-start; flex-direction: column; }
        .balance-hero { padding: 1.15rem; }
        .summary-card { min-height: 112px; }
    }

    @media (max-width: 768px) {
        [data-testid="stMetric"] {
            padding: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# INITIALIZE EXPENSE MANAGER

@st.cache_resource
def get_manager():
    return ExpenseManager()


try:
    manager = get_manager()
except (ValueError, OSError) as error:
    st.error(f"Unable to load saved transactions: {error}")
    st.stop()

# CONSTANTS

EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Education",
    "Entertainment",
    "Bills",
    "Health",
    "Travel",
    "Other",
]

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Investment",
    "Other",
]

# SIDEBAR NAVIGATION

st.sidebar.markdown("## ✦ SmartSpend")
st.sidebar.caption("PERSONAL FINANCE")
st.sidebar.divider()
st.sidebar.markdown("### Navigation")

page = st.sidebar.radio(
    "Choose a section",
    [
        "Dashboard",
        "Add Transaction",
        "Transaction History",
        "Budgets",
    ],
)

today = date.today()

month_options = [
    f"{year}-{month:02d}"
    for year in range(today.year - 3, today.year + 2)
    for month in range(1, 13)
]

current_month = f"{today.year}-{today.month:02d}"

st.sidebar.selectbox(
    "Select month for analysis",
    options=month_options,
    index=month_options.index(current_month),
    key="selected_month",
)

selected_month = st.session_state.selected_month

# HELPER FUNCTIONS

def money(amount):
    """Format an amount in Indian Rupees."""
    return f"₹{amount:,.2f}"

def get_month_dataframe(month):
    """Return transactions for a selected month."""
    records = [
        record
        for record in manager.get_transactions()
        if record["date"].startswith(month)
    ]

    columns = [
        "id",
        "amount",
        "type",
        "category",
        "description",
        "date",
    ]

    df = pd.DataFrame(records, columns=columns)

    if not df.empty:
        df["amount"] = pd.to_numeric(
            df["amount"], errors="coerce"
        ).fillna(0)

    return df

def display_summary(summary):
    """Display financial summary cards."""
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Income",
        money(summary["income"]),
    )
    col2.metric(
        "Total Expenses",
        money(summary["expenses"]),
    )
    col3.metric(
        "Balance",
        money(summary["balance"]),
        delta=(
            "Positive balance"
            if summary["balance"] >= 0
            else "Expenses exceed income"
        ),
    )
    col4.metric(
        "Savings Rate",
        f'{summary["savings_rate"]:.1f}%',
    )

def load_budgets():
    """Load budgets without silently replacing invalid data."""
    budget_file = manager.data_file.parent / "budgets.json"

    if not budget_file.exists():
        return {}

    try:
        with budget_file.open("r", encoding="utf-8") as file:
            budgets = json.load(file)

        if not isinstance(budgets, dict):
            raise ValueError("Budget data must be a JSON object.")

        return budgets

    except (json.JSONDecodeError, OSError, ValueError) as error:
        st.error(f"Unable to load saved budgets: {error}")
        return None

def save_budgets(budgets):
    """Save budgets using a temporary file."""
    budget_file = manager.data_file.parent / "budgets.json"
    temporary_file = budget_file.with_suffix(".tmp")

    try:
        budget_file.parent.mkdir(parents=True, exist_ok=True)

        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(budgets, file, indent=4)

        temporary_file.replace(budget_file)
        return True

    except OSError as error:
        if temporary_file.exists():
            temporary_file.unlink(missing_ok=True)

        st.error(f"Unable to save budgets: {error}")
        return False

# DASHBOARD

if page == "Dashboard":
    summary = manager.get_summary(selected_month)
    df = get_month_dataframe(selected_month)

    month_label = date.fromisoformat(f"{selected_month}-01").strftime("%B %Y")
    balance_label = "You're in the green this month" if summary["balance"] >= 0 else "Your expenses are higher than income"

    st.markdown(
        f"""
        <div class="dashboard-topline">
            <div>
                <div class="dashboard-brand">✦ SmartSpend / Overview</div>
                <div class="dashboard-heading">Your money, in focus.</div>
                <p class="dashboard-subheading">Track your cash flow, understand your spending, and stay on top of your goals.</p>
            </div>
            <div class="dashboard-month-pill">◷ &nbsp; {month_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="balance-hero">
            <div class="balance-orb"></div>
            <div class="balance-label">MONTHLY NET BALANCE</div>
            <div class="balance-value">{money(summary["balance"])}</div>
            <div class="balance-note">{balance_label} · Based on your recorded income and expenses</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 14px'></div>", unsafe_allow_html=True)

    metric_cols = st.columns(3)
    metric_cards = [
        ("↗", "Total income", money(summary["income"]), "Money received this month", "#34D399"),
        ("↘", "Total expenses", money(summary["expenses"]), "Money spent this month", "#FB7185"),
        ("◈", "Savings rate", f'{summary["savings_rate"]:.1f}%', "Of recorded income retained", "#A78BFA"),
    ]
    for col, (symbol, label, value, foot, accent) in zip(metric_cols, metric_cards):
        with col:
            st.markdown(
                f"""
                <div class="summary-card">
                    <div class="summary-card-label"><span style="color:{accent};font-size:1.05rem">{symbol}</span>{label}</div>
                    <div class="summary-card-value">{value}</div>
                    <div class="summary-card-foot">{foot}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="panel-shell">', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-section-title">Your financial activity</div>', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-section-caption">Charts and recent activity will appear once you add transactions.</div>', unsafe_allow_html=True)
        st.info("No transactions found for this month. Go to Add Transaction to get started.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        expenses = df[df["type"] == "Expense"].copy()
        chart_col1, chart_col2 = st.columns([1, 1])

        with chart_col1:
            st.markdown(
                '<div class="dashboard-section-title">Spending breakdown</div>'
                '<div class="dashboard-section-caption">Which categories are using your money?</div>',
                unsafe_allow_html=True,
            )
            if not expenses.empty:
                category_data = (
                    expenses.groupby("category")["amount"]
                    .sum()
                    .reset_index()
                    .sort_values("amount", ascending=False)
                )
                fig = px.pie(
                    category_data,
                    names="category",
                    values="amount",
                    hole=0.68,
                    color_discrete_sequence=[
                        "#8B5CF6", "#34D399", "#FB7185", "#60A5FA",
                        "#FBBF24", "#22D3EE", "#F472B6", "#A1A1AA",
                    ],
                )
                fig.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    marker=dict(line=dict(color="#141720", width=3)),
                    hovertemplate="<b>%{label}</b><br>₹%{value:,.2f}<extra></extra>",
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#E5E7EB",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="top", y=-0.08, xanchor="left", x=0),
                    margin=dict(l=4, r=4, t=8, b=8),
                    height=310,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expenses recorded for this month.")

        with chart_col2:
            st.markdown(
                '<div class="dashboard-section-title">Income vs. expenses</div>'
                '<div class="dashboard-section-caption">Compare what came in with what went out.</div>',
                unsafe_allow_html=True,
            )
            comparison = pd.DataFrame({
                "Type": ["Income", "Expenses"],
                "Amount": [summary["income"], summary["expenses"]],
            })
            fig = px.bar(
                comparison,
                x="Type",
                y="Amount",
                color="Type",
                color_discrete_map={"Income": "#34D399", "Expenses": "#FB7185"},
                text="Amount",
            )
            fig.update_traces(
                marker_line_width=0,
                texttemplate="₹%{y:,.0f}",
                textposition="outside",
                cliponaxis=False,
                hovertemplate="<b>%{x}</b><br>₹%{y:,.2f}<extra></extra>",
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E5E7EB",
                showlegend=False,
                xaxis_title=None,
                yaxis_title=None,
                yaxis=dict(showgrid=True, gridcolor="#292D3A", zeroline=False),
                xaxis=dict(showgrid=False),
                margin=dict(l=8, r=8, t=20, b=8),
                height=310,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        st.markdown(
            '<div class="dashboard-section-title">Recent transactions</div>'
            '<div class="dashboard-section-caption">Your latest five entries for this month.</div>',
            unsafe_allow_html=True,
        )
        recent = (
            df.sort_values(["date"], ascending=False)
            .head(5)
            .drop(columns=["id"])
            .rename(columns={
                "amount": "Amount (₹)",
                "type": "Type",
                "category": "Category",
                "description": "Description",
                "date": "Date",
            })
        )
        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Amount (₹)": st.column_config.NumberColumn("Amount (₹)", format="₹ %.2f"),
                "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            },
        )

# ADD TRANSACTION

elif page == "Add Transaction":
    st.header("➕ Add a Transaction")

    transaction_type = st.radio(
        "Transaction Type",
        ["Expense", "Income"],
        horizontal=True,
    )

    categories = (
        EXPENSE_CATEGORIES
        if transaction_type == "Expense"
        else INCOME_CATEGORIES
    )

    with st.form("transaction_form", clear_on_submit=True):
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            max_value=1_000_000_000.0,
            value=100.0,
            step=50.0,
        )

        category = st.selectbox("Category", categories)

        description = st.text_input(
            "Description",
            placeholder="e.g. Lunch, salary, bus fare",
            max_chars=150,
        )

        transaction_date = st.date_input(
            "Transaction Date",
            value=date.today(),
            max_value=date.today(),
        )

        submitted = st.form_submit_button(
            "Save Transaction",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            try:
                manager.add_transaction(
                    amount=amount,
                    transaction_type=transaction_type,
                    category=category,
                    description=description,
                    transaction_date=transaction_date.isoformat(),
                )

                st.success("Transaction saved successfully!")
                st.rerun()

            except (ValueError, OSError) as error:
                st.error(f"Could not save transaction: {error}")

# TRANSACTION HISTORY, SEARCH, EDIT AND DELETE

elif page == "Transaction History":
    st.header("📋 Transaction History")

    df = get_month_dataframe(selected_month)

    if df.empty:
        st.info("No transactions found for the selected month.")

    else:
        col1, col2 = st.columns(2)

        with col1:
            type_filter = st.selectbox(
                "Filter by type",
                ["All", "Income", "Expense"],
            )

        with col2:
            categories = [
                "All",
                *sorted(df["category"].dropna().unique().tolist()),
            ]

            category_filter = st.selectbox(
                "Filter by category",
                categories,
            )

        search = st.text_input(
            "Search descriptions",
            placeholder="Enter a keyword...",
        )

        filtered = df.copy()

        if type_filter != "All":
            filtered = filtered[
                filtered["type"] == type_filter
            ]

        if category_filter != "All":
            filtered = filtered[
                filtered["category"] == category_filter
            ]

        if search.strip():
            filtered = filtered[
                filtered["description"].str.contains(
                    search.strip(),
                    case=False,
                    na=False,
                    regex=False,
                )
            ]

        st.write(f"Matching transactions: {len(filtered)}")

        st.dataframe(
            filtered.drop(columns=["id"]),
            use_container_width=True,
            hide_index=True,
        )

        csv_data = filtered.drop(columns=["id"]).to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Export filtered transactions to CSV",
            data=csv_data,
            file_name=f"transactions_{selected_month}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # EDIT TRANSACTION

        st.divider()
        st.subheader("✏️ Edit a Transaction")

        edit_options = {
            (
                f'{row["date"]} | {row["type"]} | '
                f'{row["category"]} | {money(row["amount"])} | '
                f'{row["description"][:30]}'
            ): row.to_dict()
            for _, row in filtered.iterrows()
        }

        if edit_options:
            selected_label = st.selectbox(
                "Choose a transaction to edit",
                list(edit_options.keys()),
                key="edit_transaction_selection",
            )

            selected_record = edit_options[selected_label]

            edit_type = st.radio(
                "Edit transaction type",
                ["Expense", "Income"],
                index=(
                    0 if selected_record["type"] == "Expense" else 1
                ),
                horizontal=True,
                key="edit_transaction_type",
            )

            edit_categories = (
                EXPENSE_CATEGORIES
                if edit_type == "Expense"
                else INCOME_CATEGORIES
            )

            current_category = selected_record["category"]

            if current_category not in edit_categories:
                edit_categories = edit_categories + [current_category]

            with st.form("edit_transaction_form"):
                edit_amount = st.number_input(
                    "Edit amount (₹)",
                    min_value=0.01,
                    max_value=1_000_000_000.0,
                    value=float(selected_record["amount"]),
                    step=50.0,
                )

                edit_category = st.selectbox(
                    "Edit category",
                    edit_categories,
                    index=edit_categories.index(current_category),
                )

                edit_description = st.text_input(
                    "Edit description",
                    value=selected_record["description"],
                    max_chars=150,
                )

                edit_date = st.date_input(
                    "Edit transaction date",
                    value=date.fromisoformat(selected_record["date"]),
                    max_value=date.today(),
                )

                submitted_edit = st.form_submit_button(
                    "Save Changes",
                    type="primary",
                )

                if submitted_edit:
                    try:
                        updated = manager.update_transaction(
                            transaction_id=selected_record["id"],
                            amount=edit_amount,
                            transaction_type=edit_type,
                            category=edit_category,
                            description=edit_description,
                            transaction_date=edit_date.isoformat(),
                        )

                        if updated:
                            st.success("Transaction updated successfully!")
                            st.rerun()
                        else:
                            st.error("Transaction was not found.")

                    except (ValueError, OSError) as error:
                        st.error(f"Could not update transaction: {error}")

        #  DELETE TRANSACTION 

        st.divider()
        st.subheader("🗑️ Delete a Transaction")

        delete_options = {
            label: record["id"]
            for label, record in edit_options.items()
        }

        if delete_options:
            selected_delete = st.selectbox(
                "Choose a transaction to delete",
                list(delete_options.keys()),
                key="delete_transaction_selection",
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this transaction.",
                key="confirm_delete",
            )

            if st.button("Delete Selected Transaction"):
                if not confirm_delete:
                    st.warning("Please confirm before deleting.")
                else:
                    try:
                        success = manager.delete_transaction(
                            delete_options[selected_delete]
                        )

                        if success:
                            st.success("Transaction deleted.")
                            st.rerun()
                        else:
                            st.error("Transaction was not found.")

                    except OSError as error:
                        st.error(f"Could not delete transaction: {error}")

# MONTHLY BUDGETS

elif page == "Budgets":
    st.header("🎯 Monthly Budget Planner")
    st.caption(
        "Set category-wise spending limits and track your progress."
    )

    budgets = load_budgets()

    if budgets is not None:
        st.subheader("Set or Update a Budget")

        with st.form("budget_form"):
            budget_category = st.selectbox(
                "Expense Category",
                EXPENSE_CATEGORIES,
            )

            budget_amount = st.number_input(
                "Monthly limit (₹)",
                min_value=1.0,
                max_value=1_000_000_000.0,
                value=1000.0,
                step=100.0,
            )

            save_budget = st.form_submit_button(
                "Save Budget",
                use_container_width=True,
            )

            if save_budget:
                budget_key = f"{selected_month}|{budget_category}"
                budgets[budget_key] = budget_amount

                if save_budgets(budgets):
                    st.success("Budget saved successfully!")
                    st.rerun()

        st.divider()
        st.subheader(f"Budget Status — {selected_month}")

        df = get_month_dataframe(selected_month)

        if df.empty:
            expenses = pd.DataFrame(
                columns=["category", "amount"]
            )
        else:
            expenses = (
                df[df["type"] == "Expense"]
                .groupby("category")["amount"]
                .sum()
                .reset_index()
            )

        displayed_budgets = {
            key.split("|", 1)[1]: float(amount)
            for key, amount in budgets.items()
            if key.startswith(f"{selected_month}|")
        }

        if not displayed_budgets:
            st.info("Set your first budget above to see progress.")

        else:
            for category, limit in displayed_budgets.items():
                matching = expenses[
                    expenses["category"] == category
                ]

                spent = (
                    float(matching["amount"].sum())
                    if not matching.empty
                    else 0.0
                )

                progress = min(spent / limit, 1.0)

                st.write(f"**{category}**")
                st.progress(progress)

                st.write(
                    f"Spent {money(spent)} of {money(limit)} "
                    f"({spent / limit * 100:.1f}%)"
                )

                if spent > limit:
                    st.error("Budget exceeded!")
                elif spent >= limit * 0.8:
                    st.warning(
                        "You have used at least 80% of this budget."
                    )
                else:
                    st.success("You are within budget.")

                st.divider()

# FOOTER

st.sidebar.divider()
st.sidebar.caption("Smart Expense Tracker | © Aryan Bharadwaj 2026")
