import gradio as gr
import os
import tempfile
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from pdf_processor import extract_text_from_pdf
from ai_engine import (
    generate_cover_letter,
    generate_cv_suggestions,
    generate_skills_highlight,
    generate_interview_questions,
    generate_salary_estimate,
)

CSS = """
* {
    font-family: "SF Mono", "SFMono-Regular", ui-monospace, Menlo, monospace !important;
    box-sizing: border-box !important;
}

:root {
    color-scheme: light !important;
    --block-border-width: 0px !important;
    --block-border-color: transparent !important;
    --border-color-primary: transparent !important;
    --border-color-accent: transparent !important;
}

html, body {
    margin: 0 !important;
    padding: 0 !important;
    background: #F2F2F7 !important;
    color: #1C1C1E !important;
}

.gradio-container {
    background: #F2F2F7 !important;
    padding: 0 !important;
    max-width: 100% !important;
    min-height: 100vh !important;
}

footer { display: none !important; }

/* ── iOS Navigation Bar ── */
#ios-nav {
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    height: 44px !important;
    background: rgba(249,249,249,0.94) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border-bottom: 0.5px solid rgba(60,60,67,0.29) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 16px !important;
}

.ios-nav-title {
    font-size: 17px;
    font-weight: 700;
    letter-spacing: -0.4px;
    background: linear-gradient(90deg, #007AFF 0%, #AF52DE 50%, #FF2D55 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Body layout ── */
#ios-body {
    padding: 0 20px 40px !important;
    gap: 20px !important;
    align-items: flex-start !important;
}

/* ── Section header with optional copy button ── */
.section-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 0 4px !important;
    min-height: 44px !important;
}

.ios-sh {
    font-size: 11px !important;
    font-weight: 400 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #6D6D72 !important;
    margin: 0 !important;
    padding: 0 4px !important;
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
}

/* iOS section footer */
.ios-sf {
    font-size: 11px !important;
    color: #6D6D72 !important;
    padding: 2px 4px 0 !important;
    margin: 0 !important;
    display: block !important;
}

/* Pull ios-sf wrappers up tight against the card above */
.block:has(> .ios-sf) {
    margin-top: -10px !important;
    padding-top: 0 !important;
}
/* Remove CV button — hidden until a file is loaded */
#cv-remove-btn {
    display: none !important;
}
body:has(#ios-cv .file-preview tr) #cv-remove-btn {
    display: block !important;
}
#cv-remove-btn button {
    background: #2C2C2E !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: -0.2px !important;
    width: 100% !important;
    height: 50px !important;
    cursor: pointer !important;
    box-shadow: none !important;
    transition: opacity 0.12s !important;
}
#cv-remove-btn button:hover { opacity: 0.8 !important; }

/* ── Copy button ── */
.copy-btn {
    font-size: 11px !important;
    color: #007AFF !important;
    background: transparent !important;
    border: none !important;
    cursor: pointer !important;
    padding: 2px 4px !important;
    border-radius: 4px !important;
    font-family: inherit !important;
    letter-spacing: 0 !important;
    transition: opacity 0.15s !important;
    flex-shrink: 0 !important;
}
.copy-btn:hover { opacity: 0.6 !important; }

/* ── Regenerate button (below output card) ── */
.regen-wrap button {
    background: transparent !important;
    color: #8E8E93 !important;
    border: none !important;
    font-size: 11px !important;
    cursor: pointer !important;
    padding: 5px 4px !important;
    font-family: inherit !important;
    width: 100% !important;
    text-align: left !important;
    box-shadow: none !important;
    transition: color 0.15s !important;
    border-radius: 0 !important;
    height: auto !important;
}
.regen-wrap button:hover { color: #007AFF !important; }

/* ── iOS white grouped card ── */
#ios-jobdesc, #ios-generate,
#ios-cover, #ios-cvsugg,
#ios-skills, #ios-interview, #ios-salary,
#ios-export {
    background: #FFFFFF !important;
    border-radius: 10px !important;
    border: none !important;
    overflow: hidden !important;
    margin-bottom: 0 !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* CV card has dark background — ios-row inside stays white */
/* CV card — colour matches the other dark output boxes */
#ios-cv {
    background: var(--input-background-fill) !important;
    border-radius: 10px !important;
    border: none !important;
    overflow: hidden !important;
    margin-bottom: 0 !important;
    box-shadow: none !important;
    padding: 0 !important;
    position: relative !important;
    min-height: 370px !important;
    display: flex !important;
    flex-direction: column !important;
}

/* ── Sticky left column ── */
#left-col {
    position: sticky !important;
    top: 44px !important;
}

/* ── iOS row inside card ── */
.ios-row {
    min-height: 44px;
    padding: 11px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    background: #FFFFFF;
    border-bottom: 0.5px solid rgba(60,60,67,0.18);
}

.ios-row:hover { background: #FFFFFF !important; }

/* Clickable upload row */
#ios-cv .ios-row {
    cursor: pointer !important;
}

.ios-row-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.icon-pink   { background: #FF2D55; }
.icon-blue   { background: #007AFF; }
.icon-purple { background: #AF52DE; }
.icon-green  { background: #34C759; }
.icon-orange { background: #FF9500; }
.icon-yellow { background: #FFCC00; }
.icon-teal   { background: #5AC8FA; }
.icon-gray   { background: #8E8E93; }

.ios-row-icon-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255,255,255,0.7);
}

.ios-row-label {
    font-size: 15px !important;
    color: #000000 !important;
    flex: 1 !important;
    margin: 0 !important;
}

.ios-row-value {
    font-size: 15px !important;
    color: #8E8E93 !important;
    margin: 0 !important;
}

.ios-chevron {
    color: #C7C7CC !important;
    font-size: 17px !important;
    font-weight: 500 !important;
    line-height: 1 !important;
}

/* ── Textarea inside card ── */
label > span, .label-wrap span { display: none !important; }

textarea {
    font-size: 13px !important;
    line-height: 1.65 !important;
    color: #FFFFFF !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 12px 16px !important;
    box-shadow: none !important;
    resize: vertical !important;
    caret-color: #007AFF !important;
    transition: none !important;
}

textarea:focus {
    outline: none !important;
    box-shadow: none !important;
    border: none !important;
    background: transparent !important;
}

textarea::placeholder { color: #C7C7CC !important; }

/* ── File upload ── */
#ios-cv label, #ios-export label { display: none !important; }

/* Custom visual dropzone — full-width, I own the layout */
#cv-dropzone {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 40px 16px;
    flex: 1 1 auto;
    pointer-events: none;
    color: rgba(255,255,255,0.6);
    text-align: center;
}
#cv-dropzone svg { stroke: rgba(255,255,255,0.45); margin-bottom: 4px; }
.cvdz-title { font-size: 14px !important; color: rgba(255,255,255,0.82) !important; margin: 0 !important; }
.cvdz-or    { font-size: 12px !important; color: rgba(255,255,255,0.35) !important; margin: 0 !important; }

/* Native .wrap — transparent, absolute overlay so it handles click + drag-drop */
#ios-cv .wrap {
    position: absolute !important;
    top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important;
    width: 100% !important;
    opacity: 0 !important;
    z-index: 5 !important;
    cursor: pointer !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
}

/* Upload button inside .wrap — also full-area */
#ios-cv button[aria-dropeffect="copy"] {
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important; height: 100% !important;
    opacity: 0 !important;
    cursor: pointer !important;
    z-index: 6 !important;
    border: none !important;
    background: transparent !important;
    padding: 0 !important; margin: 0 !important;
}

/* Once a file is loaded — hide the dropzone and overlay; show preview */
#ios-cv:has(.file-preview tr) #cv-dropzone           { display: none !important; }
#ios-cv:has(.file-preview tr) .wrap                  { display: none !important; }
#ios-cv:has(.file-preview tr) button[aria-dropeffect="copy"] { display: none !important; }

.file-preview-holder {
    padding: 12px 16px !important;
    background: transparent !important;
}

.file-preview {
    width: 100% !important;
    border-collapse: collapse !important;
    background: transparent !important;
}

.file-preview tbody tr {
    display: flex !important;
    align-items: center !important;
    background: #3A3A3C !important;
    background-color: #3A3A3C !important;
    border-radius: 10px !important;
    padding: 16px 16px !important;
    gap: 10px !important;
    min-height: 62px !important;
}

/* Hide the floating component-level clear box — use per-file × in the row */
#ios-cv .icon-button-wrapper {
    display: none !important;
}

.file-preview .filename,
.file-preview .filename .stem,
.file-preview .filename .ext {
    flex: 1 !important;
    font-size: 13px !important;
    color: #FFFFFF !important;
    padding: 0 !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
}

.file-preview .download,
.file-preview .download a {
    color: rgba(255,255,255,0.55) !important;
    font-size: 12px !important;
    white-space: nowrap !important;
}

.file-preview td { padding: 0 !important; }

/* label-clear-button hidden via JS; kept accessible for programmatic click */

#ios-export .upload-container,
#ios-export [data-testid="file"] {
    padding: 0 16px !important;
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
    background: transparent !important;
}

#ios-export svg {
    width: 16px !important;
    height: 16px !important;
    color: #007AFF !important;
}

/* ── Generate button — solid iOS blue ── */
#ios-generate button.primary {
    background: #007AFF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    letter-spacing: -0.2px !important;
    height: 50px !important;
    width: calc(100% - 24px) !important;
    margin: 12px !important;
    box-shadow: 0 2px 12px rgba(0,122,255,0.30) !important;
    transition: opacity 0.12s, transform 0.1s !important;
}

#ios-generate button.primary:hover {
    opacity: 0.88 !important;
    transform: scale(0.99) !important;
    box-shadow: 0 4px 20px rgba(0,122,255,0.45) !important;
}

/* ── Progress indicator ── */
#status-out { min-height: 0; }
#status-out .progress-wrap {
    padding: 10px 16px 14px;
}
#status-out .progress-label {
    font-size: 11px;
    color: #8E8E93;
    text-align: center;
    margin-bottom: 6px;
}
#status-out .progress-track {
    background: #E5E5EA;
    border-radius: 4px;
    height: 4px;
    overflow: hidden;
}
#status-out .progress-fill {
    background: #007AFF;
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}

@keyframes fadeout {
    0%   { opacity: 1; }
    70%  { opacity: 1; }
    100% { opacity: 0; }
}

/* ── Output empty state ── */
#ios-cover:has(textarea:placeholder-shown),
#ios-cvsugg:has(textarea:placeholder-shown),
#ios-skills:has(textarea:placeholder-shown),
#ios-interview:has(textarea:placeholder-shown),
#ios-salary:has(textarea:placeholder-shown) {
    background: #FAFAFA !important;
}

/* ── Normalize section header block wrappers ── */
.block:has(> .ios-sh),
.block:has(> .section-header) {
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Row gaps ── */
#out-row-bottom { gap: 24px !important; }

/* ── Strip Gradio chrome ── */
.block, .form, .panel, .wrap {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
"""

