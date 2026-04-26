import React, { useState } from 'react'
import CfpForm from './components/CfpForm.jsx'
import TeamDisplay from './components/TeamDisplay.jsx'

export default function App() {
  const [analysis, setAnalysis] = useState(null)
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [uploadInfo, setUploadInfo] = useState(null) // {cfp_id, pages, chars, preview}

  const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

  async function analyzeCfp(text) {
    setLoading(true); setError(null); setRecommendation(null)
    try {
      const res = await fetch(`${apiBase}/cfp/analyze`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: 'CfP', text })
      })
      if (!res.ok) throw new Error(`Analyze failed: ${res.status}`)
      const data = await res.json()
      setAnalysis(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function recommend(text) {
    setLoading(true); setError(null)
    try {
      const res = await fetch(`${apiBase}/recommend`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, top_k: 3 })
      })
      if (!res.ok) throw new Error(`Recommend failed: ${res.status}`)
      const data = await res.json()
      setRecommendation(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function analyzePdf(file) {
    setLoading(true); setError(null); setRecommendation(null); setUploadInfo(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const up = await fetch(`${apiBase}/cfp/upload`, { method: 'POST', body: fd })
      if (!up.ok) throw new Error(`Upload failed: ${up.status}`)
      const upJson = await up.json()
      setUploadInfo(upJson)
      // Use preview text for analysis to show extracted elements
      await analyzeCfp(upJson.preview || '')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function recommendPdf(file) {
    setLoading(true); setError(null); setRecommendation(null)
    try {
      const fd = new FormData()
      fd.append('file', file)
      const res = await fetch(`${apiBase}/recommend/pdf`, { method: 'POST', body: fd })
      if (!res.ok) throw new Error(`Recommend PDF failed: ${res.status}`)
      const data = await res.json()
      setRecommendation(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: 16, fontFamily: 'system-ui, sans-serif' }}>
      <h1>CfP Team Matcher</h1>
      <CfpForm onAnalyze={analyzeCfp} onRecommend={recommend} onAnalyzePdf={analyzePdf} onRecommendPdf={recommendPdf} loading={loading} />
      {uploadInfo && (
        <div style={{ marginTop: 12, padding: 8, border: '1px dashed #aaa', borderRadius: 8 }}>
          <div><strong>Uploaded PDF:</strong> {uploadInfo.pages} pages, {uploadInfo.chars} chars</div>
          <div style={{ marginTop: 6, color: '#555' }}>
            <strong>Preview:</strong>
            <div style={{ whiteSpace: 'pre-wrap', marginTop: 4 }}>{uploadInfo.preview}</div>
          </div>
        </div>
      )}
      {error && <div style={{ color: 'crimson', marginTop: 8 }}>Error: {error}</div>}
      {analysis && (
        <div style={{ marginTop: 16 }}>
          <h2>Extracted Work Elements</h2>
          <ul>
            {analysis.work_elements.map(el => (
              <li key={el.id} style={{ marginBottom: 8 }}>
                <strong>{el.text}</strong>
                <div style={{ color: '#555', fontSize: 14 }}>{(el.keyphrases || []).join(', ')}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
      {recommendation && (
        <TeamDisplay data={recommendation} />
      )}
    </div>
  )
}
