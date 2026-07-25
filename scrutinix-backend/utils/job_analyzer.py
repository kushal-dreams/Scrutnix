import re
import math
import json
import urllib.request
import urllib.error
import os
from flask import current_app

RED_FLAG_RULES = [
    (
        r'(registration\s*fee|advance\s*payment|processing\s*fee|security\s*deposit|pay\s*(first|before|upfront)|joining\s*fee)',
        'Registration/advance fee mentioned',
        'high', 25
    ),
    (
        r'(send\s*(your|ur)\s*(aadhaar|aadhar|pan\s*card|bank\s*(details|account|info)|upi|passport))',
        'Personal documents (Aadhaar/PAN/bank) requested',
        'high', 25
    ),
    (
        r'(guaranteed\s*(income|salary|earning)|earn\s*₹?\s*\d+\s*(per|\/)\s*(day|hour|hr)|fixed\s*(income|salary)\s*₹?\s*\d+)',
        'Guaranteed/fixed income claims',
        'high', 20
    ),
    (
        r'(transfer\s*(money|amount|funds)|paytm|phonepe|google\s*pay).*(before|first|upfront|advance)',
        'Money transfer requested upfront',
        'high', 25
    ),
    (
        r'(whatsapp\s*only|contact\s*(on|via|through)\s*whatsapp|dm\s*(on|via)\s*whatsapp|msg\s*(on|via)\s*whatsapp)',
        'WhatsApp-only contact',
        'medium', 15
    ),
    (
        r'(work\s*from\s*home|wfh|home\s*based\s*job|online\s*job|part\s*time\s*job|typing\s*job|data\s*entry\s*job)',
        'Work-from-home / online job claim',
        'medium', 10
    ),
    (
        r'(no\s*(experience|qualification|skills?)\s*(needed|required|necessary))',
        'No experience/qualification needed',
        'medium', 10
    ),
    (
        r'(limited\s*(seats?|slots?|vacancy|openings?)|hurry|apply\s*(now|immediately|today|fast)|last\s*(date|chance)|urgent\s*(hiring|requirement|opening))',
        'Urgency/pressure tactics',
        'medium', 12
    ),
    (
        r'(100%\s*(genuine|real|trusted|verified)|not\s*a?\s*fraud|not\s*a?\s*scam|trusted\s*company)',
        'Excessive trust claims ("100% genuine")',
        'medium', 12
    ),
    (
        r'(copy\s*paste|just\s*(copy|share|forward)|simple\s*task|easy\s*(money|earning|task))',
        'Unrealistically simple work described',
        'medium', 10
    ),
    (
        r'(no\s*company\s*name|unnamed|confidential\s*company)',
        'No company name provided',
        'low', 8
    ),
    (
        r'(telegram\s*(group|channel|bot))',
        'Telegram group/channel involvement',
        'low', 6
    ),
    (
        r'(refund\s*policy|money\s*back\s*guarantee|100%\s*refund)',
        'Refund guarantees (common in scams)',
        'low', 5
    ),
    (
        r'(freelanc(e|ing)|contract\s*basis)(?!.*company)',
        'Freelance/contract with no clear employer',
        'low', 4
    ),
]

STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
    'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
    "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't",
    'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
    'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}


def tokenize(text):
    if not text:
        return []
    text = text.lower()
    
    # Common replacements for normalization
    text = text.replace('rs.', ' rupee ').replace('rs', ' rupee ').replace('inr', ' rupee ')
    text = text.replace('wfh', ' work home ').replace('watsapp', ' whatsapp ').replace('whatapp', ' whatsapp ')
    text = text.replace('aadhar', ' aadhaar ').replace('pan card', ' pancard ')
    
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = [w for w in text.split() if w not in STOPWORDS and len(w) > 2]
    
    stemmed = []
    for w in words:
        if w == 'daily':
            w = 'day'
        elif w == 'monthly':
            w = 'month'
        elif w == 'yearly':
            w = 'year'
            
        # Basic suffix stemming
        if w.endswith('ing'):
            w = w[:-3]
        elif w.endswith('ly'):
            w = w[:-2]
        elif w.endswith('ment'):
            w = w[:-4]
        elif w.endswith('ed'):
            w = w[:-2]
        elif w.endswith('es') and not w.endswith('ees'):
            w = w[:-2]
        elif w.endswith('s') and not w.endswith('ss') and not w.endswith('us') and not w.endswith('is') and not w.endswith('as'):
            w = w[:-1]
        stemmed.append(w)
        
    return stemmed


