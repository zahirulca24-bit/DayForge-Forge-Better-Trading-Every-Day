import { AIReview } from "../types";
import { BrainCircuit, ThumbsUp, HelpCircle, CheckCircle2, ChevronRight, MessageSquareCode } from "lucide-react";

interface AIReviewProps {
  reviews: AIReview[];
  onGenerateReview?: () => Promise<void>;
  generating?: boolean;
}

export default function AIReviewView({ reviews, onGenerateReview, generating }: AIReviewProps) {
  return (
    <div className="space-y-6" id="ai-review-root">
      {/* AI Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 relative overflow-hidden" id="ai-review-header">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
          <BrainCircuit className="w-32 h-32 text-rose-500" />
        </div>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-start space-x-4">
            <div className="p-3 bg-rose-500/10 text-rose-400 rounded-xl mt-0.5">
              <BrainCircuit className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-white">Algorithmic Trade Review Suite (AI)</h2>
              <p className="text-xs text-slate-400 leading-relaxed max-w-2xl mt-1">
                Our embedded Gemini micro-module reviews active positions, RSI metrics, and MACD divergence lines post-exit to constantly self-correct and adjust setup parameters.
              </p>
            </div>
          </div>

          {onGenerateReview && (
            <button
              id="generate-ai-diagnostic-btn"
              onClick={onGenerateReview}
              disabled={generating}
              className="px-4 py-2 bg-gradient-to-r from-rose-600 to-rose-500 hover:from-rose-500 hover:to-rose-400 disabled:from-slate-800 disabled:to-slate-800 text-white text-xs font-bold rounded-xl transition-all shadow-md cursor-pointer flex items-center space-x-2 shrink-0 disabled:opacity-50"
            >
              <BrainCircuit className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
              <span>{generating ? "Analyzing with Gemini..." : "Gemini System Diagnostic"}</span>
            </button>
          )}
        </div>
      </div>

      <div className="space-y-4" id="reviews-feed">
        {reviews.map((rev) => (
          <div
            key={rev.id}
            className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4"
            id={`review-card-${rev.id}`}
          >
            {/* Top row */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 pb-4 border-b border-slate-850">
              <div className="flex items-center space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-ping" />
                <h3 className="font-bold text-white font-mono text-sm uppercase">{rev.pair} Exit Review</h3>
              </div>
              <div className="flex items-center space-x-2 w-full sm:w-auto justify-between sm:justify-end">
                <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full uppercase ${
                  rev.rating === "EXCELLENT" 
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : rev.rating === "GOOD"
                    ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                    : "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                }`}>
                  Rating: {rev.rating.replace("_", " ")}
                </span>
                <span className="text-[10px] text-slate-500 font-mono">
                  {new Date(rev.timestamp).toLocaleDateString()} {new Date(rev.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>

            {/* Analysis details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6" id="review-metrics">
              <div className="space-y-2">
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300">
                  <MessageSquareCode className="w-4 h-4 text-rose-500" />
                  <span>Pattern Analysis</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed font-mono">
                  {rev.analysis}
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-300">
                  <ThumbsUp className="w-4 h-4 text-emerald-400" />
                  <span>Optimization Recommendation</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed font-mono">
                  {rev.recommendation}
                </p>
              </div>
            </div>

            {/* Footer Tag */}
            <div className="pt-2 flex items-center justify-between text-[10px] text-slate-500 font-mono" id="review-footer">
              <span>Model parameters: Gemini Ultra-v1</span>
              <span className="flex items-center text-rose-400">
                Auto-tuning feedback applied <ChevronRight className="w-3 h-3 ml-0.5" />
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
