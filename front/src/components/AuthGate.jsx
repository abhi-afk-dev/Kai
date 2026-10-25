import { useEffect, useState } from "react";
import { getKey, setKey, clearKey, verifyKey } from "../api";

export default function AuthGate({ children }) {
  const [status, setStatus] = useState("checking");
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    (async () => {
      const saved = getKey();
      if (saved && (await verifyKey(saved))) setStatus("open");
      else setStatus("locked");
    })();
  }, []);

  useEffect(() => {
    const lock = () => setStatus("locked");
    window.addEventListener("kai-unauthorized", lock);
    return () => window.removeEventListener("kai-unauthorized", lock);
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    if (await verifyKey(input)) {
      setKey(input);
      setInput("");
      setStatus("open");
    } else {
      clearKey();
      setError("Wrong password");
    }
    setBusy(false);
  };

  if (status === "open") return children;
  if (status === "checking") return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(0,0,0,0.92)",
      }}
    >
      <form
        onSubmit={submit}
        style={{
          display: "flex",
          flexDirection: "column",
          gap: 12,
          width: "min(320px, 90vw)",
        }}
      >
        <h2 style={{ color: "#fff", margin: 0 }}>Kai</h2>
        <input
          type="password"
          autoFocus
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Password"
          style={{
            padding: 12,
            borderRadius: 8,
            border: "1px solid #444",
            background: "#111",
            color: "#fff",
          }}
        />
        {error && <span style={{ color: "#f66" }}>{error}</span>}
        <button
          type="submit"
          disabled={busy || !input}
          style={{ padding: 12, borderRadius: 8, cursor: "pointer" }}
        >
          {busy ? "Checking..." : "Unlock"}
        </button>
      </form>
    </div>
  );
}
