import { NavLink, useNavigate } from 'react-router-dom';
import { HiOutlineViewGrid, HiOutlineCloudUpload, HiOutlineShieldCheck, HiOutlinePhotograph, HiOutlineDownload, HiOutlineLogout } from 'react-icons/hi';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: HiOutlineViewGrid },
  { path: '/upload', label: 'Upload Center', icon: HiOutlineCloudUpload },
  { path: '/validation', label: 'Validation', icon: HiOutlineShieldCheck },
  { path: '/media', label: 'Media Manager', icon: HiOutlinePhotograph },
  { path: '/export', label: 'Export Center', icon: HiOutlineDownload },
];

export default function Sidebar({ isOpen, onToggle }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : 'collapsed'}`}>
      <div className="sidebar-header" onClick={onToggle}>
        <div className="sidebar-logo">
          <div className="logo-icon">D</div>
          {isOpen && <span className="logo-text">Dumpsheet Creator</span>}
        </div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(({ path, label, icon: Icon }) => (
          <NavLink key={path} to={path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <Icon size={20} />
            {isOpen && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <button className="nav-item logout-btn" onClick={handleLogout}>
          <HiOutlineLogout size={20} />
          {isOpen && <span>Logout</span>}
        </button>
      </div>
      <style>{`
        .sidebar {
          position: fixed; top: 0; left: 0; height: 100vh;
          background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
          border-right: 1px solid rgba(99,102,241,0.1);
          display: flex; flex-direction: column;
          transition: width 0.3s ease;
          z-index: 50;
        }
        .sidebar.open { width: 260px; }
        .sidebar.collapsed { width: 72px; }
        .sidebar-header {
          padding: 20px 16px; cursor: pointer;
          border-bottom: 1px solid rgba(99,102,241,0.1);
          display: flex; align-items: center;
        }
        .sidebar-logo { display: flex; align-items: center; gap: 12px; }
        .logo-icon {
          width: 40px; height: 40px;
          background: linear-gradient(135deg, #6366f1, #818cf8);
          border-radius: 10px;
          display: flex; align-items: center; justify-content: center;
          font-weight: 800; font-size: 18px; color: white;
          flex-shrink: 0;
        }
        .logo-text {
          font-size: 20px; font-weight: 800;
          background: linear-gradient(135deg, #f1f5f9, #6366f1);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
          background-clip: text; white-space: nowrap;
        }
        .sidebar-nav { flex: 1; padding: 12px 8px; display: flex; flex-direction: column; gap: 4px; }
        .nav-item {
          display: flex; align-items: center; gap: 12px;
          padding: 12px 16px; border-radius: 10px;
          color: #94a3b8; text-decoration: none;
          font-size: 14px; font-weight: 500;
          transition: all 0.2s ease; border: none;
          background: none; cursor: pointer; width: 100%;
          text-align: left;
        }
        .nav-item:hover { background: rgba(99,102,241,0.08); color: #f1f5f9; }
        .nav-item.active {
          background: linear-gradient(135deg, rgba(99,102,241,0.15), rgba(99,102,241,0.05));
          color: #818cf8; font-weight: 600;
          border-left: 3px solid #6366f1;
        }
        .sidebar-footer { padding: 12px 8px; border-top: 1px solid rgba(99,102,241,0.1); }
        .logout-btn:hover { background: rgba(239,68,68,0.1); color: #f87171; }
        .sidebar.collapsed .nav-item span { display: none; }
        .sidebar.collapsed .nav-item { justify-content: center; padding: 12px; }
      `}</style>
    </aside>
  );
}
