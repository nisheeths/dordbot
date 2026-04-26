import React, { useState } from 'react'

export default function CfpForm({ onAnalyze, onRecommend, onAnalyzePdf, onRecommendPdf, loading }) {
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)

  return (
    <div style={{ marginTop: 8 }}>
      <label htmlFor="cfp" style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Paste CfP text</label>
      <textarea
        id="cfp"
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="Paste the call for proposals text here..."
        rows={10}
        style={{ width: '100%', padding: 8, fontFamily: 'monospace' }}
      />
      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <button onClick={() => onAnalyze(text)} disabled={loading || !text.trim()}>Analyze CfP</button>
        <button onClick={() => onRecommend(text)} disabled={loading || !text.trim()}>Recommend Team</button>
      </div>

      <div style={{ marginTop: 16, borderTop: '1px solid #eee', paddingTop: 12 }}>
        <label style={{ display: 'block', fontWeight: 600, marginBottom: 8 }}>Or upload a CfP PDF</label>
        <input type="file" accept="application/pdf" onChange={e => setFile(e.target.files?.[0] || null)} />
        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <button onClick={() => file && onAnalyzePdf(file)} disabled={loading || !file}>Analyze PDF</button>
          <button onClick={() => file && onRecommendPdf(file)} disabled={loading || !file}>Recommend from PDF</button>
        </div>
        {file && <div style={{ marginTop: 6, color: '#666' }}>{file.name} • {(file.size/1024).toFixed(1)} KB</div>}
      </div>
    </div>
  )
}
