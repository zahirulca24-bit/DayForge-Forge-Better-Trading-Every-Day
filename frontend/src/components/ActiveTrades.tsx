import { Trade } from "../types";
import { AlertTriangle, CheckCircle2 } from "lucide-react";


interface ActiveTradesProps {
  trades: Trade[];
}


export default function ActiveTrades({ trades }: ActiveTradesProps) {
  return (
    <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md" id="active-trades-section">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-sm font-semibold text-white tracking-tight font-sans">Active Trades ({trades.length})</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse" id="active-trades-table">
          <thead>
            <tr className="border-b border-slate-800 text-[10px] font-mono uppercase tracking-wider text-slate-500">
              <th className="py-3 px-4 font-semibold">Pair</th>
              <th className="py-3 px-4 font-semibold">Side</th>
              <th className="py-3 px-4 font-semibold text-right">Entry / SL / TP</th>
              <th className="py-3 px-4 font-semibold text-right">Quantity</th>
              <th className="py-3 px-4 font-semibold text-right">Flags</th>
              <th className="py-3 px-4 font-semibold text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/30 text-xs font-mono">
            {trades.map((trade) => (
              <tr key={trade.id} className="hover:bg-slate-900/10 transition-colors">
                <td className="py-4 px-4 font-semibold text-white">
                  {trade.pair}
                  {trade.executionMode && (
                    <span className="block text-[9px] text-slate-500 mt-1">{trade.executionMode.toUpperCase()} / {trade.journalId || "no-journal"}</span>
                  )}
                  {trade.isUnsafe && (
                    <span className="flex items-center space-x-1 text-rose-500 mt-1">
                      <AlertTriangle className="w-3 h-3" />
                      <span className="text-[9px]">UNSAFE</span>
                    </span>
                  )}
                </td>
                <td className={`py-4 px-4 font-bold ${trade.direction === "LONG" ? "text-emerald-400" : "text-red-400"}`}>{trade.direction}</td>
                <td className="py-4 px-4 text-right text-slate-300">
                  ${trade.entryPrice.toFixed(2)} / ${trade.stopLoss.toFixed(2)} / ${trade.takeProfit.toFixed(2)}
                </td>
                <td className="py-4 px-4 text-right text-slate-300">{trade.size}</td>
                <td className="py-4 px-4 text-right space-x-1">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] ${trade.orderConfirmed ? "bg-emerald-500/10 text-emerald-400" : "bg-slate-800 text-slate-500"}`} title="Order Confirmed">ORD</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] ${trade.slVerified ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`} title="SL Verified">SL</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] ${trade.tpVerified ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`} title="TP Verified">TP</span>
                  <span className={`px-1.5 py-0.5 rounded text-[9px] ${trade.positionSynced ? "bg-emerald-500/10 text-emerald-400" : "bg-slate-800 text-slate-500"}`} title="Position Synced">SYNC</span>
                </td>
                <td className="py-4 px-4 text-right">
                  <span className="inline-flex items-center gap-1 text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{trade.rawStatus || trade.status}</span>
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {trades.length === 0 && (
        <div className="py-8 text-center text-slate-500 font-mono text-xs">No active trades returned by the backend.</div>
      )}
    </div>
  );
}
