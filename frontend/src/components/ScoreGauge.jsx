import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

export default function ScoreGauge({ score }) {
  const [currentScore, setCurrentScore] = useState(0)

  useEffect(() => {
    const duration = 1000 // 1s animation
    const steps = 60
    const stepTime = duration / steps
    let current = 0
    
    const timer = setInterval(() => {
      current += score / steps
      if (current >= score) {
        setCurrentScore(score)
        clearInterval(timer)
      } else {
        setCurrentScore(Math.floor(current))
      }
    }, stepTime)

    return () => clearInterval(timer)
  }, [score])

  const getColor = (s) => {
    if (s >= 80) return 'text-green-500'
    if (s >= 50) return 'text-yellow-500'
    return 'text-red-500'
  }
  
  const getStrokeColor = (s) => {
    if (s >= 80) return '#22c55e'
    if (s >= 50) return '#eab308'
    return '#ef4444'
  }

  const radius = 60
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (currentScore / 100) * circumference

  return (
    <div className="relative w-40 h-40 flex items-center justify-center">
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 140 140">
        <circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke="#334155"
          strokeWidth="12"
        />
        <motion.circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke={getStrokeColor(score)}
          strokeWidth="12"
          strokeLinecap="round"
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeOut" }}
          style={{ strokeDasharray: circumference }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-4xl font-bold ${getColor(currentScore)}`}>
          {currentScore}%
        </span>
        <span className="text-xs text-slate-400 font-medium uppercase tracking-wider mt-1">Match</span>
      </div>
    </div>
  )
}