IOS_NAV = """
<div id="ios-nav">
    <span class="ios-nav-title">Job Application Assistant</span>
</div>
"""

SETUP_JS = """
<script>
(function() {
    function fixClearBtn(card) {
        card.querySelectorAll('.icon-button-wrapper, .label-clear-button').forEach(function(el) {
            el.style.setProperty('display', 'none', 'important');
        });
        card.querySelectorAll('.file-preview tr').forEach(function(tr) {
            tr.style.setProperty('background', '#2C2C2E', 'important');
            tr.style.setProperty('background-color', '#2C2C2E', 'important');
            tr.style.setProperty('border-radius', '10px', 'important');
        });
    }

    function setupCV() {
        var card = document.getElementById('ios-cv');
        if (!card) { setTimeout(setupCV, 500); return; }
        fixClearBtn(card);
        new MutationObserver(function() {
            setTimeout(function() { fixClearBtn(card); }, 80);
        }).observe(card, { childList: true, subtree: true });
    }
    setupCV();

    function setupCharCounter() {
        var jd = document.getElementById('ios-jobdesc');
        if (!jd) { setTimeout(setupCharCounter, 800); return; }
        var ta = jd.querySelector('textarea');
        if (!ta) { setTimeout(setupCharCounter, 800); return; }
        if (ta._counterWired) return;
        ta._counterWired = true;
        var counter = document.createElement('div');
        counter.style.cssText = 'font-size:11px;color:#8E8E93;padding:2px 4px;display:none;';
        jd.insertAdjacentElement('afterend', counter);
        ta.addEventListener('input', function() {
            var n = ta.value.length;
            counter.style.display = n > 0 ? 'block' : 'none';
            counter.style.color = n > 5000 ? '#FF3B30' : '#8E8E93';
            counter.textContent = n + ' chars' + (n > 5000 ? ' — long descriptions may slow results' : '');
        });
    }
    setTimeout(setupCharCounter, 1000);

    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.copy-btn[data-target]');
        if (!btn) return;
        var target = btn.dataset.target;
        var text;
        if (target === 'all') {
            var parts = ['ios-cover','ios-cvsugg','ios-skills','ios-interview','ios-salary']
                .map(function(id) { var el = document.querySelector('#' + id + ' textarea'); return el && el.value.trim() ? el.value : null; })
                .filter(Boolean);
            if (!parts.length) return;
            text = parts.join('\\n\\n---\\n\\n');
        } else {
            var el = document.querySelector('#' + target + ' textarea');
            if (!el || !el.value.trim()) return;
            text = el.value;
        }
        navigator.clipboard.writeText(text).then(function() {
            var orig = btn.textContent;
            btn.textContent = '✓ Copied';
            setTimeout(function() { btn.textContent = orig; }, 1600);
        });
    });
})();
</script>
"""


