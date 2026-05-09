import { useState, useEffect } from 'react';
import { HiOutlineDocumentText, HiOutlineCheckCircle, HiOutlineExclamation, HiOutlinePhotograph, HiOutlineLink, HiOutlineCloudUpload, HiOutlineChartBar } from 'react-icons/hi';
import { getDashboardStats } from '../services/api';

const STATUS_COLORS = { complete: '#10b981', pending: '#94a3b8', error: '#ef4444' };

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchStats(); }, []);

  const fetchStats = async () => {
    try {
      const res = await getDashboardStats();
      setStats(res.data);
    } catch { setStats(null); }
    finally { setLoading(false); }
  };

  if (loading) return <div style={{ padding: 40, color: '#94a3b8' }}>Loading dashboard...</div>;

  const s = stats || {};
  const pipeline = s.processing_status || {};

  const statCards = [
    { label: 'Questions Parsed', value: s.total_questions_parsed || 0, icon: HiOutlineDocumentText, color: '#6366f1' },
    { label: 'LO Mappings', value: s.total_lo_parsed || 0, icon: HiOutlineLink, color: '#0ea5e9' },
    { label: 'Merged Records', value: s.total_merged || 0, icon: HiOutlineCheckCircle, color: '#10b981' },
    { label: 'Validation Issues', value: s.total_validation_issues || 0, icon: HiOutlineExclamation, color: s.total_validation_issues > 0 ? '#ef4444' : '#10b981' },
    { label: 'Media Files', value: s.total_media_files || 0, icon: HiOutlinePhotograph, color: '#f59e0b' },
    { label: 'Uploads', value: s.total_uploads || 0, icon: HiOutlineCloudUpload, color: '#8b5cf6' },
    { label: 'Match Rate', value: `${(s.match_rate || 0).toFixed(1)}%`, icon: HiOutlineChartBar, color: '#14b8a6' },
    { label: 'Exports', value: s.total_exports || 0, icon: HiOutlineDocumentText, color: '#ec4899' },
  ];

  const pipelineSteps = [
    { key: 'upload', label: 'Upload' },
    { key: 'parsing', label: 'Question Parsing' },
    { key: 'lo_mapping', label: 'LO Mapping' },
    { key: 'merging', label: 'Merge & Resolve' },
    { key: 'generation', label: 'Sheet Generation' },
    { key: 'validation', label: 'Validation' },
    { key: 'export', label: 'Export' },
  ];

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Academic Assessment Tool — Overview</p>
      </div>

      {/* Stat Cards */}
      <div className="grid-4" style={{ marginBottom: 28 }}>
        {statCards.map(({ label, value, icon: Icon, color }, i) => (
          <div key={i} className="glass-card stat-card" style={{ padding: '20px 24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <p style={{ color: '#94a3b8', fontSize: 13, fontWeight: 500, marginBottom: 8 }}>{label}</p>
                <p style={{ fontSize: 28, fontWeight: 700, color }}>{value}</p>
              </div>
              <div style={{ padding: 10, borderRadius: 10, background: `${color}15` }}>
                <Icon size={22} color={color} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pipeline Progress */}
      <div className="card-section">
        <h2>🔄 Processing Pipeline</h2>
        <div className="glass-card" style={{ padding: 24 }}>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {pipelineSteps.map(({ key, label }, i) => {
              const status = pipeline[key] || 'pending';
              return (
                <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{
                    padding: '8px 16px', borderRadius: 8, fontSize: 13, fontWeight: 600,
                    background: status === 'complete' ? 'rgba(16,185,129,0.1)' : 'rgba(148,163,184,0.1)',
                    color: STATUS_COLORS[status] || '#94a3b8',
                    border: `1px solid ${status === 'complete' ? 'rgba(16,185,129,0.2)' : 'rgba(148,163,184,0.15)'}`,
                  }}>
                    {status === 'complete' ? '✓' : '○'} {label}
                  </div>
                  {i < pipelineSteps.length - 1 && <span style={{ color: '#475569', fontSize: 18 }}>→</span>}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Unmatched / Issues */}
      <div className="grid-2">
        <div className="glass-card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>📊 Mapping Summary</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={rowStyle}><span>Total Questions</span><span style={{ fontWeight: 700 }}>{s.total_questions_parsed || 0}</span></div>
            <div style={rowStyle}><span>Total LO Mappings</span><span style={{ fontWeight: 700 }}>{s.total_lo_parsed || 0}</span></div>
            <div style={rowStyle}><span>Successfully Merged</span><span style={{ fontWeight: 700, color: '#10b981' }}>{s.total_merged || 0}</span></div>
            <div style={rowStyle}><span>Unmatched Questions</span><span style={{ fontWeight: 700, color: s.unmatched_questions > 0 ? '#ef4444' : '#10b981' }}>{s.unmatched_questions || 0}</span></div>
            <div style={rowStyle}><span>Unmatched LO IDs</span><span style={{ fontWeight: 700, color: s.unmatched_lo_ids > 0 ? '#ef4444' : '#10b981' }}>{s.unmatched_lo_ids || 0}</span></div>
          </div>
        </div>
        <div className="glass-card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>📋 Recent Exports</h3>
          {s.recent_exports && s.recent_exports.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {s.recent_exports.map((exp, i) => (
                <div key={i} style={{ ...rowStyle, fontSize: 13 }}>
                  <span>📄 {exp.filename}</span>
                  <span className="badge badge-success">{exp.rows} rows</span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#64748b', fontSize: 14 }}>No exports yet. Process files and export to see history.</p>
          )}
        </div>
      </div>
    </div>
  );
}

const rowStyle = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '8px 0', borderBottom: '1px solid rgba(51,65,85,0.5)',
  fontSize: 14, color: '#cbd5e1',
};
