# Accessibility Audit Pipeline

## Overview

A raw HTML file is too large and too noisy to pass directly to an LLM for
accessibility evaluation. This pipeline solves that by extracting only the
semantically relevant content, splitting it into focused slices, and sending
each slice to the LLM with a purpose-specific prompt.

The result is up to **21 targeted LLM calls** that together cover the full
WCAG evaluation defined by the three Deque checklist documents in
`semantic_checklist/`.

---

## Full Flow

```
home.html (1.9 MB, ~487k tokens)
    │
    │  Step 1 — Extract
    │
    ├── llm_preprocessing/semantic_checklist_01.py ──▶ cl01_payload.json (~17.6k tokens)
    ├── llm_preprocessing/forms_checklist_02.py    ──▶ cl02_payload.json (~2.5k tokens)
    └── llm_preprocessing/nontext_checklist_03.py  ──▶ cl03_payload.json (~19.2k tokens)
                                                        combined: ~39k tokens (92% reduction)
    │
    │  Step 2 — Slice & Call
    │
    ├── CL01 payload  ──▶  7 prompt slices  ──▶  7 LLM calls
    ├── CL02 payload  ──▶  6 prompt slices  ──▶  6 LLM calls
    └── CL03 payload  ──▶  8 prompt slices  ──▶  8 LLM calls
                                                  21 LLM calls total
    │
    │  Step 3 — Merge
    │
    └── 21 JSON responses ──▶ aggregate ──▶ accessibility report
```

---

## Step 1 — Extractors

Each extractor parses the raw HTML with BeautifulSoup and returns a structured
JSON payload. All CSS, JavaScript, layout divs, inline styles, analytics, and
image URLs are discarded.

### `semantic_checklist_01.py`

| Key | What it contains |
|---|---|
| `language` | `lang` attribute from `<html>` tag |
| `page_title` | `<title>` text + `<h1>` text |
| `headings` | All `<h1>`-`<h6>` elements with level and text |
| `flagged_links` | Links with no text, generic terms, or 2-word-or-fewer labels |
| `images` | Alt text presence categorised: missing / empty / has_alt |
| `forms` | Basic label presence per field |
| `buttons` | Unique button text / aria-label |
| `landmarks` | Semantic landmark elements + role= attributes |
| `tables` | Caption and header text (sampled) |
| `iframes` | Title attribute per iframe |

### `forms_checklist_02.py`

| Key | What it contains |
|---|---|
| `forms[].fields` | Per field: type, label text, label source, aria-label, aria-labelledby (resolved to text), title, placeholder, instructions (aria-describedby resolved to text), required flag, group label |
| `forms[].groups` | Fieldset/legend groups with legend text and input types inside |
| `orphan_labels` | Labels whose `for` attribute points to an element outside a form |

`label_source` is an enum that tells the LLM exactly how the field gets its accessible name:

| Value | Meaning |
|---|---|
| `label_for` | `<label for="id">` correctly linked |
| `wrapping_label` | `<label>` wraps the input directly |
| `aria_labelledby` | `aria-labelledby` points to another element |
| `aria_label` | `aria-label` attribute on the input |
| `title` | `title` attribute (last resort, not recommended) |
| `placeholder_only` | Only accessible name is placeholder — disappears on input |
| `none` | No accessible name found |

### `nontext_checklist_03.py`

| Key | What it contains |
|---|---|
| `images.informative` | Images with non-empty alt text + pre-detected alt_flags |
| `images.decorative` | Images with `alt=""` + surrounding text context |
| `images.actionable` | Images inside `<a>` or `<button>` + parent link/button context |
| `images.complex` | Images with chart/diagram/graph hints in filename or class |
| `svgs` | Non-hidden SVGs with role, title, desc, aria-label, aria-labelledby |
| `icon_fonts` | Font Awesome / Elementor / Dashicons icons with aria-hidden status, sibling text, and `sole_content` flag |
| `media` | Video and audio elements with track info |

`alt_flags` are pre-detected quality signals on informative images:

| Flag | Meaning |
|---|---|
| `looks_like_filename` | alt text ends in `.jpg`, `.png`, etc. |
| `redundant_phrase` | alt starts with "image of", "photo of", etc. |
| `too_long` | alt text exceeds 150 characters |

`sole_content` on icon fonts is `true` when the icon is the only content inside
a link or button — making `aria-hidden="true"` on it a critical failure
(the control has no accessible name).

---

## Step 2 — Prompt Slices

Each prompt lives in `processing_scripts/llm/` and contains a `{payload}`
placeholder that is filled with the relevant JSON slice before sending to the LLM.

### Checklist 01 — Semantic Structure (`semantic_checklist_01.txt`)

| # | Prompt | Payload slice | What the LLM judges |
|---|---|---|---|
| 1 | Page Title | `page_title` | Is the title descriptive and distinct? Does it match the H1? |
| 2 | Heading Structure | `page_title` + `headings` | Does the heading hierarchy form a logical content outline? Are headings meaningful? |
| 3 | Link Clarity | `flagged_links` | Is each short/generic link text clear when read out of context? |
| 4 | Table Semantics | `tables` | Is the caption meaningful? Do headers describe the data? Is this a data table or a layout table? |
| 5 | Iframe Titles | `iframes` | Does each iframe title clearly describe the iframe's purpose? |
| 6 | Landmark Structure | `landmarks` | Are multiple navs differentiated with aria-label? Is there a main landmark? Is the structure appropriate? |
| 7 | Combined Summary | full `cl01_payload` | High/medium/low priority issues, overall semantic quality score 0-100 |

