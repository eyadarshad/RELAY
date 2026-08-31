"use client";

import React from "react";
import { TrendingDown, Sparkles, ArrowRight, DollarSign } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { CountUp } from "@/components/ui/CountUp";

interface NegotiationTrackerProps {
  supplierName?: string;
  originalPrice?: number;
  revisedPrice?: number;
  savings?: number;
}

export const NegotiationTracker: React.FC<NegotiationTrackerProps> = ({
  supplierName,
  originalPrice = 0,
  revisedPrice = 0,
  savings = 0,
}) => {
  if (!savings || savings <= 0) {
    return (
      <Card title="NEGOTIATION IMPACT ENGINE" className="text-center py-5">
        <div className="text-text-muted font-mono text-xs italic">
          Negotiation round active once initial quotes are gathered.
        </div>
      </Card>
    );
  }

  const discountPercent = originalPrice > 0 ? ((savings / originalPrice) * 100).toFixed(1) : "0.0";

  return (
    <Card
      title="AUTONOMOUS NEGOTIATION IMPACT"
      variant="glow"
      className="bg-surface-raised border-signal-amber/40"
    >
      <div className="space-y-3 font-mono">
        <div className="flex items-center justify-between text-xs pb-2 border-b border-border/80">
          <div className="flex items-center gap-1.5 text-signal-amber font-bold uppercase">
            <Sparkles className="w-3.5 h-3.5 animate-spin" /> SECOND-CALL PRICE REDUCTION
          </div>
          <span className="text-text-secondary text-[11px] uppercase tracking-wider">
            {supplierName}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2 sm:gap-3 text-center pt-1">
          {/* Before */}
          <div className="p-2.5 bg-void border border-border">
            <div className="text-[10px] text-text-muted uppercase tracking-wider">INITIAL QUOTE</div>
            <div className="text-sm sm:text-base font-bold text-text-secondary line-through mt-0.5">
              ${originalPrice.toLocaleString()}
            </div>
          </div>

          {/* After */}
          <div className="p-2.5 bg-void border border-accent/40 acid-glow-sm">
            <div className="text-[10px] text-accent uppercase tracking-wider">FINAL PRICE</div>
            <div className="text-sm sm:text-base font-bold text-accent mt-0.5">
              ${revisedPrice.toLocaleString()}
            </div>
          </div>

          {/* Savings */}
          <div className="p-2.5 bg-void border border-signal-green/40 green-glow">
            <div className="text-[10px] text-signal-green uppercase tracking-wider">SAVINGS ({discountPercent}%)</div>
            <div className="text-sm sm:text-base font-bold text-signal-green mt-0.5">
              +<CountUp value={savings} prefix="$" />
            </div>
          </div>
        </div>

        <div className="text-[10px] text-text-secondary bg-surface p-2 border border-border/60 flex items-center justify-between">
          <span>STRATEGY: Leveraged competing supplier quotes to secure volume concession.</span>
          <span className="text-signal-green font-bold uppercase">VERIFIED SAVINGS</span>
        </div>
      </div>
    </Card>
  );
};
