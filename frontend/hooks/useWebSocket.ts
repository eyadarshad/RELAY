import { useEffect, useRef } from 'react';
import { useMissionStore } from '@/store/missionStore';

export function useWebSocket(missionId?: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const {
    setMission,
    updateStatus,
    addThought,
    setActiveCall,
    updateActiveCall,
    setApprovalModal,
    setConnected,
    setCompletionData,
    addTimelineEvent,
    addCallRecord,
    updateCallRecord,
    addOffer,
    updateOffer,
    setOffers,
    updateMissionField,
  } = useMissionStore();

  useEffect(() => {
    if (!missionId) return;

    let wsUrl = `ws://127.0.0.1:8000/ws/mission/${missionId}`;
    if (process.env.NEXT_PUBLIC_WS_URL) {
      const raw = process.env.NEXT_PUBLIC_WS_URL.replace(/\/$/, "");
      wsUrl = `${raw}/ws/mission/${missionId}`;
    } else if (process.env.NEXT_PUBLIC_API_URL) {
      const raw = process.env.NEXT_PUBLIC_API_URL.replace(/\/$/, "").replace(/\/api$/, "");
      const wsBase = raw.replace(/^https?:\/\//i, (match) => match.toLowerCase() === "https://" ? "wss://" : "ws://");
      wsUrl = `${wsBase}/ws/mission/${missionId}`;
    } else if (typeof window !== "undefined") {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const host = process.env.NEXT_PUBLIC_WS_HOST || "127.0.0.1:8000";
      wsUrl = `${protocol}//${host}/ws/mission/${missionId}`;
    }

    let socket: WebSocket;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      socket = new WebSocket(wsUrl);
      wsRef.current = socket;

      socket.onopen = () => {
        setConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          const { event_type, message, data, title, timestamp } = payload;

          switch (event_type) {
            case 'STATE_SNAPSHOT':
              if (data) {
                setMission(data);
                updateStatus(data.status);
                if (data.summary_report) {
                  setCompletionData(data.summary_report);
                }
              }
              break;

            case 'AGENT_STATUS_CHANGED':
              updateStatus(data.status);
              if (message) addThought(`[STATUS] ${message}`);
              break;

            case 'AGENT_REASONING':
              addThought(data.thought || message);
              break;

            case 'CALL_STARTED': {
              const callId = data.id || data.call_id;
              const callType = data.call_type || 'INQUIRY';
              setActiveCall({
                call_id: callId,
                supplier_name: data.supplier_name,
                supplier_phone: data.supplier_phone,
                call_type: callType,
                status: 'TALKING',
                duration: 0,
              });
              addCallRecord({
                id: callId,
                calle_call_id: data.calle_call_id,
                supplier_name: data.supplier_name,
                supplier_phone: data.supplier_phone,
                call_type: callType,
                status: 'TALKING',
                duration_seconds: 0,
                transcript_snippet: '',
                structured_result: {},
                started_at: data.started_at || new Date().toISOString(),
              });
              addThought(`[CALL] Dialing ${data.supplier_name} (${data.supplier_phone || 'CALL-E'})...`);
              break;
            }

            case 'CALL_COMPLETED': {
              const callId = data.id || data.call_id;
              const transcript = data.transcript || data.transcript_snippet || '';
              updateActiveCall({
                status: 'COMPLETED',
                transcript: transcript,
                duration: data.duration_seconds || 45,
              });
              updateCallRecord(callId, {
                status: 'COMPLETED',
                duration_seconds: data.duration_seconds || 45,
                transcript_snippet: transcript,
                structured_result: data.structured_result || {},
              });
              addThought(`[CALL COMPLETED] Structured data received from ${data.supplier_name}`);
              break;
            }

            case 'OFFER_RECEIVED':
              if (data.id || data.offer_id) {
                const offerObj = {
                  id: data.id || data.offer_id,
                  supplier_name: data.supplier_name,
                  supplier_phone: data.supplier_phone || '',
                  contact_person: data.contact_person || 'Sales Desk',
                  unit_price: data.unit_price,
                  total_price: data.total_price,
                  original_price: data.original_price || data.total_price,
                  negotiated_savings: data.negotiated_savings || 0,
                  quantity_available: data.quantity_available || data.quantity || 0,
                  delivery_days: data.delivery_days,
                  delivery_date: data.delivery_date,
                  warranty_years: data.warranty_years || 1,
                  payment_terms: data.payment_terms || 'Standard',
                  composite_score: data.composite_score || 0,
                  status: data.status || 'CANDIDATE',
                  notes: data.notes || '',
                };
                addOffer(offerObj);
              }
              addThought(`[OFFER] Received quote of $${data.total_price?.toLocaleString()} from ${data.supplier_name}`);
              break;

            case 'OFFERS_EVALUATED':
              if (Array.isArray(data.offers) && data.offers.length > 0) {
                setOffers(data.offers);
              }
              addThought(`[DECISION] Evaluated supplier proposals against constraints.`);
              break;

            case 'NEGOTIATION_UPDATE':
              if (data.offer) {
                addOffer(data.offer);
              } else if (data.offer_id) {
                updateOffer(data.offer_id, {
                  total_price: data.revised_price,
                  original_price: data.original_price,
                  negotiated_savings: data.savings,
                  unit_price: data.unit_price,
                });
              }
              updateMissionField('total_savings', data.savings);
              addThought(`[NEGOTIATION] Secured $${data.savings?.toLocaleString()} discount with ${data.supplier_name}!`);
              break;

            case 'APPROVAL_REQUIRED':
              setApprovalModal({
                isOpen: true,
                data: data,
              });
              addThought(`[APPROVAL REQUIRED] Transaction exceeds threshold. Awaiting human confirmation.`);
              break;

            case 'MISSION_COMPLETED':
              setCompletionData(data);
              updateStatus('COMPLETED');
              setActiveCall(null);
              if (data.total_savings !== undefined) {
                updateMissionField('total_savings', data.total_savings);
              }
              addThought(`[MISSION COMPLETE] Successfully secured ${data.item_secured} at $${data.final_price?.toLocaleString()}!`);
              break;

            case 'TIMELINE_EVENT':
              addTimelineEvent({
                id: data.event_id || `evt_${Date.now()}`,
                timestamp: timestamp || new Date().toISOString(),
                event_type: data.event_type || 'SYSTEM',
                title: title,
                description: message,
                metadata: data.metadata || {},
              });
              break;

            case 'MISSION_ABORTED':
              updateStatus('ABORTED');
              setActiveCall(null);
              addThought(`[ABORTED] Mission was manually aborted.`);
              break;

            default:
              break;
          }
        } catch (err) {
          console.error('Error parsing WebSocket event:', err);
        }
      };

      socket.onclose = () => {
        setConnected(false);
        // Attempt reconnection after 3 seconds if not unmounted
        reconnectTimeout = setTimeout(connect, 3000);
      };

      socket.onerror = (err) => {
        console.warn('WebSocket connection error:', err);
        socket.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [missionId]);

  const sendApproval = (decision: 'APPROVE' | 'REJECT' | 'REQUEST_MORE') => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'APPROVAL', decision }));
      setApprovalModal({ isOpen: false });
    }
  };

  const sendAbort = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'ABORT' }));
    }
  };

  return { sendApproval, sendAbort };
}
