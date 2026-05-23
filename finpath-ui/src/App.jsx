import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

const examples = [
  "I have 2 lakh in savings, 1.5 lakh credit card debt at 36 percent interest, and 20000 monthly surplus. Should I repay debt first or invest?",
  "I earn 80000 per month, have 3 lakh savings, no debt, and can invest 25000 monthly for 5 years. Should I choose SIPs, PPF, or fixed deposits?",
  "I have a 12 percent car loan, 5 lakh in cash, and I want to start investing for 10 years. Should I clear the loan first or start investing now?"
];

function App() {
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleAnalyze = async () => {
    if (!query.trim()) {
      setError("Please enter your financial situation first.");
      return;
    }

    setIsLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || data?.message || "Something went wrong.");
      }

      setResult(data);
    } catch (err) {
      setError(
        typeof err.message === "string"
          ? err.message
          : "System is experiencing an issue. Please try again."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const renderValue = (value) => {
    if (value === null || value === undefined) return "—";
    if (typeof value === "object") return JSON.stringify(value, null, 2);
    return String(value);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <header className="mb-8">
          <p className="mb-2 inline-block rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            FinPath India
          </p>
          <h1 className="text-4xl font-bold tracking-tight">
            AI-assisted financial decision support
          </h1>
          <p className="mt-3 max-w-3xl text-slate-600">
            Describe your situation in plain English. FinPath will analyze the trade-offs
            and return a recommendation with supporting details.
          </p>
        </header>

        <section className="mb-8 grid gap-4 md:grid-cols-3">
          {examples.map((example, index) => (
            <button
              key={index}
              onClick={() => setQuery(example)}
              className="rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-emerald-400 hover:shadow-md"
            >
              <p className="mb-2 text-sm font-semibold text-emerald-700">
                Example {index + 1}
              </p>
              <p className="text-sm text-slate-700">{example}</p>
            </button>
          ))}
        </section>

        <section className="mb-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-xl font-semibold">Your situation</h2>
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: I have 3 lakh savings, 1 lakh debt, and can invest 20000 monthly. What should I prioritize?"
            className="min-h-[180px] w-full rounded-2xl border border-slate-300 p-4 text-base outline-none focus:border-emerald-500"
          />
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={handleAnalyze}
              disabled={isLoading}
              className="rounded-2xl bg-emerald-600 px-5 py-3 font-medium text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? "Analyzing..." : "Analyze Path"}
            </button>

            <button
              onClick={() => {
                setQuery("");
                setResult(null);
                setError("");
              }}
              className="rounded-2xl border border-slate-300 px-5 py-3 font-medium text-slate-700 transition hover:bg-slate-100"
            >
              Clear
            </button>
          </div>
        </section>

        {error && (
          <section className="mb-8 rounded-2xl border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </section>
        )}

        {result && (
          <div className="grid gap-6 lg:grid-cols-2">
            <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-xl font-semibold">Recommendation</h2>
              <pre className="whitespace-pre-wrap break-words text-sm text-slate-800">
                {renderValue(result.recommendation || result.answer || result.result || result)}
              </pre>
            </section>

            <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="mb-4 text-xl font-semibold">Full response</h2>
              <pre className="max-h-[500px] overflow-auto rounded-2xl bg-slate-900 p-4 text-sm text-slate-100">
                {JSON.stringify(result, null, 2)}
              </pre>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;