import React, { useState } from 'react'

export default function CfpForm({ onAnalyze, onRecommend, loading }) {
  const [text, setText] = useState('')

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
    </div>
  )
}
