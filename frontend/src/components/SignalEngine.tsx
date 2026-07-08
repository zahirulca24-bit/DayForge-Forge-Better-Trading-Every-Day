import { ExecutableSignal } from "../types";
import { AlertTriangle, Activity, RefreshCw, Play } from "lucide-react";


interface SignalEngineProps {
  signals: ExecutableSignal[];
  scanResults: ExecutableSignal[];
  loading: boolean;
  onRunScan: () => Promise<void>;
  onRefresh: () => Promise<void>;
}


export default function SignalEngine({
  signals,
  scanResults,
  loading,
  onRunScan,
  onRefresh,
}: SignalEngineProps) {
  return (
    <div className="space-y-6" id="signal-engine-root">
      <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md" id="scanner-banner">
        <div className="flex flex-col xl:flex-row justify-between items-start xl:items-center gap-6">
          <div className="flex items-center space-x-4">
            <div className="p-4 rounded-xl bg-rose-500/10 text-rose-400">
              <Activity className={`w-6 h-6 ${loading ? "animate-pulse" : ""}`} />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white tracking-tight font-sans">Scanner Service</h3>
              <div className="flex flex-wrap gap-4 mt-2 text-xs font-mono text-slate-400">
                <span>Source: FastAPI `/scanner/run`</span>
                <span>Latest Results: {scanResults.length}</span>
                <span>Active Signals: {signals.length}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={onRunScan}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-all border bg-emerald-600/10 text-emerald-400 border-emerald-600/20 hover:bg-emerald-600/20 disabled:opacity-50"
            >
              <Play className="w-3 h-3" /> Run Scan
            </button>
            <button
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-bold transition-all border border-slate-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} /> Refresh
            </button>
          </div>
        </div>
      </div>

      <SignalTable title="Latest Scan Results" signals={scanResults} emptyText="No scanner results available." />
      <SignalTable title="Active Signals" signals={signals} emptyText="No active signals returned by `/signals`." />
    </div>
  );
}


function SignalTable({ title, signals, emptyText }: { title: string; signals: ExecutableSignal[]; emptyText: string }) {
  return (
    <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md">
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-white tracking-tight font-sans">{title}</h3>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse whitespace-nowrap" id={`${title.toLowerCase().replace(/\s+/g, "-")}-table`}>
          <thead>
            <tr className="border-b border-slate-800 text-[10px] font-mono uppercase tracking-wider text-slate-500">
              <th className="py-3 px-4 font-semibold">Pair</th>
              <th className="py-3 px-4 font-semibold">Dir</th>
              <th className="py-3 px-4 font-semibold">Strategy</th>
              <th className="py-3 px-4 font-semibold">Entry / SL / TP</th>
              <th className="py-3 px-4 font-semibold">RR</th>
              <th className="py-3 px-4 font-semibold">Age (s)</th>
              <th className="py-3 px-4 font-semibold text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/30 text-xs font-mono">
            {signals.map((sig) => (
              <tr key={sig.id} className="hover:bg-slate-900/10 transition-colors">
                <td className="py-4 px-4 font-semibold text-white">{sig.pair}</td>
                <td className={`py-4 px-4 font-bold ${sig.direction === "LONG" ? "text-emerald-400" : "text-rose-400"}`}>{sig.direction}</td>
                <td className="py-4 px-4 text-slate-400">{sig.indicator}</td>
                <td className="py-4 px-4">${sig.entryPrice.toFixed(2)} / ${sig.stopLoss.toFixed(2)} / ${sig.takeProfit.toFixed(2)}</td>
                <td className="py-4 px-4">{sig.rr.toFixed(1)}</td>
                <td className="py-4 px-4 text-slate-400">{Math.floor(sig.ageMs / 1000)}s</td>
                <td className="py-4 px-4 text-right font-bold text-emerald-400">{sig.executionStatus}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {signals.length === 0 && (
        <div className="p-12 text-center text-slate-600 font-mono text-xs">
          <AlertTriangle className="w-8 h-8 mx-auto mb-3 text-slate-700" />
          <span>{emptyText}</span>
        </div>
      )}
    </div>
  );
}
