"use client";

import React, { useState, useEffect } from "react";
import { Phone, PhoneCall, Volume2, Mic } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { WaveformVisualizer } from "@/components/ui/WaveformVisualizer";
import { PulseRing } from "@/components/ui/PulseRing";
import { LiveCallState } from "@/store/missionStore";

interface LiveCallCardProps {
  activeCall: LiveCallState | null;
}

export const LiveCallCard: React.FC<LiveCallCardProps> = ({ activeCall }) => {
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    if (!activeCall || activeCall.status !== "TALKING") {
      setTimer(0);
      return;
    }

    const interval = setInterval(() => {
      setTimer((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [activeCall]);

  const formatSeconds = (sec: number) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  if (!activeCall) {
    return (
      <Card title="CALL-E TELEPHONY INTERFACE" variant="default" className="min-h-[220px] flex flex-col justify-center items-center text-center">
        <div className="flex flex-col items-center justify-center py-6 text-text-muted space-y-2">
          <Phone className="w-8 h-8 opacity-40 mb-1" />
          <div className="font-mono text-xs uppercase tracking-widest text-text-secondary">
            LINE STATUS: IDLE
          </div>
          <div className="font-mono text-[11px] text-text-muted max-w-xs">
            Awaiting next automated outbound dispatch via CALL-E engine.
          </div>
        </div>
      </Card>
    );
  }

  const isTalking = activeCall.status === "TALKING";
  const isNegotiation = activeCall.call_type === "NEGOTIATION";

  return (
    <Card
      title="CALL-E LIVE TELEPHONY STAGE"
      badge={
        <Badge variant={isNegotiation ? "amber" : "cyan"} pulse={isTalking}>
          {isTalking ? (isNegotiation ? "NEGOTIATING LIVE" : "IN CALL (CALL-E)") : "CALL TERMINATED"}
        </Badge>
      }
      variant={isNegotiation ? "glow" : "active"}
      className="relative overflow-hidden"
    >
      <div className="space-y-4">
        {/* Call Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3.5">
            <div className="relative">
              {isTalking ? (
                <PulseRing color={isNegotiation ? "amber" : "cyan"} size={44} />
              ) : (
                <div className="w-11 h-11 border border-border bg-surface-raised flex items-center justify-center text-signal-green">
                  <PhoneCall className="w-5 h-5" />
                </div>
              )}
            </div>
            <div>
              <h4 className="font-display font-bold text-base text-text-primary uppercase tracking-wide">
                {activeCall.supplier_name}
              </h4>
              <div className="font-mono text-xs text-text-secondary flex items-center gap-2 mt-0.5">
                <span>{activeCall.supplier_phone || "+1 (415) 555-0191"}</span>
                <span>•</span>
                <span className="text-accent uppercase tracking-wider">{activeCall.call_type}</span>
              </div>
            </div>
          </div>

          {/* Duration Timer */}
          <div className="text-right font-mono">
            <div className="text-[10px] text-text-muted uppercase tracking-widest">DURATION</div>
            <div className="text-lg font-bold text-signal-cyan">
              {formatSeconds(timer > 0 ? timer : activeCall.duration || 45)}
            </div>
          </div>
        </div>

        {/* Live Audio Equalizer */}
        <div className="border border-border/80 bg-void p-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-mono text-text-secondary">
            <Mic className="w-3.5 h-3.5 text-accent animate-pulse" />
            <span className="uppercase text-[10px] tracking-wider text-text-primary">AI VOICE SYNTHESIS ACTIVE</span>
          </div>
          <WaveformVisualizer isActive={isTalking} color={isNegotiation ? "amber" : "cyan"} barsCount={16} />
        </div>

        {/* Live Transcript / Dialogue Snippet */}
        {activeCall.transcript && (
          <div className="border border-border bg-surface-raised/80 p-3 font-mono text-xs space-y-1">
            <div className="flex items-center justify-between text-[10px] text-text-muted uppercase tracking-wider pb-1 border-b border-border/60">
              <span className="flex items-center gap-1">
                <Volume2 className="w-3 h-3 text-signal-green" /> REALTIME CALL TRANSCRIPTION
              </span>
              <span>STRUCTURED FEED</span>
            </div>
            <p className="text-text-primary whitespace-pre-line text-[11px] leading-relaxed pt-1">
              {activeCall.transcript}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};
