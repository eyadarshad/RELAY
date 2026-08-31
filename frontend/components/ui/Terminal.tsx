"use client";

import React, { useRef, useEffect } from "react";
import { Terminal as TerminalIcon } from "lucide-react";
import { clsx } from "clsx";

interface TerminalProps {
  logs: string[];
  title?: string;
  maxHeight?: string;
  className?: string;
}

export const Terminal: React.FC<TerminalProps> = ({
  logs,
  title = "AGENT_INTELLIGENCE_STREAM",
  maxHeight = "max-h-48",
  className,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = 0; // newest first or scroll to bottom
    }
  }, [logs]);

  return (
    <div className={clsx("border border-border bg-void font-mono text-xs", className)}>
      {/* Terminal Titlebar */}
      <div className="flex items-center justify-between px-3 py-1.5 bg-surface-raised border-b border-border text-[11px] text-text-secondary select-none">
        <div className="flex items-center gap-2">
          <TerminalIcon className="w-3.5 h-3.5 text-accent" />
          <span className="font-bold tracking-wider uppercase text-text-primary">
            {title}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-signal-green animate-pulse" />
          <span className="text-[9px] uppercase tracking-widest text-text-muted">LIVE</span>
        </div>
      </div>

      {/* Log Feed */}
      <div
        ref={containerRef}
        className={clsx(
          "p-3 overflow-y-auto space-y-1.5 flex flex-col-reverse select-text font-mono text-[11px] leading-relaxed",
          maxHeight
        )}
      >
        {logs.length === 0 ? (
          <div className="text-text-muted italic">Awaiting autonomous mission events...</div>
        ) : (
          logs.map((log, index) => {
            const isStatus = log.startsWith("[STATUS]");
            const isCall = log.startsWith("[CALL");
            const isOffer = log.startsWith("[OFFER");
            const isNeg = log.startsWith("[NEGOTIATION");
            const isAppr = log.startsWith("[APPROVAL");
            const isComplete = log.startsWith("[MISSION COMPLETE");

            return (
              <div key={index} className="flex items-start gap-2">
                <span className="text-accent shrink-0 select-none">›</span>
                <span
                  className={clsx(
                    "break-all",
                    isComplete && "text-signal-green font-bold",
                    isNeg && "text-signal-amber font-bold",
                    isAppr && "text-signal-amber",
                    isCall && "text-signal-cyan",
                    isOffer && "text-text-primary",
                    isStatus && "text-accent",
                    !isComplete && !isNeg && !isAppr && !isCall && !isOffer && !isStatus && "text-text-secondary"
                  )}
                >
                  {log}
                </span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