def sh(text, color):
    return gr.HTML(
        f'<span class="ios-sh" style="color:{color} !important;">{text}</span>'
    )


def sh_copy(text, color, target_id):
    return gr.HTML(f"""
<div class="section-header">
  <span class="ios-sh" style="color:{color} !important;padding:0 !important;">{text}</span>
  <button class="copy-btn" data-target="{target_id}">⎘ Copy</button>
</div>""")


def ios_sf(text):
    return gr.HTML(f'<span class="ios-sf">{text}</span>')



def ios_row_html(icon_class, label, value="", chevron=True):
    chev = '<span class="ios-chevron">›</span>' if chevron else ""
    val  = f'<span class="ios-row-value">{value}</span>' if value else ""
    return (
        f'<div class="ios-row">'
        f'<div class="ios-row-icon {icon_class}"><div class="ios-row-icon-dot"></div></div>'
        f'<span class="ios-row-label">{label}</span>'
        f'{val}{chev}</div>'
    )


def ios_row(icon_class, label, value="", chevron=True):
    return gr.HTML(ios_row_html(icon_class, label, value, chevron))


def progress_html(step_idx, step_name):
    pct = int((step_idx / 5) * 100)
    return (
        f'<div class="progress-wrap">'
        f'<div class="progress-label">Generating {step_name}… ({step_idx + 1}/5)</div>'
        f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>'
        f'</div>'
    )


