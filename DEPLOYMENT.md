# 🚀 Deployment Guide - Render.com

Complete guide to deploy your Cricket Analytics Dashboard to Render.com with custom domain.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Project works locally (`streamlit run app.py`)
- [ ] All code committed to GitHub
- [ ] .env file NOT committed (check .gitignore)
- [ ] requirements.txt is complete
- [ ] Data files in data/ directory (or will load dynamically)
- [ ] Gemini API key ready

---

## 🎯 Part 1: Deploy to Render (15 mins)

### Step 1: Create Render Account

1. Go to: https://render.com
2. Click "Get Started" or "Sign Up"
3. **Sign up with GitHub** (recommended - easiest integration)
4. Authorize Render to access your repositories

### Step 2: Create New Web Service

1. Click "New +" button (top right)
2. Select "Web Service"
3. Connect your GitHub repository:
   - Search for: `rkjat65/cricket`
   - Click "Connect"

### Step 3: Configure Service

**Basic Settings:**
```
Name: cricket-analytics-rkjat
Region: Singapore (or closest to India)
Branch: main
Runtime: Python 3
```

**Build Settings:**
```
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**Plan:**
```
Select: Free
(Starter plan is $7/month if you want 0 downtime)
```

### Step 4: Add Environment Variables

Click "Advanced" → "Add Environment Variable"

Add these:
```
Key: GEMINI_API_KEY
Value: your_actual_gemini_api_key_here
```

```
Key: PYTHON_VERSION
Value: 3.10.0
```

### Step 5: Deploy!

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes first time)
3. Watch the build logs

**You'll see:**
```
==> Building...
==> Installing dependencies...
==> Starting service...
==> Your service is live!
```

### Step 6: Verify Deployment

1. Render gives you a URL: `https://cricket-analytics-rkjat.onrender.com`
2. Click the URL
3. Wait 30 seconds for initial load (free tier spins down when idle)
4. Should see your dashboard! 🎉

---

## 🌐 Part 2: Custom Domain Setup (10 mins)

You have 3 options:

### Option A: Subdomain (FREE - Recommended for Start)

**On Hostinger:**

1. Log into Hostinger hPanel
2. Go to: **Domains** → **rkjat.in** → **DNS / Name Servers**
3. Click **Manage DNS Records**
4. Add CNAME Record:
   ```
   Type: CNAME
   Name: cricket (or cricketanalytics)
   Points to: cricket-analytics-rkjat.onrender.com
   TTL: 14400 (4 hours)
   ```
5. Save

**On Render:**

1. Go to your service dashboard
2. Click **Settings**
3. Scroll to **Custom Domain**
4. Click **Add Custom Domain**
5. Enter: `cricket.rkjat.in`
6. Click **Verify**
7. Wait for SSL certificate (automatic, 1-2 hours)

**Result:** Your app at `https://cricket.rkjat.in` ✅

---

### Option B: New Domain (~₹500/year)

**Buy domain:**
- GoDaddy, Namecheap, Hostinger
- Example: `rkjatcricket.com` or `cricketdata.in`
- Cost: ₹400-800/year

**Setup same as Option A:**
- Add CNAME record pointing to Render
- Add custom domain in Render
- SSL auto-generates

---

### Option C: Use Render's Free Subdomain (FREE)

**No setup needed!**
- URL: `cricket-analytics-rkjat.onrender.com`
- Works immediately
- Free SSL included
- Can add custom domain later

**For portfolio, this is perfectly fine!**

---

## 🔧 Part 3: Post-Deployment Configuration

### Enable Auto-Deploy

In Render dashboard:
1. Go to **Settings**
2. Scroll to **Build & Deploy**
3. **Auto-Deploy**: Yes (default)

Now every Git push auto-deploys! 🚀

### Configure Health Checks

Render automatically checks if your app is running.

If app keeps restarting:
1. Check build logs
2. Ensure `--server.port=$PORT` in start command
3. Check requirements.txt has all packages

### Monitor Performance

In Render dashboard:
- **Metrics**: CPU, Memory usage
- **Logs**: Real-time application logs
- **Events**: Deployment history

---

## 🎨 Part 4: Embedding on Main Website

### Option 1: Iframe Embed (Simple)

On `rkjat.in`, create new page: `/projects/cricket-dashboard.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cricket Analytics Dashboard - RK Jat</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            background: #f8fafc;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .header h1 {
            color: #1e293b;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            color: #64748b;
            font-size: 1.1rem;
        }
        
        .dashboard-frame {
            border: 3px solid #00a67e;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 166, 126, 0.1);
        }
        
        iframe {
            width: 100%;
            height: 900px;
            border: none;
        }
        
        .cta {
            text-align: center;
            margin-top: 2rem;
        }
        
        .btn {
            background: #00a67e;
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: #008c6a;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 166, 126, 0.3);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏏 Cricket Analytics Dashboard</h1>
            <p>Interactive analysis of IPL 2024 & T20 World Cup with AI-powered visualizations</p>
        </div>
        
        <div class="dashboard-frame">
            <iframe 
                src="https://cricket.rkjat.in"
                loading="lazy"
                title="Cricket Analytics Dashboard">
            </iframe>
        </div>
        
        <div class="cta">
            <a href="https://cricket.rkjat.in" target="_blank" class="btn">
                Open Full Dashboard →
            </a>
        </div>
    </div>
</body>
</html>
```

### Option 2: Direct Link Card

