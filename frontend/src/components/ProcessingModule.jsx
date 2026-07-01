import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Check, Loader2, Circle } from 'lucide-react'

const STAGES = [
  "Extracting resume text...",
  "Reading job description...",
  "Comparing skills & analyzing gaps...",
  "Generating targeted suggestions..."
]

export default function ProcessingModule() {
  const [currentStage, setCurrentStage] = useState(0)

  useEffect(() => {
    // Advance stages every 800ms up to the last stage
    const interval = setInterval(() => {
      setCurrentStage(prev => {
        if (prev < STAGES.length - 1) return prev + 1
        clearInterval(interval)
        return prev
      })
    }, 800)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700 rounded-2xl p-8 sm:p-12 shadow-2xl flex flex-col items-center max-w-md mx-auto">
      <div className="relative mb-8">
        <div className="absolute inset-0 bg-indigo-500/20 blur-xl rounded-full" />
        <Loader2 className="w-16 h-16 text-indigo-400 animate-spin relative z-10" />
      </div>

      <h3 className="text-2xl font-bold mb-6 text-slate-100">Analyzing Match</h3>

      <div className="w-full space-y-4">
        {STAGES.map((stageText, index) => {
          const isComplete = index < currentStage
          const isActive = index === currentStage
          const isPending = index > currentStage

          return (
            <div key={index} className="flex items-center gap-4">
              <div className="relative flex items-center justify-center w-6 h-6 shrink-0">
                {isComplete && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute inset-0 bg-green-500 rounded-full flex items-center justify-center"
                  >
                    <Check size={14} className="text-white" />
                  </motion.div>
                )}
                {isActive && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="absolute inset-0 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin"
                  />
                )}
                {isPending && (
                  <Circle size={20} className="text-slate-600 absolute inset-0 m-auto" />
                )}
              </div>
              
              <span className={`text-sm sm:text-base transition-colors duration-300
                ${isComplete ? 'text-green-400' : isActive ? 'text-indigo-300 font-medium' : 'text-slate-500'}
              `}>
                {stageText}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
