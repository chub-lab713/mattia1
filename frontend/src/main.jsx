import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AppShell } from "./components/AppShell";
import { LoginPage } from "./pages/LoginPage";
import { HomePage } from "./pages/HomePage";
import { ExpensesPage } from "./pages/ExpensesPage";
import { IncomesPage } from "./pages/IncomesPage";
import { ProfilePage } from "./pages/ProfilePage";
import { CoupleBalancePage } from "./pages/CoupleBalancePage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import "./styles.css";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AppShell />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/home" replace />} />
            <Route path="dashboard" element={<Navigate to="/home" replace />} />
            <Route path="home" element={<HomePage />} />
            <Route
              path="calendar"
              element={
                <PlaceholderPage
                  eyebrow="Calendario"
                  title="Calendario in migrazione"
                  message="La route e coerente e raggiungibile. Nel prossimo blocco verra ricostruita mantenendo mese attivo, eventi e struttura Streamlit."
                  actionLabel="Torna alla Home"
                  actionTo="/home"
                />
              }
            />
            <Route path="couple-balance" element={<CoupleBalancePage />} />
            <Route path="expenses" element={<ExpensesPage />} />
            <Route path="incomes" element={<IncomesPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <App />,
);
