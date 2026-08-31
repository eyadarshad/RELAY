"use client";

import React from "react";
import { Award, ShieldCheck, Truck, TrendingDown, DollarSign } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { clsx } from "clsx";

interface OffersTableProps {
  offers: Array<{
    id: string;
    supplier_name: string;
    unit_price?: number;
    total_price: number;
    original_price?: number;
    negotiated_savings: number;
    quantity_available: number;
    delivery_days?: number;
    warranty_years: number;
    composite_score: number;
    status: string;
    notes?: string;
  }>;
}

export const OffersTable: React.FC<OffersTableProps> = ({ offers }) => {
  return (
    <Card
      title="STRUCTURED PROPOSAL MATRIX"
      badge={<span className="font-mono text-xs text-text-secondary">({offers.length} OFFERS)</span>}
    >
      {offers.length === 0 ? (
        <div className="py-8 text-center text-text-muted font-mono text-xs italic">
          No proposals collected yet. Telephony calls in progress...
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border-collapse">
            <thead>
              <tr className="border-b border-border text-[10px] text-text-secondary uppercase tracking-widest bg-surface-raised">
                <th className="py-2.5 px-3">SUPPLIER</th>
                <th className="py-2.5 px-3 text-right">TOTAL</th>
                <th className="py-2.5 px-3 text-right">UNIT</th>
                <th className="py-2.5 px-3 text-center">DELIVERY</th>
                <th className="py-2.5 px-3 text-center">WARRANTY</th>
                <th className="py-2.5 px-3 text-right">SCORE</th>
                <th className="py-2.5 px-3 text-right">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60">
              {offers.map((offer) => {
                const isBest = offer.status === "BEST" || offer.status === "ACCEPTED";
                const isRejected = offer.status === "REJECTED";
                const hasDiscount = offer.negotiated_savings > 0;

                return (
                  <tr
                    key={offer.id}
                    className={clsx(
                      "transition-colors",
                      isBest ? "bg-accent/5 font-bold" : "hover:bg-surface-raised",
                      isRejected && "opacity-45"
                    )}
                  >
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1.5">
                        {isBest && <Award className="w-3.5 h-3.5 text-accent shrink-0" />}
                        <span className="text-text-primary uppercase truncate max-w-[140px]">
                          {offer.supplier_name}
                        </span>
                      </div>
                      {offer.notes && (
                        <div className="text-[9px] text-text-muted mt-0.5 truncate max-w-[200px]">
                          {offer.notes}
                        </div>
                      )}
                    </td>

                    <td className="py-3 px-3 text-right">
                      {hasDiscount ? (
                        <div>
                          <span className="text-[10px] text-text-muted line-through block">
                            ${offer.original_price?.toLocaleString()}
                          </span>
                          <span className="text-signal-green font-bold">
                            ${offer.total_price.toLocaleString()}
                          </span>
                        </div>
                      ) : (
                        <span className={clsx(isBest ? "text-accent" : "text-text-primary")}>
                          ${offer.total_price.toLocaleString()}
                        </span>
                      )}
                    </td>

                    <td className="py-3 px-3 text-right text-text-secondary">
                      ${offer.unit_price ? offer.unit_price.toFixed(2) : "--"}
                    </td>

                    <td className="py-3 px-3 text-center text-text-secondary">
                      {offer.delivery_days ? `${offer.delivery_days}d` : "--"}
                    </td>

                    <td className="py-3 px-3 text-center text-text-secondary">
                      {offer.warranty_years ? `${offer.warranty_years}y` : "None"}
                    </td>

                    <td className="py-3 px-3 text-right">
                      <span
                        className={clsx(
                          "font-bold",
                          offer.composite_score >= 90
                            ? "text-signal-green"
                            : offer.composite_score >= 75
                            ? "text-signal-amber"
                            : "text-text-muted"
                        )}
                      >
                        {offer.composite_score > 0 ? `${offer.composite_score}` : "--"}
                      </span>
                    </td>

                    <td className="py-3 px-3 text-right">
                      {offer.status === "BEST" && (
                        <Badge variant="accent" size="sm">BEST OFFER</Badge>
                      )}
                      {offer.status === "ACCEPTED" && (
                        <Badge variant="green" size="sm">LOCKED IN</Badge>
                      )}
                      {offer.status === "CANDIDATE" && (
                        <Badge variant="neutral" size="sm">CANDIDATE</Badge>
                      )}
                      {offer.status === "REJECTED" && (
                        <Badge variant="red" size="sm">DISQUALIFIED</Badge>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
};