def done_html():
    return '<p style="font-size:11px;color:#34C759;text-align:center;padding:10px 16px;margin:0;animation:fadeout 5s ease forwards">✓ All sections complete</p>'


def export_to_markdown(cover_letter, cv_suggestions, skills, interview_qs, salary):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(tempfile.gettempdir(), f"job_application_{timestamp}.md")
    content = f"""# Job Application Package

*Generated on {datetime.now().strftime("%B %d, %Y at %H:%M")}*

---

## Cover Letter

{cover_letter}

---

## CV Improvement Suggestions

{cv_suggestions}

---

## Top Skills to Highlight

{skills}

---

## Likely Interview Questions

{interview_qs}

---

## Salary Range Estimate

{salary}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def _extract_cv(cv_file):
    if cv_file is None:
        raise gr.Error("Please upload your CV as a PDF file.")
    try:
        cv_text = extract_text_from_pdf(cv_file)
    except Exception as e:
        raise gr.Error(str(e))
    if len(cv_text.strip()) < 100:
        raise gr.Error("CV text is too short. Please upload a text-based PDF, not a scanned image.")
    return cv_text


def _make_regen(generator_fn):
    def regen(cv_file, job_description):
        if not job_description or not job_description.strip():
            raise gr.Error("Please paste the job description first.")
        cv_text = _extract_cv(cv_file)
        result = ""
        try:
            for chunk in generator_fn(cv_text, job_description):
                result += chunk
                yield result
        except Exception as e:
            yield f"Error: {str(e)}"
    return regen


def process_application(cv_file, job_description):
    if not job_description or not job_description.strip():
        raise gr.Error("Please paste the job description.")
    cv_text = _extract_cv(cv_file)

    results = {k: "" for k in ("cover_letter", "cv_suggestions", "skills", "interview_qs", "salary")}

    steps = [
        ("cover_letter",   "Cover Letter",        generate_cover_letter),
        ("cv_suggestions", "CV Suggestions",      generate_cv_suggestions),
        ("skills",         "Skills Analysis",     generate_skills_highlight),
        ("interview_qs",   "Interview Questions", generate_interview_questions),
        ("salary",         "Salary Estimate",     generate_salary_estimate),
    ]

    for i, (key, name, fn) in enumerate(steps):
        try:
            for chunk in fn(cv_text, job_description):
                results[key] += chunk
                yield (
                    results["cover_letter"], results["cv_suggestions"],
                    results["skills"], results["interview_qs"], results["salary"],
                    progress_html(i, name), None,
                )
        except Exception as e:
            results[key] = f"Error: {str(e)}"
            yield (
                results["cover_letter"], results["cv_suggestions"],
                results["skills"], results["interview_qs"], results["salary"],
                f'<p style="font-size:11px;color:#FF3B30;text-align:center;padding:8px">⚠ {e}</p>',
                None,
            )

    yield (
        results["cover_letter"], results["cv_suggestions"],
        results["skills"], results["interview_qs"], results["salary"],
        done_html(),
        export_to_markdown(**results),
    )


def build_ui():
    with gr.Blocks(title="Job Application Assistant") as demo:

        gr.HTML(SETUP_JS)
        gr.HTML(IOS_NAV)

        with gr.Row(equal_height=False, elem_id="ios-body"):

            # ── Left column ───────────────────────────────────────────
            with gr.Column(scale=3, min_width=300, elem_id="left-col"):

                sh("CV Document", "#FF2D55")
                with gr.Group(elem_id="ios-cv"):
                    ios_row("icon-pink", "Upload PDF", chevron=False)
                    gr.HTML("""
