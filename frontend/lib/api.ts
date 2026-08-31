const getApiBase = () => {
  if (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) {
    const raw = process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "");
    return raw.endsWith("/api") ? raw : `${raw}/api`;
  }
  return "http://127.0.0.1:8000/api";
};

const API_BASE = getApiBase();

export interface CreateMissionPayload {
  objective: string;
  workflow_type?: "PROCURE" | "RESCUE" | "QUOTE" | "SCHEDULE";
  custom_budget?: number;
  custom_deadline?: string;
  approval_threshold?: number;
}

export interface MissionDTO {
  id: string;
  objective: string;
  workflow_type: string;
  status: string;
  item?: string;
  quantity?: number;
  target_budget?: number;
  deadline?: string;
  location?: string;
  approval_threshold: number;
  constraints: Record<string, any>;
  strategy: Record<string, any>;
  created_at: string;
  completed_at?: string;
  total_savings: number;
  summary_report?: Record<string, any>;
  calls: Array<{
    id: string;
    calle_call_id?: string;
    supplier_name: string;
    supplier_phone: string;
    call_type: string;
    status: string;
    duration_seconds: number;
    transcript_snippet?: string;
    structured_result: Record<string, any>;
    started_at: string;
  }>;
  offers: Array<{
    id: string;
    supplier_name: string;
    supplier_phone: string;
    contact_person?: string;
    unit_price?: number;
    total_price: number;
    original_price?: number;
    negotiated_savings: number;
    quantity_available: number;
    delivery_days?: number;
    delivery_date?: string;
    warranty_years: number;
    payment_terms?: string;
    composite_score: number;
    status: string;
    notes?: string;
  }>;
  events: Array<{
    id: string;
    timestamp: string;
    event_type: string;
    title: string;
    description: string;
    metadata: Record<string, any>;
  }>;
}

export async function createMission(payload: CreateMissionPayload): Promise<MissionDTO> {
  const res = await fetch(`${API_BASE}/missions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to create mission" }));
    throw new Error(err.detail || "Failed to create mission");
  }
  return res.json();
}

export async function getMission(id: string): Promise<MissionDTO> {
  const res = await fetch(`${API_BASE}/missions/${id}`);
  if (!res.ok) {
    throw new Error(`Mission ${id} not found`);
  }
  return res.json();
}

export async function listMissions(): Promise<MissionDTO[]> {
  const res = await fetch(`${API_BASE}/missions`);
  if (!res.ok) return [];
  return res.json();
}

export async function submitApproval(missionId: string, decision: "APPROVE" | "REJECT" | "REQUEST_MORE", notes?: string) {
  const res = await fetch(`${API_BASE}/missions/${missionId}/approval`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision, notes }),
  });
  return res.json();
}

export async function abortMission(missionId: string) {
  const res = await fetch(`${API_BASE}/missions/${missionId}/abort`, {
    method: "POST",
  });
  return res.json();
}
