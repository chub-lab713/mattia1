import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { StatusView } from "../components/StatusView";
import { Dialog } from "../components/Dialog";
import { FeedbackBanner } from "../components/FeedbackBanner";

export function IncomesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [filters, setFilters] = useState({
    month_label: "Tutti",
    search: "",
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [feedback, setFeedback] = useState("");
  const [feedbackType, setFeedbackType] = useState("success");
  const [dialogMode, setDialogMode] = useState(null);
  const [selectedIncomeId, setSelectedIncomeId] = useState(null);
  const [form, setForm] = useState(createDefaultIncomeForm());
  const [formError, setFormError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function loadIncomes() {
      setIsLoading(true);
      setError("");

      try {
        const params = new URLSearchParams(filters);
        const response = await api.get(`/api/incomes?${params.toString()}`);
        if (isMounted) {
          setData(response);
        }
      } catch (requestError) {
        if (isMounted) {
          setError(requestError.message || "Impossibile caricare le entrate.");
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    loadIncomes();

    return () => {
      isMounted = false;
    };
  }, [filters]);

  useEffect(() => {
    if (searchParams.get("action") !== "new") {
      return;
    }

    setDialogMode("create");
    setSelectedIncomeId(null);
    setFormError("");
    setForm(createDefaultIncomeForm());
    const next = new URLSearchParams(searchParams);
    next.delete("action");
    setSearchParams(next, { replace: true });
  }, [searchParams, setSearchParams]);

  if (isLoading) {
    return <StatusView title="Entrate" message="Sto caricando le entrate dal backend." />;
  }

  if (error) {
    return <StatusView title="Errore entrate" message={error} />;
  }

  if (!data) {
    return <StatusView title="Entrate" message="Nessun dato disponibile." />;
  }

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Entrate</p>
          <h2>Lista entrate</h2>
        </div>
        <div className="page-actions">
          <span className="muted">{data.count} risultati</span>
          <button
            type="button"
            className="primary-button"
            onClick={() => {
              setDialogMode("create");
              setSelectedIncomeId(null);
              setFormError("");
              setForm(createDefaultIncomeForm());
            }}
          >
            Nuova entrata
          </button>
        </div>
      </div>

      <FeedbackBanner type={feedbackType} message={feedback} />

      <div className="panel filters-grid">
        <label className="field">
          <span>Mese</span>
          <select
            value={filters.month_label}
            onChange={(event) => setFilters((current) => ({ ...current, month_label: event.target.value }))}
          >
            {(data.month_options || []).map((option) => (
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
            onChange={(event) => setFilters((current) => ({ ...current, search: event.target.value }))}
            placeholder="Fonte o descrizione"
          />
        </label>
      </div>

      <div className="panel table-panel">
        {data.items.length === 0 ? (
          <p className="muted">Nessuna entrata visibile con i filtri correnti.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Data</th>
                <th>Fonte</th>
                <th>Descrizione</th>
                <th>Importo</th>
                <th>Azioni</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id}>
                  <td>{item.income_date}</td>
                  <td>{item.source}</td>
                  <td>{item.description}</td>
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
                          setSelectedIncomeId(item.id);
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
          title={dialogMode === "create" ? "Nuova entrata" : "Modifica entrata"}
          onClose={closeDialog}
          footer={
            <>
              <button type="button" className="secondary-button" onClick={closeDialog}>
                Annulla
              </button>
              <button type="button" className="primary-button" onClick={handleSubmitIncome} disabled={isSubmitting}>
                {isSubmitting ? "Salvataggio..." : dialogMode === "create" ? "Crea entrata" : "Salva modifiche"}
              </button>
            </>
          }
        >
          <IncomeForm form={form} setForm={setForm} formError={formError} />
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
              <button type="button" className="primary-button danger-button" onClick={handleDeleteIncome} disabled={isSubmitting}>
                {isSubmitting ? "Eliminazione..." : "Elimina"}
              </button>
            </>
          }
        >
          <p>Questa entrata verrà eliminata definitivamente.</p>
        </Dialog>
      ) : null}
    </section>
  );

  async function fetchIncomes(activeFilters) {
    const params = new URLSearchParams(activeFilters);
    return api.get(`/api/incomes?${params.toString()}`);
  }

  function closeDialog() {
    setDialogMode(null);
    setSelectedIncomeId(null);
    setFormError("");
    setIsSubmitting(false);
  }

  async function refreshIncomesList(message = "", type = "success") {
    const response = await fetchIncomes(filters);
    setData(response);
    setFeedback(message);
    setFeedbackType(type);
  }

  async function openEditDialog(incomeId) {
    setDialogMode("edit");
    setSelectedIncomeId(incomeId);
    setFormError("");

    try {
      const response = await api.get(`/api/incomes/${incomeId}`);
      setForm({
        income_date: response.item.income_date,
        amount: String(response.item.amount ?? ""),
        source: response.item.source || "",
        description: response.item.description || "",
      });
    } catch (requestError) {
      setDialogMode(null);
      setFeedback(requestError.message || "Impossibile caricare il dettaglio dell'entrata.");
      setFeedbackType("error");
    }
  }

  async function handleSubmitIncome() {
    const validationMessage = validateIncomeForm(form);
    if (validationMessage) {
      setFormError(validationMessage);
      return;
    }

    setIsSubmitting(true);
    setFormError("");

    try {
      const payload = {
        income_date: form.income_date,
        amount: Number(form.amount),
        source: form.source.trim(),
        description: form.description.trim(),
      };

      if (dialogMode === "create") {
        await api.post("/api/incomes", payload);
        await refreshIncomesList("Entrata creata con successo.");
      } else if (selectedIncomeId) {
        await api.put(`/api/incomes/${selectedIncomeId}`, payload);
        await refreshIncomesList("Entrata aggiornata con successo.");
      }
      closeDialog();
    } catch (requestError) {
      setFormError(requestError.message || "Impossibile salvare l'entrata.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDeleteIncome() {
    if (!selectedIncomeId) {
      return;
    }

    setIsSubmitting(true);

    try {
      await api.delete(`/api/incomes/${selectedIncomeId}`);
      await refreshIncomesList("Entrata eliminata con successo.");
      closeDialog();
    } catch (requestError) {
      setFeedback(requestError.message || "Impossibile eliminare l'entrata.");
      setFeedbackType("error");
    } finally {
      setIsSubmitting(false);
    }
  }
}

function formatCurrency(value) {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
  }).format(Number(value || 0));
}

function createDefaultIncomeForm() {
  return {
    income_date: new Date().toISOString().slice(0, 10),
    amount: "",
    source: "",
    description: "",
  };
}

function validateIncomeForm(form) {
  if (!form.income_date) {
    return "La data è obbligatoria.";
  }
  if (!form.source.trim()) {
    return "La fonte è obbligatoria.";
  }
  if (!form.description.trim()) {
    return "La descrizione è obbligatoria.";
  }
  if (!form.amount || Number(form.amount) <= 0) {
    return "L'importo deve essere maggiore di zero.";
  }
  return "";
}

function IncomeForm({ form, setForm, formError }) {
  return (
    <div className="form-grid">
      <label className="field">
        <span>Data</span>
        <input
          type="date"
          value={form.income_date}
          onChange={(event) => setForm((current) => ({ ...current, income_date: event.target.value }))}
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
        <span>Fonte</span>
        <input
          type="text"
          value={form.source}
          onChange={(event) => setForm((current) => ({ ...current, source: event.target.value }))}
        />
      </label>

      <label className="field field-span">
        <span>Descrizione</span>
        <textarea
          rows="3"
          value={form.description}
          onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
        />
      </label>

      {formError ? <p className="error-message form-message">{formError}</p> : null}
    </div>
  );
}
