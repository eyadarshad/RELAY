import { ImageResponse } from 'next/og';

export const size = { width: 32, height: 32 };
export const contentType = 'image/png';

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          fontSize: 20,
          background: '#000000',
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#CCFF00',
          fontWeight: 900,
          border: '2px solid #CCFF00',
          fontFamily: 'monospace',
        }}
      >
        R
      </div>
    ),
    {
      ...size,
    }
  );
}
