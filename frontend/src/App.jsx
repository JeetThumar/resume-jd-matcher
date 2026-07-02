import { useState } from 'react'
import axios from 'axios'
import { AnimatePresence, motion } from 'framer-motion'
import ThreeBackground from './components/ThreeBackground'
import UploadPanel from './components/UploadPanel'
import ProcessingModule from './components/ProcessingModule'
import ResultsPanel from './components/ResultsPanel'
import { API_URL } from './config'

function App() {
  const [appState, setAppState] = useState('upload') // upload | processing | results
  const [results, setResults] = useState(null)

  const handleUploadSubmit = async (payload) => {
    setAppState('processing')
    
    try {
      const formData = new FormData()
      formData.append('resume', payload.resumeFile)
      if (payload.jdText) {
        formData.append('jd_text', payload.jdText)
      }
      if (payload.jdFile) {
        formData.append('jd_file', payload.jdFile)
      }

      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      setResults(response.data)
      setAppState('results')
    } catch (error) {
      console.error("API Error:", error)
      alert(error.response?.data?.detail || "Failed to analyze resume.")
      setAppState('upload')
    }
  }

  const resetApp = () => {
    setResults(null)
    setAppState('upload')
  }

  return (
    <main className="min-h-screen relative text-slate-100 flex flex-col items-center p-4 sm:p-8 font-sans overflow-x-hidden">
      <ThreeBackground />
      
      <div className="w-full max-w-4xl z-10 space-y-8 mt-12">
        <header className="text-center space-y-2">
          <h1 className="text-4xl sm:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-violet-400 tracking-tight">
            Resume ↔ JD Matcher
          </h1>
          <p className="text-slate-400 text-lg">AI-powered analysis to beat the ATS</p>
        </header>

        <div className="relative min-h-[500px]">
          <AnimatePresence mode="wait">
            {appState === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <UploadPanel onSubmit={handleUploadSubmit} />
              </motion.div>
            )}

            {appState === 'processing' && (
              <motion.div
                key="processing"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.05 }}
                transition={{ duration: 0.4 }}
              >
                <ProcessingModule />
              </motion.div>
            )}

            {appState === 'results' && results && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
              >
                <ResultsPanel results={results} onReset={resetApp} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </main>
  )
}

export default App
