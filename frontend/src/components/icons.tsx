export function FireIcon({ className = "", size = 32 }: { className?: string; size?: number }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 100 100" className={className}>
      <defs>
        <radialGradient id="fireGradient" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="30%" stopColor="#FFFF00" />
          <stop offset="70%" stopColor="#FF9900" />
          <stop offset="100%" stopColor="#FF3300" />
        </radialGradient>
      </defs>
      <path
        d="M50 10C45 25 30 30 25 45C20 60 25 80 50 90C75 80 80 60 75 45C70 30 55 25 50 10Z"
        fill="url(#fireGradient)"
      />
      <path
        d="M40 15C35 25 25 35 20 50C15 65 25 80 40 85C35 75 30 65 35 55C40 45 45 40 40 15Z"
        fill="#FF5500"
        fillOpacity="0.5"
      />
      <path
        d="M60 15C65 25 75 35 80 50C85 65 75 80 60 85C65 75 70 65 65 55C60 45 55 40 60 15Z"
        fill="#FF5500"
        fillOpacity="0.5"
      />
      <path
        d="M30 20L25 10M20 30L10 25M80 30L90 25M70 20L75 10"
        stroke="#FF5500"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}
