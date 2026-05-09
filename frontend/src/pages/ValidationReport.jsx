import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { HiOutlineShieldCheck, HiOutlineExclamation, HiOutlineDownload, HiOutlineRefresh } from 'react-icons/hi';
import { runValidation, getValidationReport, getValidationSummary, exportValidationReport } from '../services/api';

export default function ValidationReport() {
  const [report, setReport] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState({ sheet: 'all', severity: 'all' });

  useEffect(() => { fetchReport(); }, []);

  const fetchReport = async () => {
    try {
      const [repRes, sumRes] = await Promise.all([getValidationReport(), getValidationSummary()]);
      setReport(repRes.data);
      setSummary(sumRes.data);
    } catch {}
  };

  const handleRunValidation = async () => {
    setLoading(true);
    try {
      const res = await runValidation('English,Assamese,Hindi');
      setReport(res.data);
      toast.success(`Validation complete: ${res.data.total_errors} issue(s) found`);
      const sumRes = await getValidationSummary();
      setSummary(sumRes.data);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Validation failed');
    } finally { setLoading(false); }
  };

  const handleExport = async () => {
    try {
      const res = await exportValidationReport();
      toast.success('Validation report exported');
      window.open(res.data.download_url, '_blank');
    } catch (e) {
      toast.error('Export failed');
    }
  };

  const errors = report?.errors || [];
  const filtered = errors.filter(e => {
    if (filter.sheet !== 'all' && e.sheet !== filter.sheet) return false;
    if (filter.severity !== 'all' && e.severity !== filter.severity) return false;
    return true;
  });

  const sheets = [...new Set(errors.map(e => e.sheet))];
  const critical = errors.filter(e => e.severity === 'critical').length;
  const warnings = errors.filter(e => e.severity === 'warning').length;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>Validation Report</h1>
            <p>SBA guardrail validation results</p>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-primary" onClick={handleRunValidation} disabled={loading}>
              <HiOutlineRefresh size={16} className={loading ? 'animate-spin' : ''} />
              {loading ? 'Validating...' : 'Run Validation'}
            </button>
            <button className="btn btn-secondary" onClick={handleExport}>
              <HiOutlineDownload size={16} /> Export Report
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        <div className="glass-card stat-card" style={{ padding: '18px 22px' }}>
          <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 6 }}>Status</p>
          <p style={{ fontSize: 22, fontWeight: 700, color: report?.is_valid ? '#10b981' : '#ef4444' }}>
            {report?.is_valid ? '✅ Valid' : '❌ Invalid'}
          </p>
        </div>
        <div className="glass-card stat-card" style={{ padding: '18px 22px' }}>
          <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 6 }}>Rules Checked</p>
          <p style={{ fontSize: 22, fontWeight: 700, color: '#6366f1' }}>{report?.total_rules_checked || 0}</p>
        </div>
        <div className="glass-card stat-card" style={{ padding: '18px 22px' }}>
          <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 6 }}>Critical Errors</p>
          <p style={{ fontSize: 22, fontWeight: 700, color: critical > 0 ? '#ef4444' : '#10b981' }}>{critical}</p>
        </div>
        <div className="glass-card stat-card" style={{ padding: '18px 22px' }}>
          <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 6 }}>Warnings</p>
          <p style={{ fontSize: 22, fontWeight: 700, color: warnings > 0 ? '#f59e0b' : '#10b981' }}>{warnings}</p>
        </div>
      </div>

      {/* Sheet Summary */}
      {summary?.sheets && Object.keys(summary.sheets).length > 0 && (
        <div className="card-section">
          <h2><HiOutlineShieldCheck /> Sheet Summary</h2>
          <div className="grid-3">
            {Object.entries(summary.sheets).map(([sheet, data]) => (
              <div key={sheet} className="glass-card" style={{ padding: 20 }}>
                <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>{sheet}</h4>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                  {data.critical > 0 && <span className="badge badge-danger">{data.critical} critical</span>}
                  {data.warning > 0 && <span className="badge badge-warning">{data.warning} warnings</span>}
                  {data.critical === 0 && data.warning === 0 && <span className="badge badge-success">All clear</span>}
                </div>
                {data.columns && (
                  <div style={{ marginTop: 10 }}>
                    {Object.entries(data.columns).slice(0, 5).map(([col, count]) => (
                      <div key={col} style={{ fontSize: 12, color: '#94a3b8', display: 'flex', justifyContent: 'space-between', padding: '3px 0' }}>
                        <span>{col}</span><span>{count}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="glass-card" style={{ padding: '12px 20px', marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center' }}>
        <span style={{ fontSize: 13, color: '#94a3b8', fontWeight: 600 }}>Filter:</span>
        <select value={filter.sheet} onChange={e => setFilter(p => ({ ...p, sheet: e.target.value }))} className="input-field" style={{ width: 200 }}>
          <option value="all">All Sheets</option>
          {sheets.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={filter.severity} onChange={e => setFilter(p => ({ ...p, severity: e.target.value }))} className="input-field" style={{ width: 150 }}>
          <option value="all">All Severity</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
        </select>
        <span style={{ fontSize: 13, color: '#64748b' }}>{filtered.length} error(s)</span>
      </div>

      {/* Error Table */}
      <div className="glass-card" style={{ overflow: 'auto', maxHeight: 500 }}>
        {filtered.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Sheet</th><th>Row</th><th>Column</th><th>Rule</th><th>Severity</th><th>Message</th><th>Value</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((e, i) => (
                <tr key={i}>
                  <td>{e.sheet}</td>
                  <td>{e.row}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{e.column}</td>
                  <td><span className="badge badge-info">{e.rule}</span></td>
                  <td>
                    <span className={`badge ${e.severity === 'critical' ? 'badge-danger' : 'badge-warning'}`}>
                      {e.severity}
                    </span>
                  </td>
                  <td style={{ maxWidth: 300 }}>{e.message}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: 12, color: '#f87171' }}>{e.current_value || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
            <HiOutlineShieldCheck size={48} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
            <p>{errors.length === 0 ? 'No validation has been run yet. Click "Run Validation" to start.' : 'No errors match the current filter.'}</p>
          </div>
        )}
      </div>
    </div>
  );
}
