"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { 
  ArrowLeft, 
  XCircle, 
  ShieldCheck, 
  Activity, 
  PhoneCall, 
  RefreshCw,
  Clock,
  Layers
} from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Terminal } from "@/components/ui/Terminal";
import { AgentStatus } from "@/components/mission/AgentStatus";
import { LiveCallCard } from "@/components/mission/LiveCallCard";
import { CallQueue } from "@/components/mission/CallQueue";
import { OffersTable } from "@/components/mission/OffersTable";
import { NegotiationTracker } from "@/components/mission/NegotiationTracker";
import { MissionTimeline } from "@/components/mission/MissionTimeline";
import { BudgetGaugeCard } from "@/components/mission/BudgetGauge";
import { AgentReasoning } from "@/components/mission/AgentReasoning";
import { ApprovalGate } from "@/components/mission/ApprovalGate";
import { MissionComplete } from "@/components/mission/MissionComplete";

import { useMissionStore } from "@/store/missionStore";
import { useWebSocket } from "@/hooks/useWebSocket";
import { getMission, abortMission, submitApproval } from "@/lib/api";

export default function MissionControlPage() {
  const params = useParams();
  const router = useRouter();
  const missionId = params?.id as string;

  const {
    mission,
    agentStatus,
    currentThought,
    thoughtLog,
    activeCall,
    approvalModal,
    isConnected,
    completionData,
    setMission,
    reset,
  } = useMissionStore();

  const { sendApproval, sendAbort } = useWebSocket(missionId);
  const [isLoading, setIsLoading] = useState(true);

  // Initial load of mission state
  useEffect(() => {
    if (!missionId) return;

    let isMounted = true;
    async function load() {
      try {
        const data = await getMission(missionId);
        if (isMounted) {
          setMission(data);
          setIsLoading(false);
        }
      } catch (err) {
        console.error("Failed to load mission:", err);
        if (isMounted) setIsLoading(false);
      }
    }

    load();

    return () => {
      isMounted = false;
    };
  }, [missionId, setMission]);

  const handleAbort = async () => {
    if (confirm("Are you sure you want to abort this active mission?")) {
      sendAbort();
      await abortMission(missionId);
    }
  };

  const handleApprove = async () => {
    sendApproval("APPROVE");
    await submitApproval(missionId, "APPROVE");
  };

  const handleReject = async () => {
    sendApproval("REJECT");
    await submitApproval(missionId, "REJECT");
  };

  const handleRequestMore = async () => {
    sendApproval("REQUEST_MORE");
    await submitApproval(missionId, "REQUEST_MORE");
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 font-mono space-y-4">
        <Activity className="w-8 h-8 text-accent animate-spin" />
        <div className="text-sm font-bold uppercase tracking-wider text-text-primary">
          CONNECTING TO MISSION CONTROL ROOM...
        </div>
      </div>
    );
  }

  if (!mission) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 font-mono space-y-4">
        <div className="text-signal-red font-bold text-base">MISSION NOT FOUND</div>
        <Button variant="secondary" onClick={() => router.push("/")}>
          RETURN TO HOME
        </Button>
      </div>
    );
  }

  // Find best offer data if available
  const bestOffer = mission.offers.find((o) => o.status === "BEST" || o.status === "ACCEPTED");

  return (
    <div className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 space-y-6 font-mono">
      {/* Top Mission Control Command Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              reset();
              router.push("/");
            }}
            icon={<ArrowLeft className="w-3.5 h-3.5" />}
          >
            HOME
          </Button>

          <div className="h-4 w-[1px] bg-border hidden sm:block" />

          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-text-muted uppercase tracking-widest">MISSION ID</span>
              <span className="font-bold text-xs text-accent uppercase">{mission.id}</span>
              <Badge variant={isConnected ? "green" : "amber"} size="sm">
                {isConnected ? "WEBSOCKET STREAMING" : "CONNECTING"}
              </Badge>
            </div>
            <h2 className="font-display font-bold text-sm sm:text-base text-text-primary uppercase tracking-wide truncate max-w-md mt-0.5">
              {mission.item ? `${mission.quantity} ${mission.item}` : mission.objective}
            </h2>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          <AgentStatus status={agentStatus} />

          {agentStatus !== "COMPLETED" && agentStatus !== "ABORTED" && (
            <Button
              variant="danger"
              size="sm"
              icon={<XCircle className="w-3.5 h-3.5" />}
              onClick={handleAbort}
            >
              ABORT
            </Button>
          )}
        </div>
      </div>

      {/* Completion View Overlay if Completed */}
      {completionData && agentStatus === "COMPLETED" && (
        <MissionComplete
          report={completionData as any}
          onNewMission={() => {
            reset();
            router.push("/");
          }}
        />
      )}

      {/* 3-Column Mission Control Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Left Column (Width: 3/12) — Mission Intel */}
        <div className="lg:col-span-3 space-y-5">
          {/* Mission Objective Card */}
          <Card title="OBJECTIVE INTEL">
            <div className="space-y-3 font-mono text-xs">
              <p className="text-text-primary text-[11px] leading-relaxed italic bg-void p-2.5 border border-border">
                &quot;{mission.objective}&quot;
              </p>

              <div className="space-y-2 pt-1">
                <div className="flex justify-between">
                  <span className="text-text-muted text-[10px]">WORKFLOW</span>
                  <span className="font-bold text-accent">{mission.workflow_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted text-[10px]">TARGET LOCATION</span>
                  <span className="text-text-primary">{mission.location || "Lahore"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted text-[10px]">DEADLINE SLA</span>
                  <span className="text-signal-cyan font-bold">{mission.deadline}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-text-muted text-[10px]">APPROVAL THRESHOLD</span>
                  <span className="text-signal-amber font-bold">
                    &gt; ${mission.approval_threshold.toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Budget Gauge */}
          <BudgetGaugeCard
            currentPrice={bestOffer ? bestOffer.total_price : 0}
            maxBudget={mission.target_budget || 15000}
            totalSavings={mission.total_savings || 0}
          />

          {/* Reasoning Core */}
          <AgentReasoning currentThought={currentThought} />
        </div>

        {/* Center Column (Width: 5/12) — Live Telephony Stage & Queue */}
        <div className="lg:col-span-5 space-y-5">
          {/* Primary Active Call Card */}
          <LiveCallCard activeCall={activeCall} />

          {/* Outreach Call Queue */}
          <CallQueue calls={mission.calls} />

          {/* Terminal Intelligence Log Stream */}
          <Terminal logs={thoughtLog} maxHeight="max-h-56" />
        </div>

        {/* Right Column (Width: 4/12) — Decision Matrix & Timeline */}
        <div className="lg:col-span-4 space-y-5">
          {/* Negotiation Tracker */}
          <NegotiationTracker
            supplierName={bestOffer?.supplier_name}
            originalPrice={bestOffer?.original_price || bestOffer?.total_price || 0}
            revisedPrice={bestOffer?.total_price || 0}
            savings={bestOffer?.negotiated_savings || mission.total_savings || 0}
          />

          {/* Offers Table */}
          <OffersTable offers={mission.offers} />

          {/* Mission Timeline Audit */}
          <MissionTimeline events={mission.events} />
        </div>
      </div>

      {/* Approval Gate Modal */}
      <ApprovalGate
        isOpen={approvalModal.isOpen}
        data={approvalModal.data}
        onApprove={handleApprove}
        onReject={handleReject}
        onRequestMore={handleRequestMore}
      />
    </div>
  );
}