Add to your portfolio page:

```html
<div class="project-card">
    <img src="cricket-dashboard-preview.png" alt="Cricket Analytics">
    <h3>🏏 Cricket Analytics Dashboard</h3>
    <p>Full-stack data analysis project with AI-powered visualizations</p>
    <div class="tech-stack">
        <span>Python</span>
        <span>Streamlit</span>
        <span>Google Gemini</span>
        <span>Plotly</span>
    </div>
    <a href="https://cricket.rkjat.in" target="_blank">View Live →</a>
    <a href="https://github.com/rkjat65/cricket" target="_blank">GitHub →</a>
</div>
```

---

## 🐛 Troubleshooting

### Issue: App keeps restarting

**Solution:**
1. Check logs in Render dashboard
2. Verify start command:
   ```
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```
3. Check Python version matches requirements

### Issue: ModuleNotFoundError

**Solution:**
- Missing package in requirements.txt
- Add the package and push to GitHub
- Render will auto-redeploy

### Issue: App loads but crashes when using AI

**Solution:**
- Check GEMINI_API_KEY is set in Render environment variables
- Verify API key is valid
- Check API quota

### Issue: Slow performance

**Solution:**
- Free tier spins down after 15 mins idle
- Upgrade to Starter ($7/month) for always-on
- Optimize data loading (cache with @st.cache_data)

### Issue: Custom domain not working

**Solution:**
- Wait 1-2 hours for DNS propagation
- Check CNAME record is correct
- Verify in Render that domain is verified
- Check SSL certificate status

### Issue: Data not loading

**Solution:**
- Check if data files are in repo (or load dynamically)
- Verify database initialization runs
- Check file paths are relative, not absolute

---

## 📊 Cost Analysis

### Free Tier (Recommended for Portfolio)
```
Render: FREE
- 750 hours/month
- Spins down after 15 min inactivity
- 30 second restart time
- Perfect for portfolio/demo

Domain: FREE (subdomain) or ₹500/year (new domain)

Gemini API: FREE
- Generous free tier
- Plenty for demo purposes

Total: ₹0-500/year
```

### Paid Tier (For Production)
```
Render Starter: $7/month = ~₹600/month
- Always on (no spin down)
- Faster performance
- More resources

Domain: ₹500-1000/year

Gemini API: Pay-as-you-go
- After free tier

Total: ~₹7,700/year
```

**Recommendation:** Start FREE, upgrade later if needed.

---

## 🎯 Post-Deployment Tasks

### 1. Test Everything
- [ ] Dashboard loads
- [ ] All pages accessible
- [ ] AI feature works
- [ ] Visualizations render
- [ ] Mobile responsive
- [ ] No console errors

### 2. Add to Portfolio
- [ ] Update resume with project
- [ ] Add to LinkedIn projects
- [ ] Update GitHub profile README
- [ ] Tweet about launch 🐦

### 3. Create Content
- [ ] Screenshot for social media
- [ ] Record demo video (2-3 mins)
- [ ] Write blog post on rkjat.in
- [ ] Share on Twitter with #DataAnalytics

### 4. Monitor
- [ ] Check Render logs weekly
- [ ] Monitor API usage
- [ ] Track visitor analytics (optional)

---

## 🚀 Launch Checklist

Before announcing publicly:

- [ ] App deployed and working
- [ ] Custom domain configured (if using)
- [ ] All features tested
- [ ] Mobile version works
- [ ] No obvious bugs
- [ ] README updated with live link
- [ ] Demo screenshots ready
- [ ] Twitter thread drafted

---

## 📱 Sharing Your Project

### Twitter Thread Template:

```
🏏 Just launched my Cricket Analytics Dashboard!

An end-to-end data project analyzing IPL 2024 & T20 World Cup with:
✅ 50,000+ ball-by-ball data points
✅ Interactive Plotly visualizations
✅ Google Gemini AI integration
✅ Deployed on custom domain

🔗 https://cricket.rkjat.in

Thread 🧵👇

1/ The Data Pipeline:
- Automated scraping from Cricsheet
- SQLite database for 150+ matches
- Pandas transformation pipeline
- Real-time analysis capabilities

[Image: Data flow diagram]

2/ Key Insights Uncovered:
[Share 3-4 interesting findings with charts]

3/ The AI Feature:
Integrated Google Gemini for experimental AI-generated visualizations
Shows innovation beyond traditional tools

[Image: AI-generated chart]

4/ Tech Stack:
🐍 Python + Pandas
📊 Streamlit + Plotly
🤖 Google Gemini API
☁️ Deployed on Render
🌐 Custom domain

100% production-ready portfolio project

5/ Open Source:
Full code on GitHub: https://github.com/rkjat65/cricket
PRs welcome! ⭐

Built in 6 weeks as part of my data analytics portfolio
Thanks for reading! 🙏

#DataAnalytics #Python #Cricket #IPL2024
```

---

## ✅ Success! What's Next?

Once deployed:

1. **Share widely** - LinkedIn, Twitter, portfolio
2. **Gather feedback** - Ask viewers for suggestions
3. **Iterate** - Add requested features
4. **Next project** - Apply learnings to new domain

**You now have:**
- ✅ Live, production-ready dashboard
- ✅ End-to-end data pipeline
- ✅ AI integration experience
- ✅ Deployment skills
- ✅ Strong portfolio piece

---

**🎉 Congratulations on deploying your project!**

*Built with 💚 by RK Jat*
