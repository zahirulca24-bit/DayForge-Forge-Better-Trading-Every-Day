import {
  AccountResponse,
  BotControlState,
  ExchangeStatusResponse,
  ExecutableSignal,
  MetricsResponse,
  PortfolioSummary,
  SystemReadiness,
  Trade,
  TradeHistoryEntry,
} from "../types";
import { AlertTriangle, Clock, Coins, ArrowUpRight, ArrowDownRight, Zap, Bot } from "lucide-react";


interface DashboardViewProps {
  readiness: SystemReadiness;
  botStatus: BotControlState;
  exchangeStatus: ExchangeStatusResponse;
  account: AccountResponse;
  metrics: MetricsResponse;
  portfolio: PortfolioSummary;
  activeTrades: Trade[];
  signals: ExecutableSignal[];
  tradeHistory: TradeHistoryEntry[];
  lastSync?: Date | null;
  isStale?: boolean;
}


function numberValue(value: string | number | undefined) {
  const numeric = Number(value || 0);
  return Number.isFinite(numeric) ? numeric : 0;
}


export default function DashboardView({
  readiness,
  botStatus,
  exchangeStatus,
  account,
  metrics,
  portfolio,
  activeTrades,
  signals,
  tradeHistory,
  lastSync,
  isStale,
}: DashboardViewProps) {
  const wallet = account.wallet.data || {};
  const totalBalance = numberValue(wallet.totalWalletBalance || wallet.totalEquity);
  const availableBalance = numberValue(wallet.totalAvailableBalance);
  const exposure = activeTrades.reduce((sum, trade) => sum + (trade.size * trade.entryPrice), 0);
  const openPnl = 0;
  const exposurePct = totalBalance > 0 ? Math.min((exposure / totalBalance) * 100, 100) : 0;

  return (
    <div className="space-y-6" id="dashboard-view-root">
      <div className="bg-bento-card-sec/40 border border-slate-800/80 rounded-2xl p-6 flex flex-col xl:flex-row justify-between items-start xl:items-center gap-4 shadow-lg backdrop-blur-md" id="dashboard-banner">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight font-sans flex items-center gap-3">
            Algorithmic Scalping Engine
            {isStale && (
              <span className="bg-rose-500/10 text-rose-400 text-[10px] px-2 py-0.5 rounded-full border border-rose-500/20 flex items-center font-mono">
                <AlertTriangle className="w-3 h-3 mr-1" /> STALE DATA
              </span>
            )}
            {!isStale && !exchangeStatus.reachable && (
              <span className="bg-amber-500/10 text-amber-400 text-[10px] px-2 py-0.5 rounded-full border border-amber-500/20 flex items-center font-mono">
                Backend Online / Exchange Unreachable
              </span>
            )}
          </h1>
          <p className="text-xs text-slate-400 mt-1 flex items-center gap-2">
            {botStatus.status === "running" ? "Bot is running and ready to scan protected endpoints." : "Bot is not running. Execution remains blocked."}
            {lastSync && (
              <span className="flex items-center gap-1 bg-slate-800/50 px-2 py-0.5 rounded-md text-[10px] text-slate-400 font-mono">
                <Clock className="w-3 h-3 text-slate-500" />
                Last Sync: {lastSync.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 shrink-0" id="dashboard-status-indicator">
          <div className="px-3 py-1.5 bg-[#0A0B0E] border border-slate-800 rounded-xl flex items-center space-x-2 font-mono text-[10px]">
            <span className={`w-1.5 h-1.5 rounded-full ${botStatus.emergency_stop ? "bg-red-500 animate-ping" : botStatus.status === "running" ? "bg-emerald-500 animate-pulse" : "bg-slate-500"}`} />
            <span className={botStatus.emergency_stop ? "text-red-400 font-semibold" : botStatus.status === "running" ? "text-emerald-400 font-semibold" : "text-slate-400 font-semibold"}>
              {botStatus.emergency_stop ? "EMERGENCY STOP" : `BOT ${botStatus.status.toUpperCase()}`}
            </span>
          </div>
          <div className="px-3 py-1.5 bg-[#0A0B0E] border border-slate-800 rounded-xl flex items-center space-x-2 font-mono text-[10px]">
            <span className="text-slate-500 font-medium">READINESS:</span>
            <span className={`font-semibold ${readiness.ready_for_execution ? "text-emerald-400" : "text-amber-400"}`}>
              {readiness.ready_for_execution ? "READY" : "NOT READY"}
            </span>
          </div>
          <div className="px-3 py-1.5 bg-[#0A0B0E] border border-slate-800 rounded-xl flex items-center space-x-2 font-mono text-[10px]">
            <span className="text-slate-500 font-medium">MODE:</span>
            <span className={`font-semibold ${(botStatus.execution_mode || "demo") === "live" ? "text-amber-400" : "text-emerald-400"}`}>
              {(botStatus.execution_mode || "demo").toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4" id="stats-grid">
        <div className="bg-bento-card border border-slate-800/80 rounded-2xl p-5 bento-card-glow shadow-md" id="stat-card-balance">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-semibold">Total Portfolio Value</span>
            <div className="p-2 bg-rose-500/10 text-rose-400 rounded-xl border border-rose-500/10">
              <Coins className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-bold text-white tracking-tight font-sans">
              ${totalBalance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </h3>
          </div>
        </div>

        <div className="bg-bento-card border border-slate-800/80 rounded-2xl p-5 bento-card-glow shadow-md" id="stat-card-pnl">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-semibold">Simple PnL</span>
            <div className={`p-2 rounded-xl border ${metrics.pnl_r >= 0 ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/10" : "bg-red-500/10 text-red-400 border-red-500/10"}`}>
              {metrics.pnl_r >= 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
            </div>
          </div>
          <div className="mt-4">
            <h3 className={`text-2xl font-bold tracking-tight font-sans ${metrics.pnl_r >= 0 ? "text-emerald-400" : "text-red-400"}`}>
              {metrics.pnl_r >= 0 ? "+" : ""}{metrics.pnl_r.toFixed(2)}R
            </h3>
          </div>
        </div>

        <div className="bg-bento-card border border-slate-800/80 rounded-2xl p-5 bento-card-glow shadow-md" id="stat-card-exposure">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-semibold">Active Exposure</span>
            <div className="p-2 bg-violet-500/10 text-violet-400 rounded-xl border border-violet-500/10">
              <Zap className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-bold text-white tracking-tight font-sans">
              ${exposure.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </h3>
            <p className="text-xs text-slate-500 mt-2 flex items-center space-x-1 font-mono">
              <span>Running:</span>
              <span className="text-rose-400 font-semibold bg-rose-500/10 px-1.5 py-0.5 rounded">{activeTrades.length} positions</span>
            </p>
          </div>
        </div>

        <div className="bg-bento-card border border-slate-800/80 rounded-2xl p-5 bento-card-glow shadow-md" id="stat-card-signals">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider font-semibold">Live Signals Captured</span>
            <div className="p-2 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/10">
              <Bot className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-4">
            <h3 className="text-2xl font-bold text-white tracking-tight font-sans">{signals.length} Active</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" id="dashboard-midsection">
        <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 lg:col-span-2 flex flex-col justify-between shadow-md" id="engine-overview">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-semibold text-white tracking-tight font-sans">Execution Setup & Status</h2>
              <span className="text-[9px] text-slate-500 font-mono tracking-wider font-bold">TELEMETRY</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4" id="states-overview-grid">
              <StatusCard label="Admin Auth" ok={readiness.checks.admin_auth_configured} />
              <StatusCard label="API Keys" ok={readiness.checks.api_keys_present} />
              <StatusCard label="Exchange" ok={readiness.checks.exchange_reachable} />
              <StatusCard label="Wallet Fetch" ok={readiness.checks.wallet_fetch_success} />
              <StatusCard label="Bot Status" value={botStatus.status.toUpperCase()} ok={botStatus.status === "running"} />
              <StatusCard label="Emergency" value={botStatus.emergency_stop ? "ACTIVE" : "CLEAR"} ok={!botStatus.emergency_stop} />
              <StatusCard label="Win Rate" value={`${(metrics.win_rate * 100).toFixed(1)}%`} ok={metrics.win_rate >= 0.5 || metrics.total_trades === 0} />
              <StatusCard label="Available Bal" value={`$${availableBalance.toFixed(2)}`} ok={availableBalance > 0} />
            </div>
          </div>

          {(!readiness.ready_for_execution || exchangeStatus.error || readiness.errors.exchange || readiness.errors.wallet) && (
            <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 mt-4">
              <h3 className="text-xs font-semibold text-amber-400 mb-2">Current Blocking Reasons</h3>
              <ul className="list-disc pl-4 space-y-1">
                {!readiness.checks.admin_auth_configured && <li className="text-amber-400/80 text-[10px] font-mono">Admin auth is not configured.</li>}
                {!readiness.checks.api_keys_present && <li className="text-amber-400/80 text-[10px] font-mono">Bybit demo API keys are missing.</li>}
                {!readiness.checks.exchange_reachable && <li className="text-amber-400/80 text-[10px] font-mono">{readiness.errors.exchange || exchangeStatus.error || "Exchange is not reachable."}</li>}
                {!readiness.checks.wallet_fetch_success && <li className="text-amber-400/80 text-[10px] font-mono">{readiness.errors.wallet || "Wallet fetch failed."}</li>}
                {botStatus.emergency_stop && <li className="text-amber-400/80 text-[10px] font-mono">Emergency stop is active.</li>}
                {botStatus.status !== "running" && <li className="text-amber-400/80 text-[10px] font-mono">Bot is not running.</li>}
              </ul>
            </div>
          )}

          <div className="mt-6 space-y-3" id="risk-metric-visual">
            <div className="flex justify-between items-center">
              <span className="text-xs text-slate-400 font-mono">Active Exposure relative to total cap:</span>
              <span className="text-xs text-white font-mono font-semibold">{totalBalance > 0 ? `${exposurePct.toFixed(1)}%` : "0.0%"}</span>
            </div>
            <div className="w-full bg-[#0A0B0E] h-2.5 rounded-full overflow-hidden border border-slate-800" id="exposure-bar-container">
              <div className="bg-gradient-to-r from-rose-600 to-rose-400 h-full rounded-full transition-all duration-1000" style={{ width: `${exposurePct}%` }} />
            </div>
          </div>
        </div>

        <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md" id="asset-allocation-overview">
          <h2 className="text-sm font-semibold text-white mb-4 tracking-tight font-sans">Portfolio Summary</h2>
          <div className="space-y-3" id="assets-split-list">
            <SummaryRow label="Total Trades" value={portfolio.total_trades} />
            <SummaryRow label="Active Trades" value={portfolio.active_trades} />
            <SummaryRow label="Closed Trades" value={portfolio.closed_trades} />
            <SummaryRow label="Win Trades" value={metrics.win_trades} />
            <SummaryRow label="Loss Trades" value={metrics.loss_trades} />
            <SummaryRow label="Closed History" value={tradeHistory.length} />
            <SummaryRow label="Execution Mode" value={(portfolio.execution_mode || botStatus.execution_mode || "demo").toUpperCase()} />
            <SummaryRow label="Available Balance" value={`$${availableBalance.toFixed(2)}`} />
            <SummaryRow label="Open PnL" value={`$${openPnl.toFixed(2)}`} />
          </div>
        </div>
      </div>
    </div>
  );
}


function StatusCard({ label, ok, value }: { label: string; ok: boolean; value?: string }) {
  return (
    <div className="bg-[#0A0B0E] border border-slate-800/60 rounded-xl p-3 text-center">
      <p className="text-[9px] text-slate-500 uppercase tracking-wider font-mono font-medium">{label}</p>
      <p className={`text-xs font-semibold mt-1 font-mono ${ok ? "text-emerald-400" : "text-amber-400"}`}>
        {value || (ok ? "READY" : "BLOCKED")}
      </p>
    </div>
  );
}


function SummaryRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-[#0A0B0E] border border-slate-800/40 p-3 rounded-xl flex items-center justify-between">
      <span className="text-xs font-semibold text-slate-200">{label}</span>
      <span className="text-xs font-semibold text-white font-mono">{value}</span>
    </div>
  );
}
