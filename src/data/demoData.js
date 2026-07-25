export const DEMO_REPORTS = [
  { id: 'd1', category: 'job_fraud', city: 'New Delhi', state: 'Delhi', masked_target: '+91 98XX-XXX-210', upvotes: 42, downvotes: 2, trust_score: .88, risk: 91, source: 'Online forum', proof_level: 'Transaction proof', message: 'WhatsApp HR offered data entry work from home and demanded Rs 799 registration fee before interview.' },
  { id: 'd2', category: 'phishing', city: 'Mumbai', state: 'Maharashtra', masked_target: '+91 91XX-XXX-780', upvotes: 36, downvotes: 1, trust_score: .84, risk: 88, source: 'Community', proof_level: 'Screenshot', message: 'Caller claimed bank KYC expired and asked for PAN, OTP, and screen sharing app installation.' },
  { id: 'd3', category: 'job_fraud', city: 'Bengaluru', state: 'Karnataka', masked_target: '+91 90XX-XXX-111', upvotes: 31, downvotes: 3, trust_score: .82, risk: 86, source: 'Kaggle seed pattern', proof_level: 'Screenshot', message: 'Telegram rating task promised daily income but asked users to recharge wallet before salary payout.' },
  { id: 'd4', category: 'loan_scam', city: 'Pune', state: 'Maharashtra', masked_target: '+91 91XX-XXX-780', upvotes: 27, downvotes: 2, trust_score: .77, risk: 79, source: 'TRAI DND seed', proof_level: 'Official dataset', message: 'Repeated instant loan calls asked processing fee and bank details before loan approval.' },
  { id: 'd5', category: 'phishing', city: 'Chennai', state: 'Tamil Nadu', masked_target: '+91 88XX-XXX-777', upvotes: 44, downvotes: 1, trust_score: .9, risk: 93, source: 'Community', proof_level: 'Screenshot', message: 'SMS included fake bank link and asked PAN card, Aadhaar, and OTP to unblock account.' },
  { id: 'd6', category: 'job_fraud', city: 'Kolkata', state: 'West Bengal', masked_target: 'hr.fastcareer.offer@gmail.com', upvotes: 24, downvotes: 0, trust_score: .79, risk: 82, source: 'Email report', proof_level: 'Screenshot', message: 'Airport ground staff offer promised no interview and requested uniform fee by UPI.' },
  { id: 'd7', category: 'harassment', city: 'Hyderabad', state: 'Telangana', masked_target: '+91 86XX-XXX-345', upvotes: 16, downvotes: 1, trust_score: .68, risk: 68, source: 'Community', proof_level: 'Text copied', message: 'Caller threatened legal action unless a fake unpaid courier charge was paid immediately.' },
  { id: 'd8', category: 'spam', city: 'Ahmedabad', state: 'Gujarat', masked_target: '+91 77XX-XXX-666', upvotes: 11, downvotes: 2, trust_score: .64, risk: 44, source: 'TRAI DND seed', proof_level: 'Official dataset', message: 'Frequent insurance marketing calls continued even after opt-out request.' },
  { id: 'd9', category: 'job_fraud', city: 'Jaipur', state: 'Rajasthan', masked_target: 'Message-only report', upvotes: 19, downvotes: 0, trust_score: .73, risk: 76, source: 'Survey response', proof_level: 'Text copied', message: 'MNC backend role promised instant joining, no experience needed, and employee ID after registration fee.' },
  { id: 'd10', category: 'phishing', city: 'Kochi', state: 'Kerala', masked_target: '+91 88XX-XXX-777', upvotes: 21, downvotes: 1, trust_score: .75, risk: 74, source: 'Community', proof_level: 'Text copied', message: 'Bank support impersonator asked user to install screen sharing app for card verification.' },
  { id: 'd11', category: 'job_fraud', city: 'Noida', state: 'Uttar Pradesh', masked_target: '+91 98XX-XXX-210', upvotes: 22, downvotes: 1, trust_score: .8, risk: 81, source: 'Community', proof_level: 'Transaction proof', message: 'Recruiter asked for training fee and Aadhaar/PAN before sharing the real company details.' },
  { id: 'd12', category: 'identity_theft', city: 'Gurugram', state: 'Haryana', masked_target: '+91 98XX-XXX-210', upvotes: 18, downvotes: 0, trust_score: .76, risk: 78, source: 'Community', proof_level: 'Screenshot', message: 'Fake appointment letter requested Aadhaar, PAN, bank passbook photo, and security deposit.' },
  { id: 'd13', category: 'job_fraud', city: 'Indore', state: 'Madhya Pradesh', masked_target: '+91 90XX-XXX-678', upvotes: 29, downvotes: 0, trust_score: .81, risk: 87, source: 'Campus survey', proof_level: 'Screenshot', message: 'Campus placement shortlist scam asked students to pay Rs 499 verification fee before interview link.' },
  { id: 'd14', category: 'identity_theft', city: 'Bhopal', state: 'Madhya Pradesh', masked_target: '+91 90XX-XXX-678', upvotes: 23, downvotes: 1, trust_score: .79, risk: 83, source: 'Community', proof_level: 'Text copied', message: 'Recruiter requested Aadhaar, PAN, bank passbook, and selfie before disclosing company registration.' },
  { id: 'd15', category: 'job_fraud', city: 'Hyderabad', state: 'Telangana', masked_target: 'recruitment.quickhire@outlook.com', upvotes: 28, downvotes: 1, trust_score: .83, risk: 85, source: 'Online forum', proof_level: 'Screenshot', message: 'Software trainee offer from free email domain demanded laptop security deposit of Rs 2500.' },
  { id: 'd16', category: 'phishing', city: 'Ludhiana', state: 'Punjab', masked_target: '+91 93XX-XXX-901', upvotes: 19, downvotes: 2, trust_score: .7, risk: 72, source: 'Community', proof_level: 'Text copied', message: 'Courier support impersonator requested OTP to release a non-existent parcel.' },
  { id: 'd17', category: 'job_fraud', city: 'Bhubaneswar', state: 'Odisha', masked_target: '+91 94XX-XXX-876', upvotes: 34, downvotes: 2, trust_score: .86, risk: 89, source: 'Kaggle seed pattern', proof_level: 'Transaction proof', message: 'Instagram review job asked user to deposit Rs 1000 to unlock premium task wallet.' },
  { id: 'd18', category: 'phishing', city: 'New Delhi', state: 'Delhi', masked_target: '+91 95XX-XXX-345', upvotes: 39, downvotes: 1, trust_score: .88, risk: 92, source: 'Community', proof_level: 'Screenshot', message: 'Credit-card limit upgrade caller asked full card number, CVV, and OTP.' },
  { id: 'd19', category: 'job_fraud', city: 'Patna', state: 'Bihar', masked_target: 'Message-only report', upvotes: 18, downvotes: 0, trust_score: .72, risk: 77, source: 'Survey response', proof_level: 'Text copied', message: 'Online captcha work promised Rs 1800 daily and demanded software activation fee.' },
  { id: 'd20', category: 'harassment', city: 'Vijayawada', state: 'Andhra Pradesh', masked_target: '+91 96XX-XXX-777', upvotes: 13, downvotes: 1, trust_score: .66, risk: 65, source: 'Community', proof_level: 'Text copied', message: 'Caller used abusive threats and demanded fake tax penalty payment.' },
  { id: 'd21', category: 'spam', city: 'Bengaluru', state: 'Karnataka', masked_target: '+91 92XX-XXX-999', upvotes: 16, downvotes: 2, trust_score: .69, risk: 48, source: 'TRAI DND seed', proof_level: 'Official dataset', message: 'Repeated education loan promotional calls continued after DND complaint.' },
  { id: 'd22', category: 'job_fraud', city: 'Guwahati', state: 'Assam', masked_target: '+91 91XX-XXX-222', upvotes: 22, downvotes: 0, trust_score: .76, risk: 80, source: 'Online forum', proof_level: 'Screenshot', message: 'Fake government internship message asked application processing fee and documents on WhatsApp.' },
  { id: 'd23', category: 'loan_scam', city: 'Lucknow', state: 'Uttar Pradesh', masked_target: '+91 97XX-XXX-654', upvotes: 25, downvotes: 3, trust_score: .73, risk: 71, source: 'Community', proof_level: 'Transaction proof', message: 'Instant loan agent asked advance insurance fee before disbursal.' },
  { id: 'd24', category: 'job_fraud', city: 'Chandigarh', state: 'Chandigarh', masked_target: '+91 98XX-XXX-444', upvotes: 17, downvotes: 0, trust_score: .71, risk: 74, source: 'Campus survey', proof_level: 'Text copied', message: 'Work-from-home packing job asked candidate to buy starter kit before joining.' },
  { id: 'd25', category: 'phishing', city: 'Ranchi', state: 'Jharkhand', masked_target: '+91 89XX-XXX-888', upvotes: 20, downvotes: 1, trust_score: .74, risk: 78, source: 'Community', proof_level: 'Screenshot', message: 'Electricity bill disconnection SMS redirected to fake payment page.' },
  { id: 'd26', category: 'job_fraud', city: 'Nagpur', state: 'Maharashtra', masked_target: '+91 93XX-XXX-222', upvotes: 27, downvotes: 1, trust_score: .8, risk: 84, source: 'Community', proof_level: 'Screenshot', message: 'Back-office job offered instant joining and demanded refundable ID card fee.' },
  { id: 'd27', category: 'identity_theft', city: 'Surat', state: 'Gujarat', masked_target: '+91 76XX-XXX-333', upvotes: 18, downvotes: 2, trust_score: .68, risk: 70, source: 'Community', proof_level: 'Text copied', message: 'Fake recruiter asked for scanned marksheets, Aadhaar, PAN, and bank details before interview.' },
  { id: 'd28', category: 'spam', city: 'Coimbatore', state: 'Tamil Nadu', masked_target: '+91 82XX-XXX-112', upvotes: 10, downvotes: 1, trust_score: .61, risk: 39, source: 'TRAI DND seed', proof_level: 'Official dataset', message: 'Repeated automated stock trading promotion calls from rotating numbers.' }
];