def _call_gemini_api(text, api_key, model_name):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    prompt = f"""
Analyze this job description for signs of recruitment scams. Pay close attention to Indian job scam patterns (like upfront fees, security deposits, part-time work-from-home, WhatsApp-only contact, lack of official email domain, and pressure tactics).

CRITICAL INSTRUCTION: Understand negations and semantic context. If the text says "no registration fee required" or "zero joining fee", do NOT flag it as "Registration/advance fee mentioned". Only raise flags if the scam indicators are actually present/required.

Job Description to analyze:
\"\"\"{text}\"\"\"
"""
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "score": {"type": "INTEGER", "description": "Suspicion score from 0 to 100"},
                    "band": {"type": "STRING", "description": "Risk band: 'low', 'medium', or 'high'"},
                    "flags": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "flag": {"type": "STRING", "description": "Brief description of the red flag pattern detected (e.g. 'Registration/advance fee mentioned')"},
                                "severity": {"type": "STRING", "description": "Severity: 'low', 'medium', or 'high'"}
                            },
                            "required": ["flag", "severity"]
                        }
                    },
                    "recommendation": {"type": "STRING", "description": "Detailed recommendation advice for the user based on the analysis"}
                },
                "required": ["score", "band", "flags", "recommendation"]
            }
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        res_data = response.read().decode('utf-8')
        res_json = json.loads(res_data)
        
        candidates = res_json.get('candidates', [])
        if not candidates:
            raise ValueError("No candidates returned from Gemini API")
            
        content = candidates[0].get('content', {})
        parts = content.get('parts', [])
        if not parts:
            raise ValueError("No parts returned in Gemini candidate content")
            
        res_text = parts[0].get('text', '').strip()
        analysis_result = json.loads(res_text)
        
        # Enforce schemas structure just in case
        return {
            'score': int(analysis_result.get('score', 0)),
            'band': str(analysis_result.get('band', 'low')).lower(),
            'flags': list(analysis_result.get('flags', [])),
            'recommendation': str(analysis_result.get('recommendation', ''))
        }


