# Push-to-Prod Hackathon – Project Submission Guide

## Required Fields

| Field | Details |
|---|---|
| `name` | Project name, 2–50 characters |
| `tagline` | 2–50 characters |
| `hashtags` | Technologies used, 1–10 entries (array) |
| `pictures` | 1–6 **real screenshots** of the running project. No AI-generated screenshots — grounds for disqualification. Store under `assets/` in project root. |
| `projectFieldAnswers` | Answers to all 4 organizer questions (see below) |

---

## Organizer Questions (all required)

All answers must be in **Markdown format** (headings, bold, bullet lists, code fences, multi-paragraph expected).

### 1. The problem your project solves
- UUID: `d3f5e1ee318f426a98fb0ff1105a5688`
- Placeholder: *Describe the problem your project solves.*
- Hint: Tell us what problem you are solving, why it is worth solving, and the impact it can have.

### 2. How you are solving it
- UUID: `f11c9bfcef62456ea62a96b7a2e6bd78`
- Placeholder: *Describe your solution to the problem.*
- Hint: Describe your approach, what you built, and how your solution works.

### 3. Use of Genspark
- UUID: `f8fbafeb71594d44876bd2892843f142`
- Placeholder: *Describe how you are using Genspark to solve your problem.*
- Hint: Tell us if and how you used Genspark in your project. What role did it play?

### 4. Use of Claude
- UUID: `d26a382a545f4efeacd497c03d3b4ac8`
- Placeholder: *Describe how you are using Claude in your project.*
- Hint: Tell us if and how you used Claude in your project. How did you integrate or leverage it?

---

## Optional but Strongly Recommended

| Field | Details |
|---|---|
| `links` | Array of 0–5 URLs. **Include a public Git repo URL** (GitHub/GitLab/Bitbucket). Repo must be public and URL must resolve — judges use this to verify authorship. |
| `video_url` | Demo or pitch video URL |
| `platforms` | Target platforms, 0–5 entries |
| `cover_img` | Cover image — storage path or URL. AI-generated branding OK here. |
| `favicon` | Project logo — storage path or URL. AI-generated branding OK here. |
| `problemSolved` | Narrative text (max 2000 chars). Pair with `challengesSurmounted` to build description blocks. |
| `challengesSurmounted` | Narrative text (max 2000 chars). Pair with `problemSolved`. |
| `status` | `draft` (default) or `publish` |
| `commitMessage` | 2–50 characters |
| `tracksToApplyTo` | Track UUID + application markdown (get UUIDs from `getHackathonTracksAndPrizes`) |

---

## Validation Rules

- Name: 2–50 characters
- Tagline: 2–50 characters
- Technologies (`hashtags`): 1–10 entries
- Pictures: 1–6 image references (storage path preferred over URL)
- Links: 0–5
- Platforms: 0–5
- Commit message: 2–50 characters
- Description blocks (non-empty): ≥ 10 characters each
- Do **not** pass a raw `description` field — the server builds it from `problemSolved` + `challengesSurmounted`
- `projectFieldAnswers` format: `{ projectFieldUUID, value }[]`

### Field Type Formatting for `projectFieldAnswers`

| Type | Format |
|---|---|
| `long` | Markdown — headings, bold, bullet lists, code fences. Multi-paragraph expected. |
| `short` | Plain single-line text, no Markdown |
| `url` | One valid URL |
| `image` | Storage path from `getSignedUploadUrl(project_field)` + PUT |
| `bool` | `"true"` or `"false"` |
| `radio` / `select` | Exactly one value from `options` |
| `checkbox` | Comma-separated subset of `options` |

---

## Screenshots Policy

- **Must be real screenshots** of the actual running project (UI, terminal output, diagrams from code, etc.)
- **Never use AI-generated screenshots** — misrepresents the project and is grounds for disqualification
- AI-generated imagery is only acceptable for branding: `favicon`, `cover_img`, logos, hero banners
- Organize all project assets under an `assets/` directory in the project root

---

## Image Upload Flow

1. Call `getSignedUploadUrl` with type `hackathon_project_pic`
2. PUT the image to the returned signed URL
3. Pass the returned storage path in the `pictures` array
