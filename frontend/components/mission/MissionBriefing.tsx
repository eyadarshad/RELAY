"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Compass, CheckCircle2, DollarSign, Calendar, Package, Truck, FileSpreadsheet, CalendarCheck2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

interface MissionBriefingProps {
  isOpen: boolean;
  objective: string;
  workflowType?: "PROCURE" | "RESCUE" | "QUOTE" | "SCHEDULE";
  initialData: {
    item: string;
    quantity: number;
    budget: number;
    deadline: string;
    location: string;
    approvalThreshold: number;
  };
  onConfirm: (editedData: any) => void;
  onCancel: () => void;
}

export const MissionBriefing: React.FC<MissionBriefingProps> = ({
  isOpen,
  objective,
  workflowType = "PROCURE",
  initialData,
  onConfirm,
  onCancel,
}) => {
  const [data, setData] = useState(initialData);

  React.useEffect(() => {
    setData(initialData);
  }, [initialData]);

  if (!isOpen) return null;

  const getWorkflowBadge = () => {
    switch (workflowType) {
      case "RESCUE":
        return <Badge variant="amber">EMERGENCY LOGISTICS</Badge>;
      case "QUOTE":
        return <Badge variant="cyan">COMPARATIVE BIDDING</Badge>;
      case "SCHEDULE":
        return <Badge variant="green">WAITLIST RESCUE</Badge>;
      default:
        return <Badge variant="accent">AUTONOMOUS SOURCING</Badge>;
    }
  };

  const getStrategyItems = () => {
    switch (workflowType) {
      case "RESCUE":
        return [
          "Scan regional emergency transport fleet in directory",
          "Sequentially dial dispatchers via CALL-E with strict 2-hour SLA constraint",
          "Lock immediate driver dispatch with first qualified carrier meeting price & ETA",
          "Generate instant dispatch audit certificate with tracking reference"
        ];
      case "QUOTE":
        return [
          "Identify certified commercial equipment suppliers in region",
          "Execute multi-vendor calls via CALL-E to request turnkey technical proposals",
          "Extract and normalize hardware model, warranty, installation, and payment terms",
          "Rank all bids into a normalized comparative decision matrix"
        ];
      case "SCHEDULE":
        return [
          "Load priority client waitlist for cancellation opening",
          "Call priority candidates sequentially via CALL-E to offer opening slot",
          "Confirm immediate acceptance and lock appointment in calendar",
          "Log booking confirmation reference and sync status"
        ];
      default:
        return [
          "Search and rank candidate suppliers in directory",
          "Execute phone inquiries via CALL-E and extract structured pricing",
          "Run multi-criteria decision scoring and initiate second-round negotiation call",
          `Pause at approval gate if final total exceeds $${data.approvalThreshold.toLocaleString()} threshold`,
          "Make final confirmation call to lock in Purchase Order reference"
        ];
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md">
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: 16 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 16 }}
          transition={{ duration: 0.2 }}
          className="w-full max-w-2xl border-2 border-accent bg-surface p-6 sm:p-7 font-mono text-xs space-y-5 acid-glow relative"
        >
          {/* Corner Crosshairs */}
          <span className="absolute -top-2.5 -left-2.5 text-accent font-mono font-bold text-sm">
            [+]
          </span>
          <span className="absolute -top-2.5 -right-2.5 text-accent font-mono font-bold text-sm">
            [+]
          </span>

          {/* Header */}
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div className="flex items-center gap-2.5 text-accent font-bold uppercase tracking-wider text-sm">
              <Compass className="w-5 h-5 animate-spin" />
              <span>PRE-FLIGHT MISSION BRIEFING // {workflowType}</span>
            </div>
            {getWorkflowBadge()}
          </div>

          {/* Raw Objective Reference */}
          <div className="p-3 bg-void border border-border space-y-1">
            <span className="text-[10px] text-text-muted uppercase tracking-widest block">
              ENTERED OBJECTIVE:
            </span>
            <p className="text-text-primary text-xs leading-relaxed italic">
              &quot;{objective}&quot;
            </p>
          </div>

          {/* Editable Extracted Parameters */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-text-secondary pb-1 border-b border-border/60">
              <span className="font-bold text-text-primary uppercase">EXTRACTED CONSTRAINTS</span>
              <span className="text-[10px] text-text-muted">EDITABLE VALUES</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-[10px] text-text-muted uppercase">
                  {workflowType === "RESCUE" ? "SERVICE REQUIRED" : workflowType === "SCHEDULE" ? "TARGET SLOT" : "TARGET ITEM / SPECS"}
                </label>
                <div className="flex items-center bg-void border border-border px-3 py-2">
                  <Package className="w-4 h-4 text-accent mr-2 shrink-0" />
                  <input
                    type="text"
                    value={data.item}
                    onChange={(e) => setData({ ...data, item: e.target.value })}
                    className="w-full bg-transparent text-text-primary focus:outline-none font-bold"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-text-muted uppercase">
                  {workflowType === "RESCUE" || workflowType === "SCHEDULE" ? "UNITS / SLOTS" : "REQUIRED QUANTITY"}
                </label>
                <div className="flex items-center bg-void border border-border px-3 py-2">
                  <span className="text-accent font-bold mr-2 text-xs">#</span>
                  <input
                    type="number"
                    value={data.quantity}
                    onChange={(e) => setData({ ...data, quantity: parseInt(e.target.value) || 0 })}
                    className="w-full bg-transparent text-text-primary focus:outline-none font-bold"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-text-muted uppercase">
                  {workflowType === "SCHEDULE" ? "CONSULTATION FEE (USD)" : "BUDGET CEILING (USD)"}
                </label>
                <div className="flex items-center bg-void border border-border px-3 py-2">
                  <DollarSign className="w-4 h-4 text-signal-green mr-1.5 shrink-0" />
                  <input
                    type="number"
                    value={data.budget}
                    onChange={(e) => setData({ ...data, budget: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-transparent text-text-primary focus:outline-none font-bold"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] text-text-muted uppercase">
                  {workflowType === "RESCUE" ? "ARRIVAL SLA / ETA" : "DELIVERY / APPOINTMENT DEADLINE"}
                </label>
                <div className="flex items-center bg-void border border-border px-3 py-2">
                  <Calendar className="w-4 h-4 text-signal-cyan mr-2 shrink-0" />
                  <input
                    type="text"
                    value={data.deadline}
                    onChange={(e) => setData({ ...data, deadline: e.target.value })}
                    className="w-full bg-transparent text-text-primary focus:outline-none font-bold"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Autonomous Strategy Summary */}
          <div className="p-3 bg-surface-raised border border-border space-y-1 text-[11px] text-text-secondary leading-relaxed">
            <span className="text-accent font-bold uppercase block mb-1">
              AUTONOMOUS CALL-E STRATEGY:
            </span>
            <ul className="list-disc pl-4 space-y-1 text-text-muted text-[11px]">
              {getStrategyItems().map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <Button variant="ghost" size="md" onClick={onCancel}>
              CANCEL
            </Button>
            <Button
              variant="primary"
              size="lg"
              icon={<CheckCircle2 className="w-4 h-4" />}
              onClick={() => onConfirm(data)}
            >
              CONFIRM & LAUNCH RUN ▸
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
