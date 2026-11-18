# FitEats Instagram Scheduler (free)

Posts Reels, single images and carousels to **@fit_eats_25** at the time you choose, using Instagram's free official API and GitHub Actions. No paid scheduler needed.

**How it works:** every 15 minutes GitHub checks the `queue/` folder. Any post whose time has come is published to Instagram, then moved to `posted/` (with the Instagram link) or to `failed/` (with the reason).

> This repo is public so Instagram can download the images. Queued posts are visible here before they go live, but your login token is never stored in the code — it lives in GitHub Secrets.

---

## One-time setup (about 30 minutes)

### 1. Make Instagram a professional account
Instagram app → **Settings → Account type and tools** → make sure it says **Business** or **Creator**. (FitEats probably already is.)

### 2. Create a Meta app and get the Instagram token
1. Go to **developers.facebook.com** → log in with your Facebook → **My Apps → Create App**.
2. Name: `FitEats Scheduler` → choose the use case **"Manage messaging & content on Instagram"** → if it asks for a business portfolio, choose **"I don't want to connect a business portfolio yet"** → **Create app**.
3. Left menu **App roles → Roles → Add People → Instagram Tester** → type `fit_eats_25` → Add.
4. On your phone: Instagram → **Settings → Website permissions → Apps and websites → Tester invites** → **Accept**.
5. Back in the app: **Use cases → Manage messaging & content on Instagram → Customize → API setup with Instagram login**.
6. Under **"Generate access tokens"** click **Add account** → log in as `fit_eats_25` → **Allow** all permissions (keep "content publish" ticked).
7. Click **Generate token** next to fit_eats_25 → copy the long token. Keep it private.

### 3. Save the token in GitHub
Open this repo → **Settings → Secrets and variables → Actions → New repository secret**
- Name: `IG_TOKEN`  Value: the token from step 2.

### 4. Let GitHub renew the token automatically
Instagram tokens expire after 60 days; a weekly job renews it, and needs permission to save it.
1. Go to **github.com/settings/personal-access-tokens/new**
2. Name `fiteats-token-refresh`, Expiration **1 year** (or no expiration), Repository access **Only select repositories → fiteats-scheduler**.
3. Permissions → Repository permissions → **Secrets: Read and write** → **Generate token** → copy.
4. Add it as another repository secret: Name `GH_PAT`, Value: that token.

### 5. Test the connection
Repo → **Actions** tab → **Publish due posts** → **Run workflow** → mode **check** → Run.
A green tick and `Connected to Instagram: ... fit_eats_25` in the log means you're done.

---

## Adding a post

Easiest: send Claude the video/image and say when to post. Claude adds it to `queue/` for you.

By hand (GitHub website → `queue` → **Add file → Upload files**), make a folder like `queue/2026-11-22_1200_lunch-menu/` with:

| File | What |
|---|---|
| `post.json` | `{"time": "2026-11-22 12:00", "type": "reel"}` — time is Indian time; type is `reel`, `image` or `carousel` |
| `caption.txt` | the caption with hashtags |
| Reel | `video.mp4` (9:16, under 90 s) and optionally `cover.jpg` |
| Image | `image.jpg` (JPEG only) |
| Carousel | `1.jpg`, `2.jpg` … up to `10.jpg` |

**Timing:** GitHub runs every 15 minutes and can be a few minutes late at busy times, so a 7:45 PM post usually goes out between 7:45 and 8:05 PM.

**Limits:** Instagram allows up to 100 API posts a day — far more than you need.

## If something fails
GitHub emails you. The post moves to `failed/` with an `result.json` explaining why. Fix it and move the folder back into `queue/`.

`drafts/` is ignored by the scheduler — move a folder into `queue/` to schedule it.
