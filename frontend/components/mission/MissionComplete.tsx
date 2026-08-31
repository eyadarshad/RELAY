"use client";

import React, { useEffect } from "react";
import { motion } from "motion/react";
import confetti from "canvas-confetti";
import { CheckCircle2, Award, Download, ArrowRight, PhoneCall, TrendingDown, Clock, ShieldCheck, Truck, FileSpreadsheet, CalendarCheck2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { CountUp } from "@/components/ui/CountUp";

interface MissionCompleteProps {
  report: {
    mission_id: string;
    workflow_type?: string;
    objective: string;
    item_secured: string;
    final_price: number;
    original_budget: number;
    total_savings: number;
    delivery_commitment: string;
    warranty: string;
    supplier_confirmed: string;
    po_reference: string;
    calls_initiated: number;
    successful_conversations: number;
    negotiation_rounds: number;
    execution_time_seconds: number;
  };
  onNewMission: () => void;
}

export const MissionComplete: React.FC<MissionCompleteProps> = ({ report, onNewMission }) => {
  const wf = report.workflow_type || "PROCURE";

  useEffect(() => {
    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 },
        colors: ["#CCFF00", "#00FF88", "#00E5FF", "#FFFFFF"],
      });
    } catch {
      // Ignore if canvas not supported
    }
  }, []);

  const downloadReportJson = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(report, null, 2));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `relay_mission_${report.mission_id}_report.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const getWorkflowTitle = () => {
    switch (wf) {
      case "RESCUE":
        return "EMERGENCY TRANSPORT SECURED";
      case "QUOTE":
        return "COMMERCIAL BID MATRIX FINALIZED";
      case "SCHEDULE":
        return "WAITLIST APPOINTMENT CONFIRMED";
      default:
        return "MISSION ACCOMPLISHED";
    }
  };

  const getPoLabel = () => {
    switch (wf) {
      case "RESCUE":
        return "DISPATCH AUDIT CERTIFICATE";
      case "QUOTE":
        return "RECOMMENDED BID REFERENCE";
      case "SCHEDULE":
        return "CALENDAR BOOKING REFERENCE";
      default:
        return "OFFICIAL PURCHASE ORDER";
    }
  };

  const getSummaryText = () => {
    switch (wf) {
      case "RESCUE":
        return `RELAY parsed the emergency logistics failure, executed rapid sequential priority dialing to local fleet dispatchers via CALL-E, and secured immediate driver dispatch from ${report.supplier_confirmed} within the 2-hour SLA constraint.`;
      case "QUOTE":
        return `RELAY contacted certified equipment suppliers via CALL-E, collected turnkey proposals, normalized warranty and technical specifications into a multi-attribute decision matrix, and identified ${report.supplier_confirmed} as the optimal commercial bid.`;
      case "SCHEDULE":
        return `RELAY accessed the priority waitlist, sequentially placed automated calls via CALL-E to find an immediate match for the cancelled slot, and successfully confirmed and locked the appointment with ${report.supplier_confirmed}.`;
      default:
        return `RELAY ingested the high-level business objective, formulated a calling plan, queried suppliers via CALL-E, scored proposals, autonomously negotiated a verified $${report.total_savings.toLocaleString()} discount, paused for executive approval, and executed the final confirmation call.`;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-4xl mx-auto border-2 border-signal-green bg-surface p-6 sm:p-8 font-mono space-y-6 acid-glow relative"
    >
      {/* Corner crosshairs */}
      <span className="absolute -top-2.5 -left-2.5 text-signal-green font-mono font-bold text-sm">
        [✓]
      </span>
      <span className="absolute -top-2.5 -right-2.5 text-signal-green font-mono font-bold text-sm">
        [✓]
      </span>

      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-border gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-signal-green/10 border border-signal-green text-signal-green">
            <CheckCircle2 className="w-7 h-7" />
          </div>
          <div>
            <h2 className="font-display font-black text-xl sm:text-2xl text-text-primary uppercase tracking-wide">
              {getWorkflowTitle()}
            </h2>
            <div className="text-xs text-text-secondary">
              MISSION ID: {report.mission_id} • WORKFLOW: {wf} • STATUS: VERIFIED
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={<Download className="w-3.5 h-3.5" />}
            onClick={downloadReportJson}
          >
            AUDIT REPORT
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={<ArrowRight className="w-3.5 h-3.5" />}
            onClick={onNewMission}
          >
            NEW MISSION
          </Button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 bg-void border border-border">
          <div className="text-[10px] text-text-muted uppercase tracking-wider">
            {wf === "SCHEDULE" ? "SLOT BOOKED" : wf === "RESCUE" ? "CARRIER DISPATCHED" : "ITEM SECURED"}
          </div>
          <div className="text-sm sm:text-base font-bold text-text-primary mt-1 truncate" title={report.item_secured}>
            {report.item_secured}
          </div>
        </div>

        <div className="p-4 bg-void border border-accent/40 acid-glow-sm">
          <div className="text-[10px] text-accent uppercase tracking-wider">
            {wf === "SCHEDULE" ? "FEE SCHEDULE" : "FINAL PRICE"}
          </div>
          <div className="text-base sm:text-lg font-bold text-accent mt-1">
            ${report.final_price > 0 ? <CountUp value={report.final_price} /> : "0.00 (Standard)"}
          </div>
        </div>

        <div className="p-4 bg-void border border-signal-green/40 green-glow">
          <div className="text-[10px] text-signal-green uppercase tracking-wider">
            {wf === "SCHEDULE" ? "EXECUTION SPEED" : "TOTAL SAVINGS"}
          </div>
          <div className="text-base sm:text-lg font-bold text-signal-green mt-1">
            {wf === "SCHEDULE" ? `${report.execution_time_seconds || 15}s` : `+$${report.total_savings.toLocaleString()}`}
          </div>
        </div>

        <div className="p-4 bg-void border border-signal-cyan/40 cyan-glow">
          <div className="text-[10px] text-signal-cyan uppercase tracking-wider">COMMITMENT / ETA</div>
          <div className="text-xs sm:text-sm font-bold text-signal-cyan mt-1 truncate">
            {report.delivery_commitment}
          </div>
          <div className="text-[10px] text-text-muted mt-0.5">{report.warranty}</div>
        </div>
      </div>

      {/* Confirmation Details Card */}
      <div className="bg-void border border-border p-4 sm:p-5 space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-border/60 text-xs">
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-accent" />
            <span className="font-bold text-text-primary uppercase">{getPoLabel()}</span>
          </div>
          <span className="font-mono text-accent font-bold">{report.po_reference}</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs pt-1">
          <div>
            <span className="text-text-muted block text-[10px]">CONFIRMED PARTY</span>
            <span className="text-text-primary font-bold">{report.supplier_confirmed}</span>
          </div>
          <div>
            <span className="text-text-muted block text-[10px]">BUDGET TARGET</span>
            <span className="text-text-secondary">${report.original_budget > 0 ? report.original_budget.toLocaleString() : "N/A"}</span>
          </div>
          <div>
            <span className="text-text-muted block text-[10px]">TELEPHONY OUTREACH METRICS</span>
            <span className="text-signal-green font-bold">
              {report.calls_initiated} Calls • {report.negotiation_rounds} Negotiations
            </span>
          </div>
        </div>
      </div>

      {/* Hackathon Judge Summary Callout */}
      <div className="p-4 bg-surface-raised border border-border text-xs text-text-secondary leading-relaxed">
        <span className="text-accent font-bold uppercase block mb-1">
          AUTONOMOUS OPERATIONS SUMMARY:
        </span>
        {getSummaryText()}
      </div>
    </motion.div>
  );
};
