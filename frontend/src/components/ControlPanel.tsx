import type { ReactNode } from "react";
import { BotControlState, ExchangeStatusResponse, SystemReadiness } from "../types";
import { Link, Sliders, ShieldAlert, Activity, Server, Play, Square, AlertTriangle, RefreshCw } from "lucide-react";


interface ControlPanelProps {
  botStatus: BotControlState;
  readiness: SystemReadiness;
  exchangeStatus: ExchangeStatusResponse;
  healthStatus: "ONLINE" | "OFFLINE";
  loading: boolean;
  actionLoading: string | null;
  onStart: () => Promise<void>;
  onStop: () => Promise<void>;
  onEmergencyStop: () => Promise<void>;
  onResume: () => Promise<void>;
  onRunScanner: () => Promise<void>;
  onRefresh: () => Promise<void>;
  onModeChange: (mode: "demo" | "live") => Promise<void>;
  onAutoTradingToggle: (enabled: boolean) => Promise<void>;
}


export default function ControlPanel({
  botStatus,
  readiness,
  exchangeStatus,
  healthStatus,
  loading,
  actionLoading,
  onStart,
  onStop,
  onEmergencyStop,
  onResume,
  onRunScanner,
  onRefresh,
  onModeChange,
  onAutoTradingToggle,
}: ControlPanelProps) {
  return (
    <div className="space-y-6" id="control-panel-root">
      <div className={`bg-bento-card border ${exchangeStatus.reachable ? "border-emerald-500/30" : "border-slate-800/80"} rounded-2xl p-6 relative overflow-hidden shadow-lg backdrop-blur-md`} id="ctrl-panel-warning">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
          <ShieldAlert className={`w-32 h-32 ${exchangeStatus.reachable ? "text-emerald-500" : "text-amber-500"}`} />
        </div>
        <div className="flex items-start space-x-4">
          <div className={`p-3 rounded-xl mt-0.5 border ${exchangeStatus.reachable ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/10" : "bg-amber-500/10 text-amber-400 border-amber-500/10"}`}>
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div className="space-y-2">
            <h2 className="text-sm font-semibold text-white tracking-tight">Exchange & Bot State: {exchangeStatus.reachable ? "ONLINE" : "OFFLINE"}</h2>
            <p className="text-xs text-slate-400 leading-relaxed max-w-2xl">
              This panel is connected to the FastAPI backend. Bot controls, scanner actions, and safety switches now use live backend endpoints instead of local UI logic.
            </p>
            <div className="inline-flex items-center space-x-2 bg-[#0A0B0E] px-3 py-1.5 rounded-xl border border-slate-800">
              <span className={`w-2 h-2 rounded-full animate-ping ${botStatus.emergency_stop ? "bg-red-400" : botStatus.status === "running" ? "bg-emerald-400" : "bg-slate-500"}`} />
              <span className="text-[10px] text-slate-400 font-mono font-medium">
                BOT {botStatus.status.toUpperCase()} / {botStatus.emergency_stop ? "EMERGENCY STOP" : "NORMAL"}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" id="controls-grid">
        <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 flex flex-col justify-between shadow-md bento-card-glow" id="connection-suite">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-sm font-semibold text-white tracking-tight font-sans">Connection Suite</h3>
                <p className="text-xs text-slate-500 mt-0.5">Backend, exchange, and readiness telemetry</p>
              </div>
              <span className="p-1.5 bg-[#0A0B0E] border border-slate-800/60 rounded-xl text-slate-500">
                <Link className="w-4 h-4" />
              </span>
            </div>

            <div className="space-y-4 mt-6" id="connection-controls">
              <StatusBox label="FastAPI Health" value={healthStatus} active={healthStatus === "ONLINE"} />
              <StatusBox label="Exchange Reachable" value={exchangeStatus.reachable ? "CONNECTED" : "OFFLINE"} active={exchangeStatus.reachable} />
              <StatusBox label="API Keys Present" value={readiness.checks.api_keys_present ? "YES" : "NO"} active={readiness.checks.api_keys_present} />
              <StatusBox label="Wallet Fetch" value={readiness.checks.wallet_fetch_success ? "SUCCESS" : "FAILED"} active={readiness.checks.wallet_fetch_success} />
              <StatusBox label="Execution Mode" value={(botStatus.execution_mode || "demo").toUpperCase()} active={(botStatus.execution_mode || "demo") === "demo" || !!botStatus.live_mode_available} />
            </div>
          </div>

          <button
            id="control-refresh-btn"
            onClick={onRefresh}
            disabled={loading}
            className="mt-8 pt-4 border-t border-slate-800/80 text-center text-[10px] text-slate-500 font-mono flex items-center justify-center space-x-1 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-slate-600 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh backend telemetry</span>
          </button>
        </div>

        <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md bento-card-glow" id="execution-engine-controls">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white tracking-tight font-sans">Bot & Scanner Controls</h3>
              <p className="text-xs text-slate-500 mt-0.5">FastAPI bot controls and manual scan trigger</p>
            </div>
            <span className="p-1.5 bg-[#0A0B0E] border border-slate-800/60 rounded-xl text-slate-500">
              <Sliders className="w-4 h-4" />
            </span>
          </div>

          <div className="space-y-4 mt-6" id="engine-toggles-container">
            <ActionRow
              title="Bot Start"
              description="Set bot status to running"
              buttonLabel="START"
              onClick={onStart}
              loading={actionLoading === "bot-start"}
              accent="emerald"
              icon={<Play className="w-3 h-3" />}
            />
            <ActionRow
              title="Bot Stop"
              description="Set bot status to stopped"
              buttonLabel="STOP"
              onClick={onStop}
              loading={actionLoading === "bot-stop"}
              accent="amber"
              icon={<Square className="w-3 h-3" />}
            />
            <ActionRow
              title="Manual Scanner Run"
              description="Trigger POST /scanner/run and refresh signals"
              buttonLabel="RUN SCAN"
              onClick={onRunScanner}
              loading={actionLoading === "scanner"}
              accent="rose"
              icon={<Play className="w-3 h-3" />}
            />
            <ActionRow
              title="Switch To Demo"
              description="Use demo Bybit keys and testnet execution"
              buttonLabel="DEMO"
              onClick={() => onModeChange("demo")}
              loading={actionLoading === "bot-config-mode"}
              accent="emerald"
              icon={<Play className="w-3 h-3" />}
            />
            <ActionRow
              title="Switch To Live"
              description={botStatus.live_mode_available ? "Enable real Bybit execution after validation" : "Requires live Bybit API keys first"}
              buttonLabel="LIVE"
              onClick={() => onModeChange("live")}
              loading={actionLoading === "bot-config-mode"}
              accent="amber"
              icon={<AlertTriangle className="w-3 h-3" />}
            />
          </div>
        </div>

        <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md bento-card-glow" id="system-health-section">
          <h3 className="text-sm font-semibold text-white tracking-tight font-sans mb-4 flex items-center gap-2">
            <Server className="w-4 h-4 text-emerald-400" /> System Health
          </h3>
          <div className="space-y-3 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-500">Backend</span>
              <span className={healthStatus === "ONLINE" ? "text-emerald-400" : "text-rose-500"}>{healthStatus}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Bot Status</span>
              <span className={botStatus.status === "running" ? "text-emerald-400" : "text-slate-400"}>{botStatus.status.toUpperCase()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Readiness</span>
              <span className={readiness.ready_for_execution ? "text-emerald-400" : "text-amber-400"}>
                {readiness.ready_for_execution ? "READY" : "BLOCKED"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Emergency Stop</span>
              <span className={botStatus.emergency_stop ? "text-rose-500" : "text-emerald-400"}>
                {botStatus.emergency_stop ? "ACTIVE" : "CLEAR"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Auto Trading</span>
              <button
                onClick={() => onAutoTradingToggle(!(botStatus.auto_trading_enabled ?? true))}
                className={`text-right ${botStatus.auto_trading_enabled ? "text-emerald-400" : "text-amber-400"}`}
              >
                {botStatus.auto_trading_enabled ? "ENABLED" : "DISABLED"}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-bento-card border border-slate-800 rounded-2xl p-6 shadow-md bento-card-glow" id="emergency-commands-section">
        <h3 className="text-sm font-semibold text-white mb-1 tracking-tight font-sans">Safety & Emergency Commands</h3>
        <p className="text-xs text-slate-500 mb-6">Execution is blocked while emergency stop is active</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4" id="emergency-buttons">
          <ActionRow
            title="Emergency Stop"
            description="POST /bot/emergency-stop"
            buttonLabel="ACTIVATE"
            onClick={onEmergencyStop}
            loading={actionLoading === "bot-emergency"}
            accent="red"
            icon={<AlertTriangle className="w-3 h-3" />}
          />
          <ActionRow
            title="Resume Bot"
            description="POST /bot/resume"
            buttonLabel="RESUME"
            onClick={onResume}
            loading={actionLoading === "bot-resume"}
            accent="emerald"
            icon={<Play className="w-3 h-3" />}
          />
        </div>
      </div>
    </div>
  );
}


function StatusBox({ label, value, active }: { label: string; value: string; active: boolean }) {
  return (
    <div className="p-4 bg-[#0A0B0E] border border-slate-800/65 rounded-xl flex items-center justify-between">
      <div>
        <h4 className="text-xs font-semibold text-slate-200">{label}</h4>
        <p className="text-[10px] text-slate-500 mt-1">{value}</p>
      </div>
      <span className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${active ? "bg-emerald-500/10 text-emerald-400" : "bg-slate-800 text-slate-500"}`}>
        {active ? "OK" : "WAIT"}
      </span>
    </div>
  );
}


function ActionRow({
  title,
  description,
  buttonLabel,
  onClick,
  loading,
  accent,
  icon,
}: {
  title: string;
  description: string;
  buttonLabel: string;
  onClick: () => Promise<void>;
  loading: boolean;
  accent: "emerald" | "amber" | "rose" | "red";
  icon: ReactNode;
}) {
  const styles = {
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20 hover:bg-amber-500/20",
    rose: "bg-rose-500/10 text-rose-400 border-rose-500/20 hover:bg-rose-500/20",
    red: "bg-red-500/10 text-red-400 border-red-500/20 hover:bg-red-500/20",
  }[accent];

  return (
    <div className="p-4 bg-[#0A0B0E] border border-slate-800/65 rounded-xl flex items-center justify-between">
      <div>
        <h4 className="text-xs font-semibold text-slate-200">{title}</h4>
        <p className="text-[10px] text-slate-500 mt-1">{description}</p>
      </div>
      <button
        onClick={onClick}
        disabled={loading}
        className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all border flex items-center space-x-1.5 ${styles} disabled:opacity-50 cursor-pointer`}
      >
        {icon}
        <span>{loading ? "..." : buttonLabel}</span>
      </button>
    </div>
  );
}
