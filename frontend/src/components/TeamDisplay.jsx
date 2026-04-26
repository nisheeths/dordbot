import React from 'react'

export default function TeamDisplay({ data }) {
  const { assignments = [], coverage_score, confidence_score, gaps = [] } = data || {}
  return (
    <div style={{ marginTop: 24 }}>
      <h2>Team Recommendation</h2>
      <div style={{ display: 'flex', gap: 24, marginBottom: 12 }}>
        <div><strong>Coverage:</strong> {(coverage_score * 100).toFixed(0)}%</div>
        <div><strong>Confidence:</strong> {(confidence_score * 100).toFixed(0)}%</div>
      </div>

      <ol>
        {assignments.map((a, idx) => (
          <li key={a.work_element_id || idx} style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 14, color: '#666' }}>Work element {idx + 1}</div>
            <div style={{ marginTop: 4 }}>
              {(a.candidates || []).slice(0,3).map(c => (
                <div key={c.employee_id} style={{ padding: 6, border: '1px solid #ddd', borderRadius: 8, marginBottom: 6 }}>
                  <strong>{c.name}</strong>
                  <span style={{ marginLeft: 8, color: '#666' }}>{c.rationale}</span>
                  <span style={{ marginLeft: 12 }}>sim {(c.similarity*100).toFixed(1)}%</span>
                </div>
              ))}
              {(!a.candidates || a.candidates.length === 0) && (
                <div style={{ color: 'crimson' }}>No strong match found</div>
              )}
            </div>
          </li>
        ))}
      </ol>

      {gaps.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <h3>Gaps</h3>
          <ul>
            {gaps.map((g, i) => (<li key={i} style={{ color: 'crimson' }}>{g}</li>))}
          </ul>
        </div>
      )}
    </div>
  )
}