def analyze_with_gemini(text, api_key):
    """
    Tries calling gemini-2.5-flash first, falls back to gemini-1.5-flash.
    """
    last_error = None
    for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
        try:
            return _call_gemini_api(text, api_key, model_name)
        except Exception as e:
            last_error = e
            print(f"[Warning] Failed to call {model_name}: {e}")
            continue
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def analyze_job_description(text, existing_reports=None):
    if not text or not text.strip():
        return {
            'score': 0,
            'band': 'low',
            'flags': [],
            'recommendation': 'No text provided to analyze.',
            'similarity_matches': []
        }

    # Check for Gemini API key configuration
    api_key = None
    try:
        api_key = current_app.config.get('GEMINI_API_KEY')
    except Exception:
        # Fallback for offline/script usage
        api_key = os.environ.get('GEMINI_API_KEY')

    base_result = None
    if api_key and api_key.strip() and not api_key.startswith('fake-api-key'):
        try:
            print(f"[AI Analyzer] Sending request to Gemini...")
            base_result = analyze_with_gemini(text, api_key)
            print(f"[AI Analyzer] Gemini returned score: {base_result['score']}")
        except Exception as e:
            print(f"[AI Analyzer] Gemini error, falling back to local regex: {e}")
            base_result = None

    # Fallback to local regex rule-based matching if Gemini is not available or failed
    if not base_result:
        text_lower = text.lower()
        found_flags = []
        total_weight = 0

        # Rule-based matching
        for pattern, label, severity, weight in RED_FLAG_RULES:
            if re.search(pattern, text_lower):
                found_flags.append({
                    'flag': label,
                    'severity': severity,
                })
                total_weight += weight

        score = min(100, total_weight)
        if score > 60:
            band = 'high'
        elif score > 30:
            band = 'medium'
        else:
            band = 'low'

        if score > 60:
            recommendation = (
                'High risk. This job description matches multiple known scam patterns. '
                'Do NOT share personal details or pay any fees. Report this immediately.'
            )
        elif score > 30:
            recommendation = (
                'Moderate risk. Some suspicious elements detected. '
                'Verify the company independently before proceeding. '
                'Never pay upfront fees for any job.'
            )
        elif score > 0:
            recommendation = (
                'Low risk. Minor concerns detected but could be legitimate. '
                'Still, exercise caution and verify company details.'
            )
        else:
            recommendation = (
                'No red flags detected. This appears to be a standard job listing. '
                'Always verify with the official company website.'
            )

        base_result = {
            'score': score,
            'band': band,
            'flags': found_flags,
            'recommendation': recommendation
        }

    similarity_matches = []
    
    # NLP-based Similarity Analysis with existing reports (always active!)
    if existing_reports:
        valid_reports = [r for r in existing_reports if r.get('job_desc') and r['job_desc'].strip()]
        if valid_reports:
            query_tokens = tokenize(text)
            docs_tokens = [tokenize(r['job_desc']) for r in valid_reports]
            
            # Calculate Document Frequency (DF) across query + corpus
            df = {}
            all_docs = docs_tokens + [query_tokens]
            for doc in all_docs:
                unique_tokens = set(doc)
                for t in unique_tokens:
                    df[t] = df.get(t, 0) + 1
            
            # Query TF
            query_tf = {}
            for t in query_tokens:
                query_tf[t] = query_tf.get(t, 0) + 1
                
            N = len(all_docs)
            
            # Query TF-IDF vector
            query_tfidf = {}
            for t, count in query_tf.items():
                tf = count
                idf = math.log((N + 1) / (df.get(t, 0) + 1)) + 1
                query_tfidf[t] = tf * idf
                
            # Compute TF-IDF & Cosine/Overlap Hybrid Similarity
            for idx, report in enumerate(valid_reports):
                doc_tokens = docs_tokens[idx]
                if not doc_tokens:
                    continue
                
                # 1. Cosine Similarity
                doc_tf = {}
                for t in doc_tokens:
                    doc_tf[t] = doc_tf.get(t, 0) + 1
                    
                doc_tfidf = {}
                for t, count in doc_tf.items():
                    tf = count
                    idf = math.log((N + 1) / (df.get(t, 0) + 1)) + 1
                    doc_tfidf[t] = tf * idf
                    
                dot_product = sum(query_tfidf.get(t, 0) * val for t, val in doc_tfidf.items())
                query_mag = math.sqrt(sum(val ** 2 for val in query_tfidf.values()))
                doc_mag = math.sqrt(sum(val ** 2 for val in doc_tfidf.values()))
                
                cosine_sim = dot_product / (query_mag * doc_mag) if query_mag * doc_mag > 0 else 0.0
                
                # 2. Overlap Coeff
                q_set = set(query_tokens)
                d_set = set(doc_tokens)
                intersection = q_set.intersection(d_set)
                min_len = min(len(q_set), len(d_set))
                overlap_coeff = len(intersection) / min_len if min_len > 0 else 0.0
                
                hybrid_similarity = (cosine_sim + overlap_coeff) / 2
                    
                if hybrid_similarity >= 0.35:
                    similarity_matches.append({
                        'report_id': report.get('id'),
                        'phone': report.get('phone'),
                        'category': report.get('category'),
                        'state': report.get('state'),
                        'city': report.get('city'),
                        'date': report.get('date'),
                        'similarity': int(hybrid_similarity * 100)
                    })
                    
            similarity_matches.sort(key=lambda x: x['similarity'], reverse=True)

    # Check top similarity match to flag duplicate scams
    top_match = similarity_matches[0] if similarity_matches else None
    if top_match and top_match['similarity'] >= 40:
        # Check if similar flag is already in the list to avoid duplicates
        has_similar_flag = any("Similar to an already reported scam" in f['flag'] for f in base_result['flags'])
        if not has_similar_flag:
            base_result['flags'].append({
                'flag': f"Similar to an already reported scam ({top_match['similarity']}% match)",
                'severity': 'high'
            })
        
        sim_val = top_match['similarity']
        boosted_score = int(85 + (sim_val - 40) * (15 / 60))
        boosted_score = min(100, max(85, boosted_score))
        
        base_result['score'] = max(base_result['score'], boosted_score)
        
        if base_result['score'] > 60:
            base_result['band'] = 'high'
            base_result['recommendation'] = (
                'High risk. This job description matches multiple known scam patterns or '
                'is highly similar to an already reported scam in our database. '
                'Do NOT share personal details or pay any fees. Report this immediately.'
            )

    return {
        'score': base_result['score'],
        'band': base_result['band'],
        'flags': base_result['flags'],
        'recommendation': base_result['recommendation'],
        'similarity_matches': similarity_matches[:5]
    }