export const DEMO_STATS = {
  total_reports: 428,
  unique_numbers: 139,
  users: 96,
  money_lost: 742850,
  by_category: [
    { category: 'job_fraud', count: 172 },
    { category: 'phishing', count: 96 },
    { category: 'identity_theft', count: 54 },
    { category: 'loan_scam', count: 43 },
    { category: 'spam', count: 39 },
    { category: 'harassment', count: 24 }
  ],
  by_state: [
    { state: 'Delhi', count: 58 },
    { state: 'Maharashtra', count: 52 },
    { state: 'Karnataka', count: 46 },
    { state: 'Tamil Nadu', count: 39 },
    { state: 'Uttar Pradesh', count: 36 },
    { state: 'Telangana', count: 31 },
    { state: 'West Bengal', count: 28 },
    { state: 'Gujarat', count: 24 },
    { state: 'Madhya Pradesh', count: 22 },
    { state: 'Rajasthan', count: 19 },
    { state: 'Kerala', count: 17 },
    { state: 'Odisha', count: 14 }
  ]
};

export const MONTHLY_TRENDS = [
  { month: 'Jan', reports: 42, job: 18 },
  { month: 'Feb', reports: 58, job: 24 },
  { month: 'Mar', reports: 66, job: 29 },
  { month: 'Apr', reports: 82, job: 36 },
  { month: 'May', reports: 91, job: 42 },
  { month: 'Jun', reports: 89, job: 39 }
];

