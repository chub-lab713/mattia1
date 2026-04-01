from __future__ import annotations

import hashlib
import hmac
from datetime import date, datetime
from io import StringIO
from io import BytesIO

import pandas as pd

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase.pdfmetrics import stringWidth
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    REPORTLAB_AVAILABLE = False

from database import get_connection


EXPENSE_TYPE_OPTIONS = ["Personale", "Condivisa"]
SPLIT_TYPE_OPTIONS = ["50/50", "Personalizzata"]
CATEGORY_OPTIONS = [
    "Spesa",
    "Casa",
    "Trasporti",
    "Ristoranti",
    "Svago",
    "Salute",
    "Abbonamenti",
    "Viaggi",
    "Regali",
    "Altro",
]


def authenticate_user(username: str, password: str) -> dict | None:
    """Verifica le credenziali dell'utente e restituisce i dati base se valide."""
    clean_username = username.strip().lower()
    if not clean_username:
        return None

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, full_name, username, email, password_hash
            FROM users
            WHERE username = ?
            """,
            (clean_username,),
        ).fetchone()

    if row is None:
        return None

    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    if not hmac.compare_digest(row["password_hash"], password_hash):
        return None

    return {
        "id": row["id"],
        "full_name": row["full_name"],
        "username": row["username"],
        "email": row["email"] or "",
    }


def get_user_by_id(user_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, full_name, username, email
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    return dict(row) if row is not None else None


def get_usernames() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT username FROM users ORDER BY id ASC"
        ).fetchall()
    return [row["username"] for row in rows]


def update_user_profile(
    user_id: int,
    full_name: str,
    username: str,
    email: str,
    new_password: str = "",
) -> tuple[bool, str, dict | None]:
    clean_name = full_name.strip()
    clean_username = username.strip().lower()
    clean_email = email.strip()

    if not clean_name:
        return False, "Il nome non puo essere vuoto.", None
    if not clean_username:
        return False, "Lo username non puo essere vuoto.", None

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM users WHERE LOWER(username) = LOWER(?) AND id != ?",
            (clean_username, user_id),
        ).fetchone()
        if existing is not None:
            return False, "Questo username e gia in uso.", None

        if new_password.strip():
            connection.execute(
                """
                UPDATE users
                SET full_name = ?, username = ?, email = ?, password_hash = ?
                WHERE id = ?
                """,
                (clean_name, clean_username, clean_email, hashlib.sha256(new_password.encode("utf-8")).hexdigest(), user_id),
            )
        else:
            connection.execute(
                """
                UPDATE users
                SET full_name = ?, username = ?, email = ?
                WHERE id = ?
                """,
                (clean_name, clean_username, clean_email, user_id),
            )

    updated_user = get_user_by_id(user_id)
    return True, "Profilo aggiornato con successo.", updated_user


def get_categories() -> list[str]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT name FROM categories ORDER BY LOWER(name) ASC"
        ).fetchall()
    return [row["name"] for row in rows]


def add_category(name: str) -> tuple[bool, str]:
    clean_name = name.strip()
    if not clean_name:
        return False, "Il nome della categoria non puo essere vuoto."

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM categories WHERE LOWER(name) = LOWER(?)",
            (clean_name,),
        ).fetchone()
        if existing is not None:
            return False, "Questa categoria esiste gia."

        connection.execute("INSERT INTO categories (name) VALUES (?)", (clean_name,))

    return True, "Categoria aggiunta con successo."


def delete_category(name: str) -> tuple[bool, str]:
    clean_name = name.strip()
    if not clean_name:
        return False, "Categoria non valida."

    with get_connection() as connection:
        usage = connection.execute(
            "SELECT COUNT(*) AS total FROM expenses WHERE LOWER(category) = LOWER(?)",
            (clean_name,),
        ).fetchone()
        if usage is not None and int(usage["total"]) > 0:
            return False, "Non puoi eliminare una categoria gia usata in una o piu spese."

        existing = connection.execute(
            "SELECT id FROM categories WHERE LOWER(name) = LOWER(?)",
            (clean_name,),
        ).fetchone()
        if existing is None:
            return False, "Questa categoria non esiste."

        connection.execute(
            "DELETE FROM categories WHERE LOWER(name) = LOWER(?)",
            (clean_name,),
        )

    return True, "Categoria eliminata con successo."


def validate_expense_data(data: dict) -> list[str]:
    """Controlla i campi obbligatori e restituisce eventuali errori."""
    errors: list[str] = []

    if data["amount"] <= 0:
        errors.append("L'importo deve essere maggiore di zero.")

    if not data["name"].strip():
        errors.append("Il nome non puo essere vuoto.")

    if data["expense_type"] == "Condivisa":
        share = data.get("my_share_percentage")
        if share is None or share < 0 or share > 100:
            errors.append("La percentuale personalizzata deve essere tra 0 e 100.")

    return errors


def create_expense(
    expense_date: date,
    amount: float,
    name: str,
    category: str,
    description: str,
    payer: str,
    expense_type: str,
    split_type: str | None = None,
    my_share_percentage: float | None = None,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO expenses (
                expense_date,
                amount,
                name,
                category,
                description,
                payer,
                expense_type,
                split_type,
                my_share_percentage
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                expense_date.isoformat(),
                amount,
                name.strip(),
                category,
                description.strip(),
                payer,
                expense_type,
                split_type,
                my_share_percentage,
            ),
        )


def validate_income_data(data: dict) -> list[str]:
    errors: list[str] = []

    if data["amount"] <= 0:
        errors.append("L'importo dell'entrata deve essere maggiore di zero.")

    if not data["source"].strip():
        errors.append("La fonte dell'entrata non puo essere vuota.")

    if not data["description"].strip():
        errors.append("La descrizione dell'entrata non puo essere vuota.")

    return errors


def create_income(
    income_date: date,
    amount: float,
    source: str,
    description: str,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO incomes (
                income_date,
                amount,
                source,
                description
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                income_date.isoformat(),
                amount,
                source.strip(),
                description.strip(),
            ),
        )


def update_expense(
    expense_id: int,
    expense_date: date,
    amount: float,
    name: str,
    category: str,
    description: str,
    payer: str,
    expense_type: str,
    split_type: str | None = None,
    my_share_percentage: float | None = None,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE expenses
            SET
                expense_date = ?,
                amount = ?,
                name = ?,
                category = ?,
                description = ?,
                payer = ?,
                expense_type = ?,
                split_type = ?,
                my_share_percentage = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                expense_date.isoformat(),
                amount,
                name.strip(),
                category,
                description.strip(),
                payer,
                expense_type,
                split_type,
                my_share_percentage,
                expense_id,
            ),
        )


def delete_expense(expense_id: int) -> None:
    with get_connection() as connection:
        connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))


def get_expenses() -> pd.DataFrame:
    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            """
            SELECT
                id,
                expense_date,
                amount,
                name,
                category,
                description,
                payer,
                expense_type,
                split_type,
                my_share_percentage,
                created_at,
                updated_at
            FROM expenses
            ORDER BY expense_date DESC, id DESC
            """,
            connection,
        )

    if dataframe.empty:
        return dataframe

    dataframe["expense_date"] = pd.to_datetime(dataframe["expense_date"])
    dataframe["month_label"] = dataframe["expense_date"].dt.strftime("%Y-%m")
    dataframe["my_share_amount"] = dataframe.apply(
        lambda row: _calculate_user_share_amount(row, _get_tracked_usernames()[0]),
        axis=1,
    )
    dataframe["partner_share_amount"] = dataframe["amount"] - dataframe["my_share_amount"]
    return dataframe


def get_visible_expenses(dataframe: pd.DataFrame, current_username: str) -> pd.DataFrame:
    if dataframe.empty:
        return dataframe.copy()

    visible = dataframe[
        (dataframe["expense_type"] == "Condivisa") | (dataframe["payer"] == current_username)
    ].copy()

    visible["my_share_amount"] = visible.apply(
        lambda row: _calculate_user_share_amount(row, current_username),
        axis=1,
    )
    visible["partner_share_amount"] = visible["amount"] - visible["my_share_amount"]
    return visible


def get_incomes() -> pd.DataFrame:
    with get_connection() as connection:
        dataframe = pd.read_sql_query(
            """
            SELECT
                id,
                income_date,
                amount,
                source,
                description,
                created_at,
                updated_at
            FROM incomes
            ORDER BY income_date DESC, id DESC
            """,
            connection,
        )

    if dataframe.empty:
        return dataframe

    dataframe["income_date"] = pd.to_datetime(dataframe["income_date"])
    dataframe["month_label"] = dataframe["income_date"].dt.strftime("%Y-%m")
    return dataframe


def apply_income_filters(dataframe: pd.DataFrame, month_label: str | None) -> pd.DataFrame:
    filtered = dataframe.copy()
    if month_label and month_label != "Tutti":
        filtered = filtered[filtered["month_label"] == month_label]
    return filtered.sort_values(by=["income_date", "id"], ascending=[False, False])


def apply_filters(
    dataframe: pd.DataFrame,
    month_label: str | None,
    category: str | None,
    payer: str | None,
    expense_type: str | None,
) -> pd.DataFrame:
    filtered = dataframe.copy()

    if month_label and month_label != "Tutti":
        filtered = filtered[filtered["month_label"] == month_label]
    if category and category != "Tutte":
        filtered = filtered[filtered["category"] == category]
    if payer and payer != "Tutti":
        filtered = filtered[filtered["payer"] == payer]
    if expense_type and expense_type != "Tutte":
        filtered = filtered[filtered["expense_type"] == expense_type]

    return filtered.sort_values(by=["expense_date", "id"], ascending=[False, False])


def build_dashboard_metrics(month_dataframe: pd.DataFrame, current_username: str) -> dict:
    total_month = float(month_dataframe["amount"].sum()) if not month_dataframe.empty else 0.0

    my_personal = month_dataframe[
        (month_dataframe["expense_type"] == "Personale") & (month_dataframe["payer"] == current_username)
    ]["amount"].sum()

    shared_total = month_dataframe[month_dataframe["expense_type"] == "Condivisa"]["amount"].sum()
    balance = calculate_balance(month_dataframe, current_username)

    return {
        "total_month": float(total_month),
        "my_personal": float(my_personal),
        "shared_total": float(shared_total),
        "balance": float(balance),
    }


def build_category_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Restituisce un riepilogo per categoria utile per la dashboard analitica."""
    if dataframe.empty:
        return pd.DataFrame()

    summary = (
        dataframe.groupby("category", as_index=False)
        .agg(
            totale=("amount", "sum"),
            numero_spese=("id", "count"),
            quota_mia=("my_share_amount", "sum"),
            quota_compagna=("partner_share_amount", "sum"),
        )
        .sort_values(by="totale", ascending=False)
    )

    summary["spesa_media"] = summary["totale"] / summary["numero_spese"]
    return summary


