# GitHub Pages Deployment Guide

## 🚀 Quick Setup

### 1. Enable GitHub Pages
1. Go to your repository: `https://github.com/whereismyguts/firedev`
2. Click **Settings** → **Pages**
3. Under **Source**, select **Deploy from a branch**
4. Choose **main** branch and **/ (root)** folder
5. Click **Save**

### 2. Move Files to Root (Option A - Simpler)
```bash
# Copy GitHub Pages files to root
cp docs/index.html ./github-pages-index.html
cp docs/config.js ./github-pages-config.js

# Then commit and push
git add .
git commit -m "Add GitHub Pages files"
git push
```

### 3. Use /docs folder (Option B - Cleaner)
1. In GitHub Settings → Pages, select **main** branch and **/docs** folder
2. The files are already in `/docs/` ready to go!

## 🔐 Security Notes

**✅ Safe to commit:**
- `apiKey` - Public Firebase client key
- `authDomain` - Public domain
- `projectId` - Public project identifier
- `databaseURL` - Public read endpoint (secured by database rules)

**❌ Never commit:**
- Service account JSON files (firebase-adminsdk.json)
- Private keys
- Bot tokens

## 🛡️ Firebase Security Rules

Your database is protected by these rules (already set):
```json
{
  "rules": {
    "locations": {
      ".read": true,
      ".write": "auth != null"
    }
  }
}
```

This means:
- ✅ Anyone can **read** the map data (for public viewing)
- ❌ Only **authenticated services** (your bot) can write data

## 🌐 Access Your Map

After deployment, your map will be available at:
- **https://whereismyguts.github.io/firedev/**

## 🔄 Update Bot Map URL

Update your bot code to use the GitHub Pages URL:

```python
# In bot/main.py, update the map URL:
await callback.message.edit_text(
    f"✅ **{category_emoji.get(category, '📍')} {category} location saved!**\n\n"
    f"View the map: https://whereismyguts.github.io/firedev/"
)
```

## 📝 Custom Domain (Optional)

To use your own domain (like `map.yourdomain.com`):

1. Add a `CNAME` file to `/docs/`:
```
map.yourdomain.com
```

2. Configure DNS with your domain provider:
```
CNAME   map   whereismyguts.github.io
```

## 🔧 Local Development

Test the GitHub Pages version locally:
```bash
cd docs
python -m http.server 8000
# Visit http://localhost:8000
```

## ✅ Verification Steps

1. ✅ GitHub Pages enabled and deployed
2. ✅ Map loads at your GitHub Pages URL
3. ✅ Firebase connection works (check browser console)
4. ✅ Bot updated with new map URL
5. ✅ Test: Send location via bot → appears on GitHub Pages map
