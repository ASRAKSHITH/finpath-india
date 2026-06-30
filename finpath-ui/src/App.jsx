import { useState, useRef, useEffect } from "react";

const API_BASE = import.meta.env.DEV ? "http://127.0.0.1:8000" : "";

const examples = [
  "I have 2 lakh in savings, 1.5 lakh credit card debt at 36 percent interest, and 20000 monthly surplus. Should I repay debt first or invest?",
  "I earn 80000 per month, have 3 lakh savings, no debt, and can invest 25000 monthly for 5 years. Should I choose SIPs, PPF, or fixed deposits?",
  "I have a 12 percent car loan, 5 lakh in cash, and I want to start investing for 10 years. Should I clear the loan first or start investing now?"
];

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleFeedback = async (traceId, feedbackType) => {
    try {
      await fetch(`${API_BASE}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trace_id: traceId, feedback: feedbackType }),
      });
      alert(`Feedback recorded: ${feedbackType}`);
    } catch (err) {
      console.error("Failed to submit feedback", err);
    }
  };

  const handleAnalyze = async (overrideInput = null) => {
    const textToAnalyze = overrideInput || input;
    if (!textToAnalyze.trim()) {
      setError("Please enter your financial situation first.");
      return;
    }

    const newUserMsg = { role: "user", content: textToAnalyze };
    const historyPayload = messages.map(m => ({ role: m.role, content: m.role === "user" ? m.content : (m.recommendation || "System response") }));
    
    setMessages(prev => [...prev, newUserMsg]);
    setInput("");
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: textToAnalyze, history: historyPayload }),
      });

      const data = await response.json();

      if (!response.ok || data?.error) {
        throw new Error(data?.error || data?.detail || data?.message || "Something went wrong.");
      }

      const newModelMsg = { 
        role: "model", 
        recommendation: data.recommendation,
        vibe_diff: data.vibe_diff,
        trace_id: data.trace_id,
        telemetry: data
      };

      setMessages(prev => [...prev, newModelMsg]);
    } catch (err) {
      setError(
        typeof err.message === "string"
          ? err.message
          : "System is experiencing an issue. Please try again."
      );
      // Remove the optimistic user message if it failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <div className="mx-auto max-w-6xl w-full px-6 py-10 flex-grow flex flex-col">
        <header className="mb-8 text-center">
          <p className="mb-2 inline-block rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            FinPath India
          </p>
          <h1 className="text-4xl font-bold tracking-tight mb-4">
            Counterfactual Decision Support Engine
          </h1>
          <p className="text-slate-600 max-w-2xl mx-auto text-lg leading-relaxed">
            Explore alternative realities and see the true long-term impact of your financial choices. 
            Describe your situation below (or click an example) to generate a transparent, data-driven "Vibe Diff" execution plan.
          </p>
        </header>

        {messages.length === 0 && (
          <section className="mb-8 grid gap-4 md:grid-cols-3">
            {examples.map((example, index) => (
              <button
                key={index}
                onClick={() => handleAnalyze(example)}
                className="rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-emerald-400 hover:shadow-md"
              >
                <p className="mb-2 text-sm font-semibold text-emerald-700">
                  Example {index + 1}
                </p>
                <p className="text-sm text-slate-700">{example}</p>
              </button>
            ))}
          </section>
        )}

        <div className="flex-grow overflow-auto mb-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
              {msg.role === "user" ? (
                <div className="max-w-2xl bg-emerald-600 text-white p-4 rounded-3xl rounded-br-sm shadow-sm whitespace-pre-wrap">
                  {msg.content}
                </div>
              ) : (
                <div className="w-full space-y-6">
                  {msg.vibe_diff && (
                    <section className="rounded-3xl border border-blue-200 bg-blue-50 p-6 shadow-sm">
                      <h2 className="mb-4 text-xl font-semibold text-blue-900">Agent Execution Plan (Vibe Diff)</h2>
                      <pre className="whitespace-pre-wrap break-words text-sm text-blue-800 font-mono">
                        {msg.vibe_diff}
                      </pre>
                    </section>
                  )}

                  <div className="grid gap-6 lg:grid-cols-2">
                    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                      <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold">Recommendation</h2>
                        <div className="flex gap-2 print:hidden">
                          <button onClick={() => handleFeedback(msg.trace_id, "thumbs_up")} className="p-2 hover:bg-slate-100 rounded-full transition" title="Helpful">
                            👍
                          </button>
                          <button onClick={() => handleFeedback(msg.trace_id, "thumbs_down")} className="p-2 hover:bg-slate-100 rounded-full transition" title="Not Helpful">
                            👎
                          </button>
                          <button onClick={() => window.print()} className="p-2 hover:bg-slate-100 rounded-full transition" title="Export PDF">
                            🖨️
                          </button>
                        </div>
                      </div>
                      <pre className="whitespace-pre-wrap break-words text-sm text-slate-800 font-sans">
                        {msg.recommendation}
                      </pre>
                    </section>

                    <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col hidden lg:flex">
                      <h2 className="mb-4 text-xl font-semibold">System Telemetry (JSON)</h2>
                      <pre className="max-h-[500px] flex-grow overflow-auto rounded-2xl bg-slate-900 p-4 text-sm text-emerald-400 font-mono">
                        {JSON.stringify(msg.telemetry, null, 2)}
                      </pre>
                    </section>
                  </div>
                </div>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex items-start">
              <div className="bg-slate-200 text-slate-700 p-4 rounded-3xl rounded-bl-sm shadow-sm flex gap-2 items-center">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                Running Vibe Check...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <section className="mb-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700 text-center">
            {error}
          </section>
        )}

        <section className="sticky bottom-0 bg-slate-50 pt-4 pb-2 border-t border-slate-200">
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a follow-up question..."
              className="flex-grow min-h-[60px] max-h-[200px] rounded-2xl border border-slate-300 p-4 text-base outline-none focus:border-emerald-500 resize-none shadow-sm"
              rows={1}
            />
            <button
              onClick={() => handleAnalyze()}
              disabled={isLoading || !input.trim()}
              className="rounded-2xl bg-emerald-600 px-6 font-medium text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60 shadow-sm"
            >
              Send
            </button>
            {messages.length > 0 && (
              <button
                onClick={() => { setMessages([]); setError(""); }}
                className="rounded-2xl border border-slate-300 px-4 text-slate-700 transition hover:bg-slate-100 shadow-sm"
                title="Clear Chat"
              >
                Clear
              </button>
            )}
          </div>
        </section>
      </div>

      <footer className="bg-slate-100 py-4 border-t border-slate-200 mt-auto text-center print:hidden">
        <p className="text-xs text-slate-500 max-w-4xl mx-auto px-4">
          <strong>Disclaimer:</strong> AI generated financial scenarios for demonstration purposes only. 
          Not professional financial advice. Consult a SEBI-registered advisor.
        </p>
      </footer>
    </div>
  );
}

export default App;