### Checklist 02 — Forms (`forms_checklist_02.txt`)

| # | Prompt | Payload slice | What the LLM judges |
|---|---|---|---|
| 1 | Label Quality | All fields with an `effective_label` | Are labels descriptive, plain-language, and self-sufficient? |
| 2 | Placeholder-as-Label | Fields where `label_source = "placeholder_only"` | How severe is the impact? What should the visible label be? |
| 3 | Group Label Quality | All `forms[].groups` (fieldset/legend) | Does the legend provide enough context for radio/checkbox groups? |
| 4 | Required Field Indicators | Fields where `required: true` | Is required status communicated in the label or instructions, not just programmatically? |
| 5 | Form Instructions | Fields where `instructions` is non-null | Are aria-describedby instructions helpful, clear, and non-redundant? |
| 6 | Overall Form Summary | full `cl02_payload` | Patterns across all forms, high/medium/low issues, overall score 0-100 |

### Checklist 03 — Non-text Content (`nontext_checklist_03.txt`)

| # | Prompt | Payload slice | What the LLM judges |
|---|---|---|---|
| 1 | Informative Alt Quality | `images.informative` | Is alt text accurate, concise, and meaningful? Addresses any `alt_flags`. |
| 2 | Decorative Verification | `images.decorative` | Are empty-alt images genuinely decorative, or do they carry informational content? |
| 3 | Actionable Image Alt | `images.actionable` | Does the alt text describe the link destination or button action — not the image appearance? |
| 4 | Complex Descriptions | `images.complex` | Does the alt text or linked long description adequately convey the data in charts/diagrams? |
| 5 | SVG Accessibility | `svgs` | Is `role="img"` set? Is there a `<title>`? Is `aria-labelledby` linking to it? Is the title meaningful? |
| 6 | Icon Font Accessibility | `icon_fonts` | Is each icon correctly decorative (hidden) or informative (labelled)? Flags `sole_content` + `aria-hidden` as unlabeled controls. |
| 7 | Media Captions | `media` | Do videos have caption tracks? Does audio have controls? Are tracks labelled with srclang? |
| 8 | Overall Summary | full `cl03_payload` | Patterns across all non-text content, high/medium/low issues, overall score 0-100 |

---

## Step 3 — Output Format

Every prompt returns structured JSON. Example responses:

**Prompt 3 — Link Clarity:**
```json
[
  {
    "text": "here",
    "is_clear": false,
    "reason": "Generic term provides no destination context for screen reader users",
    "suggested_improvement": "Replace with destination page name, e.g. 'Learn about our vision programs'"
  }
]
```

**Prompt 6 — Icon Font Accessibility:**
```json
[
  {
    "classes": "fas fa-search",
    "aria_hidden": true,
    "sole_content": true,
    "pattern": "unlabeled_control",
    "issues": ["Search button has no accessible name — aria-hidden hides the only content"],
    "recommendation": "Add aria-label='Search' to the parent button element"
  }
]
```

**Summary prompts (CL01-7, CL02-6, CL03-8):**
```json
{
  "high_priority_issues": ["..."],
  "moderate_issues": ["..."],
  "low_priority_issues": ["..."],
  "patterns_observed": ["..."],
  "overall_score": 62
}
```

---

## File Map

```
visionaid-a11y-llm-audit/
│
├── semantic_checklist/               <- Deque WCAG reference documents (source of truth)
│   ├── 01-semantic-checklist.pdf
│   ├── 02-forms-checklist.pdf
│   └── 03-nontext-checklist.pdf
│
├── test_files/
│   └── home.html                     <- Raw HTML input (1.9 MB)
│
├── processing_scripts/
│   │
│   ├── llm_preprocessing/            <- Step 1: Extract structured payloads
│   │   ├── semantic_checklist_01.py  <- CL01 extractor (headings, links, landmarks...)
│   │   ├── forms_checklist_02.py     <- CL02 extractor (labels, groups, instructions...)
│   │   ├── nontext_checklist_03.py   <- CL03 extractor (images, SVG, icons, media...)
│   │   └── semantic_preprocessing_walkthrough.ipynb
│   │
│   └── llm/                          <- Step 2: Prompt library
│       ├── semantic_checklist_01.txt <- 7 prompts for CL01
│       ├── forms_checklist_02.txt    <- 6 prompts for CL02
│       └── nontext_checklist_03.txt  <- 8 prompts for CL03
│
└── docs/
    └── pipeline.md                   <- this file
```

---

## Key Numbers (visionaid.org homepage)

| | Raw HTML | CL01 | CL02 | CL03 | All 3 |
|---|---|---|---|---|---|
| Tokens | ~487,000 | ~17,600 | ~2,500 | ~19,200 | ~39,300 |
| Reduction | baseline | 96% | 99% | 96% | 92% |
| LLM calls | — | 7 | 6 | 8 | **21** |

---

## LLM Settings

All prompts are designed to be run with:

- **Temperature**: 0.1 — low randomness for consistent, deterministic output
- **JSON mode**: on — enforce structured responses
- **Model**: Any capable instruction-following model (Claude Sonnet 4.6, GPT-4o, etc.)
