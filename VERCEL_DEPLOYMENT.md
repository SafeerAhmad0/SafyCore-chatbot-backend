# Deploy SafyCore Chatbot to Vercel

## Prerequisites

1. Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm install -g vercel`
3. Groq API key from https://console.groq.com/keys

## Step-by-Step Deployment

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Deploy from project directory**
   ```bash
   cd C:\Users\safee\Documents\Projects\SafyCore-backend
   vercel
   ```

3. **Follow prompts**
   - Set up and deploy? `Y`
   - Which scope? Select your account
   - Link to existing project? `N`
   - Project name? `safycore-chatbot` (or your choice)
   - Directory? `./`
   - Override settings? `N`

4. **Add Environment Variable**
   ```bash
   vercel env add GROQ_API_KEY
   ```
   Then paste your Groq API key when prompted.
   - Select environment: Production, Preview, Development (select all 3)

5. **Redeploy with environment variable**
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via Vercel Dashboard

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Click "Import Project"
   - Select your GitHub repository
   - Click "Import"

3. **Configure Project**
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

4. **Add Environment Variables**
   - In project settings → Environment Variables
   - Add: `GROQ_API_KEY` = `your_groq_api_key_here`
   - Apply to: Production, Preview, Development

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete

## After Deployment

Your API will be available at:
```
https://your-project-name.vercel.app
```

### Test Your Deployment

```bash
curl https://your-project-name.vercel.app/
```

## Update Frontend

After deployment, update `frontend_example.html`:

```javascript
// Change this line:
const API_URL = 'http://localhost:8000';

// To your Vercel URL:
const API_URL = 'https://your-project-name.vercel.app';
```

## Important Notes

### Vercel Limitations

1. **Function Timeout**: 10 seconds (Hobby plan) / 60 seconds (Pro plan)
   - Streaming responses work but may timeout on long conversations

2. **Stateless Functions**: `conversations = {}` will reset on each request
   - **Solution**: Use external storage (see below)

3. **Cold Starts**: First request may be slower (2-5 seconds)

### Recommended: Add Database for Production

For production use, replace in-memory storage with a database:

**Option A: Vercel KV (Redis)**
```bash
npm install @vercel/kv
```

**Option B: Upstash Redis** (Free tier available)
```python
from upstash_redis import Redis

redis = Redis(url=os.getenv("UPSTASH_REDIS_URL"), token=os.getenv("UPSTASH_REDIS_TOKEN"))

# Store conversation
redis.set(f"conversation:{session_id}", json.dumps(messages))

# Retrieve conversation
messages = json.loads(redis.get(f"conversation:{session_id}") or "[]")
```

## Troubleshooting

### Error: "Module not found"
- Check `requirements-vercel.txt` includes all dependencies
- Redeploy: `vercel --prod`

### Error: "GROQ_API_KEY not provided"
- Add environment variable in Vercel dashboard
- Redeploy after adding

### Error: "Function execution timed out"
- Reduce `max_completion_tokens` in app.py
- Upgrade to Vercel Pro for 60s timeout

### Streaming not working
- Vercel supports streaming, but some browsers may buffer
- Test with direct API calls using `curl`

## Monitoring

View logs in Vercel dashboard:
- Go to your project → Deployments → Select deployment → Functions

## Custom Domain (Optional)

1. Go to project settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate auto-generated

## Cost

- **Vercel Hobby Plan**: FREE
  - 100 GB bandwidth/month
  - Serverless function execution: 100 GB-hours
  - 10 second function timeout

- **Vercel Pro Plan**: $20/month
  - 1 TB bandwidth/month
  - 1000 GB-hours execution
  - 60 second function timeout