def build_income_vs_expense_summary(incomes: pd.DataFrame, expenses: pd.DataFrame) -> pd.DataFrame:
    income_monthly = (
        incomes.groupby("month_label", as_index=False)["amount"].sum().rename(columns={"amount": "Entrate"})
        if not incomes.empty
        else pd.DataFrame(columns=["month_label", "Entrate"])
    )
    expense_monthly = (
        expenses.groupby("month_label", as_index=False)["amount"].sum().rename(columns={"amount": "Uscite"})
        if not expenses.empty
        else pd.DataFrame(columns=["month_label", "Uscite"])
    )

    summary = income_monthly.merge(expense_monthly, on="month_label", how="outer").fillna(0)
    if summary.empty:
        return summary

    summary["Saldo"] = summary["Entrate"] - summary["Uscite"]
    return summary.sort_values("month_label")


def calculate_balance(dataframe: pd.DataFrame, current_username: str) -> float:
    """Valore positivo: l'altra persona deve soldi a me. Negativo: io devo soldi all'altra persona."""
    shared = dataframe[dataframe["expense_type"] == "Condivisa"]
    balance = 0.0

    for _, row in shared.iterrows():
        if row["payer"] == current_username:
            balance += row["partner_share_amount"]
        else:
            balance -= row["my_share_amount"]

    return float(balance)


