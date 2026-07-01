import { useState, useRef } from 'react'
import { UploadCloud, FileText, File as FileIcon, X } from 'lucide-react'

export default function UploadPanel({ onSubmit }) {
  const [resumeFile, setResumeFile] = useState(null)
  const [jdMode, setJdMode] = useState('text') // 'text' or 'file'
  const [jdText, setJdText] = useState('')
  const [jdFile, setJdFile] = useState(null)
  
  const resumeInputRef = useRef(null)
  const jdFileInputRef = useRef(null)

  const handleResumeDrop = (e) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setResumeFile(e.dataTransfer.files[0])
    }
  }

  const handleJdDrop = (e) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setJdFile(e.dataTransfer.files[0])
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!resumeFile) return
    if (jdMode === 'text' && !jdText.trim()) return
    if (jdMode === 'file' && !jdFile) return
    
    onSubmit({
      resumeFile,
      jdText: jdMode === 'text' ? jdText : null,
      jdFile: jdMode === 'file' ? jdFile : null
    })
  }

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900/60 backdrop-blur-xl border border-slate-700 rounded-2xl p-6 sm:p-8 shadow-2xl space-y-8">
      
      {/* Resume Section */}
      <section className="space-y-3">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <FileText className="text-indigo-400" />
          1. Upload Resume
        </h2>
        
        <div 
          className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-colors cursor-pointer
            ${resumeFile ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-600 hover:border-indigo-400 hover:bg-slate-800/50'}`}
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleResumeDrop}
          onClick={() => resumeInputRef.current?.click()}
        >
          <input 
            type="file" 
            ref={resumeInputRef} 
            onChange={(e) => setResumeFile(e.target.files?.[0])}
            accept=".pdf" 
            className="hidden" 
          />
          {resumeFile ? (
            <div className="flex items-center gap-3 text-indigo-300">
              <FileIcon size={32} />
              <div className="text-left">
                <p className="font-medium text-slate-200">{resumeFile.name}</p>
                <p className="text-sm opacity-70">{(resumeFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <button 
                type="button"
                onClick={(e) => { e.stopPropagation(); setResumeFile(null); }}
                className="ml-4 p-2 hover:bg-indigo-500/20 rounded-full transition-colors"
              >
                <X size={20} />
              </button>
            </div>
          ) : (
            <>
              <UploadCloud size={40} className="text-slate-400 mb-3" />
              <p className="text-slate-300 font-medium">Click or drag PDF to upload</p>
              <p className="text-slate-500 text-sm mt-1">PDF files only (max 5MB)</p>
            </>
          )}
        </div>
      </section>

      <hr className="border-slate-700" />

      {/* JD Section */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <FileText className="text-violet-400" />
            2. Job Description
          </h2>
          <div className="bg-slate-800 rounded-lg p-1 flex gap-1">
            <button
              type="button"
              onClick={() => setJdMode('text')}
              className={`px-3 py-1.5 text-sm rounded-md transition-all ${jdMode === 'text' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Paste Text
            </button>
            <button
              type="button"
              onClick={() => setJdMode('file')}
              className={`px-3 py-1.5 text-sm rounded-md transition-all ${jdMode === 'file' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Upload PDF
            </button>
          </div>
        </div>

        {jdMode === 'text' ? (
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste the job description here..."
            className="w-full h-40 bg-slate-950/50 border border-slate-700 rounded-xl p-4 text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none transition-all"
          />
        ) : (
          <div 
            className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-colors cursor-pointer
              ${jdFile ? 'border-violet-500 bg-violet-500/10' : 'border-slate-600 hover:border-violet-400 hover:bg-slate-800/50'}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleJdDrop}
            onClick={() => jdFileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={jdFileInputRef} 
              onChange={(e) => setJdFile(e.target.files?.[0])}
              accept=".pdf" 
              className="hidden" 
            />
            {jdFile ? (
              <div className="flex items-center gap-3 text-violet-300">
                <FileIcon size={32} />
                <div className="text-left">
                  <p className="font-medium text-slate-200">{jdFile.name}</p>
                  <p className="text-sm opacity-70">{(jdFile.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button 
                  type="button"
                  onClick={(e) => { e.stopPropagation(); setJdFile(null); }}
                  className="ml-4 p-2 hover:bg-violet-500/20 rounded-full transition-colors"
                >
                  <X size={20} />
                </button>
              </div>
            ) : (
              <>
                <UploadCloud size={40} className="text-slate-400 mb-3" />
                <p className="text-slate-300 font-medium">Click or drag PDF to upload</p>
                <p className="text-slate-500 text-sm mt-1">PDF files only (max 5MB)</p>
              </>
            )}
          </div>
        )}
      </section>

      <button
        type="submit"
        disabled={!resumeFile || (jdMode === 'text' ? !jdText.trim() : !jdFile)}
        className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-4 rounded-xl shadow-lg shadow-indigo-500/20 transition-all active:scale-[0.98]"
      >
        Analyze Match
      </button>

    </form>
  )
}
