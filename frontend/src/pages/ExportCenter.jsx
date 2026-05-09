import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { HiOutlineDownload, HiOutlineDocumentText, HiOutlineArchive, HiOutlineRefresh, HiOutlineTrash } from 'react-icons/hi';
import { exportToExcel, getOutputFiles, getExportHistory, createMediaZip, createBundle, runValidation, clearExport } from '../services/api';

export default function ExportCenter() {
  const [outputFiles, setOutputFiles] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [exportConfig, setExportConfig] = useState({
    filename: 'dump_sheet.xlsx',
    languages: 'English',
    applyValidation: true,
  });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [filesRes, histRes] = await Promise.all([getOutputFiles(), getExportHistory()]);
      setOutputFiles(filesRes.data.files || []);
      setHistory(histRes.data.history || []);
    } catch {}
  };

  const handleExportExcel = async () => {
    setLoading(true);
    try {
      // Run validation first if enabled
      if (exportConfig.applyValidation) {
        try { await runValidation(exportConfig.languages); } catch {}
      }
      const res = await exportToExcel(exportConfig.filename, exportConfig.languages, exportConfig.applyValidation);
      toast.success('Excel exported successfully!');
      if (res.data.download_url) window.open(res.data.download_url, '_blank');
      fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Export failed');
    } finally { setLoading(false); }
  };

  const handleMediaZip = async () => {
    setLoading(true);
    try {
      const res = await createMediaZip();
      toast.success('Media ZIP created!');
      if (res.data.download_url) window.open(res.data.download_url, '_blank');
      fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'ZIP creation failed');
    } finally { setLoading(false); }
  };

  const handleBundle = async () => {
    setLoading(true);
    try {
      const res = await createBundle(true, true, true);
      toast.success('Export bundle created!');
      if (res.data.download_url) window.open(res.data.download_url, '_blank');
      fetchData();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Bundle creation failed');
    } finally { setLoading(false); }
  };

  const handleClear = async () => {
    if (!window.confirm('Are you sure you want to clear all available downloads? This cannot be undone.')) return;
    setLoading(true);
    try {
      await clearExport();
      toast.success('All files cleared');
      fetchData();
    } catch (e) {
      toast.error('Failed to clear files');
    } finally { setLoading(false); }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Export Center</h1>
        <p>Download dump sheets, media bundles, and validation reports</p>
      </div>

      <div className="grid-2">
        {/* Export Actions */}
        <div>
          {/* Excel Export Config */}
          <div className="glass-card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>📊 Export Dump Sheet</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={labelStyle}>Filename</label>
                <input className="input-field" value={exportConfig.filename}
                  onChange={e => setExportConfig(p => ({ ...p, filename: e.target.value }))} />
              </div>
              <div>
                <label style={labelStyle}>Languages</label>
                <input className="input-field" value={exportConfig.languages}
                  onChange={e => setExportConfig(p => ({ ...p, languages: e.target.value }))}
                  placeholder="English,Assamese,Hindi" />
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer', fontSize: 14, color: '#cbd5e1' }}>
                <input type="checkbox" checked={exportConfig.applyValidation}
                  onChange={e => setExportConfig(p => ({ ...p, applyValidation: e.target.checked }))}
                  style={{ accentColor: '#6366f1' }} />
                Apply validation highlighting
              </label>
              <button className="btn btn-primary" onClick={handleExportExcel} disabled={loading}
                style={{ width: '100%', justifyContent: 'center' }}>
                <HiOutlineDocumentText size={18} />
                {loading ? 'Exporting...' : 'Export Excel Workbook'}
              </button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="glass-card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>⚡ Quick Export</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button className="btn btn-secondary" onClick={handleMediaZip} disabled={loading}
                style={{ width: '100%', justifyContent: 'center' }}>
                <HiOutlineArchive size={16} /> Download Media ZIP
              </button>
              <button className="btn btn-success" onClick={handleBundle} disabled={loading}
                style={{ width: '100%', justifyContent: 'center' }}>
                <HiOutlineDownload size={16} /> Download Full Bundle
              </button>
              <p style={{ fontSize: 12, color: '#64748b', textAlign: 'center' }}>
                Bundle includes: dump sheet + media + validation report
              </p>
            </div>
          </div>
        </div>

        {/* Files + History */}
        <div>
          {/* Available Files */}
          <div className="glass-card" style={{ padding: 24, marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600 }}>📁 Available Downloads</h3>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn btn-secondary btn-sm" onClick={fetchData} title="Refresh List">
                  <HiOutlineRefresh size={14} />
                </button>
                <button className="btn btn-danger btn-sm" onClick={handleClear} disabled={loading} title="Clear All Files">
                  <HiOutlineTrash size={14} />
                </button>
              </div>
            </div>
            {outputFiles.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {outputFiles.map((f, i) => (
                  <div key={i} style={fileRow}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <HiOutlineDocumentText size={18} color="#818cf8" />
                      <div>
                        <p style={{ fontSize: 14, fontWeight: 500 }}>{f.name}</p>
                        <p style={{ fontSize: 11, color: '#64748b' }}>{formatSize(f.size)} • {new Date(f.modified).toLocaleString()}</p>
                      </div>
                    </div>
                    <a href={`/api/export/download/${f.name}`} target="_blank" rel="noreferrer"
                      className="btn btn-primary btn-sm">
                      <HiOutlineDownload size={14} />
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#64748b', fontSize: 14 }}>No files available. Generate and export first.</p>
            )}
          </div>

          {/* Export History */}
          <div className="glass-card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>📋 Export History</h3>
            {history.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {history.map((h, i) => (
                  <div key={i} style={fileRow}>
                    <div>
                      <p style={{ fontSize: 13, fontWeight: 500 }}>{h.filename}</p>
                      <p style={{ fontSize: 11, color: '#64748b' }}>{h.timestamp}</p>
                    </div>
                    <span className="badge badge-success">{h.rows} rows</span>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: '#64748b', fontSize: 14 }}>No exports yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const labelStyle = { display: 'block', fontSize: 12, fontWeight: 600, color: '#94a3b8', marginBottom: 4 };
const fileRow = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '12px 14px', background: 'rgba(30,41,59,0.4)', borderRadius: 8,
  border: '1px solid rgba(51,65,85,0.4)',
};
