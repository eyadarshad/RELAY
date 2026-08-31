"use client";

import React from "react";
import { Clock, ShieldAlert, PhoneCall, TrendingDown, CheckCircle2, FileText, Search } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { clsx } from "clsx";

interface TimelineEvent {
  id: string;
  timestamp: string;
  event_type: string;
  title: string;
  description: string;
  metadata?: Record<string, any>;
}

interface MissionTimelineProps {
  events: TimelineEvent[];
}

export const MissionTimeline: React.FC<MissionTimelineProps> = ({ events }) => {
  const getEventIcon = (type: string) => {
    switch (type) {
      case "CALL":
        return <PhoneCall className="w-3.5 h-3.5 text-signal-cyan" />;
      case "DISCOVERY":
        return <Search className="w-3.5 h-3.5 text-accent" />;
      case "NEGOTIATION":
        return <TrendingDown className="w-3.5 h-3.5 text-signal-amber" />;
      case "APPROVAL_GATE":
      case "APPROVAL":
        return <ShieldAlert className="w-3.5 h-3.5 text-signal-amber" />;
      case "CONFIRMATION":
        return <CheckCircle2 className="w-3.5 h-3.5 text-signal-green" />;
      default:
        return <Clock className="w-3.5 h-3.5 text-text-secondary" />;
    }
  };

  const formatTime = (ts: string) => {
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    } catch {
      return "00:00:00";
    }
  };

  return (
    <Card
      title="AUTONOMOUS MISSION TIMELINE"
      badge={<span className="font-mono text-xs text-text-secondary">({events.length} STEPS)</span>}
    >
      {events.length === 0 ? (
        <div className="py-6 text-center text-text-muted font-mono text-xs italic">
          Initializing telemetry timeline...
        </div>
      ) : (
        <div className="space-y-4 max-h-[360px] overflow-y-auto pr-1">
          {events.map((ev, i) => (
            <div key={ev.id || i} className="relative pl-6 border-l border-border/80 pb-2">
              {/* Timeline Node Icon */}
              <div className="absolute -left-[9px] top-0.5 p-1 bg-surface border border-border">
                {getEventIcon(ev.event_type)}
              </div>

              <div className="font-mono text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-text-primary uppercase tracking-wide">
                    {ev.title}
                  </span>
                  <span className="text-[10px] text-text-muted">
                    {formatTime(ev.timestamp)}
                  </span>
                </div>
                <p className="text-text-secondary text-[11px] leading-relaxed">
                  {ev.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
