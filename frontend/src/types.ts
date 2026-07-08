export interface BotSettings {
  maxActiveTrades: number;
  riskPerTrade: number;
  targetProfit: number;
  scannerUniverse: string[];
  timeframe: string;
  leverage: number;
}

export interface Trade {
  id: string;
  pair: string;
  strategy: string;
  direction: 'LONG' | 'SHORT';
  entryPrice: number;
  currentPrice: number;
  stopLoss: number;
  takeProfit: number;
  size: number;
  margin: number;
  leverage: number;
  unrealizedPnl: number;
  pnlPercent: number;
  status: 'OPEN' | 'CLOSED';
  timestamp: string;
  orderConfirmed?: boolean;
  slVerified?: boolean;
  tpVerified?: boolean;
  positionSynced?: boolean;
  isUnsafe?: boolean;
  orderId?: string;
  rawStatus?: string;
  journalId?: string;
  executionMode?: 'demo' | 'live';
  result?: 'TP' | 'SL' | 'UNKNOWN';
  closedAt?: string;
  slHitReason?: string | null;
  exitPrice?: number;
}

export interface TradeHistoryEntry extends Omit<Trade, 'result' | 'closedAt' | 'exitPrice'> {
  exitPrice: number;
  pnl: number;
  result: 'PROFIT' | 'LOSS';
  reason: string;
  closedAt: string;
}

export interface PortfolioMetrics {
  totalBalance: number;
  equity: number;
  availableBalance: number;
  usedMargin: number;
  openPnl: number;
  dailyPnl: number;
  realizedPnl: number;
  winRate: number;
  profitFactor: number;
  maxDrawdown: number;
  marginBalance?: number;
  unrealizedPnl?: number;
  totalTrades?: number;
  activeTradesCount?: number;
  closedTradesCount?: number;
  winTrades?: number;
  lossTrades?: number;
  pnlR?: number;
}

export type SignalGrade = 'A+' | 'A' | 'B+' | 'REJECT';

export interface Signal {
  id: string;
  pair: string;
  timeframe: string;
  direction: 'LONG' | 'SHORT';
  indicator: string;
  price: number;
  strength: 'STRONG' | 'MEDIUM' | 'WEAK';
  timestamp: string;
  grade: SignalGrade;
  score: number;
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
  rr: number;
  rejectionReason?: string;
  status: 'PENDING' | 'EXECUTED' | 'REJECTED';
}

export interface PairData {
  symbol: string;
  price: number;
  rsi: number;
  ema200: number;
  isLiquiditySweep: boolean;
  isBosOrChoch: boolean;
  fvgConfirmed: boolean;
}

export interface PortfolioAsset {
  symbol: string;
  balance: number;
  valueUsdt: number;
  allocation: number;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
  message: string;
}

export interface AIReview {
  id: string;
  timestamp: string;
  tradeId?: string;
  pair: string;
  rating: 'EXCELLENT' | 'GOOD' | 'NEEDS_IMPROVEMENT' | 'AVOID';
  analysis: string;
  recommendation: string;
}

export type ScannerStatus = 'DISABLED' | 'IDLE' | 'SCANNING' | 'COMPLETED' | 'COMPLETED_WITH_ERRORS' | 'ERROR' | 'DATA_UNAVAILABLE';
export type ScanResultStatus = 'ACCEPTED' | 'REJECTED' | 'DATA_ERROR' | 'EXPIRED';
export type SignalExecutionStatus = 'NEW' | 'VALIDATED' | 'BLOCKED' | 'READY' | 'EXECUTING' | 'EXECUTED' | 'FAILED' | 'EXPIRED';

export interface ScanResult {
  symbol: string;
  apiSymbol?: string;
  turnover4h?: number;
  direction: 'LONG' | 'SHORT';
  strategy: string;
  score: number;
  grade: SignalGrade;
  entryPrice: number;
  stopLoss: number;
  takeProfit: number;
  rr: number;
  result: ScanResultStatus;
  rejectionReason?: string;
  candleCloseTime: string;
  scanTime: string;
}

