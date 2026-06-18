# Khabar Dashboard

The Streamlit-based B2B intelligence dashboard for Khabar.
Reads live data from the same Supabase database the scraper writes to.
Free hosting on Streamlit Community Cloud, free at MVP scale.

## What you need before starting

- A GitHub account (the one you already use for the scraper repo is fine)
- Access to your Supabase project `xxombbrgeppbhuklwhjc`
- A web browser

That's it. No Python install on your laptop. No command line.

## Deployment in five steps

### Step 1 — Create the users table in Supabase

1. Open Supabase, go to your project.
2. Left sidebar → **SQL Editor** → **New query**.
3. Open `setup.sql` from this repo, copy the contents, paste into the editor.
4. Click **Run**. You'll see "Success. No rows returned."

### Step 2 — Put the code in a new GitHub repo

The easiest way without command-line:
1. Go to https://github.com/new and create a new **private** repo named `khabar-dashboard`. Don't add a README or .gitignore; leave it empty.
2. On the new empty-repo page, click **uploading an existing file**.
3. Unzip `khabar-dashboard.zip` on your computer. Drag every file and folder from inside the unzipped folder into the upload area. (Important: drag the contents, not the wrapping folder itself.)
4. Scroll down, write a commit message ("Initial dashboard"), click **Commit changes**.

### Step 3 — Get your Supabase anon key

1. Supabase → **Project Settings** (gear icon) → **API**.
2. Find the section **Project API keys** → copy the value labelled `anon` `public`. It's a long string starting with `eyJ...`.

### Step 4 — Deploy on Streamlit Community Cloud

1. Go to https://share.streamlit.io and sign in with the same GitHub account.
2. Click **Create app** → **Deploy a public app from GitHub**.
3. Fill in:
   - **Repository**: `your-username/khabar-dashboard`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: pick something like `khabar-intel` (gives you `khabar-intel.streamlit.app`)
4. Click **Advanced settings**. In the **Secrets** field, paste exactly:

   ```
   [supabase]
   url = "https://xxombbrgeppbhuklwhjc.supabase.co"
   key = "PASTE_YOUR_ANON_KEY_HERE"
   ```

   Replace the placeholder with the anon key from Step 3.

5. Click **Deploy**. First build takes 2–4 minutes. You'll see the build log scroll past.

### Step 5 — Create your account in the app

When the deploy finishes, your browser opens the live app URL.

Because the `dashboard_users` table is empty, the app shows a **Create your account** form (not a login form). Fill it in:
- Choose a username (lowercase, no spaces — e.g. `mohamed`)
- Choose a password, at least 8 characters
- Confirm the password
- Full name and company are optional

Click **Create account**. The page refreshes into the normal Sign in form. Sign in with the username and password you just set.

You're in. The homepage shows the anomaly feed pulling real data from your scraper.

## Adding more users later

Open Supabase → **Table editor** → `dashboard_users` → **Insert row**. You'd need to bcrypt-hash their password — easiest is to run `make_password.py` in a GitHub Codespace (open your repo on github.com, press `.` to open the in-browser editor, open a terminal, run `pip install bcrypt && python make_password.py`).

Or, easier path: at week 2 I'll add an admin-only "Add user" page inside Settings so you can create new accounts directly from the dashboard. Until then, expect just your own account.

## Tiers

- `basic` — sees the four L1 sections plus the basic L2 product preview
- `pro` — adds Production Blueprint, Supply Chain Stress Index
- `enterprise` — everything

Your first account is automatically created as `enterprise`. To change a user's tier, edit the row in Supabase.

## Things that might go wrong

**"Module not found" error on deploy**
Streamlit Cloud installs from `requirements.txt`. If the build failed, check that file uploaded correctly.

**Login form shows immediately instead of "Create account"**
The `dashboard_users` table already has rows (perhaps from a test). To re-bootstrap, delete all rows from `dashboard_users` in Supabase.

**Anomaly feed is empty**
This means the scraper hasn't recorded a significant price drop, stockout-during-discount, or launch cluster in the last 24h. Trigger a manual scraper run or wait for the next scheduled one — the dashboard falls back to a 7-day pulse summary so the page is never empty.

**App is slow to open after deploy**
Streamlit Community Cloud "sleeps" apps that haven't been visited in a while. First visit after sleep takes 30–60s to wake up. Subsequent visits are instant.

## Files

```
khabar-dashboard/
├── streamlit_app.py          ← entry point + navigation
├── requirements.txt          ← Python dependencies
├── setup.sql                 ← creates the dashboard_users table
├── make_password.py          ← helper for adding extra users later (optional)
│
├── .streamlit/
│   ├── config.toml           ← Khabar dark theme
│   └── secrets.toml.example  ← template (real secrets go in Streamlit Cloud)
│
├── lib/
│   ├── auth.py               ← login, logout, bootstrap registration
│   ├── components.py         ← reusable UI parts
│   ├── db.py                 ← Supabase client
│   ├── queries.py            ← anomaly-feed queries
│   └── styles.py             ← Khabar CSS
│
└── views/
    ├── home.py               ← anomaly feed (homepage)
    ├── price.py              ← Price section (stubs in v1)
    ├── inventory.py          ← Inventory section (includes proof-template tab)
    ├── lifecycle.py          ← Lifecycle section stubs
    ├── competitive.py        ← Competitive section stubs
    ├── intelligence.py       ← L2 products directory
    └── settings.py           ← user preferences + sign out
```

## Cost

- Streamlit Community Cloud — free for unlimited public/private apps. Unlimited users.
- GitHub — free for private repos.
- Supabase — currently on free tier.

Total: **$0/month** for the dashboard.

## What ships next

- **Week 2** — Inventory → "Where is the market under-supplying?" fully built (heatmap + asymmetry index + opportunities table + dynamic Today's Read)
- **Week 3** — The other 11 L1 tabs replicate the template
- **Week 4** — First L2 product page
- **Week 5** — Remaining entry-bundle L2 products + soft launch
