import { create } from 'zustand';
import { MissionDTO } from '@/lib/api';

export interface LiveCallState {
  call_id: string;
  supplier_name: string;
  supplier_phone: string;
  call_type: string;
  status: 'QUEUED' | 'TALKING' | 'COMPLETED' | 'FAILED';
  duration: number;
  transcript?: string;
  is_real_call?: boolean;
}

export interface ApprovalModalState {
  isOpen: boolean;
  data?: {
    supplier_name: string;
    supplier_phone: string;
    quantity: number;
    unit_price?: number;
    total_price: number;
    original_budget: number;
    savings: number;
    delivery_days?: number;
    delivery_date?: string;
    warranty_years?: number;
    payment_terms?: string;
    reasoning?: string;
  };
}

interface MissionState {
  mission: MissionDTO | null;
  agentStatus: string;
  currentThought: string;
  thoughtLog: string[];
  activeCall: LiveCallState | null;
  approvalModal: ApprovalModalState;
  isConnected: boolean;
  completionData: Record<string, any> | null;
  
  // Actions
  setMission: (m: MissionDTO) => void;
  updateStatus: (status: string) => void;
  addThought: (thought: string) => void;
  setActiveCall: (call: LiveCallState | null) => void;
  updateActiveCall: (updates: Partial<LiveCallState>) => void;
  setApprovalModal: (state: ApprovalModalState) => void;
  setConnected: (connected: boolean) => void;
  setCompletionData: (data: Record<string, any> | null) => void;
  addTimelineEvent: (event: any) => void;
  addCallRecord: (call: any) => void;
  updateCallRecord: (callId: string, updates: any) => void;
  addOffer: (offer: any) => void;
  updateOffer: (offerId: string, updates: any) => void;
  setOffers: (offers: any[]) => void;
  updateMissionField: (key: string, value: any) => void;
  reset: () => void;
}

export const useMissionStore = create<MissionState>((set) => ({
  mission: null,
  agentStatus: 'CREATED',
  currentThought: 'Standing by for mission parameters...',
  thoughtLog: ['[SYS] RELAY Autonomous Operations Core initialized.'],
  activeCall: null,
  approvalModal: { isOpen: false },
  isConnected: false,
  completionData: null,

  setMission: (m) => set({ 
    mission: m, 
    agentStatus: m.status,
    completionData: m.summary_report || null 
  }),
  updateStatus: (status) => set((state) => ({
    agentStatus: status,
    mission: state.mission ? { ...state.mission, status } : null,
  })),
  addThought: (thought) => set((state) => ({
    currentThought: thought,
    thoughtLog: [thought, ...state.thoughtLog].slice(0, 50),
  })),
  setActiveCall: (call) => set({ activeCall: call }),
  updateActiveCall: (updates) => set((state) => ({
    activeCall: state.activeCall ? { ...state.activeCall, ...updates } : null,
  })),
  setApprovalModal: (approvalModal) => set({ approvalModal }),
  setConnected: (isConnected) => set({ isConnected }),
  setCompletionData: (completionData) => set({ completionData }),
  addTimelineEvent: (event) => set((state) => {
    if (!state.mission) return state;
    const exists = state.mission.events.some((e) => e.id === event.id);
    if (exists) return state;
    return {
      mission: {
        ...state.mission,
        events: [event, ...state.mission.events],
      },
    };
  }),
  addCallRecord: (call) => set((state) => {
    if (!state.mission) return state;
    const exists = state.mission.calls.some((c) => c.id === call.id);
    const updatedCalls = exists
      ? state.mission.calls.map((c) => (c.id === call.id ? { ...c, ...call } : c))
      : [...state.mission.calls, call];
    return {
      mission: {
        ...state.mission,
        calls: updatedCalls,
      },
    };
  }),
  updateCallRecord: (callId, updates) => set((state) => {
    if (!state.mission) return state;
    return {
      mission: {
        ...state.mission,
        calls: state.mission.calls.map((c) => (c.id === callId ? { ...c, ...updates } : c)),
      },
    };
  }),
  addOffer: (offer) => set((state) => {
    if (!state.mission) return state;
    const exists = state.mission.offers.some((o) => o.id === offer.id);
    const updatedOffers = exists
      ? state.mission.offers.map((o) => (o.id === offer.id ? { ...o, ...offer } : o))
      : [...state.mission.offers, offer];
    return {
      mission: {
        ...state.mission,
        offers: updatedOffers,
      },
    };
  }),
  updateOffer: (offerId, updates) => set((state) => {
    if (!state.mission) return state;
    return {
      mission: {
        ...state.mission,
        offers: state.mission.offers.map((o) => (o.id === offerId ? { ...o, ...updates } : o)),
      },
    };
  }),
  setOffers: (offers) => set((state) => {
    if (!state.mission) return state;
    return {
      mission: {
        ...state.mission,
        offers,
      },
    };
  }),
  updateMissionField: (key, value) => set((state) => {
    if (!state.mission) return state;
    return {
      mission: {
        ...state.mission,
        [key]: value,
      },
    };
  }),
  reset: () => set({
    mission: null,
    agentStatus: 'CREATED',
    currentThought: '',
    thoughtLog: [],
    activeCall: null,
    approvalModal: { isOpen: false },
    completionData: null,
  }),
}));