export const PLAYBOOKS = [
  ['Fake job fee trap', 'Registration fee, training fee, security deposit, uniform fee, software activation charge.'],
  ['Identity harvest', 'Aadhaar, PAN, bank passbook, selfie, marksheets requested before verified interview.'],
  ['Payment-app pressure', 'UPI, wallet recharge, task wallet unlock, refundable deposit, urgent seat reservation.'],
  ['Bank/KYC phishing', 'Fake KYC expiry, OTP request, screen sharing app, CVV collection, fake payment link.']
];

export const COLLEGE_INSIGHTS = {
  campus_reports: 312,
  colleges: 18,
  students_seen_scam: 71,
  alert_opt_in: 84,
  channels: [
    { label: 'WhatsApp', value: 42 },
    { label: 'Telegram', value: 21 },
    { label: 'Phone calls', value: 18 },
    { label: 'Email', value: 12 },
    { label: 'Instagram', value: 7 }
  ],
  leaderboard: [
    { college: 'Scrutnix Institute', reports: 48, verified: 39, score: 92 },
    { college: 'Delhi University', reports: 36, verified: 30, score: 86 },
    { college: 'Mumbai University', reports: 29, verified: 22, score: 78 },
    { college: 'Christ University', reports: 25, verified: 20, score: 74 }
  ],
  workshops: [
    ['Orientation booth', 'Students paste suspicious messages and learn the risk score live.'],
    ['Placement-cell alerts', 'Verified scam numbers are shared with department groups.'],
    ['Survey drive', 'Collect original campus data for project report and charts.'],
    ['Awareness posters', 'Show top red flags: fee demand, no interview, OTP, Aadhaar/PAN.']
  ]
};

