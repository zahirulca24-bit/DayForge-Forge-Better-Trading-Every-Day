import { LogEntry } from "../types";
import { Terminal, Shield, RefreshCw, Trash2, Search, Filter } from "lucide-react";
import { useState } from "react";

interface LogsProps {
  logs: LogEntry[];
  onClearLogs: () => void;
  loading: boolean;
  onRefresh: () => Promise<void>;
}

export default function Logs({
  logs,
  onClearLogs,
  loading,
  onRefresh
}: LogsProps) {
  const [filter, setFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredLogs = logs.filter((log) => {
    const matchesFilter = filter === "ALL" || log.level === filter;
    const matchesSearch = log.message.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col h-[calc(100vh-8rem)]" id="logs-view-root">
      {/* Logs Tool Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-800" id="logs-header">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center space-x-1.5">
            <Terminal className="w-4 h-4 text-rose-500" />
            <span>Diagnostics Terminal Output</span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">Real-time status loops from local scalp orchestrators</p>
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto justify-between sm:justify-end">
          <button
            id="refresh-logs-btn"
            onClick={onRefresh}
            disabled={loading}
            className="p-2 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded-xl transition-all border border-slate-800 cursor-pointer disabled:opacity-50"
            title="Force refresh logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
          <button
            id="clear-logs-btn"
            onClick={onClearLogs}
            className="p-2 hover:bg-slate-800 text-slate-400 hover:text-rose-400 rounded-xl transition-all border border-slate-800 cursor-pointer"
            title="Clear active terminal screen"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Filter and search bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 my-4" id="logs-controls">
        <div className="relative sm:col-span-2">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            id="log-search-input"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search terminal outputs..."
            className="w-full bg-slate-950 border border-slate-850 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-300 placeholder-slate-600 focus:outline-none focus:border-rose-500/50"
          />
        </div>

        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
          <select
            id="log-level-filter"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full bg-slate-950 border border-slate-850 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-300 focus:outline-none focus:border-rose-500/50 cursor-pointer appearance-none"
          >
            <option value="ALL">ALL LEVELS</option>
            <option value="INFO">INFO</option>
            <option value="SUCCESS">SUCCESS</option>
            <option value="WARNING">WARNING</option>
            <option value="ERROR">ERROR</option>
          </select>
        </div>
      </div>

      {/* Code style Terminal Console */}
      <div className="flex-1 bg-slate-950 rounded-xl border border-slate-850 p-4 font-mono text-[11px] overflow-y-auto leading-relaxed select-text" id="terminal-screen">
        <div className="flex items-center space-x-2 text-slate-500 pb-2 border-b border-slate-900 mb-3" id="terminal-identity">
          <Shield className="w-3.5 h-3.5 text-emerald-500" />
          <span>SESSION HANDSHAKE ON PIPELINE 'LOCAL_MOCK_1'</span>
        </div>

        <div className="space-y-1.5" id="logs-lines-container">
          {filteredLogs.map((log) => {
            let colorClass = "text-slate-400";
            if (log.level === "SUCCESS") colorClass = "text-emerald-400 font-semibold";
            if (log.level === "WARNING") colorClass = "text-amber-400 font-semibold";
            if (log.level === "ERROR") colorClass = "text-rose-500 font-bold";

            return (
              <div key={log.id} className="hover:bg-slate-900/40 p-1 rounded transition-colors flex items-start gap-2.5">
                <span className="text-slate-600 shrink-0 select-none">
                  [{new Date(log.timestamp).toLocaleTimeString()}]
                </span>
                <span className={`shrink-0 select-none uppercase tracking-wide font-bold [width:65px] ${colorClass}`}>
                  {log.level}
                </span>
                <span className="text-slate-300 break-all">{log.message}</span>
              </div>
            );
          })}

          {filteredLogs.length === 0 && (
            <div className="text-center text-slate-700 py-12" id="empty-terminal">
              <span>-- NO DIAGNOSTIC LOGS MATCH SEARCH CRITERIA --</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
