import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { login } from '../services/api';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const res = await login(data.username, data.password);
      localStorage.setItem('token', res.data.access_token);
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch {
      toast.error('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.wrapper}>
      <div style={styles.bgOrb1} />
      <div style={styles.bgOrb2} />
      <div style={styles.card} className="glass-card animate-fade-in">
        <div style={styles.logoBox}>
          <div style={styles.logoIcon}>D</div>
          <h1 style={styles.title}>Dumpsheet Creator</h1>
          <p style={styles.subtitle}>Academic Assessment Tool</p>
        </div>
        <form onSubmit={handleSubmit(onSubmit)} style={styles.form}>
          <div>
            <label style={styles.label}>Email Address</label>
            <input {...register('username', { required: 'Email is required' })}
              type="email" className="input-field" placeholder="Enter your email" autoFocus />
            {errors.username && <span style={styles.error}>{errors.username.message}</span>}
          </div>
          <div>
            <label style={styles.label}>Password</label>
            <input {...register('password', { required: 'Password is required' })}
              type="password" className="input-field" placeholder="Enter password" />
            {errors.password && <span style={styles.error}>{errors.password.message}</span>}
          </div>
          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}
            style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}

const styles = {
  wrapper: {
    minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
    background: '#0f172a', position: 'relative', overflow: 'hidden',
  },
  bgOrb1: {
    position: 'absolute', width: 400, height: 400, borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(99,102,241,0.15), transparent 70%)',
    top: '-10%', right: '-5%',
  },
  bgOrb2: {
    position: 'absolute', width: 300, height: 300, borderRadius: '50%',
    background: 'radial-gradient(circle, rgba(14,165,233,0.1), transparent 70%)',
    bottom: '-10%', left: '-5%',
  },
  card: { width: 420, padding: '48px 40px', zIndex: 1 },
  logoBox: { textAlign: 'center', marginBottom: 32 },
  logoIcon: {
    width: 64, height: 64, borderRadius: 16, margin: '0 auto 16px',
    background: 'linear-gradient(135deg, #6366f1, #818cf8)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    fontSize: 28, fontWeight: 800, color: 'white',
  },
  title: {
    fontSize: 32, fontWeight: 800,
    background: 'linear-gradient(135deg, #f1f5f9, #818cf8)',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
  },
  subtitle: { color: '#94a3b8', fontSize: 14, marginTop: 4 },
  form: { display: 'flex', flexDirection: 'column', gap: 20 },
  label: { display: 'block', fontSize: 13, fontWeight: 600, color: '#94a3b8', marginBottom: 6 },
  error: { color: '#f87171', fontSize: 12, marginTop: 4 },
};