export const CASE_STUDIES = [
  {
    title: 'WhatsApp Data Entry Fee Scam',
    target: '+91 98XX-XXX-210',
    loss: 'Rs 2,499',
    risk: 91,
    signals: ['registration fee', 'no interview', 'UPI payment', 'Aadhaar request'],
    outcome: 'Flagged as Critical after four independent reports and transaction proof.'
  },
  {
    title: 'Fake Bank KYC Support',
    target: '+91 88XX-XXX-777',
    loss: 'Prevented',
    risk: 93,
    signals: ['OTP request', 'PAN card', 'fake bank link', 'screen sharing'],
    outcome: 'Community confirmations moved the report to high-priority phishing queue.'
  },
  {
    title: 'Campus Placement Shortlist Trap',
    target: '+91 90XX-XXX-678',
    loss: 'Rs 499',
    risk: 87,
    signals: ['verification fee', 'campus shortlist', 'WhatsApp only', 'urgent deadline'],
    outcome: 'Added to placement-cell alerts and survey analytics.'
  }
];

export const INGESTION_STEPS = [
  ['Community report', 'Phone/message/email submitted with city, source and proof level.'],
  ['Data cleaning', 'Phone normalization, duplicate detection and noisy text cleanup.'],
  ['Risk engine', 'Severity, recency, Bayesian votes, trust, proof and NLP signals.'],
  ['Moderation', 'High-risk reports are queued for review and campus alerting.']
];

export const MODERATION_QUEUE = [
  { id: 'MQ-1042', type: 'Job fraud', priority: 'Critical', evidence: 'Transaction proof', action: 'Alert placement cell' },
  { id: 'MQ-1038', type: 'Phishing', priority: 'Critical', evidence: 'Screenshot', action: 'Mark verified' },
  { id: 'MQ-1029', type: 'Loan scam', priority: 'High', evidence: '2 confirmations', action: 'Needs proof' },
  { id: 'MQ-1021', type: 'Spam', priority: 'Medium', evidence: 'DND seed', action: 'Monitor pattern' }
];
