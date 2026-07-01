import { motion } from 'framer-motion'
import { Check, X } from 'lucide-react'

export default function SkillPills({ skills, isMatch }) {
  if (!skills || skills.length === 0) {
    return <p className="text-slate-500 text-sm italic">None found</p>
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.05 }
    }
  }

  const item = {
    hidden: { opacity: 0, x: -10 },
    show: { opacity: 1, x: 0 }
  }

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="flex flex-wrap gap-2"
    >
      {skills.map((skill, index) => (
        <motion.div
          key={index}
          variants={item}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border ${
            isMatch 
              ? 'bg-green-500/10 text-green-400 border-green-500/20' 
              : 'bg-red-500/10 text-red-400 border-red-500/20'
          }`}
        >
          {isMatch ? <Check size={14} /> : <X size={14} />}
          {skill}
        </motion.div>
      ))}
    </motion.div>
  )
}
