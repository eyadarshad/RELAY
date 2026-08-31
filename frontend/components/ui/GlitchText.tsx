"use client";

import React, { useState, useEffect } from "react";
import { clsx } from "clsx";

interface GlitchTextProps {
  text: string;
  triggerKey?: any;
  className?: string;
}

export const GlitchText: React.FC<GlitchTextProps> = ({
  text,
  triggerKey,
  className,
}) => {
  const [isGlitching, setIsGlitching] = useState(false);

  useEffect(() => {
    setIsGlitching(true);
    const timeout = setTimeout(() => setIsGlitching(false), 350);
    return () => clearTimeout(timeout);
  }, [text, triggerKey]);

  return (
    <span
      className={clsx(
        "relative inline-block transition-colors duration-150",
        isGlitching && "animate-glitch text-accent font-bold",
        className
      )}
    >
      {text}
    </span>
  );
};
