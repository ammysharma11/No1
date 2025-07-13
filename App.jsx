import { useState } from "react";
import "./App.css";

export default function App() {
  const [prompt,   setPrompt]   = useState("");
  const [subject,  setSubject]  = useState("");
  const [receiver, setReceiver] = useState("");
  const [file,     setFile]     = useState(null);
  const [result,   setResult]   = useState(
    "Type a prompt, subject & receiver, then send."
  );
  const [loading,  setLoading]  = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!prompt.trim() || !subject.trim() || !receiver.trim()) {
      setResult("❗ All three fields are required.");
      return;
    }

    const data = new FormData();
    data.append("prompt",   prompt.trim());
    data.append("subject",  subject.trim());
    data.append("receiver", receiver.trim());
    if (file) data.append("file", file);

    try {
      setLoading(true);
      setResult("Running agent… ⏳");

      const res = await fetch("http://127.0.0.1:8000/process/", {
        method: "POST",
        body: data,
      });
      const json = await res.json();
      setResult(res.ok ? json.result : `❌ ${JSON.stringify(json)}`);
    } catch (err) {
      setResult("❌ Network error: " + err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="wrapper">
      <h1>Multi-Agent AI Assistant</h1>

      <form className="card" onSubmit={handleSubmit}>
        <label>Prompt&nbsp;*
          <textarea rows={3} required
            value={prompt} onChange={e=>setPrompt(e.target.value)} />
        </label>

        <label>Email subject&nbsp;*
          <input required
            value={subject} onChange={e=>setSubject(e.target.value)} />
        </label>

        <label>Receiver e-mail&nbsp;*
          <input type="email" required
            value={receiver} onChange={e=>setReceiver(e.target.value)} />
        </label>

        <label className="fileRow">
          <span>{file ? file.name : "Choose PDF / image (optional)"}</span>
          <input type="file" accept="application/pdf,image/*"
            onChange={e=>setFile(e.target.files?.[0] || null)} />
        </label>

        <button disabled={loading}>
          {loading ? "Processing…" : "Send"}
        </button>
      </form>

      <section className="card response">
        <h2>Response</h2>
        <pre>{result}</pre>
      </section>
    </main>
  );
}

