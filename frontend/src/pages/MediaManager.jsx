import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import { HiOutlinePhotograph, HiOutlineTrash, HiOutlineRefresh, HiOutlineCheck, HiOutlineX } from 'react-icons/hi';
import { getMediaFiles, getMediaStats, deleteMediaFile, clearAllMedia, validateMediaPaths } from '../services/api';

export default function MediaManager() {
  const [files, setFiles] = useState({});
  const [stats, setStats] = useState({});
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [filesRes, statsRes] = await Promise.all([getMediaFiles(), getMediaStats()]);
      setFiles(filesRes.data.files || {});
      setStats(statsRes.data.stats || {});
    } catch {} finally { setLoading(false); }
  };

  const handleDelete = async (cat, name) => {
    try {
      await deleteMediaFile(cat, name);
      toast.success('File deleted');
      fetchData();
    } catch { toast.error('Delete failed'); }
  };

  const handleClearAll = async () => {
    if (!confirm('Clear all media files?')) return;
    try {
      await clearAllMedia();
      toast.success('All media cleared');
      fetchData();
    } catch { toast.error('Clear failed'); }
  };

  const handleValidate = async () => {
    try {
      const res = await validateMediaPaths();
      setValidation(res.data);
      toast.success(res.data.all_valid ? 'All paths valid!' : `${res.data.missing.length} missing path(s)`);
    } catch { toast.error('Validation failed'); }
  };

  const categories = [
    { key: 'images', label: 'Images', icon: '🖼️', color: '#6366f1' },
    { key: 'tables', label: 'Tables', icon: '📊', color: '#0ea5e9' },
    { key: 'audio', label: 'Audio', icon: '🔊', color: '#f59e0b' },
    { key: 'documents', label: 'Documents', icon: '📄', color: '#10b981' },
  ];

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1048576).toFixed(1)} MB`;
  };

  if (loading) return <div style={{ padding: 40, color: '#94a3b8' }}>Loading media files...</div>;

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1>Media Manager</h1>
            <p>Manage extracted images, tables, audio, and documents</p>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-primary btn-sm" onClick={handleValidate}>
              <HiOutlineCheck size={14} /> Validate Paths
            </button>
            <button className="btn btn-secondary btn-sm" onClick={fetchData}>
              <HiOutlineRefresh size={14} /> Refresh
            </button>
            <button className="btn btn-danger btn-sm" onClick={handleClearAll}>
              <HiOutlineTrash size={14} /> Clear All
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid-4" style={{ marginBottom: 24 }}>
        {categories.map(({ key, label, icon, color }) => (
          <div key={key} className="glass-card stat-card" style={{ padding: '18px 22px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ color: '#94a3b8', fontSize: 12 }}>{icon} {label}</p>
                <p style={{ fontSize: 24, fontWeight: 700, color, marginTop: 4 }}>{stats[key]?.count || 0}</p>
                <p style={{ fontSize: 11, color: '#64748b' }}>{formatSize(stats[key]?.total_size_bytes || 0)}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Validation Results */}
      {validation && (
        <div className={`glass-card`} style={{ padding: 20, marginBottom: 20, borderColor: validation.all_valid ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {validation.all_valid ? <HiOutlineCheck size={20} color="#10b981" /> : <HiOutlineX size={20} color="#ef4444" />}
            <div>
              <p style={{ fontWeight: 600, fontSize: 14 }}>
                {validation.all_valid ? 'All media paths are valid' : `${validation.missing.length} missing path(s)`}
              </p>
              <p style={{ fontSize: 12, color: '#94a3b8' }}>{validation.valid} / {validation.total_paths} paths verified</p>
            </div>
          </div>
          {validation.missing?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              {validation.missing.map((p, i) => (
                <div key={i} style={{ fontSize: 12, color: '#f87171', fontFamily: 'monospace', padding: '3px 0' }}>⚠ {p}</div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* File Lists */}
      {categories.map(({ key, label, icon }) => {
        const catFiles = files[key] || [];
        if (catFiles.length === 0) return null;
        return (
          <div key={key} className="card-section">
            <h2>{icon} {label} ({catFiles.length})</h2>
            <div className="glass-card" style={{ overflow: 'auto' }}>
              <table className="data-table">
                <thead><tr><th>Filename</th><th>Path</th><th>Size</th><th>Actions</th></tr></thead>
                <tbody>
                  {catFiles.map((f, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight: 500 }}>{f.name}</td>
                      <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{f.path}</td>
                      <td>{formatSize(f.size)}</td>
                      <td>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(key, f.name)}>
                          <HiOutlineTrash size={12} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}

      {Object.values(files).every(arr => arr.length === 0) && (
        <div className="glass-card" style={{ padding: 60, textAlign: 'center' }}>
          <HiOutlinePhotograph size={48} style={{ margin: '0 auto 12px', opacity: 0.3, color: '#64748b' }} />
          <p style={{ color: '#64748b' }}>No media files extracted yet. Upload and parse question papers to extract media.</p>
        </div>
      )}
    </div>
  );
}
