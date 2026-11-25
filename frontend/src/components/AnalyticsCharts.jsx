import React from 'react';

export function RadarChart({ leaderboard }) {
  if (!leaderboard || leaderboard.length === 0) return null;

  const size = 340;
  const center = size / 2;
  const radius = center - 52;
  const angleStep = (2 * Math.PI) / leaderboard.length;

  const points = leaderboard
    .map((item, idx) => {
      const angle = idx * angleStep - Math.PI / 2;
      const r = (item.overall_fit / 100) * radius;
      const x = center + r * Math.cos(angle);
      const y = center + r * Math.sin(angle);
      return `${x},${y}`;
    })
    .join(' ');

  const gridLevels = [0.25, 0.5, 0.75, 1.0];

  return (
    <div className="flex flex-col items-center justify-center p-2" role="img" aria-label="8-Role Career Readiness Radar Chart">
      <svg width={size} height={size} className="overflow-visible">
        {/* Concentric grid rings with percentage marks */}
        {gridLevels.map((lvl, i) => (
          <g key={i}>
            <circle
              cx={center}
              cy={center}
              r={radius * lvl}
              fill="none"
              stroke="#D9D3C4"
              strokeWidth="1"
              strokeDasharray={lvl < 1 ? '2 2' : 'none'}
            />
            <text
              x={center + 4}
              y={center - radius * lvl + 10}
              fill="#8C877A"
              fontSize="9"
              fontFamily="JetBrains Mono, monospace"
            >
              {lvl * 100}%
            </text>
          </g>
        ))}

        {/* Axis Spokes and Role Labels */}
        {leaderboard.map((item, idx) => {
          const angle = idx * angleStep - Math.PI / 2;
          const x2 = center + radius * Math.cos(angle);
          const y2 = center + radius * Math.sin(angle);
          const labelDist = radius + 22;
          const labelX = center + labelDist * Math.cos(angle);
          const labelY = center + labelDist * Math.sin(angle);

          const roleWords = item.role.split(' ');
          const line1 = roleWords[0];
          const line2 = roleWords.slice(1).join(' ');

          return (
            <g key={idx}>
              <line x1={center} y1={center} x2={x2} y2={y2} stroke="#D9D3C4" strokeWidth="1" />
              <text
                x={labelX}
                y={labelY - (line2 ? 4 : 0)}
                textAnchor={Math.abs(Math.cos(angle)) < 0.25 ? 'middle' : Math.cos(angle) > 0 ? 'start' : 'end'}
                dominantBaseline="central"
                fill="#14130F"
                fontSize="11"
                fontFamily="IBM Plex Sans, sans-serif"
                fontWeight="600"
              >
                {line1}
              </text>
              {line2 && (
                <text
                  x={labelX}
                  y={labelY + 9}
                  textAnchor={Math.abs(Math.cos(angle)) < 0.25 ? 'middle' : Math.cos(angle) > 0 ? 'start' : 'end'}
                  dominantBaseline="central"
                  fill="#5B574D"
                  fontSize="10"
                  fontFamily="IBM Plex Sans, sans-serif"
                >
                  {line2}
                </text>
              )}
            </g>
          );
        })}

        {/* Data Polygon */}
        <polygon
          points={points}
          fill="rgba(43, 76, 155, 0.16)"
          stroke="#2B4C9B"
          strokeWidth="2"
        />

        {/* Data Points */}
        {leaderboard.map((item, idx) => {
          const angle = idx * angleStep - Math.PI / 2;
          const r = (item.overall_fit / 100) * radius;
          const x = center + r * Math.cos(angle);
          const y = center + r * Math.sin(angle);

          return (
            <circle
              key={idx}
              cx={x}
              cy={y}
              r="3.5"
              fill="#2B4C9B"
              stroke="#FBF9F4"
              strokeWidth="1.5"
            />
          );
        })}
      </svg>
      <span className="sr-only">
        {leaderboard.map((item) => `${item.role}: ${item.overall_fit}% fit`).join(', ')}
      </span>
    </div>
  );
}

