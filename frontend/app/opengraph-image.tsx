import { ImageResponse } from 'next/og';

export const alt = 'RELAY // Autonomous Business Operations Agent';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: '#000000',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          padding: '60px',
          border: '4px solid #1C1C1C',
          fontFamily: 'sans-serif',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div
              style={{
                width: '48px',
                height: '48px',
                background: '#CCFF00',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#000000',
                fontSize: '28px',
                fontWeight: 900,
                fontFamily: 'monospace',
              }}
            >
              R
            </div>
            <div style={{ display: 'flex', fontSize: '32px', fontWeight: 900, color: '#F4F4F4', letterSpacing: '2px' }}>
              <span>RELAY</span>
              <span style={{ color: '#CCFF00' }}>.OPS</span>
            </div>
          </div>
          <div
            style={{
              display: 'flex',
              padding: '8px 16px',
              border: '1px solid #CCFF00',
              color: '#CCFF00',
              fontSize: '16px',
              fontWeight: 700,
              fontFamily: 'monospace',
            }}
          >
            CALL-E HACKATHON 2026
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', fontSize: '60px', fontWeight: 900, color: '#F4F4F4', lineHeight: 1.1 }}>
            <span>GIVE AI A MISSION.</span>
            <span style={{ color: '#CCFF00' }}>IT HANDLES THE CALLS.</span>
          </div>
          <div style={{ display: 'flex', fontSize: '24px', color: '#8E8E8E', maxWidth: '900px' }}>
            Autonomous multi-call operational engine for procurement, logistics rescue, bidding, and scheduling.
          </div>
        </div>

        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            borderTop: '1px solid #1C1C1C',
            paddingTop: '24px',
            fontSize: '18px',
            color: '#555555',
            fontFamily: 'monospace',
          }}
        >
          <div style={{ display: 'flex' }}>MULTI-CALL AUTONOMY • NEGOTIATION • HUMAN APPROVAL GATE</div>
          <div style={{ display: 'flex', color: '#00FF88' }}>POWERED BY CALL-E v1.0 SDK</div>
        </div>
      </div>
    ),
    {
      ...size,
    }
  );
}