<div id="cv-dropzone">
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
       fill="none" stroke="currentColor" stroke-width="1.5"
       stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
  <p class="cvdz-title">Drop File Here</p>
  <p class="cvdz-or">— or —</p>
  <p class="cvdz-title">Click to Upload</p>
</div>""")
                    cv_upload = gr.File(label="", file_types=[".pdf"], type="filepath")
                ios_sf("Select your CV or resume as a PDF file.")
                remove_cv_btn = gr.Button("Remove CV", elem_id="cv-remove-btn")

                sh("Job Description", "#007AFF")
                with gr.Group(elem_id="ios-jobdesc"):
                    ios_row("icon-blue", "Paste Description", chevron=False)
                    job_desc = gr.Textbox(
                        label="",
                        placeholder="Paste the full job description here...",
                        lines=12,
                    )

                sh("Actions", "#AF52DE")
                with gr.Group(elem_id="ios-generate"):
                    generate_btn = gr.Button(
                        "Generate Application Package",
                        variant="primary",
                        size="lg",
                    )
                    status_out = gr.HTML("", elem_id="status-out")

            # ── Right column ──────────────────────────────────────────
            with gr.Column(scale=5):

                sh_copy("Cover Letter", "#34C759", "ios-cover")
                with gr.Group(elem_id="ios-cover"):
                    cover_letter_out = gr.Textbox(
                        label="", lines=13,
                        placeholder="Your tailored cover letter will appear here...",
                    )
                with gr.Row(elem_classes=["regen-wrap"]):
                    rb_cover = gr.Button("↺  Regenerate cover letter", size="sm", visible=False)

                sh_copy("CV Suggestions", "#FF9500", "ios-cvsugg")
                with gr.Group(elem_id="ios-cvsugg"):
                    cv_suggestions_out = gr.Textbox(
                        label="", lines=10,
                        placeholder="Specific CV improvements will appear here...",
                    )
                with gr.Row(elem_classes=["regen-wrap"]):
                    rb_cv = gr.Button("↺  Regenerate CV suggestions", size="sm", visible=False)

                with gr.Row(equal_height=True, elem_id="out-row-bottom"):
                    with gr.Column():
                        sh_copy("Skills", "#FFCC00", "ios-skills")
                        with gr.Group(elem_id="ios-skills"):
                            skills_out = gr.Textbox(label="", lines=9, placeholder="Skills to highlight...")
                        with gr.Row(elem_classes=["regen-wrap"]):
                            rb_skills = gr.Button("↺  Regenerate", size="sm", visible=False)
                    with gr.Column():
                        sh_copy("Interview Questions", "#5AC8FA", "ios-interview")
                        with gr.Group(elem_id="ios-interview"):
                            interview_out = gr.Textbox(label="", lines=9, placeholder="Likely questions...")
                        with gr.Row(elem_classes=["regen-wrap"]):
                            rb_iq = gr.Button("↺  Regenerate", size="sm", visible=False)
                    with gr.Column():
                        sh_copy("Salary Estimate", "#FF2D55", "ios-salary")
                        with gr.Group(elem_id="ios-salary"):
                            salary_out = gr.Textbox(label="", lines=9, placeholder="Salary range...")
                        with gr.Row(elem_classes=["regen-wrap"]):
                            rb_salary = gr.Button("↺  Regenerate", size="sm", visible=False)

                gr.HTML("""
