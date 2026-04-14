import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { StatusView } from "../components/StatusView";
import { Dialog } from "../components/Dialog";
import { FeedbackBanner } from "../components/FeedbackBanner";
import { useAuth } from "../context/AuthContext";

export function ExpensesPage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [meta, setMeta] = useState(null);
  const [filters, setFilters] = useState({
    month_label: "Tutti",
    category: "Tutte",
    payer: "Tutti",
    expense_type: "Tutte",
    search: "",
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const [feedbackType, setFeedbackType] = useState("success");
  const [dialogMode, setDialogMode] = useState(null);
  const [selectedExpenseId, setSelectedExpenseId] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const [form, setForm] = useState(createDefaultExpenseForm(""));
  const summaryMode = searchParams.get("summary");

  const payerOptions = useMemo(() => meta?.usernames || data?.filters?.payer_options?.filter((item) => item !== "Tutti") || [], [meta, data]);
  const categoryOptions = useMemo(() => meta?.categories || data?.filters?.category_options?.filter((item) => item !== "Tutte") || [], [meta, data]);
  const splitOptions = meta?.split_options || ["equal", "custom"];
  const expenseTypeOptions = meta?.expense_types || ["Personale", "Condivisa"];

  useEffect(() => {
    if (!user?.username) {
      return;
    }
    setForm(createDefaultExpenseForm(user.username));
  }, [user]);

  useEffect(() => {
    const nextFilters = {
      month_label: searchParams.get("month_label") || "Tutti",
      category: searchParams.get("category") || "Tutte",
      payer: searchParams.get("payer") || "Tutti",
      expense_type: searchParams.get("expense_type") || "Tutte",
      search: searchParams.get("search") || "",
    };

    setFilters((current) => {
      if (JSON.stringify(current) === JSON.stringify(nextFilters)) {
        return current;
      }
      return nextFilters;
    });
  }, [searchParams]);

  useEffect(() => {
    if (searchParams.get("action") !== "new") {
      return;
    }

    setDialogMode("create");
    setSelectedExpenseId(null);
    setFormError("");
    setForm(createDefaultExpenseForm(user?.username || ""));
    const next = new URLSearchParams(searchParams);
    next.delete("action");
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams, user]);

  useEffect(() => {
    let isMounted = true;

    async function bootstrap() {
      setIsLoading(true);
      setError("");

      try {
        const [expensesResponse, metaResponse] = await Promise.all([
          fetchExpenses(filters),
          api.get("/api/meta/options"),
        ]);
        if (!isMounted) {
          return;
        }
        setData(expensesResponse);
        setMeta(metaResponse);
      } catch (requestError) {
        if (isMounted) {
          setError(requestError.message || "Impossibile caricare le spese.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    bootstrap();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!data) {
      return;
    }

    let isMounted = true;

    async function refreshList() {
      try {
        const response = await fetchExpenses(filters);
        if (isMounted) {
          setData(response);
        }
      } catch (requestError) {
        if (isMounted) {
          setError(requestError.message || "Impossibile aggiornare le spese.");
        }
      }
    }

    refreshList();

    return () => {
      isMounted = false;
    };
  }, [filters]);

  if (isLoading) {
    return <StatusView title="Spese" message="Sto caricando le spese dal backend." />;
  }

  if (error) {
    return <StatusView title="Errore spese" message={error} />;
  }

  if (!data) {
    return <StatusView title="Spese" message="Nessun dato disponibile." />;
  }

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Spese</p>
          <h2>{summaryMode ? "Riepilogo spese" : "Lista spese"}</h2>
        </div>
        <div className="page-actions">
          <span className="muted">{data.count} risultati</span>
          <button
            type="button"
            className="primary-button"
            onClick={() => {
              setDialogMode("create");
              setSelectedExpenseId(null);
              setFormError("");
              setForm(createDefaultExpenseForm(user?.username || ""));
            }}
          >
            Nuova spesa
          </button>
        </div>
      </div>

      <FeedbackBanner type={feedbackType} message={feedback} />
      {summaryMode ? (
        <div className="panel compact-panel">
          <p className="eyebrow">Vista operativa</p>
          <p className="muted">
            {summaryMode === "net"
              ? "Questa vista raccoglie le uscite del mese attivo per leggere il saldo del periodo in modo coerente con la dashboard."
              : "Questa vista usa la sezione Uscite come riepilogo temporaneo del periodo selezionato."}
          </p>
        </div>
      ) : null}

      <div className="panel filters-grid">
        <label className="field">
          <span>Mese</span>
          <select
            value={filters.month_label}
            onChange={(event) => updateFilter("month_label", event.target.value)}
          >
            {(data.month_options || []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Categoria</span>
          <select
            value={filters.category}
            onChange={(event) => updateFilter("category", event.target.value)}
          >
            {(data.filters?.category_options || []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Pagatore</span>
          <select
            value={filters.payer}
            onChange={(event) => updateFilter("payer", event.target.value)}
          >
            {(data.filters?.payer_options || []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Tipo</span>
          <select
            value={filters.expense_type}
            onChange={(event) => updateFilter("expense_type", event.target.value)}
          >
            {(data.filters?.expense_type_options || []).map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="field field-span">
          <span>Ricerca</span>
          <input
            type="search"
            value={filters.search}
            onChange={(event) => updateFilter("search", event.target.value)}
            placeholder="Nome, descrizione, categoria, pagatore"
          />
        </label>
      </div>

      <div className="panel table-panel">
        {data.items.length === 0 ? (
          <p className="muted">Nessuna spesa visibile con i filtri correnti.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Nome</th>
                <th>Categoria</th>
                <th>Pagata da</th>
                <th>Tipo</th>
                <th>Stato</th>
                <th>Importo</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id}>
                  <td>{item.expense_date}</td>
                  <td>
                    <strong>{item.name || item.description}</strong>
                    <div className="row-subtitle">{item.description}</div>
                  </td>
                  <td>{item.category}</td>
                  <td>{item.paid_by}</td>
                  <td>{item.expense_type}</td>
                  <td>
                    {item.expense_type === "Condivisa" ? (
                      <label className="toggle-field">
                        <input
                          type="checkbox"
                          checked={Boolean(item.is_settled)}
                          onChange={() => handleToggleSettled(item)}
                        />
                        <span>{item.is_settled ? "Pagata" : "Da regolare"}</span>
                      </label>
                    ) : (
                      <span className="muted">Privata</span>
                    )}
                  </td>
                  <td>{formatCurrency(item.amount)}</td>
                  <td>
                    <div className="row-actions">
                      <button type="button" className="text-button" onClick={() => openEditDialog(item.id)}>
                        Modifica
                      </button>
                      <button
                        type="button"
                        className="text-button danger"
                        onClick={() => {
                          setDialogMode("delete");
                          setSelectedExpenseId(item.id);
                          setFeedback("");
                        }}
                      >
                        Elimina
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {dialogMode === "create" || dialogMode === "edit" ? (
        <Dialog
          title={dialogMode === "create" ? "Nuova spesa" : "Modifica spesa"}
          onClose={closeDialog}
          footer={
            <>
              <button type="button" className="secondary-button" onClick={closeDialog}>
                Annulla
              </button>
              <button type="button" className="primary-button" onClick={handleSubmitExpense} disabled={isSubmitting}>
                {isSubmitting ? "Salvataggio..." : dialogMode === "create" ? "Crea spesa" : "Salva modifiche"}
              </button>
            </>
          }
        >
          <ExpenseForm
            form={form}
            setForm={setForm}
            formError={formError}
            payerOptions={payerOptions}
            categoryOptions={categoryOptions}
            splitOptions={splitOptions}
            expenseTypeOptions={expenseTypeOptions}
            currentUsername={user?.username || ""}
          />
        </Dialog>
      ) : null}

      {dialogMode === "delete" ? (
        <Dialog
          title="Conferma eliminazione"
          onClose={closeDialog}
          footer={
            <>
              <button type="button" className="secondary-button" onClick={closeDialog}>
                Annulla
              </button>
              <button type="button" className="primary-button danger-button" onClick={handleDeleteExpense} disabled={isSubmitting}>
                {isSubmitting ? "Eliminazione..." : "Elimina"}
              </button>
            </>
          }
        >
          <p>Questa spesa verrà eliminata definitivamente.</p>
        </Dialog>
      ) : null}
    </section>
  );

  async function fetchExpenses(activeFilters) {
    const params = new URLSearchParams(activeFilters);
    return api.get(`/api/expenses?${params.toString()}`);
  }

  function closeDialog() {
    setDialogMode(null);
    setSelectedExpenseId(null);
    setFormError("");
    setIsSubmitting(false);
  }

  function updateFilter(key, value) {
    setFilters((current) => ({ ...current, [key]: value }));
    const next = new URLSearchParams(searchParams);
    if (value && value !== "Tutti" && value !== "Tutte") {
      next.set(key, value);
    } else if (key === "search" && value) {
      next.set(key, value);
    } else {
      next.delete(key);
    }
    setSearchParams(next, { replace: true });
  }

  async function refreshExpensesList(message = "", type = "success") {
    const response = await fetchExpenses(filters);
    setData(response);
    setFeedback(message);
    setFeedbackType(type);
  }

  async function openEditDialog(expenseId) {
    setDialogMode("edit");
    setSelectedExpenseId(expenseId);
    setFormError("");
    setIsSubmitting(false);

    try {
      const response = await api.get(`/api/expenses/${expenseId}`);
      setForm(normalizeExpenseForForm(response.item, user?.username || ""));
    } catch (requestError) {
      setDialogMode(null);
      setFeedback(requestError.message || "Impossibile caricare il dettaglio della spesa.");
      setFeedbackType("error");
    }
  }

  async function handleSubmitExpense() {
    const validationMessage = validateExpenseForm(form);
    if (validationMessage) {
      setFormError(validationMessage);
      return;
    }

    setIsSubmitting(true);
    setFormError("");

    try {
      const payload = buildExpensePayload(form, user?.username || "");
      if (dialogMode === "create") {
        await api.post("/api/expenses", payload);
        await refreshExpensesList("Spesa creata con successo.");
      } else if (selectedExpenseId) {
        await api.put(`/api/expenses/${selectedExpenseId}`, payload);
        await refreshExpensesList("Spesa aggiornata con successo.");
      }
      closeDialog();
    } catch (requestError) {
      setFormError(requestError.message || "Impossibile salvare la spesa.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteExpense() {
    if (!selectedExpenseId) {
      return;
    }

    setIsSubmitting(true);

    try {
      await api.delete(`/api/expenses/${selectedExpenseId}`);
      await refreshExpensesList("Spesa eliminata con successo.");
      closeDialog();
    } catch (requestError) {
      setFormError(requestError.message || "Impossibile eliminare la spesa.");
      setFeedback(requestError.message || "Impossibile eliminare la spesa.");
      setFeedbackType("error");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleToggleSettled(item) {
    try {
      await api.patch(`/api/expenses/${item.id}/settled`, { is_settled: !item.is_settled });
      await refreshExpensesList("Stato spesa aggiornato con successo.");
    } catch (requestError) {
      setFeedback(requestError.message || "Impossibile aggiornare lo stato.");
      setFeedbackType("error");
    }
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
  }).format(Number(value || 0));
}

function createDefaultExpenseForm(currentUsername) {
  return {
    expense_date: new Date().toISOString().slice(0, 10),
    amount: "",
    name: "",
    category: "Casa",
    description: "",
    paid_by: currentUsername,
    expense_type: "Condivisa",
    split_type: "equal",
    split_ratio: 0.5,
    is_settled: false,
  };
}

function normalizeExpenseForForm(item, currentUsername) {
  return {
    expense_date: item.expense_date || new Date().toISOString().slice(0, 10),
    amount: String(item.amount ?? ""),
    name: item.name || "",
    category: item.category || "Casa",
    description: item.description || "",
    paid_by: item.expense_type === "Personale" ? currentUsername : item.paid_by || currentUsername,
    expense_type: item.expense_type || "Condivisa",
    split_type: item.split_type || "equal",
    split_ratio: Number(item.split_ratio ?? 0.5),
    is_settled: Boolean(item.is_settled),
  };
}

function buildExpensePayload(form, currentUsername) {
  const expenseType = form.expense_type;
  const splitType = expenseType === "Personale" ? "equal" : form.split_type;
  const splitRatio = expenseType === "Personale" ? 1.0 : Number(form.split_ratio);

  return {
    expense_date: form.expense_date,
    amount: Number(form.amount),
    name: form.name.trim(),
    category: form.category,
    description: form.description.trim(),
    paid_by: expenseType === "Personale" ? currentUsername : form.paid_by,
    expense_type: expenseType,
    split_type: splitType,
    split_ratio: splitRatio,
  };
}

function validateExpenseForm(form) {
  if (!form.expense_date) {
    return "La data è obbligatoria.";
  }
  if (!form.name.trim()) {
    return "Il nome della spesa è obbligatorio.";
  }
  if (!form.category) {
    return "La categoria è obbligatoria.";
  }
  if (!form.description.trim()) {
    return "La descrizione è obbligatoria.";
  }
  if (!form.amount || Number(form.amount) <= 0) {
    return "L'importo deve essere maggiore di zero.";
  }
  if (form.expense_type === "Condivisa" && !form.paid_by) {
    return "Seleziona chi ha pagato.";
  }
  return "";
}

function ExpenseForm({
  form,
  setForm,
  formError,
  payerOptions,
  categoryOptions,
  splitOptions,
  expenseTypeOptions,
  currentUsername,
}) {
  const isPersonal = form.expense_type === "Personale";

  return (
    <div className="form-grid">
      <label className="field">
        <span>Data</span>
        <input
          type="date"
          value={form.expense_date}
          onChange={(event) => setForm((current) => ({ ...current, expense_date: event.target.value }))}
        />
      </label>

      <label className="field">
        <span>Importo</span>
        <input
          type="number"
          min="0"
          step="0.01"
          value={form.amount}
          onChange={(event) => setForm((current) => ({ ...current, amount: event.target.value }))}
        />
      </label>

      <label className="field field-span">
        <span>Nome</span>
        <input
          type="text"
          value={form.name}
          onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
        />
      </label>

      <label className="field">
        <span>Categoria</span>
        <select
          value={form.category}
          onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))}
        >
          {categoryOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Tipo spesa</span>
        <select
          value={form.expense_type}
          onChange={(event) =>
            setForm((current) => ({
              ...current,
              expense_type: event.target.value,
              paid_by: event.target.value === "Personale" ? currentUsername : current.paid_by || currentUsername,
              split_type: event.target.value === "Personale" ? "equal" : current.split_type,
              split_ratio: event.target.value === "Personale" ? 1 : current.split_ratio || 0.5,
            }))
          }
        >
          {expenseTypeOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label className="field field-span">
        <span>Descrizione</span>
        <textarea
          rows="3"
          value={form.description}
          onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
        />
      </label>

      <label className="field">
        <span>Pagata da</span>
        <select
          value={isPersonal ? currentUsername : form.paid_by}
          disabled={isPersonal}
          onChange={(event) => setForm((current) => ({ ...current, paid_by: event.target.value }))}
        >
          {payerOptions.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Divisione</span>
        <select
          value={isPersonal ? "equal" : form.split_type}
          disabled={isPersonal}
          onChange={(event) => setForm((current) => ({ ...current, split_type: event.target.value }))}
        >
          {splitOptions.map((option) => (
            <option key={option} value={option}>
              {option === "equal" ? "50/50" : "Personalizzata"}
            </option>
          ))}
        </select>
      </label>

      {!isPersonal && form.split_type === "custom" ? (
        <label className="field field-span">
          <span>Quota di chi paga</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={form.split_ratio}
            onChange={(event) => setForm((current) => ({ ...current, split_ratio: Number(event.target.value) }))}
          />
          <small>{Math.round(Number(form.split_ratio) * 100)}%</small>
        </label>
      ) : null}

      {formError ? <p className="error-message form-message">{formError}</p> : null}
    </div>
  );
}
