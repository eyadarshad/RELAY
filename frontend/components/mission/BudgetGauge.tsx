"use client";

import React from "react";
import { Gauge } from "@/components/ui/Gauge";
import { Card } from "@/components/ui/Card";
import { CountUp } from "@/components/ui/CountUp";

interface BudgetGaugeCardProps {
  currentPrice: number;
  maxBudget: number;
  totalSavings: number;
}

export const BudgetGaugeCard: React.FC<BudgetGaugeCardProps> = ({
  currentPrice,
  maxBudget,
  totalSavings,
}) => {
  const remaining = Math.max(0, maxBudget - currentPrice);

  return (
    <Card title="BUDGET EFFICIENCY">
      <div className="flex items-center justify-between gap-4 font-mono">
        <Gauge
          value={currentPrice > 0 ? currentPrice : 0}
          max={maxBudget}
          size={120}
          label="UTILIZED"
          sublabel={currentPrice <= maxBudget ? "IN BUDGET" : "OVER"}
        />

        <div className="flex-1 space-y-2 text-xs border-l border-border pl-4">
          <div>
            <div className="text-[10px] text-text-muted uppercase tracking-widest">BUDGET CEILING</div>
            <div className="text-sm font-bold text-text-primary">
              ${maxBudget.toLocaleString()}
            </div>
          </div>

          <div>
            <div className="text-[10px] text-text-muted uppercase tracking-widest">COMMITTED PRICE</div>
            <div className="text-sm font-bold text-accent">
              ${currentPrice > 0 ? currentPrice.toLocaleString() : "--"}
            </div>
          </div>

          <div>
            <div className="text-[10px] text-signal-green uppercase tracking-widest">SAVINGS ACHIEVED</div>
            <div className="text-sm font-bold text-signal-green">
              +<CountUp value={totalSavings} prefix="$" />
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