export interface ScanSummary {
  totalScanned: number;
  accepted: number;
  rejected: number;
  aPlus: number;
  a: number;
  dataErrors: number;
  durationMs: number;
}

export interface ExecutableSignal extends Signal {
  ageMs: number;
  executionStatus: SignalExecutionStatus;
}

export interface ScannerState {
  scannerEnabled: boolean;
  scannerStatus: ScannerStatus;
  scannerPaused: boolean;
  scanInProgress: boolean;
  lastScanStartedAt: string | null;
  lastScanCompletedAt: string | null;
  nextScanAt: string | null;
  scanDurationMs: number;
  lastScanError: string | null;
}

export interface BotState {
  apiConnected: boolean;
  bybitConnected: boolean;
  walletSynced: boolean;
  apiAuthenticated: boolean;
  scannerOn: boolean;
  autoTradeOn: boolean;
  webScrapingOn: boolean;
  emergencyStopped: boolean;
  liveUnlocked: boolean;
}

export interface BotControlState {
  status: 'idle' | 'running' | 'stopped';
  emergency_stop: boolean;
  execution_mode?: 'demo' | 'live';
  auto_trading_enabled?: boolean;
  live_mode_available?: boolean;
  readiness?: SystemReadiness;
}

export interface SystemHealth {
  apiStatus: 'ONLINE' | 'OFFLINE';
  scannerStatus: 'RUNNING' | 'IDLE';
  strategyStatus: 'ACTIVE' | 'ERROR';
  riskStatus: 'OK' | 'WARNING' | 'CRITICAL';
}

export interface SystemReadiness {
  mode?: 'demo' | 'live';
  checks: {
    admin_auth_configured: boolean;
    api_keys_present: boolean;
    exchange_reachable: boolean;
    wallet_fetch_success: boolean;
  };
  errors: {
    exchange: string | null;
    wallet: string | null;
  };
  ready_for_execution: boolean;
  demo?: {
    mode: string;
    checks: {
      api_keys_present: boolean;
      exchange_reachable: boolean;
      wallet_fetch_success: boolean;
    };
    errors: {
      exchange: string | null;
      wallet: string | null;
    };
    ready: boolean;
  };
  live?: {
    mode: string;
    checks: {
      api_keys_present: boolean;
      exchange_reachable: boolean;
      wallet_fetch_success: boolean;
    };
    errors: {
      exchange: string | null;
      wallet: string | null;
    };
    ready: boolean;
    live_mode_available?: boolean;
  };
}

export interface ExchangeStatusResponse {
  mode?: 'demo' | 'live';
  demo_only: boolean;
  base_url: string;
  api_keys_present: boolean;
  reachable: boolean;
  error: string | null;
  demo?: {
    mode: string;
    demo_only: boolean;
    base_url: string;
    api_keys_present: boolean;
    reachable: boolean;
    error: string | null;
  };
  live?: {
    mode: string;
    demo_only: boolean;
    base_url: string;
    api_keys_present: boolean;
    reachable: boolean;
    error: string | null;
  };
}

export interface HealthResponse {
  status: string;
}

export interface MetricsResponse {
  total_trades: number;
  active_trades_count: number;
  closed_trades_count: number;
  win_trades: number;
  loss_trades: number;
  win_rate: number;
  pnl_r: number;
}

export interface PortfolioSummary {
  active_trades: number;
  closed_trades: number;
  total_trades: number;
  win_rate: number;
  pnl_r: number;
  execution_mode?: 'demo' | 'live';
}

export interface AccountResponse {
  ok: boolean;
  mode?: 'demo' | 'live';
  wallet: {
    ok: boolean;
    data: Record<string, string | number> | null;
    error: string | null;
  };
  positions: {
    ok: boolean;
    data: Array<Record<string, string | number>>;
    error: string | null;
  };
}
