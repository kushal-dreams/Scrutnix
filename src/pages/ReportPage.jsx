import { useState } from 'react';
import { api } from '../services/api';
import '../styles/report.css';

const REPORT_TYPES = [
  { value: 'sms', label: 'SMS Message', icon: '', desc: 'Report a suspicious text message' },
  { value: 'whatsapp', label: 'WhatsApp Message', icon: '', desc: 'Report a WhatsApp scam' },
  { value: 'email', label: 'Email / Job Offer', icon: '', desc: 'Report a fraudulent email or job offer' },
];

const CATEGORIES = [
  { value: 'job_fraud', label: 'Job Fraud' },
  { value: 'spam', label: 'Spam' },
  { value: 'phishing', label: 'Phishing' },
  { value: 'harassment', label: 'Harassment' },
  { value: 'other', label: 'Other' },
];

export function ReportPage({ user, refresh, notify, setView }) {
  const [step, setStep] = useState(1);
  const [reportType, setReportType] = useState('');
  const [loading, setLoading] = useState(false);

  const [form, setForm] = useState({
    phone_number: '',
    email_id: '',
    message_description: '',
    job_description: '',
    category: '',
    additional_notes: '',
  });
  const [proofFiles, setProofFiles] = useState([]);
  const [errors, setErrors] = useState({});

  const updateForm = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }));
    setErrors(prev => ({ ...prev, [field]: '' }));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files).slice(0, 5);
    setProofFiles(files);
  };

  const validate = () => {
    const errs = {};
    if (!form.category) errs.category = 'Category is required';
    if (!form.message_description || form.message_description.trim().length < 20) {
      errs.message_description = 'Description must be at least 20 characters';
    }

    if (reportType === 'whatsapp' && !form.phone_number) {
      errs.phone_number = 'Phone number is required for WhatsApp reports';
    }
    if (reportType === 'email') {
      if (!form.email_id) errs.email_id = 'Sender email is required';
      if (!form.job_description) errs.job_description = 'Job description is required for email reports';
    }

    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async () => {
    if (!user) {
      notify('Please login before submitting a report');
      return;
    }
    if (!validate()) return;
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('report_type', reportType);
      formData.append('category', form.category);
      formData.append('message_description', form.message_description);

      if (form.phone_number) formData.append('phone_number', form.phone_number);
      if (form.email_id) formData.append('email_id', form.email_id);
      if (form.job_description) formData.append('job_description', form.job_description);
      if (form.additional_notes) formData.append('additional_notes', form.additional_notes);

      proofFiles.forEach(file => {
        formData.append('proof_images', file);
      });

      await api('/reports', { method: 'POST', body: formData });
      await refresh();
      notify('Report submitted. Thank you for helping the community.');
      setView('community');
    } catch (err) {
      notify(err.message || 'Failed to submit report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="report-page">
      <div className="report-wrapper container">
        <div className="report-header">
          <h1>Submit a Report</h1>
          <p>Help the community by reporting suspicious contacts</p>
        </div>

        <div className="progress-bar">
          <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
            <span className="step-dot">1</span>
            <span className="step-label">Type</span>
          </div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
            <span className="step-dot">2</span>
            <span className="step-label">Details</span>
          </div>
          <div className="progress-line"></div>
          <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
            <span className="step-dot">3</span>
            <span className="step-label">Review</span>
          </div>
        </div>

        {step === 1 && (
          <div className="step-content animate-fade-in">
            <h3>What type of report?</h3>
            <div className="type-cards">
              {REPORT_TYPES.map(t => (
                <button
                  key={t.value}
                  className={`type-card ${reportType === t.value ? 'selected' : ''}`}
                  onClick={() => setReportType(t.value)}
                >
                  <span className="type-icon">{t.icon}</span>
                  <span className="type-label">{t.label}</span>
                  <span className="type-desc">{t.desc}</span>
                </button>
              ))}
            </div>
            <button
              className="btn btn-primary btn-lg mt-6"
              disabled={!reportType}
              onClick={() => setStep(2)}
            >
              Continue 
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="step-content animate-fade-in">
            <h3>Report Details</h3>
            <div className="report-form">
              {(reportType === 'sms' || reportType === 'whatsapp') && (
                <div className="form-group">
                  <label className="form-label">
                    Phone Number {reportType === 'whatsapp' ? '(Required)' : '(Optional)'}
                  </label>
                  <input
                    type="tel"
                    className={`form-input ${errors.phone_number ? 'error' : ''}`}
                    placeholder="9876543210"
                    value={form.phone_number}
                    onChange={(e) => updateForm('phone_number', e.target.value.replace(/\D/g, '').slice(0, 10))}
                  />
                  {errors.phone_number && <span className="form-error">{errors.phone_number}</span>}
                </div>
              )}

              {(reportType === 'email' || reportType === 'whatsapp') && (
                <div className="form-group">
                  <label className="form-label">
                    {reportType === 'email' ? 'Sender Email (Required)' : 'Email (if mentioned)'}
                  </label>
                  <input
                    type="email"
                    className={`form-input ${errors.email_id ? 'error' : ''}`}
                    placeholder="scammer@example.com"
                    value={form.email_id}
                    onChange={(e) => updateForm('email_id', e.target.value)}
                  />
                  {errors.email_id && <span className="form-error">{errors.email_id}</span>}
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Category (Required)</label>
                <select
                  className={`form-input ${errors.category ? 'error' : ''}`}
                  value={form.category}
                  onChange={(e) => updateForm('category', e.target.value)}
                >
                  <option value="">Select category...</option>
                  {CATEGORIES.map(c => (
                    <option key={c.value} value={c.value}>{c.label}</option>
                  ))}
                </select>
                {errors.category && <span className="form-error">{errors.category}</span>}
              </div>

              <div className="form-group">
                <label className="form-label">Message Description (Required)</label>
                <textarea
                  className={`form-input ${errors.message_description ? 'error' : ''}`}
                  placeholder="Describe the scam message in detail..."
                  value={form.message_description}
                  onChange={(e) => updateForm('message_description', e.target.value)}
                  rows={5}
                />
                <span className="text-muted" style={{fontSize:'0.75rem'}}>
                  {form.message_description.length} characters
                </span>
                {errors.message_description && <span className="form-error">{errors.message_description}</span>}
              </div>

              {(form.category === 'job_fraud' || reportType === 'email') && (
                <div className="form-group">
                  <label className="form-label">
                    Job Description {reportType === 'email' ? '(Required)' : '(Optional  helps our analyzer)'}
                  </label>
                  <textarea
                    className={`form-input ${errors.job_description ? 'error' : ''}`}
                    placeholder="Paste the job offer text here..."
                    value={form.job_description}
                    onChange={(e) => updateForm('job_description', e.target.value)}
                    rows={4}
                  />
                  {errors.job_description && <span className="form-error">{errors.job_description}</span>}
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Proof Screenshots (Optional, up to 5)</label>
                <div className="upload-zone">
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleFileChange}
                    className="upload-input"
                    id="proof-upload"
                  />
                  <label htmlFor="proof-upload" className="upload-label">
                    <span></span>
                    <span>{proofFiles.length > 0 ? `${proofFiles.length} file(s) selected` : 'Click or drag to upload'}</span>
                  </label>
                </div>
                {proofFiles.length > 0 && (
                  <div className="upload-previews">
                    {proofFiles.map((f, i) => (
                      <div key={i} className="preview-item">
                        <img src={URL.createObjectURL(f)} alt={`Preview ${i}`} />
                        <span>{f.name}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Additional Notes (Optional)</label>
                <textarea
                  className="form-input"
                  placeholder="Any extra context..."
                  value={form.additional_notes}
                  onChange={(e) => updateForm('additional_notes', e.target.value)}
                  rows={2}
                />
              </div>

              <div className="step-actions">
                <button className="btn btn-ghost" onClick={() => setStep(1)}> Back</button>
                <button className="btn btn-primary" onClick={() => { if (validate()) setStep(3); }}>
                  Review 
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="step-content animate-fade-in">
            <h3>Review Your Report</h3>
            <div className="review-card card">
              <div className="review-row">
                <span className="review-label">Type:</span>
                <span>{REPORT_TYPES.find(t => t.value === reportType)?.label}</span>
              </div>
              {form.phone_number && (
                <div className="review-row">
                  <span className="review-label">Phone:</span>
                  <span className="font-mono">{form.phone_number}</span>
                </div>
              )}
              {form.email_id && (
                <div className="review-row">
                  <span className="review-label">Email:</span>
                  <span>{form.email_id}</span>
                </div>
              )}
              <div className="review-row">
                <span className="review-label">Category:</span>
                <span className="badge badge-warning">{CATEGORIES.find(c => c.value === form.category)?.label}</span>
              </div>
              <div className="review-row">
                <span className="review-label">Description:</span>
                <span>{form.message_description.slice(0, 100)}...</span>
              </div>
              {proofFiles.length > 0 && (
                <div className="review-row">
                  <span className="review-label">Proof:</span>
                  <span>{proofFiles.length} image(s)</span>
                </div>
              )}
            </div>

            <div className="step-actions mt-6">
              <button className="btn btn-ghost" onClick={() => setStep(2)}> Edit</button>
              <button
                className="btn btn-primary btn-lg"
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? <div className="spinner" style={{width:18,height:18,borderWidth:2}}></div> : ' Submit Report'}
              </button>
            </div>
          </div>
        )}
      </div>

    </main>
  );
}
