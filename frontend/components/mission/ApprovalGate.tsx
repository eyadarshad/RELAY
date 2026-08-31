"use client";

import React from "react";
import { motion, AnimatePresence } from "motion/react";
import { ShieldAlert, CheckCircle2, XCircle, RotateCcw, Award, DollarSign } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { CountUp } from "@/components/ui/CountUp";

interface ApprovalGateProps {
  isOpen: boolean;
  data?: {
    supplier_name: string;
    supplier_phone: string;
    quantity: number;
    unit_price?: number;
    total_price: number;
    original_budget: number;
    savings: number;
    delivery_days?: number;
    delivery_date?: string;
    warranty_years?: number;
    payment_terms?: string;
    reasoning?: string;
  };
  onApprove: () => void;
  onReject: () => void;
  onRequestMore: () => void;
}

export const ApprovalGate: React.FC<ApprovalGateProps> = ({
  isOpen,
  data,
  onApprove,
  onReject,
  onRequestMore,
}) => {
  if (!isOpen || !data) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: 12 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 12 }}
          transition={{ duration: 0.2, ease: "easeOut" }}
          className="w-full max-w-xl border-2 border-signal-amber bg-surface p-6 font-mono text-xs space-y-5 acid-glow relative"
        >
          {/* Brutalist Corner Markers */}
          <span className="absolute -top-2.5 -left-2.5 text-signal-amber font-mono font-bold text-sm select-none">
            [!]
          </span>
          <span className="absolute -top-2.5 -right-2.5 text-signal-amber font-mono font-bold text-sm select-none">
            [!]
          </span>

          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div className="flex items-center gap-2 text-signal-amber font-bold uppercase tracking-wider text-sm">
              <ShieldAlert className="w-5 h-5 animate-pulse" />
              <span>HUMAN-IN-THE-LOOP AUTHORIZATION GATE</span>
            </div>
            <Badge variant="amber">PAUSED FOR APPROVAL</Badge>
          </div>

          {/* Summary Box */}
          <div className="bg-void border border-border p-4 space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-border/60">
              <div>
                <span className="text-[10px] text-text-muted uppercase tracking-widest block">RECOMMENDED SUPPLIER</span>
                <span className="text-base font-bold text-text-primary uppercase">{data.supplier_name}</span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-text-muted uppercase tracking-widest block">TOTAL COMMITMENT</span>
                <span className="text-lg font-bold text-accent">${data.total_price.toLocaleString()}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-[11px] pt-1">
              <div>
                <span className="text-text-muted block text-[10px]">QUANTITY</span>
                <span className="text-text-primary font-bold">{data.quantity} units</span>
              </div>
              <div>
                <span className="text-text-muted block text-[10px]">UNIT PRICE</span>
                <span className="text-text-primary font-bold">${data.unit_price ? data.unit_price.toFixed(2) : "--"}</span>
              </div>
              <div>
                <span className="text-text-muted block text-[10px]">DELIVERY</span>
                <span className="text-text-primary font-bold">{data.delivery_date || `${data.delivery_days} days`}</span>
              </div>
              <div>
                <span className="text-text-muted block text-[10px]">WARRANTY</span>
                <span className="text-text-primary font-bold">{data.warranty_years} years</span>
              </div>
            </div>

            {data.savings > 0 && (
              <div className="bg-signal-green/10 border border-signal-green/30 p-2 flex items-center justify-between text-signal-green font-bold text-xs">
                <span>ESTIMATED BUDGET SAVINGS:</span>
                <span>+${data.savings.toLocaleString()}</span>
              </div>
            )}
          </div>

          {/* Agent Recommendation */}
          <div className="p-3 bg-surface-raised border border-border text-text-secondary text-[11px] leading-relaxed">
            <span className="text-accent font-bold uppercase block mb-1">AGENT RECOMMENDATION:</span>
            {data.reasoning || "XYZ Supplies satisfies all constraints, provides full quantity, and offers lowest compliant price."}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
            <Button
              variant="primary"
              size="lg"
              className="w-full sm:flex-1 py-3 text-xs"
              icon={<CheckCircle2 className="w-4 h-4" />}
              onClick={onApprove}
            >
              APPROVE & CONFIRM CALL ▸
            </Button>

            <Button
              variant="ghost"
              size="md"
              className="w-full sm:w-auto border border-border hover:border-signal-amber hover:text-signal-amber text-xs"
              icon={<RotateCcw className="w-3.5 h-3.5" />}
              onClick={onRequestMore}
            >
              MORE OPTIONS
            </Button>

            <Button
              variant="danger"
              size="md"
              className="w-full sm:w-auto text-xs"
              icon={<XCircle className="w-3.5 h-3.5" />}
              onClick={onReject}
            >
              REJECT
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
