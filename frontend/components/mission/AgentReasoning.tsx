"use client";

import React from "react";
import { Brain, Cpu } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { GlitchText } from "@/components/ui/GlitchText";

interface AgentReasoningProps {
  currentThought: string;
}

export const AgentReasoning: React.FC<AgentReasoningProps> = ({ currentThought }) => {
  return (
    <Card
      title="AUTONOMOUS REASONING CORE"
      badge={
        <div className="flex items-center gap-1.5 font-mono text-[10px] text-accent font-semibold">
          <Cpu className="w-3.5 h-3.5 animate-spin" />
          <span>NEURAL COGNITION</span>
        </div>
      }
      variant="default"
      className="bg-surface-raised border-border"
    >
      <div className="font-mono text-xs space-y-2">
        <div className="flex items-start gap-2.5 p-3 bg-void border border-border/80 min-h-[60px]">
          <span className="text-accent font-bold select-none text-sm">›</span>
          <p className="text-text-primary text-xs leading-relaxed font-mono">
            <GlitchText text={currentThought || "Autonomous operations agent active. Monitoring workflow..."} />
          </p>
        </div>
      </div>
    </Card>
  );
};
