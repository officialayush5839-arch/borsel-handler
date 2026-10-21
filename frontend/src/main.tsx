import { Component, StrictMode, type ErrorInfo, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

class RootErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught application error:", error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 32, fontFamily: "sans-serif", background: "#f8fafc", minHeight: "100vh" }}>
          <div style={{ maxWidth: 800, margin: "0 auto", background: "#ffffff", padding: 24, borderRadius: 12, border: "1px solid #fee2e2", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }}>
            <h1 style={{ color: "#dc2626", fontSize: 20, fontWeight: "bold", marginBottom: 12 }}>Application Encountered an Error</h1>
            <p style={{ color: "#475569", fontSize: 14, marginBottom: 16 }}>An unhandled error occurred while rendering the dashboard:</p>
            <div style={{ background: "#fef2f2", color: "#991b1b", padding: 16, borderRadius: 8, fontSize: 13, fontFamily: "monospace", overflowX: "auto", marginBottom: 16 }}>
              {this.state.error?.toString()}
            </div>
            {this.state.error?.stack && (
              <details style={{ marginTop: 12 }}>
                <summary style={{ cursor: "pointer", color: "#2563eb", fontSize: 13, fontWeight: "bold" }}>Show Stack Trace</summary>
                <pre style={{ background: "#f1f5f9", padding: 12, borderRadius: 6, fontSize: 12, overflowX: "auto", marginTop: 8 }}>
                  {this.state.error.stack}
                </pre>
              </details>
            )}
            <button
              onClick={() => {
                try {
                  sessionStorage.clear();
                } catch (_) {}
                window.location.reload();
              }}
              style={{ marginTop: 20, padding: "8px 16px", background: "#2563eb", color: "#ffffff", border: "none", borderRadius: 6, cursor: "pointer", fontWeight: 600, fontSize: 13 }}
            >
              Reset Session & Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RootErrorBoundary>
      <App />
    </RootErrorBoundary>
  </StrictMode>
);
