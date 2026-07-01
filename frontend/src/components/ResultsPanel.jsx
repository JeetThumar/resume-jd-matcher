import { motion } from 'framer-motion'
import { RotateCcw, Lightbulb } from 'lucide-react'
import ScoreGauge from './ScoreGauge'
import SkillPills from './SkillPills'

export default function ResultsPanel({ results, onReset }) {
  const { match_score, matched_skills, missing_skills, suggested_resume_tweaks } = results

  return (
    <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-700 rounded-2xl p-6 sm:p-10 shadow-2xl space-y-10">
      
      {/* Header & Score */}
      <div className="flex flex-col md:flex-row items-center md:items-start justify-between gap-8">
        <div className="space-y-2 text-center md:text-left flex-1">
          <h2 className="text-2xl font-bold text-slate-100">Analysis Complete</h2>
          <p className="text-slate-400 max-w-lg">
            We've compared your resume against the job description. Focus on the missing skills and suggestions below to improve your chances.
          </p>
        </div>
        <div className="shrink-0 bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50">
          <ScoreGauge score={match_score} />
        </div>
      </div>

      <hr className="border-slate-700/50" />

      {/* Skills Analysis */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-200">Matched Skills</h3>
          <SkillPills skills={matched_skills} isMatch={true} />
        </div>
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-200">Missing Skills</h3>
          <SkillPills skills={missing_skills} isMatch={false} />
        </div>
      </div>

      {/* Suggestions */}
      {suggested_resume_tweaks && suggested_resume_tweaks.length > 0 && (
        <>
          <hr className="border-slate-700/50" />
          <div className="space-y-6">
            <h3 className="text-xl font-semibold flex items-center gap-2 text-slate-200">
              <Lightbulb className="text-yellow-400" />
              Suggested Tweaks
            </h3>
            <div className="grid gap-4">
              {suggested_resume_tweaks.map((tweak, index) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  className="bg-slate-800/60 border border-slate-700 rounded-xl p-4 flex gap-4"
                >
                  <div className="mt-1">
                    <div className="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-sm font-bold">
                      {index + 1}
                    </div>
                  </div>
                  <p className="text-slate-300 leading-relaxed">{tweak}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Footer */}
      <div className="pt-6 flex justify-center">
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium rounded-xl border border-slate-600 transition-colors"
        >
          <RotateCcw size={18} />
          Analyze Another
        </button>
      </div>
      
    </div>
  )
}
