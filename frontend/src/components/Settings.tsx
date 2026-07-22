import React, { useState, useEffect } from "react";
import { BotSettings } from "../types";
import { Save, AlertCircle, Sparkles, Check, CheckCircle } from "lucide-react";

interface SettingsProps {
  settings: BotSettings;
  onSaveSettings: (updated: BotSettings) => Promise<void>;
  loading: boolean;
}

export default function SettingsView({
  settings,
  onSaveSettings,
  loading
}: SettingsProps) {
  const [maxActiveTrades, setMaxActiveTrades] = useState(settings.maxActiveTrades);
  const [riskPerTrade, setRiskPerTrade] = useState(settings.riskPerTrade);
  const [targetProfit, setTargetProfit] = useState(settings.targetProfit);
  const [timeframe, setTimeframe] = useState(settings.timeframe);
  const [scannerUniverse, setScannerUniverse] = useState<string[]>(settings.scannerUniverse);
  const [leverage, setLeverage] = useState(settings.leverage);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Sync state if backend settings changed
  useEffect(() => {
    setMaxActiveTrades(settings.maxActiveTrades);
    setRiskPerTrade(settings.riskPerTrade);
    setTargetProfit(settings.targetProfit);
    setTimeframe(settings.timeframe);
    setScannerUniverse(settings.scannerUniverse);
    setLeverage(settings.leverage);
  }, [settings]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaveSuccess(false);
    await onSaveSettings({
      maxActiveTrades,
      riskPerTrade,
      targetProfit,
      timeframe,
      scannerUniverse,
      leverage
    });
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 4000);
  };

  return (
    <form onSubmit={handleSave} className="space-y-6" id="settings-form">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex justify-between items-center" id="settings-header">
        <div>
          <h3 className="text-sm font-semibold text-white">Algorithm & Risk Parameters</h3>
          <p className="text-xs text-slate-500 mt-0.5">Define core multipliers, execution limits, and scanning universe</p>
        </div>
        <button
          id="settings-save-btn"
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 text-white text-xs font-semibold rounded-xl flex items-center space-x-2 transition-all shadow-md cursor-pointer disabled:opacity-50"
        >
          <Save className="w-4 h-4" />
          <span>{loading ? "Saving Parameters..." : "Apply Configurations"}</span>
        </button>
      </div>

      {saveSuccess && (
        <div className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 p-4 rounded-2xl flex items-start space-x-2 font-mono text-xs" id="settings-success-alert">
          <CheckCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold text-emerald-300">Parameters active!</strong> Configured values updated in the backend instance successfully and applied to active scanning loops.
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6" id="settings-grids">
        {/* Risk & Limits */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-6" id="settings-risk-panel">
          <h4 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest pb-3 border-b border-slate-850">Risk Allocation Framework</h4>

          {/* Max Active Trades */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-200">Max Active Scalp Positions</label>
              <span className="font-mono text-rose-400 font-semibold">{maxActiveTrades} concurrent</span>
            </div>
            <p className="text-[11px] text-slate-500">Maximum concurrent open leverage contracts before the scanner halts entries.</p>
            <input
              id="settings-max-trades"
              type="number"
              min="1"
              max="20"
              value={maxActiveTrades}
              onChange={(e) => setMaxActiveTrades(Number(e.target.value))}
              className="w-full bg-slate-950 border border-slate-850 rounded-xl px-4 py-2.5 text-xs text-slate-300 focus:outline-none focus:border-rose-500/50"
            />
          </div>

          {/* Risk Per Trade */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-200">Risk Allocation Per Position</label>
              <span className="font-mono text-rose-400 font-semibold">{riskPerTrade}%</span>
            </div>
            <p className="text-[11px] text-slate-500">Percentage of total wallet balance size committed to single setups (Stop-Loss trigger target).</p>
            <div className="flex items-center space-x-4">
              <input
                id="settings-risk-slider"
                type="range"
                min="0.1"
                max="5"
                step="0.1"
                value={riskPerTrade}
                onChange={(e) => setRiskPerTrade(Number(e.target.value))}
                className="flex-1 accent-rose-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
              />
              <input
                id="settings-risk-num"
                type="number"
                min="0.1"
                max="5"
                step="0.1"
                value={riskPerTrade}
                onChange={(e) => setRiskPerTrade(Number(e.target.value))}
                className="w-20 bg-slate-950 border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-slate-300 text-center font-mono focus:outline-none focus:border-rose-500/50"
              />
            </div>
          </div>

          {/* Target Profit */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-200">Take Profit (Target Return)</label>
              <span className="font-mono text-rose-400 font-semibold">{targetProfit}%</span>
            </div>
            <p className="text-[11px] text-slate-500">Percent target for scaling exits on standard 10x-20x leverage trades.</p>
            <div className="flex items-center space-x-4">
              <input
                id="settings-profit-slider"
                type="range"
                min="0.5"
                max="10"
                step="0.1"
                value={targetProfit}
                onChange={(e) => setTargetProfit(Number(e.target.value))}
                className="flex-1 accent-rose-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
              />
              <input
                id="settings-profit-num"
                type="number"
                min="0.5"
                max="10"
                step="0.1"
                value={targetProfit}
                onChange={(e) => setTargetProfit(Number(e.target.value))}
                className="w-20 bg-slate-950 border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-slate-300 text-center font-mono focus:outline-none focus:border-rose-500/50"
              />
            </div>
          </div>
          
          {/* Leverage */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-200">Account Leverage</label>
              <span className="font-mono text-rose-400 font-semibold">{leverage}x</span>
            </div>
            <p className="text-[11px] text-slate-500">Leverage applied to margin to determine position size.</p>
            <div className="flex items-center space-x-4">
              <input
                id="settings-leverage-slider"
                type="range"
                min="1"
                max="100"
                step="1"
                value={leverage}
                onChange={(e) => setLeverage(Number(e.target.value))}
                className="flex-1 accent-rose-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none"
              />
              <input
                id="settings-leverage-num"
                type="number"
                min="1"
                max="100"
                step="1"
                value={leverage}
                onChange={(e) => setLeverage(Number(e.target.value))}
                className="w-20 bg-slate-950 border border-slate-850 rounded-xl px-3 py-1.5 text-xs text-slate-300 text-center font-mono focus:outline-none focus:border-rose-500/50"
              />
            </div>
          </div>
        </div>

        {/* Setup Parameters */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-6" id="settings-setup-panel">
          <h4 className="text-xs font-mono font-bold text-slate-400 uppercase tracking-widest pb-3 border-b border-slate-850">Strategy Timeline & Universe</h4>

          {/* Timeframe selector */}
          <div className="space-y-3">
            <label className="text-xs font-semibold text-slate-200 block">Core Setup Timeframe</label>
            <div className="grid grid-cols-2 gap-2" id="timeframe-selectors">
              {[
                "5M setup + 1M entry",
                "15M setup + 3M entry",
                "30M setup + 5M entry",
                "1H setup + 15M entry"
              ].map((tf) => (
                <button
                  id={`tf-${tf.replace(/\s+/g, '-')}`}
                  key={tf}
                  type="button"
                  onClick={() => setTimeframe(tf)}
                  className={`p-3 rounded-xl border text-xs font-mono font-semibold transition-all cursor-pointer text-center ${
                    timeframe === tf
                      ? "bg-rose-500/10 border-rose-500/30 text-rose-400"
                      : "bg-slate-950 border-slate-850 text-slate-400 hover:border-slate-800"
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>

          {/* Universe Pool list */}
          <div className="space-y-3">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-200">Scanner Liquidity Universe</label>
              <span className="font-mono text-emerald-400 font-semibold">AUTO</span>
            </div>
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
              <div className="text-emerald-400 font-bold text-xs mb-1">Dynamic Top 20 — Last 4H Liquidity</div>
              <p className="text-[10px] text-slate-400">
                The scanner will automatically fetch all active Bybit linear USDT perpetual instruments, calculate their latest 4-hour quote turnover, and select the top 20 most liquid pairs before every new scheduled scan.
              </p>
            </div>
          </div>
        </div>
      </div>
    </form>
  );
}
