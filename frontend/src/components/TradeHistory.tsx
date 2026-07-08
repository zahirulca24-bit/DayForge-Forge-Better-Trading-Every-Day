import { TradeHistoryEntry } from "../types";

interface TradeHistoryProps {
  history: TradeHistoryEntry[];
}

export default function TradeHistory({ history }: TradeHistoryProps) {
  const list = history || [];
  return (
    <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md" id="trade-history-section">
      <h3 className="text-sm font-semibold text-white tracking-tight font-sans mb-6 font-sans">Trade History ({list.length})</h3>
      <div className="overflow-x-auto">
        {list.length === 0 ? (
          <div className="py-8 text-center text-slate-500 font-mono text-xs">
            No closed positions logged. Activated strategies will log scalps here.
          </div>
        ) : (
          <table className="w-full text-left border-collapse" id="trade-history-table">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] font-mono uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4 font-semibold">Pair</th>
                <th className="py-3 px-4 font-semibold text-right">Entry/Exit</th>
                <th className="py-3 px-4 font-semibold text-right">PnL</th>
                <th className="py-3 px-4 font-semibold text-right">Result</th>
                <th className="py-3 px-4 font-semibold text-right">SL Reason</th>
                <th className="py-3 px-4 font-semibold text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/30 text-xs font-mono">
              {list.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-900/10 transition-colors">
                  <td className="py-4 px-4 font-semibold text-white">
                    {entry.pair}
                    <span className="block text-[9px] text-slate-500 font-normal">{entry.strategy || "EMA Rejection"}</span>
                  </td>
                  <td className="py-4 px-4 text-right">
                    ${(entry.entryPrice || 0).toFixed(4)} / ${(entry.exitPrice || 0).toFixed(4)}
                  </td>
                  <td className={`py-4 px-4 text-right ${(entry.pnl || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    ${(entry.pnl || 0).toFixed(2)} ({(entry.pnlPercent || 0).toFixed(2)}%)
                  </td>
                  <td className={`py-4 px-4 text-right font-bold ${(entry.result || 'PROFIT') === 'PROFIT' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {entry.result || "PROFIT"}
                  </td>
                  <td className="py-4 px-4 text-right text-slate-400">
                    {entry.result === "LOSS" ? (entry.reason || "unknown") : "-"}
                  </td>
                  <td className="py-4 px-4 text-right text-slate-500">
                    {entry.closedAt ? new Date(entry.closedAt).toLocaleTimeString() : "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
