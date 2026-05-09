import { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { HiOutlineCloudUpload, HiOutlineDocumentText, HiOutlineTrash, HiOutlineCog,
         HiOutlineCheck, HiOutlineX, HiOutlineChevronDown, HiOutlineChevronUp } from 'react-icons/hi';
import { uploadFiles, getUploadedFiles, deleteUploadedFile, clearAllUploads,
         parseQuestionPaper, parseLOMapping, resolveMappings, generateDumpSheet } from '../services/api';

const MEDIUMS = ['Assamese', 'Bengali', 'Bodo', 'English', 'Hindi', 'Karbi'];
const LO_SUBJECTS = ['Language 1', 'Language 2 (English)', 'Mathematics', 'EVS (The World Around Us)'];

export default function UploadCenter() {
  const [qpFiles, setQpFiles] = useState([]);
  const [loFiles, setLoFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [parseResults, setParseResults] = useState(null);
  const [step, setStep] = useState(1);
  const [expandedResults, setExpandedResults] = useState({});

  const { register, watch } = useForm({
    defaultValues: {
      qp_medium: 'Auto-Detect', qp_class: '',
      lo_subject: 'Auto-Detect', lo_class: '',
      academic_year: '2025-26', assessment_type: 'PAT',
      launch_date: '2025-06-01', close_date: '2025-06-30',
    }
  });
  const formValues = watch();

  useEffect(() => { refreshFiles(); }, []);

  // ─── Question Paper Dropzone ──────────────────────────
  const onDropQP = useCallback((accepted) => {
    setQpFiles(prev => [...prev, ...accepted.map(f => ({ file: f }))]);
  }, []);
  const qpDropzone = useDropzone({
    onDrop: onDropQP, multiple: true,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'] },
  });

  // ─── LO Mapping Dropzone ─────────────────────────────
  const onDropLO = useCallback((accepted) => {
    setLoFiles(prev => [...prev, ...accepted.map(f => ({ file: f }))]);
  }, []);
  const loDropzone = useDropzone({
    onDrop: onDropLO, multiple: true,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'], 'application/vnd.ms-excel': ['.xls'] },
  });

  // ─── Upload Handlers ─────────────────────────────────
  const handleUploadQP = async () => {
    if (!qpFiles.length) return toast.error('No question paper files selected');
    setUploading(true);
    try {
      const res = await uploadFiles(qpFiles.map(f => f.file), {
        medium: formValues.qp_medium === 'Auto-Detect' ? '' : formValues.qp_medium,
        classLevel: formValues.qp_class || '0',
        subject: '',
        uploadType: 'question_paper',
      });
      if (res.data.total_uploaded > 0) {
        toast.success(`Uploaded ${res.data.total_uploaded} question paper(s)`);
        setQpFiles([]);
        await refreshFiles();
        if (step < 2) setStep(2);
      } else {
        toast.error(res.data.results?.[0]?.error || 'Upload failed');
      }
    } catch (e) { toast.error(e.response?.data?.detail || 'Upload failed'); }
    finally { setUploading(false); }
  };

  const handleUploadLO = async () => {
    if (!loFiles.length) return toast.error('No LO mapping files selected');
    setUploading(true);
    try {
      const res = await uploadFiles(loFiles.map(f => f.file), {
        medium: '',
        classLevel: formValues.lo_class || '0',
        subject: formValues.lo_subject === 'Auto-Detect' ? '' : formValues.lo_subject,
        uploadType: 'lo_mapping',
      });
      if (res.data.total_uploaded > 0) {
        toast.success(`Uploaded ${res.data.total_uploaded} LO mapping(s)`);
        setLoFiles([]);
        await refreshFiles();
        if (step < 2) setStep(2);
      } else {
        toast.error(res.data.results?.[0]?.error || 'Upload failed');
      }
    } catch (e) { toast.error(e.response?.data?.detail || 'Upload failed'); }
    finally { setUploading(false); }
  };

  const refreshFiles = async () => {
    try { const res = await getUploadedFiles(); setUploadedFiles(res.data.files || []); } catch {}
  };

  // ─── Parse ────────────────────────────────────────────
  const handleParse = async () => {
    setProcessing(true);
    try {
      const qFiles = uploadedFiles.filter(f => f.file_type === 'question_paper');
      const loFilesList = uploadedFiles.filter(f => f.file_type === 'lo_mapping');
      let allQResults = [], allLOResults = [];

      for (const f of qFiles) {
        const res = await parseQuestionPaper(f.file_id, f.medium || '', f.class_level || 0);
        allQResults.push(res.data);
      }
      for (const f of loFilesList) {
        const res = await parseLOMapping(f.file_id, f.subject || '', f.class_level || 0);
        allLOResults.push(res.data);
      }

      setParseResults({ questions: allQResults, lo: allLOResults });
      toast.success('Parsing complete!');
      setStep(3);
    } catch (e) { toast.error(e.response?.data?.detail || 'Parsing failed'); }
    finally { setProcessing(false); }
  };

  const handleResolve = async () => {
    setProcessing(true);
    try {
      const res = await resolveMappings(formValues.qp_medium || '');
      setParseResults(prev => ({ ...prev, merged: res.data }));
      toast.success(`Resolved ${res.data.total_merged} mappings (${res.data.match_rate?.toFixed(1)}%)`);
      setStep(4);
    } catch (e) { toast.error(e.response?.data?.detail || 'Resolve failed'); }
    finally { setProcessing(false); }
  };

  const handleGenerate = async () => {
    setProcessing(true);
    try {
      const res = await generateDumpSheet({
        project_name: 'Assessment Project',
        subjects: 'auto', classes: formValues.qp_class,
        mediums: formValues.qp_medium, academic_year: formValues.academic_year,
        assessment_type: formValues.assessment_type,
        launch_date: formValues.launch_date, close_date: formValues.close_date,
      });
      toast.success('Dump sheet generated!');
      setParseResults(prev => ({ ...prev, generated: res.data }));
    } catch (e) { toast.error(e.response?.data?.detail || 'Generation failed'); }
    finally { setProcessing(false); }
  };

  const handleClearAll = async () => {
    try { await clearAllUploads(); setUploadedFiles([]); setParseResults(null); setStep(1); toast.success('Cleared'); } catch {}
  };

  const toggleResult = (key) => setExpandedResults(prev => ({ ...prev, [key]: !prev[key] }));

  const steps = [
    { num: 1, label: 'Upload Files' }, { num: 2, label: 'Parse Content' },
    { num: 3, label: 'Resolve Mappings' }, { num: 4, label: 'Generate Sheet' },
  ];

  const qpUploaded = uploadedFiles.filter(f => f.file_type === 'question_paper');
  const loUploaded = uploadedFiles.filter(f => f.file_type === 'lo_mapping');

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h1>Upload Center</h1>
        <p>Upload question papers (per medium + class) and LO mappings (per subject + class)</p>
      </div>

      {/* Step Indicator */}
      <div className="glass-card" style={{ padding: '16px 24px', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          {steps.map(({ num, label }, i) => (
            <div key={num} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '6px 16px',
                borderRadius: 20, fontSize: 13, fontWeight: 600,
                background: step >= num ? 'rgba(99,102,241,0.15)' : 'rgba(51,65,85,0.3)',
                color: step >= num ? '#818cf8' : '#64748b',
                border: step === num ? '1px solid rgba(99,102,241,0.3)' : '1px solid transparent',
              }}>
                {step > num ? <HiOutlineCheck size={14} /> : num}. {label}
              </div>
              {i < steps.length - 1 && <span style={{ color: '#334155' }}>→</span>}
            </div>
          ))}
        </div>
      </div>

      <div className="grid-2">
        {/* ═══════ Left Column: Upload Sections ═══════ */}
        <div>
          {/* ── Question Paper Upload ── */}
          <div className="glass-card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>📄 Question Papers</h3>
            <p style={{ fontSize: 12, color: '#64748b', marginBottom: 16 }}>
              One PDF per medium + class. Subjects are auto-detected from Q-number ranges.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
              <div>
                <label style={labelStyle}>Medium (Fallback)</label>
                <select {...register('qp_medium')} className="input-field">
                  <option>Auto-Detect</option>
                  {MEDIUMS.map(m => <option key={m}>{m}</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Class (Fallback)</label>
                <input {...register('qp_class')} className="input-field" type="number" min="1" max="12" placeholder="Auto" />
              </div>
            </div>

            <div className={`dropzone ${qpDropzone.isDragActive ? 'active' : ''}`} {...qpDropzone.getRootProps()}
              style={{ padding: '20px 16px', minHeight: 80 }}>
              <input {...qpDropzone.getInputProps()} />
              <HiOutlineCloudUpload size={28} color="#6366f1" style={{ marginBottom: 4 }} />
              <p style={{ fontSize: 13, fontWeight: 600, margin: 0 }}>
                {qpDropzone.isDragActive ? 'Drop here...' : 'Drop question paper PDFs'}
              </p>
              <p style={{ color: '#64748b', fontSize: 11, margin: 0 }}>PDF or DOCX</p>
            </div>

            {qpFiles.length > 0 && (
              <div style={{ marginTop: 10 }}>
                {qpFiles.map(({ file }, i) => (
                  <div key={i} style={fileRowStyle}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
                      <HiOutlineDocumentText size={16} color="#818cf8" />
                      <span style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{file.name}</span>
                      <span style={{ fontSize: 10, color: '#64748b' }}>({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button onClick={() => setQpFiles(prev => prev.filter((_, idx) => idx !== i))}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#f87171' }}>
                      <HiOutlineX size={14} />
                    </button>
                  </div>
                ))}
                <button className="btn btn-primary" style={{ marginTop: 8, width: '100%', justifyContent: 'center' }}
                  onClick={handleUploadQP} disabled={uploading}>
                  {uploading ? 'Uploading...' : `Upload ${qpFiles.length} Question Paper(s)`}
                </button>
              </div>
            )}
          </div>

          {/* ── LO Mapping Upload ── */}
          <div className="glass-card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>📊 LO Mappings</h3>
            <p style={{ fontSize: 12, color: '#64748b', marginBottom: 16 }}>
              One PDF/DOCX per subject. Multiple classes supported. Subject & class auto-detected.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
              <div>
                <label style={labelStyle}>Subject (Fallback)</label>
                <select {...register('lo_subject')} className="input-field">
                  <option>Auto-Detect</option>
                  {LO_SUBJECTS.map(s => <option key={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label style={labelStyle}>Class (Fallback)</label>
                <input {...register('lo_class')} className="input-field" type="number" min="1" max="12" placeholder="Auto" />
              </div>
            </div>

            <div className={`dropzone ${loDropzone.isDragActive ? 'active' : ''}`} {...loDropzone.getRootProps()}
              style={{ padding: '20px 16px', minHeight: 80 }}>
              <input {...loDropzone.getInputProps()} />
              <HiOutlineCloudUpload size={28} color="#0ea5e9" style={{ marginBottom: 4 }} />
              <p style={{ fontSize: 13, fontWeight: 600, margin: 0 }}>
                {loDropzone.isDragActive ? 'Drop here...' : 'Drop LO mapping files'}
              </p>
              <p style={{ color: '#64748b', fontSize: 11, margin: 0 }}>PDF, DOCX, or Excel</p>
            </div>

            {loFiles.length > 0 && (
              <div style={{ marginTop: 10 }}>
                {loFiles.map(({ file }, i) => (
                  <div key={i} style={fileRowStyle}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1, minWidth: 0 }}>
                      <HiOutlineDocumentText size={16} color="#38bdf8" />
                      <span style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{file.name}</span>
                      <span style={{ fontSize: 10, color: '#64748b' }}>({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button onClick={() => setLoFiles(prev => prev.filter((_, idx) => idx !== i))}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#f87171' }}>
                      <HiOutlineX size={14} />
                    </button>
                  </div>
                ))}
                <button className="btn btn-primary" style={{ marginTop: 8, width: '100%', justifyContent: 'center',
                  background: 'linear-gradient(135deg, #0ea5e9, #0284c7)' }}
                  onClick={handleUploadLO} disabled={uploading}>
                  {uploading ? 'Uploading...' : `Upload ${loFiles.length} LO Mapping(s)`}
                </button>
              </div>
            )}
          </div>

          {/* ── Project Config ── */}
          <div className="glass-card" style={{ padding: 24 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>⚙️ Project Config</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={labelStyle}>Assessment Type</label>
                <select {...register('assessment_type')} className="input-field">
                  <option>PAT</option><option>SBA</option><option>NIPUN</option>
                </select>
              </div>
              <div>
                <label style={labelStyle}>Academic Year</label>
                <input {...register('academic_year')} className="input-field" />
              </div>
              <div>
                <label style={labelStyle}>Launch Date</label>
                <input {...register('launch_date')} className="input-field" type="date" />
              </div>
              <div>
                <label style={labelStyle}>Close Date</label>
                <input {...register('close_date')} className="input-field" type="date" />
              </div>
            </div>
          </div>
        </div>

        {/* ═══════ Right Column: Actions + Results ═══════ */}
        <div>
          {/* Pipeline Actions */}
          <div className="glass-card" style={{ padding: 24, marginBottom: 20 }}>
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>🚀 Processing Pipeline</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button className="btn btn-primary" onClick={handleParse}
                disabled={processing || uploadedFiles.length === 0}
                style={{ width: '100%', justifyContent: 'center' }}>
                <HiOutlineCog size={18} /> {processing ? 'Processing...' : '2. Parse All Uploaded Files'}
              </button>
              <button className="btn btn-success" onClick={handleResolve}
                disabled={processing || step < 3}
                style={{ width: '100%', justifyContent: 'center' }}>
                <HiOutlineCheck size={18} /> 3. Resolve Mappings (Q ↔ LO)
              </button>
              <button className="btn btn-primary" onClick={handleGenerate}
                disabled={processing || step < 4}
                style={{ width: '100%', justifyContent: 'center', background: 'linear-gradient(135deg, #8b5cf6, #6d28d9)' }}>
                <HiOutlineDocumentText size={18} /> 4. Generate Dump Sheet
              </button>
            </div>
          </div>

          {/* Parse Results */}
          {parseResults && (
            <div className="glass-card" style={{ padding: 24, marginBottom: 20 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>📊 Results</h3>

              {/* Question Paper Results */}
              {parseResults.questions?.map((qr, i) => (
                <div key={`qr-${i}`} style={{ marginBottom: 12 }}>
                  <div onClick={() => toggleResult(`qr-${i}`)} style={{ ...resultBlock, cursor: 'pointer' }}>
                    <span>📄 Q.Paper — Class {qr.detected_class} {qr.detected_medium}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="badge badge-success">{qr.total_questions} Qs</span>
                      {expandedResults[`qr-${i}`] ? <HiOutlineChevronUp size={14}/> : <HiOutlineChevronDown size={14}/>}
                    </div>
                  </div>
                  {expandedResults[`qr-${i}`] && qr.subject_breakdown && (
                    <div style={{ paddingLeft: 16, marginTop: 4 }}>
                      {Object.entries(qr.subject_breakdown).map(([subj, info]) => (
                        <div key={subj} style={{ ...resultBlock, fontSize: 12, padding: '4px 0' }}>
                          <span style={{ color: '#94a3b8' }}>{subj}</span>
                          <span className="badge badge-info" style={{ fontSize: 10 }}>{info.count} Qs</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {/* LO Results */}
              {parseResults.lo?.map((lr, i) => (
                <div key={`lr-${i}`} style={{ marginBottom: 12 }}>
                  <div onClick={() => toggleResult(`lr-${i}`)} style={{ ...resultBlock, cursor: 'pointer' }}>
                    <span>📊 LO — {lr.detected_subject} {lr.detected_class !== 0 ? `(Class ${lr.detected_class} etc)` : ''}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span className="badge badge-info">{lr.total_mappings} LOs</span>
                      {expandedResults[`lr-${i}`] ? <HiOutlineChevronUp size={14}/> : <HiOutlineChevronDown size={14}/>}
                    </div>
                  </div>
                  {expandedResults[`lr-${i}`] && lr.lo_summary && (
                    <div style={{ paddingLeft: 16, marginTop: 4 }}>
                      {Object.entries(lr.lo_summary).map(([key, count]) => (
                        <div key={key} style={{ ...resultBlock, fontSize: 12, padding: '4px 0' }}>
                          <span style={{ color: '#94a3b8' }}>{key}</span>
                          <span className="badge badge-info" style={{ fontSize: 10 }}>{count} LOs</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {/* Merged Results */}
              {parseResults.merged && (
                <>
                  <div style={{ borderTop: '1px solid #334155', margin: '12px 0' }} />
                  <div style={resultBlock}>
                    <span>✅ Merged Records</span>
                    <span className="badge badge-success">{parseResults.merged.total_merged}</span>
                  </div>
                  <div style={resultBlock}>
                    <span>Match Rate</span>
                    <span className="badge badge-info">{parseResults.merged.match_rate?.toFixed(1)}%</span>
                  </div>
                  {parseResults.merged.subject_breakdown && (
                    <div style={{ marginTop: 8 }}>
                      <p style={{ fontSize: 11, color: '#64748b', fontWeight: 600, marginBottom: 4 }}>Per Subject:</p>
                      {Object.entries(parseResults.merged.subject_breakdown).map(([subj, info]) => (
                        <div key={subj} style={{ ...resultBlock, fontSize: 12, padding: '4px 0' }}>
                          <span style={{ color: '#94a3b8' }}>{subj}</span>
                          <span>{info.total} merged</span>
                        </div>
                      ))}
                    </div>
                  )}
                  {parseResults.merged.unmatched_questions?.length > 0 && (
                    <div style={resultBlock}>
                      <span>Unmatched Qs</span>
                      <span className="badge badge-danger">{parseResults.merged.unmatched_questions.length}</span>
                    </div>
                  )}
                </>
              )}

              {/* Generated */}
              {parseResults.generated && (
                <>
                  <div style={{ borderTop: '1px solid #334155', margin: '12px 0', paddingTop: 12 }}>
                    <p style={{ fontSize: 13, color: '#10b981', fontWeight: 600 }}>✅ Dump Sheet Generated</p>
                  </div>
                  <div style={resultBlock}><span>Topic Master</span><span>{parseResults.generated.topic_master_rows}</span></div>
                  <div style={resultBlock}><span>Assessment Master</span><span>{parseResults.generated.assessment_master_rows}</span></div>
                  <div style={resultBlock}><span>Question Master</span><span>{parseResults.generated.question_master_rows}</span></div>
                </>
              )}
            </div>
          )}

          {/* Uploaded Files List */}
          <div className="glass-card" style={{ padding: 24 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ fontSize: 15, fontWeight: 600 }}>📁 Uploaded Files ({uploadedFiles.length})</h3>
              {uploadedFiles.length > 0 && (
                <button className="btn btn-danger btn-sm" onClick={handleClearAll}>
                  <HiOutlineTrash size={12} /> Clear All
                </button>
              )}
            </div>

            {/* Question Papers */}
            {qpUploaded.length > 0 && (
              <div style={{ marginBottom: 12 }}>
                <p style={{ fontSize: 11, fontWeight: 700, color: '#818cf8', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>
                  Question Papers
                </p>
                {qpUploaded.map((f, i) => (
                  <div key={`qp-${i}`} style={fileRowStyle}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {f.original_name}
                        </span>
                        <span className={`badge ${f.status === 'parsed' ? 'badge-success' : 'badge-pending'}`}>{f.status}</span>
                      </div>
                      <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>
                        Medium: {f.medium || 'Auto'} • Class: {f.class_level || 'Auto'}
                      </div>
                    </div>
                    <button onClick={async () => { await deleteUploadedFile(f.file_id); refreshFiles(); }}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#f87171' }}>
                      <HiOutlineTrash size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* LO Mappings */}
            {loUploaded.length > 0 && (
              <div>
                <p style={{ fontSize: 11, fontWeight: 700, color: '#38bdf8', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 1 }}>
                  LO Mappings
                </p>
                {loUploaded.map((f, i) => (
                  <div key={`lo-${i}`} style={fileRowStyle}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {f.original_name}
                        </span>
                        <span className={`badge ${f.status === 'parsed' ? 'badge-success' : 'badge-pending'}`}>{f.status}</span>
                      </div>
                      <div style={{ fontSize: 10, color: '#64748b', marginTop: 2 }}>
                        Subject: {f.subject || 'Auto'} • Class: {f.class_level || 'Auto'}
                      </div>
                    </div>
                    <button onClick={async () => { await deleteUploadedFile(f.file_id); refreshFiles(); }}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#f87171' }}>
                      <HiOutlineTrash size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {uploadedFiles.length === 0 && (
              <p style={{ color: '#64748b', fontSize: 13 }}>No files uploaded yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const labelStyle = { display: 'block', fontSize: 12, fontWeight: 600, color: '#94a3b8', marginBottom: 4 };
const fileRowStyle = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '10px 14px', background: 'rgba(30,41,59,0.5)', borderRadius: 8,
  marginBottom: 6, border: '1px solid rgba(51,65,85,0.5)',
};
const resultBlock = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  padding: '8px 0', borderBottom: '1px solid rgba(51,65,85,0.3)',
  fontSize: 14, color: '#cbd5e1',
};
