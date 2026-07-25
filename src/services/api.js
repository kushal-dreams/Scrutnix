let rawApi = (import.meta.env.VITE_API_URL || 'https://scrutnix.onrender.com/api').replace(/\/+$/, '');
if (rawApi && !rawApi.endsWith('/api')) {
  rawApi = `${rawApi}/api`;
}
const API = rawApi;

function normalizeCategory(report) {
  if (report.category_raw) return report.category_raw;
  return String(report.category || 'other').toLowerCase().replaceAll(' ', '_');
}

function normalizeReport(report) {
  const notes = report.additional_notes || '';
  const stateMatch = notes.match(/state:\s*([^,;]+)/i);
  const cityMatch = notes.match(/city:\s*([^,;]+)/i);
  return {
    ...report,
    category: normalizeCategory(report),
    masked_target: report.phone_number || report.email_id || 'Message-only report',
    message: report.message_description || report.job_description || 'No description provided.',
    city: cityMatch?.[1]?.trim() || 'Community',
    state: stateMatch?.[1]?.trim() || 'India',
    risk: Math.min(95, 35 + Number(report.upvotes || 0) * 3),
    trust_score: Math.min(.95, .5 + Number(report.upvotes || 0) / 100),
    source: report.reporter_username ? 'Community' : 'Seed data',
    proof_level: report.proof_image_urls?.length ? 'Screenshot' : 'Text report'
  };
}

function normalizeAnalysis(result) {
  const flags = (result.flags || []).map((flag) => ({
    phrase: flag.flag || flag.phrase || 'text pattern',
    reason: `${flag.severity || 'warning'} scam indicator`
  }));
  const similarity = result.similarity_matches || [];
  const keywordScore = Math.min(100, flags.length * 15);
  const communityScore = Math.round(Number(result.corpus_similarity || 0) * 100);

  return {
    score: result.score,
    label: result.label,
    summary: result.reasoning || 'The job description was checked by the local model and rule layers.',
    flags,
    recommendations: [
      'Verify the company through its official careers page.',
      'Do not pay registration, training, security, or equipment fees.',
      'Do not share Aadhaar, PAN, bank details, or OTP before verification.'
    ],
    similar_reports: similarity,
    layers: result.layers || {
      layer_1_ml_model: {
        name: 'TF-IDF and Logistic Regression model',
        score: result.ml_score ?? result.score,
        label: result.label,
        confidence: Math.abs(Number(result.score || 50) - 50) / 50,
        top_terms: (result.flagged_keywords || []).slice(0, 6).map((term) => ({ term, direction: 'scam' }))
      },
      layer_2_scam_keywords: {
        score: result.keyword_score ?? keywordScore,
        matched_patterns: flags.length,
        safe_signals: []
      },
      layer_3_user_reports: {
        score: result.community_score ?? communityScore,
        matched_reports: similarity.length,
        top_similarity: Number(result.corpus_similarity || 0)
      }
    },
    model_metadata: {
      model: 'TF-IDF with Logistic Regression',
      training_rows: 17880,
      classes: ['fraudulent', 'legitimate']
    }
  };
}

async function rawRequest(path, options = {}) {
  const token = localStorage.getItem('scrutinix_token');
  const headers = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {})
  };
  if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  
  let response;
  try {
    response = await fetch(`${API}${path}`, { ...options, headers });
  } catch (err) {
    throw new Error('Network error. Check backend connection or internet.');
  }

  const text = await response.text();
  let data = {};
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = {};
    }
  }

  if (!response.ok) {
    const errorMsg = data.message || data.error || (response.status === 401 ? 'Invalid username or password' : `Request failed (${response.status})`);
    throw new Error(errorMsg);
  }
  return data;
}

export async function api(path, options = {}) {
  if (path === '/stats') {
    const data = await rawRequest('/reports?page=1');
    const reports = (data.reports || []).map(normalizeReport);
    const categoryCounts = reports.reduce((counts, report) => {
      counts[report.category] = (counts[report.category] || 0) + 1;
      return counts;
    }, {});
    return {
      total_reports: data.total || reports.length,
      unique_numbers: new Set(reports.map((report) => report.masked_target)).size,
      users: new Set(reports.map((report) => report.reporter_username).filter(Boolean)).size,
      money_lost: 0,
      by_category: Object.entries(categoryCounts).map(([category, count]) => ({ category, count })),
      by_state: []
    };
  }

  if (path.startsWith('/search')) {
    const data = await rawRequest(path, options);
    return {
      query: data.number || data.email,
      type: data.type,
      risk: {
        score: data.score,
        label: data.label,
        report_count: data.report_count,
        unique_reporters: data.unique_reporters || 0,
        confidence: Math.min(1, (data.report_count || 0) / 8),
        method: 'Five-component report score from the Flask backend.'
      },
      reports: (data.reports || []).map(normalizeReport)
    };
  }

  if (path === '/analyze/job') {
    const body = JSON.parse(options.body || '{}');
    const result = await rawRequest(path, {
      ...options,
      body: JSON.stringify({ description: body.text || body.description || '' })
    });
    return { analysis: normalizeAnalysis(result) };
  }

  if (path === '/reports' && (!options.method || options.method === 'GET')) {
    const data = await rawRequest('/reports?page=1', options);
    return { ...data, reports: (data.reports || []).map(normalizeReport) };
  }

  if (path === '/reports' && options.method === 'POST') {
    if (options.body instanceof FormData) return rawRequest('/reports', options);
    const form = JSON.parse(options.body || '{}');
    const category = ['job_fraud', 'spam', 'phishing', 'harassment', 'other'].includes(form.category)
      ? form.category
      : 'other';
    return rawRequest('/reports', {
      method: 'POST',
      body: JSON.stringify({
        report_type: form.target_type === 'email' ? 'email' : form.target_type === 'phone' ? 'whatsapp' : 'sms',
        phone_number: form.phone || '',
        email_id: form.email || '',
        message_description: form.message || '',
        job_description: category === 'job_fraud' ? form.message || '' : '',
        category,
        additional_notes: `State: ${form.state || 'Not provided'}, City: ${form.city || 'Not provided'}, Proof: ${form.proof_level || 'none'}, Money lost: ${form.money_lost || 0}`
      })
    });
  }

  if (path === '/auth/login') {
    const form = JSON.parse(options.body || '{}');
    return rawRequest(path, {
      method: 'POST',
      body: JSON.stringify({ identifier: form.identifier || form.email, password: form.password })
    });
  }

  return rawRequest(path, options);
}