def get_month_options(dataframe: pd.DataFrame) -> list[str]:
    if dataframe.empty:
        return ["Tutti"]

    months = sorted(dataframe["month_label"].dropna().unique().tolist(), reverse=True)
    return ["Tutti"] + months


def get_expense_by_id(expense_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()

    if row is None:
        return None

    expense = dict(row)
    expense["expense_date"] = datetime.strptime(expense["expense_date"], "%Y-%m-%d").date()
    return expense


def export_expenses_to_csv(dataframe: pd.DataFrame) -> str:
    export_frame = dataframe.copy()
    if export_frame.empty:
        return ""

    export_frame["expense_date"] = export_frame["expense_date"].dt.strftime("%Y-%m-%d")
    export_frame = export_frame.rename(
        columns={
            "id": "ID",
            "expense_date": "Data",
            "amount": "Importo",
            "name": "Nome",
            "category": "Categoria",
            "description": "Descrizione",
            "payer": "Pagato da",
            "expense_type": "Tipo spesa",
            "split_type": "Tipo divisione",
            "my_share_percentage": "Percentuale mia quota",
        }
    )

    selected_columns = [
        "ID",
        "Data",
        "Importo",
        "Nome",
        "Categoria",
        "Descrizione",
        "Pagato da",
        "Tipo spesa",
        "Tipo divisione",
        "Percentuale mia quota",
    ]

    buffer = StringIO()
    export_frame[selected_columns].to_csv(buffer, index=False)
    return buffer.getvalue()


def export_expenses_to_pdf(dataframe: pd.DataFrame) -> bytes:
    if not REPORTLAB_AVAILABLE:
        raise ModuleNotFoundError("reportlab non installato")

    export_frame = dataframe.copy()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    if export_frame.empty:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(40, height - 50, "Riepilogo spese")
        pdf.setFont("Helvetica", 11)
        pdf.drawString(40, height - 75, "Nessuna spesa disponibile con i filtri attivi.")
        pdf.save()
        return buffer.getvalue()

    export_frame["expense_date"] = export_frame["expense_date"].dt.strftime("%Y-%m-%d")
    export_frame = export_frame.sort_values(by=["expense_date", "id"], ascending=[False, False])

    def draw_header(page_title: str, total_count: int) -> float:
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40, height - 45, page_title)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(40, height - 62, f"Totale movimenti: {total_count}")
        return height - 90

    def truncate_text(text: str, max_width: float, font_name: str = "Helvetica", font_size: int = 10) -> str:
        clean_text = str(text or "")
        if stringWidth(clean_text, font_name, font_size) <= max_width:
            return clean_text

        truncated = clean_text
        while truncated and stringWidth(f"{truncated}...", font_name, font_size) > max_width:
            truncated = truncated[:-1]
        return f"{truncated}..." if truncated else "..."

    y_position = draw_header("Riepilogo spese", len(export_frame))

    for _, row in export_frame.iterrows():
        if y_position < 100:
            pdf.showPage()
            y_position = draw_header("Riepilogo spese", len(export_frame))

        title = truncate_text(
            f"{row.get('name', '') or row.get('description', '') or 'Spesa'} - {format_currency(float(row['amount']))}",
            width - 80,
            "Helvetica-Bold",
            11,
        )
        line_one = truncate_text(
            f"{row['expense_date']} | {row['category']} | {row['payer']} | {row['expense_type']}",
            width - 80,
        )
        split_label = row["split_type"] if pd.notna(row["split_type"]) else "-"
        line_two = truncate_text(
            f"Divisione: {split_label} | Quota mia: {format_currency(float(row['my_share_amount']))} | "
            f"Quota compagna: {format_currency(float(row['partner_share_amount']))}",
            width - 80,
        )

        description = str(row.get("description") or "").strip()
        note_line = truncate_text(f"Note: {description}", width - 80) if description else ""

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(40, y_position, title)
        y_position -= 16

        pdf.setFont("Helvetica", 10)
        pdf.drawString(40, y_position, line_one)
        y_position -= 14
        pdf.drawString(40, y_position, line_two)
        y_position -= 14

        if note_line:
            pdf.drawString(40, y_position, note_line)
            y_position -= 14

        pdf.line(40, y_position, width - 40, y_position)
        y_position -= 18

    pdf.save()
    return buffer.getvalue()


def format_currency(value: float) -> str:
    formatted_value = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {formatted_value}"


def _calculate_user_share_amount(row: pd.Series, current_username: str) -> float:
    if row["expense_type"] == "Personale":
        return row["amount"] if row["payer"] == current_username else 0.0

    share_percentage = row["my_share_percentage"] if pd.notna(row["my_share_percentage"]) else 50
    if row["payer"] == current_username:
        return float(row["amount"] - (row["amount"] * share_percentage / 100))
    return float(row["amount"] * share_percentage / 100)


def _get_tracked_usernames() -> tuple[str, str]:
    usernames = get_usernames()
    my_username = usernames[0] if usernames else "io"
    partner_username = usernames[1] if len(usernames) > 1 else "compagna"
    return my_username, partner_username
