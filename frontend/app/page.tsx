"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { HeroSection } from "@/components/landing/HeroSection";
import { WorkflowCards } from "@/components/landing/WorkflowCards";
import { MissionBriefing } from "@/components/mission/MissionBriefing";
import { createMission } from "@/lib/api";

import { ToastContainer } from "@/components/ui/Toast";

export default function LandingPage() {
  const router = useRouter();
  const [objective, setObjective] = useState(
    "We need 500 ergonomic office chairs delivered to our Lahore office before Friday. Keep the total cost below $15,000."
  );
  const [workflowType, setWorkflowType] = useState<"PROCURE" | "RESCUE" | "QUOTE" | "SCHEDULE">("PROCURE");
  const [isLoading, setIsLoading] = useState(false);
  const [isBriefingOpen, setIsBriefingOpen] = useState(false);
  const [toasts, setToasts] = useState<Array<{ id: string; type?: "error" | "success" | "info" | "warning"; title?: string; message: string }>>([]);

  const addToast = (message: string, type: "error" | "success" | "info" | "warning" = "info", title?: string) => {
    const id = `toast_${Date.now()}_${Math.random()}`;
    setToasts((prev) => [...prev, { id, type, title, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const [briefingData, setBriefingData] = useState({
    item: "Ergonomic Office Chairs",
    quantity: 500,
    budget: 15000,
    deadline: "Friday (September 4)",
    location: "Lahore, Pakistan",
    approvalThreshold: 5000,
  });

  const handleSelectPreset = (
    presetPrompt: string,
    type: "PROCURE" | "RESCUE" | "QUOTE" | "SCHEDULE"
  ) => {
    setObjective(presetPrompt);
    setWorkflowType(type);

    if (type === "RESCUE") {
      setBriefingData({
        item: "26ft Emergency Freight Truck",
        quantity: 1,
        budget: 800,
        deadline: "Under 2 hours (Immediate)",
        location: "Downtown Logistics Hub",
        approvalThreshold: 500,
      });
    } else if (type === "QUOTE") {
      setBriefingData({
        item: "Commercial 50kVA Diesel Generator",
        quantity: 1,
        budget: 20000,
        deadline: "Within 5 business days",
        location: "Regional Industrial Zone",
        approvalThreshold: 5000,
      });
    } else if (type === "SCHEDULE") {
      setBriefingData({
        item: "3:00 PM Consultation Opening",
        quantity: 1,
        budget: 0,
        deadline: "Today (3:00 PM)",
        location: "Central Medical Suite",
        approvalThreshold: 0,
      });
    } else {
      setBriefingData({
        item: "Ergonomic Office Chairs",
        quantity: 500,
        budget: 15000,
        deadline: "Friday (September 4)",
        location: "Lahore, Pakistan",
        approvalThreshold: 5000,
      });
    }

    setIsBriefingOpen(true);
  };

  const handleStartMissionClick = () => {
    // Quick heuristic parser for briefing preview
    const isRescue = objective.toLowerCase().includes("truck") || objective.toLowerCase().includes("rescue");
    const isQuote = objective.toLowerCase().includes("generator") || objective.toLowerCase().includes("quote");
    const isSchedule = objective.toLowerCase().includes("appointment") || objective.toLowerCase().includes("waitlist");

    if (isRescue) {
      setWorkflowType("RESCUE");
      setBriefingData({
        item: "26ft Freight Box Truck",
        quantity: 1,
        budget: 800,
        deadline: "Under 2 hours",
        location: "Downtown Hub",
        approvalThreshold: 500,
      });
    } else if (isQuote) {
      setWorkflowType("QUOTE");
      setBriefingData({
        item: "Commercial 50kVA Generator",
        quantity: 1,
        budget: 20000,
        deadline: "Within 5 days",
        location: "Industrial Center",
        approvalThreshold: 5000,
      });
    } else if (isSchedule) {
      setWorkflowType("SCHEDULE");
      setBriefingData({
        item: "3:00 PM Consultation Slot",
        quantity: 1,
        budget: 0,
        deadline: "Today 3 PM",
        location: "City Center",
        approvalThreshold: 0,
      });
    } else {
      setWorkflowType("PROCURE");
      setBriefingData({
        item: "Ergonomic Office Chairs",
        quantity: 500,
        budget: 15000,
        deadline: "Friday (September 4)",
        location: "Lahore, Pakistan",
        approvalThreshold: 5000,
      });
    }

    setIsBriefingOpen(true);
  };

  const handleConfirmLaunch = async (editedData: typeof briefingData) => {
    setIsBriefingOpen(false);
    setIsLoading(true);

    try {
      const mission = await createMission({
        objective,
        workflow_type: workflowType,
        custom_budget: editedData.budget,
        custom_deadline: editedData.deadline,
        approval_threshold: editedData.approvalThreshold,
      });

      router.push(`/mission/${mission.id}`);
    } catch (err: any) {
      addToast(err.message || "Failed to initialize mission", "error", "LAUNCH FAILED");
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-12 sm:space-y-16">
      {/* Hero with Objective Terminal */}
      <HeroSection
        objective={objective}
        setObjective={setObjective}
        onStartMission={handleStartMissionClick}
        isLoading={isLoading}
      />

      {/* 4 Supported Workflow Presets */}
      <WorkflowCards onSelectPreset={handleSelectPreset} />

      {/* Pre-Flight Briefing Modal */}
      <MissionBriefing
        isOpen={isBriefingOpen}
        objective={objective}
        workflowType={workflowType}
        initialData={briefingData}
        onConfirm={handleConfirmLaunch}
        onCancel={() => setIsBriefingOpen(false)}
      />

      {/* Toast Notification Container */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  );
}
