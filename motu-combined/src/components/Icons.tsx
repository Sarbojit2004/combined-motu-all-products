import React from "react";

// ─────────────────────────────────────────────────────────────────────────────
// Glyphs drawn as SVG rather than imported as bitmaps, so they stay crisp at
// 2160 x 3840 and can be recoloured per ground. Both are used only on the
// outro — nothing branded appears in the body of this reel.
// ─────────────────────────────────────────────────────────────────────────────

export const WhatsAppIcon: React.FC<{ size: number; color: string }> = ({ size, color }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
    <path
      d="M16.02 3.2C8.96 3.2 3.23 8.93 3.23 15.99c0 2.26.59 4.46 1.72 6.4L3.14 28.8l6.57-1.72a12.74 12.74 0 0 0 6.31 1.66h.01c7.05 0 12.79-5.73 12.79-12.79 0-3.42-1.33-6.63-3.75-9.05a12.7 12.7 0 0 0-9.05-3.7Zm0 23.34h-.01c-1.9 0-3.77-.51-5.4-1.48l-.39-.23-4.02 1.05 1.07-3.92-.25-.4a10.6 10.6 0 0 1-1.63-5.67c0-5.86 4.77-10.63 10.64-10.63 2.84 0 5.51 1.11 7.52 3.12a10.56 10.56 0 0 1 3.11 7.52c0 5.87-4.77 10.64-10.64 10.64Z"
      fill={color}
    />
    <path
      d="M21.85 18.66c-.32-.16-1.89-.93-2.18-1.04-.29-.11-.5-.16-.71.16-.21.32-.82 1.04-1.01 1.25-.19.21-.37.24-.69.08-.32-.16-1.35-.5-2.57-1.59-.95-.85-1.59-1.89-1.78-2.21-.19-.32-.02-.5.14-.66.15-.14.32-.37.48-.56.16-.19.21-.32.32-.53.11-.21.05-.4-.03-.56-.08-.16-.71-1.72-.98-2.35-.26-.62-.52-.53-.71-.54l-.61-.01c-.21 0-.56.08-.85.4-.29.32-1.11 1.09-1.11 2.65 0 1.56 1.14 3.07 1.3 3.28.16.21 2.25 3.43 5.44 4.81.76.33 1.35.52 1.81.67.76.24 1.46.21 2.01.13.61-.09 1.89-.77 2.15-1.52.27-.74.27-1.38.19-1.51-.08-.13-.29-.21-.61-.37Z"
      fill={color}
    />
  </svg>
);

export const SiteIcon: React.FC<{ size: number; color: string }> = ({ size, color }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
    <circle cx="16" cy="16" r="12.4" stroke={color} strokeWidth="2.1" />
    <ellipse cx="16" cy="16" rx="5.1" ry="12.4" stroke={color} strokeWidth="2.1" />
    <path d="M4.3 12.1h23.4M4.3 19.9h23.4" stroke={color} strokeWidth="2.1" strokeLinecap="round" />
  </svg>
);
