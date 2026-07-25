# Scrutinix Backend

Python Flask + SQLite backend for the Scrutinix scam intelligence platform.

## Quick Setup

### 1. Create virtual environment
```bash
cd scrutinix-backend
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
copy .env.example .env
```

### 4. Run the server
```bash
python app.py
```
Server starts on http://localhost:5000

### 5. Seed test data
```bash
python seed_data.py
```

## Using PostgreSQL (optional)

If you want to use PostgreSQL instead of SQLite:

1. Install PostgreSQL on your machine
2. Create a database:
   ```sql
   CREATE DATABASE scrutinix;
   ```
3. Update `.env`:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/scrutinix
   ```

## API Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/api/health` | No | Health check |
| GET | `/api/search?q=<phone>` | No | Search phone number |
| POST | `/api/report` | JWT | Submit scam report |
| GET | `/api/community?page=<n>` | No | Community feed |
| POST | `/api/analyze-job` | No | Analyze job description |
| GET | `/api/stats` | No | Platform statistics |
| GET | `/api/recent-reports` | No | Latest reports |
| POST | `/api/auth/send-otp` | No | Send OTP |
| POST | `/api/auth/verify-otp` | No | Verify OTP |
| POST | `/api/auth/google` | No | Google login |
| POST | `/api/auth/signup` | No | Complete signup |
| GET | `/api/me` | JWT | Get user profile |
| GET | `/api/my-reports` | JWT | Get user's reports |

## Testing with curl

```bash
# Health check
curl http://localhost:5000/api/health

# Search a number
curl http://localhost:5000/api/search?q=7012345678

# Get stats
curl http://localhost:5000/api/stats

# Get community feed
curl http://localhost:5000/api/community?page=1

# Analyze a job description
curl -X POST http://localhost:5000/api/analyze-job \
  -H "Content-Type: application/json" \
  -d "{\"description\": \"Urgent hiring! Earn Rs 800/day. Pay registration fee of Rs 2000. WhatsApp only.\"}"

# Send OTP (check terminal for the code)
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d "{\"phone\": \"9876543210\"}"

# Verify OTP (use the code printed in the terminal)
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d "{\"phone\": \"9876543210\", \"otp\": \"CODE_FROM_TERMINAL\"}"
```

## Folder Structure

```
scrutinix-backend/
├── app.py              
├── config.py           
├── extensions.py       
├── requirements.txt    
├── seed_data.py        
├── .env                
├── models/             
│   ├── user.py         
│   ├── report.py       
│   └── otp.py          
├── routes/             
│   ├── auth.py         
│   ├── search.py       
│   ├── report.py       
│   ├── community.py    
│   ├── analyzer.py     
│   ├── stats.py        
│   └── profile.py      
├── utils/              
│   ├── auth_middleware.py  
│   ├── scoring.py         
│   └── job_analyzer.py    
└── uploads/            
```

## Notes

- OTP codes are printed to the terminal (no SMS service configured yet)
- Google OAuth is stubbed — accepts any token for now
- SQLite is the default database — switch to PostgreSQL in `.env`
- CORS is configured for localhost:3000, 3001, and 5173
