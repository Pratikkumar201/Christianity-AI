"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import { runEvaluation, EvaluationMetrics, EvalSuiteResult } from "@/lib/api";

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSuite, setExpandedSuite] = useState<string | null>(null);

  const handleRun = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const data = await runEvaluation();
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed. Make sure the backend is running.");
    } finally {
      setIsRunning(false);
    }
  };

  const metricCards = metrics
    ? [
        { label: "Fake Verse Detection", value: metrics.fake_verse_detection_rate, icon: "🔍", color: "text-emerald-400" },
        { label: "Real Verse Accuracy", value: metrics.real_verse_accuracy, icon: "📖", color: "text-blue-400" },
        { label: "Safety Block Rate", value: metrics.safety_block_rate, icon: "🛡️", color: "text-red-400" },
        { label: "Safety Allow Rate", value: metrics.safety_allow_rate, icon: "✅", color: "text-green-400" },
        { label: "Hallucination Prevention", value: metrics.hallucination_prevention_rate, icon: "🧠", color: "text-purple-400" },
        { label: "Overall Score", value: metrics.overall_score, icon: "⭐", color: "text-gold-400" },
      ]
    : [];

  return (
    <div className="min-h-screen bg-navy-950">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-gold-400 to-gold-700 flex items-center justify-center text-2xl mx-auto mb-4 glow-gold">
            📊
          </div>
          <h1 className="text-3xl font-bold gold-text mb-2" style={{ fontFamily: "Cinzel, serif" }}>
            Evaluation Dashboard
          </h1>
          <p className="text-gray-400 text-sm max-w-xl mx-auto">
            Quantitative assessment of hallucination prevention, fake verse detection, safety filtering, and adversarial resistance across all test suites.
          </p>
        </div>

        {/* Test Categories Description */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
          {[
            { icon: "🔍", label: "Fake Verse", desc: "Invalid ch/verse detection" },
            { icon: "📖", label: "Real Verse", desc: "Valid reference accuracy" },
            { icon: "🛡️", label: "Safety Block", desc: "Harmful content blocking" },
            { icon: "✅", label: "Safety Allow", desc: "Benign content passing" },
            { icon: "🧠", label: "Hallucination", desc: "Fabrication prevention" },
          ].map((c) => (
            <div key={c.label} className="glass-light rounded-xl p-3 text-center">
              <div className="text-xl mb-1">{c.icon}</div>
              <p className="text-xs font-semibold text-gray-200">{c.label}</p>
              <p className="text-[10px] text-gray-500 mt-0.5">{c.desc}</p>
            </div>
          ))}
        </div>

        {/* Run button */}
        <div className="text-center mb-8">
          <button
            onClick={handleRun}
            disabled={isRunning}
            className="btn-gold px-8 py-3 rounded-xl text-sm flex items-center gap-2 mx-auto"
          >
            {isRunning ? (
              <>
                <div className="w-4 h-4 border-2 border-navy-900/40 border-t-navy-900 rounded-full animate-spin" />
                Running Evaluation Suite...
              </>
            ) : (
              <> 🚀 Run Full Evaluation Suite </>
            )}
          </button>
          {isRunning && (
            <p className="text-xs text-gray-500 mt-2">
              Running safety checks, verse verification, and hallucination tests...
            </p>
          )}
        </div>

        {error && (
          <div className="glass rounded-xl p-4 border border-red-500/20 text-red-400 text-sm mb-6 text-center">
            ❌ {error}
          </div>
        )}

        {/* Metrics Grid */}
        {metrics && (
          <div className="animate-fade-in space-y-8">
            {/* Score cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {metricCards.map((m) => (
                <div key={m.label} className="metric-card text-center">
                  <div className="text-2xl mb-2">{m.icon}</div>
                  <div className={`text-3xl font-bold ${m.color} mb-1`}>
                    {(m.value * 100).toFixed(1)}%
                  </div>
                  <p className="text-xs text-gray-400">{m.label}</p>
                  <div className="progress-bar mt-3">
                    <div
                      className="progress-fill"
                      style={{ width: `${m.value * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="glass rounded-xl p-5 flex items-center justify-between flex-wrap gap-4">
              <div>
                <p className="text-xs text-gray-400 mb-1">Total Tests Run</p>
                <p className="text-2xl font-bold text-gray-100">{metrics.total_tests}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Tests Passed</p>
                <p className="text-2xl font-bold text-emerald-400">{metrics.total_passed}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Tests Failed</p>
                <p className="text-2xl font-bold text-red-400">{metrics.total_tests - metrics.total_passed}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Eval Time</p>
                <p className="text-2xl font-bold text-gray-100">{metrics.eval_time_ms}ms</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Overall Score</p>
                <p className={`text-3xl font-bold ${metrics.overall_score >= 0.9 ? "text-emerald-400" : metrics.overall_score >= 0.7 ? "text-gold-400" : "text-red-400"}`}>
                  {(metrics.overall_score * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Per-suite details */}
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
                Detailed Results by Suite
              </h2>
              {Object.entries(metrics.results).map(([key, suite]) => (
                <SuiteCard
                  key={key}
                  suiteKey={key}
                  suite={suite}
                  expanded={expandedSuite === key}
                  onToggle={() => setExpandedSuite(expandedSuite === key ? null : key)}
                />
              ))}
            </div>
          </div>
        )}

        {!metrics && !isRunning && (
          <div className="glass rounded-xl p-16 text-center">
            <div className="text-5xl mb-4 opacity-20">📊</div>
            <p className="text-gray-500 text-sm">Click "Run Full Evaluation Suite" to begin</p>
            <p className="text-gray-600 text-xs mt-1">
              Tests hallucination prevention, fake verse detection, safety filters, and more
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function SuiteCard({
  suiteKey,
  suite,
  expanded,
  onToggle,
}: {
  suiteKey: string;
  suite: EvalSuiteResult;
  expanded: boolean;
  onToggle: () => void;
}) {
  const pct = (suite.accuracy * 100).toFixed(1);
  const color =
    suite.accuracy >= 0.9
      ? "text-emerald-400"
      : suite.accuracy >= 0.7
      ? "text-gold-400"
      : "text-red-400";

  return (
    <div className="glass rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-gold-900/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`text-lg font-bold ${color}`}>{pct}%</div>
          <div className="text-left">
            <p className="text-sm font-medium text-gray-200">{suite.test}</p>
            <p className="text-xs text-gray-500">
              {suite.passed}/{suite.total} passed
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-32 progress-bar">
            <div className="progress-fill" style={{ width: `${suite.accuracy * 100}%` }} />
          </div>
          <span className="text-gray-400 text-xs">{expanded ? "▲" : "▼"}</span>
        </div>
      </button>

      {expanded && (
        <div className="border-t border-gold-700/10 p-4 animate-fade-in">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="text-gray-500 border-b border-navy-700/40">
                  <th className="text-left py-1.5 pr-3">Input/Reference</th>
                  <th className="text-left py-1.5 pr-3">Expected</th>
                  <th className="text-left py-1.5 pr-3">Got</th>
                  <th className="text-left py-1.5">Result</th>
                </tr>
              </thead>
              <tbody>
                {suite.details.map((d, i) => (
                  <tr key={i} className="border-b border-navy-700/20 hover:bg-gold-900/5 transition-colors">
                    <td className="py-1.5 pr-3 text-gray-300 max-w-[200px] truncate">
                      {d.input || d.reference || d.id}
                    </td>
                    <td className="py-1.5 pr-3 text-gray-400">{d.expected || "—"}</td>
                    <td className="py-1.5 pr-3 text-gray-400">{d.got || "—"}</td>
                    <td className="py-1.5">
                      <span
                        className={`badge ${d.passed ? "badge-safe" : "badge-danger"}`}
                      >
                        {d.passed ? "✓ PASS" : "✗ FAIL"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