<div class="section-header">
  <span class="ios-sh" style="color:#5AC8FA !important;padding:0 !important;">Export</span>
  <button class="copy-btn" data-target="all">⎘ Copy All</button>
</div>""")
                with gr.Group(elem_id="ios-export"):
                    ios_row("icon-teal", "Download Markdown", chevron=True)
                    download_file = gr.File(label="")
                ios_sf("Save your complete application package as a Markdown file.")

        # ── Event wiring ──────────────────────────────────────────────
        all_outputs = [
            cover_letter_out, cv_suggestions_out,
            skills_out, interview_out, salary_out,
            status_out, download_file,
        ]

        remove_cv_btn.click(
            fn=lambda: gr.update(value=None),
            inputs=None,
            outputs=cv_upload,
            queue=False,
        )

        regen_btns = [rb_cover, rb_cv, rb_skills, rb_iq, rb_salary]

        def _lock():
            return [gr.update(interactive=False)] + [gr.update(visible=False)] * 5

        def _unlock():
            return [gr.update(interactive=True)] + [gr.update(visible=True)] * 5

        (
            generate_btn.click(
                fn=_lock, inputs=None, outputs=[generate_btn] + regen_btns,
            ).then(
                fn=process_application, inputs=[cv_upload, job_desc], outputs=all_outputs,
            ).then(
                fn=_unlock, inputs=None, outputs=[generate_btn] + regen_btns,
            )
        )

        for btn, fn, out in [
            (rb_cover,  generate_cover_letter,    cover_letter_out),
            (rb_cv,     generate_cv_suggestions,  cv_suggestions_out),
            (rb_skills, generate_skills_highlight, skills_out),
            (rb_iq,     generate_interview_questions, interview_out),
            (rb_salary, generate_salary_estimate, salary_out),
        ]:
            (
                btn.click(
                    fn=lambda b=btn: gr.update(interactive=False),
                    inputs=None, outputs=btn,
                ).then(
                    fn=_make_regen(fn), inputs=[cv_upload, job_desc], outputs=out,
                ).then(
                    fn=lambda b=btn: gr.update(interactive=True),
                    inputs=None, outputs=btn,
                )
            )

    return demo


if __name__ == "__main__":
    demo = build_ui()
    demo.queue()
    demo.launch(
        server_port=7860,
        share=False,
        allowed_paths=["/Users/test/Documents/job-assistant/"],
        theme=gr.themes.Base(
            primary_hue="blue",
            neutral_hue="gray",
        ),
        css=CSS,
    )