export function BellCurve({ peer }) {
  if (!peer) return null;

  const width = 460;
  const height = 210;
  const paddingL = 40;
  const paddingR = 30;
  const paddingT = 25;
  const paddingB = 35;

  const mean = peer.peer_mean_skills || 5.2;
  const sigma = 1.8;
  const userVal = peer.user_skill_count || 0;

  // Normal distribution pdf
  const pdf = (x) => (1 / (sigma * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / sigma, 2));

  const xMin = 0;
  const xMax = 12;
  const yMax = pdf(mean) * 1.18;

  const scaleX = (x) => paddingL + ((x - xMin) / (xMax - xMin)) * (width - paddingL - paddingR);
  const scaleY = (y) => height - paddingB - (y / yMax) * (height - paddingT - paddingB);

  const points = [];
  const fillPoints = [`${scaleX(xMin)},${height - paddingB}`];

  for (let x = xMin; x <= xMax; x += 0.15) {
    const y = pdf(x);
    const px = scaleX(x);
    const py = scaleY(y);
    points.push(`${px},${py}`);
    if (x <= userVal) {
      fillPoints.push(`${px},${py}`);
    }
  }

  const boundedUserVal = Math.min(xMax, Math.max(xMin, userVal));
  const userPx = scaleX(boundedUserVal);
  const userPy = scaleY(pdf(boundedUserVal));
  fillPoints.push(`${userPx},${height - paddingB}`);

  return (
    <div className="w-full flex flex-col items-center" role="img" aria-label={`Gaussian distribution curve. You have ${userVal} skills, ranking at the ${peer.percentile}th percentile.`}>
      <svg width={width} height={height} className="overflow-visible w-full max-w-[460px]">
        {/* Shaded Percentile Area */}
        <polygon points={fillPoints.join(' ')} fill="rgba(43, 76, 155, 0.18)" />

        {/* Bell Curve Line */}
        <polyline points={points.join(' ')} fill="none" stroke="#14130F" strokeWidth="2" />

        {/* Baseline Axis */}
        <line x1={paddingL} y1={height - paddingB} x2={width - paddingR} y2={height - paddingB} stroke="#D9D3C4" strokeWidth="1" />

        {/* User Vertical Line */}
        <line
          x1={userPx}
          y1={userPy}
          x2={userPx}
          y2={height - paddingB}
          stroke="#2B4C9B"
          strokeWidth="2"
          strokeDasharray="3 3"
        />

        <circle cx={userPx} cy={userPy} r="4.5" fill="#2B4C9B" stroke="#FBF9F4" strokeWidth="1.5" />

        <text x={userPx} y={Math.max(16, userPy - 8)} textAnchor="middle" fill="#2B4C9B" fontSize="11" fontFamily="JetBrains Mono, monospace" fontWeight="600">
          You ({userVal} skills)
        </text>

        {/* Mean Indicator */}
        <line
          x1={scaleX(mean)}
          y1={scaleY(pdf(mean))}
          x2={scaleX(mean)}
          y2={height - paddingB}
          stroke="#8C877A"
          strokeWidth="1"
          strokeDasharray="2 2"
        />
        <text
          x={scaleX(mean)}
          y={height - paddingB + 16}
          textAnchor="middle"
          fill="#5B574D"
          fontSize="10"
          fontFamily="JetBrains Mono, monospace"
        >
          μ={mean}
        </text>

        {/* Axis Ticks */}
        {[0, 2, 4, 6, 8, 10, 12].map((tick) => (
          <text
            key={tick}
            x={scaleX(tick)}
            y={height - paddingB + 16}
            textAnchor="middle"
            fill="#8C877A"
            fontSize="10"
            fontFamily="JetBrains Mono, monospace"
          >
            {tick}
          </text>
        ))}
      </svg>
    </div>
  );
}
