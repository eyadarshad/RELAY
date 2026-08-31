"use client";

import React from "react";
import { Phone, CheckCircle2, Clock, XCircle, PhoneForwarded } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { clsx } from "clsx";

interface CallQueueProps {
  calls: Array<{
    id: string;
    supplier_name: string;
    supplier_phone: string;
    call_type: string;
    status: string;
    duration_seconds: number;
  }>;
}

export const CallQueue: React.FC<CallQueueProps> = ({ calls }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return <CheckCircle2 className="w-3.5 h-3.5 text-signal-green shrink-0" />;
      case "TALKING":
        return <Phone className="w-3.5 h-3.5 text-signal-cyan animate-pulse shrink-0" />;
      case "FAILED":
      case "UNAVAILABLE":
        return <XCircle className="w-3.5 h-3.5 text-signal-red shrink-0" />;
      default:
        return <Clock className="w-3.5 h-3.5 text-text-muted shrink-0" />;
    }
  };

  const getStatusBadge = (status: string, call_type: string) => {
    if (status === "TALKING") {
      return (
        <Badge variant={call_type === "NEGOTIATION" ? "amber" : "cyan"} pulse size="sm">
          {call_type === "NEGOTIATION" ? "NEGOTIATING" : "TALKING"}
        </Badge>
      );
    }
    if (status === "COMPLETED") {
      return <Badge variant="green" size="sm">COMPLETE</Badge>;
    }
    if (status === "FAILED") {
      return <Badge variant="red" size="sm">FAILED</Badge>;
    }
    return <Badge variant="neutral" size="sm">QUEUED</Badge>;
  };

  return (
    <Card title="OUTREACH CALL QUEUE" badge={<span className="font-mono text-xs text-text-secondary">({calls.length})</span>}>
      {calls.length === 0 ? (
        <div className="py-6 text-center text-text-muted font-mono text-xs italic">
          No calls queued yet.
        </div>
      ) : (
        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {calls.map((c, i) => {
            const isTalking = c.status === "TALKING";
            return (
              <div
                key={c.id || i}
                className={clsx(
                  "flex items-center justify-between p-2.5 border transition-all duration-150 font-mono text-xs",
                  isTalking
                    ? "bg-surface-raised border-signal-cyan/60"
                    : "bg-surface border-border hover:border-border-active"
                )}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  {getStatusIcon(c.status)}
                  <div className="truncate">
                    <div className="font-bold text-text-primary uppercase truncate">
                      {c.supplier_name}
                    </div>
                    <div className="text-[10px] text-text-secondary">
                      {c.supplier_phone} {c.call_type !== "INQUIRY" && `• [${c.call_type}]`}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2.5 shrink-0">
                  {c.duration_seconds > 0 && (
                    <span className="text-[10px] text-text-muted">{c.duration_seconds}s</span>
                  )}
                  {getStatusBadge(c.status, c.call_type)}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
};
