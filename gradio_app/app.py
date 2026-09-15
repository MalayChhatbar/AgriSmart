"""
AgriSmart Gradio — Judge Demo (Core + Metrics)
Theme: oklch approximated to hex (no JS):
  bg #F6F7F2, primary #5B21B6 (oklch 0.51 0.23 276), secondary #0E9F8A (0.70 0.12 182),
  accent #F59E0B (0.76 0.16 70), border #000, ring #8B5CF6, radius 1rem
Run: uv run python gradio/app.py  OR  python gradio/app.py
"""
import os
import sys
import json
import tempfile
from pathlib import Path

import gradio as gr
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.predict import predict_topk, META, ADVICE

# oklch -> hex theme (approx)
COLORS = {
    "bg": "#F6F7F2",
    "primary": "#5B21B6",   # primary 0.51 0.23 276
    "primary_fg": "#FFFFFF",
    "secondary": "#0E9F8A", # secondary 0.70 0.12 182
    "accent": "#F59E0B",    # accent 0.76 0.16 70
    "border": "#111111",
    "muted": "#E8E9E3",
    "ring": "#8B5CF6",
}

CSS = f"""
:root {{
  --bg: {COLORS['bg']};
  --primary: {COLORS['primary']};
  --secondary: {COLORS['secondary']};
  --accent: {COLORS['accent']};
  --border: {COLORS['border']};
  --ring: {COLORS['ring']};
  --radius: 1rem;
}}
body, .gradio-container {{ background: var(--bg) !important; font-family: 'DM Sans', system-ui, sans-serif; }}
#header {{ background: var(--bg); border: 2px solid var(--border); border-radius: var(--radius); padding: 18px 20px; }}
#header h1 {{ margin: 0; font-size: 1.6rem; letter-spacing: -0.02em; }}
#header p {{ margin: 6px 0 0; color: #333; }}
.gradio-container .gr-button.primary {{ background: var(--primary) !important; color: var(--primary_fg) !important; border: 2px solid var(--border) !important; border-radius: 999px !important; }}
.gradio-container .gr-button.secondary {{ background: white !important; border: 2px solid var(--border) !important; border-radius: 999px !important; }}
.gr-box, .gr-panel, .gr-form {{ border: 2px solid var(--border) !important; border-radius: var(--radius) !important; box-shadow: none !important; }}
#metric-cards .metric {{ border: 2px solid var(--border); border-radius: var(--radius); padding: 14px; background: white; }}
#metric-cards .metric h3 {{ margin: 0; font-size: 0.9rem; color: #555; }}
#metric-cards .metric .val {{ font-size: 1.4rem; font-weight: 700; }}
.badge {{ display:inline-block; padding: 4px 10px; border-radius: 999px; border: 2px solid var(--border); font-size: 0.85rem; font-weight: 600; }}
.badge-primary {{ background: var(--primary); color: white; }}
.badge-secondary {{ background: var(--secondary); color: white; }}
.badge-accent {{ background: var(--accent); color: #111; }}
"""

def run_predict(img, topk, restrict):
    if img is None:
        return None, "Upload a leaf image.", "", {}
    # gradio Image type="pil" gives PIL
    if isinstance(img, dict) and "composite" in img:
        img = img["composite"]
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        # img is PIL
        if isinstance(img, Image.Image):
            img.save(tmp.name)
        else:
            Image.fromarray(img).save(tmp.name)
        tmp_path = tmp.name
    try:
        top, engine = predict_topk(tmp_path, topk=int(topk), restrict=restrict, offline=False)
        label, conf = top[0]
        advice = ADVICE.get(label, "No advice available.")
        # status badge
        tier = "confident" if conf >= 0.70 else "uncertain"
        conf_pct = f"{conf:.1%}"
        # build markdown
        status_color = COLORS['primary'] if conf >= 0.70 else COLORS['accent']
        md = f"""
<div style="border:2px solid {COLORS['border']}; border-radius:1rem; padding:16px; background:white;">
  <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
    <span class="badge badge-primary">Engine: {engine}</span>
    <span class="badge" style="background:{status_color}; color:white; border-color:{COLORS['border']}">{tier} • {conf_pct}</span>
    <span class="badge badge-secondary">{label.split('___')[0].replace('_',' ')}</span>
  </div>
  <h3 style="margin:12px 0 4px;">Prediction: <code>{label}</code></h3>
  <div style="font-size:1.1rem;">Confidence <b>{conf_pct}</b> (top-1)</div>
  <hr style="border:none; border-top:2px solid {COLORS['border']}; margin:12px 0;" />
  <h4 style="margin:0 0 6px;">Precaution / Treatment</h4>
  <p style="margin:0; line-height:1.5;">{advice}</p>
</div>
"""
        # table for topk
        table_md = "| Rank | Label | Confidence |\n|---|---|---|\n"
        for i, (l, p) in enumerate(top, 1):
            table_md += f"| {i} | `{l}` | {p:.3f} ({p:.1%}) |\n"
        probs = {l: float(p) for l, p in top}
        return probs, md, table_md, {"prediction": label, "engine": engine, "topk": top}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    return None, "", "", {}

def build_demo():
    with gr.Blocks(title="AgriSmart AI — Crop Disease Detector", css=CSS, theme=gr.themes.Soft(primary_hue="violet", secondary_hue="teal")) as demo:
        with gr.Column(elem_id="header"):
            gr.Markdown("# AgriSmart AI — Crop Disease Detection")
            gr.Markdown("Upload a leaf photo. Core model: `convnext_small.fb_in22k_ft_in1k` (38 classes, 28 shared) — ONNX Runtime → HF Space → heuristic fallback. Reports honest field metrics, not lab-inflated numbers.")

        with gr.Tabs():
            with gr.Tab("Detect"):
                with gr.Row():
                    with gr.Column():
                        inp_img = gr.Image(type="pil", label="Leaf image", height=360)
                        with gr.Row():
                            topk = gr.Slider(1, 5, value=3, step=1, label="Top-K")
                            restrict = gr.Checkbox(value=True, label="Restrict to 28 shared classes")
                        btn = gr.Button("Diagnose", variant="primary")
                        clear = gr.Button("Clear", variant="secondary")
                    with gr.Column():
                        out_label = gr.Label(num_top_classes=3, label="Top predictions")
                        out_md = gr.Markdown()
                        out_table = gr.Markdown()
                        out_json = gr.JSON(label="Raw JSON", visible=False)

                gr.Examples(
                    examples=[[str(ROOT / "model" / "sample_leaf.jpg"), 3, True]],
                    inputs=[inp_img, topk, restrict],
                    label="Try sample_leaf.jpg → Potato___Late_blight",
                )
                btn.click(fn=run_predict, inputs=[inp_img, topk, restrict], outputs=[out_label, out_md, out_table, out_json])
                clear.click(lambda: (None, None, "", ""), None, [inp_img, out_label, out_md, out_table])

            with gr.Tab("Metrics & Report"):
                m = META.get("metrics", {})
                with gr.Row(elem_id="metric-cards"):
                    with gr.Column(elem_classes="metric"):
                        gr.Markdown(f"### Macro-F1 (field)\n<div class='val'>{m.get('field_macro_f1_cnn', 0.7412):.4f}</div>\nPrimary metric (PlantDoc TEST 236 imgs)")
                    with gr.Column(elem_classes="metric"):
                        gr.Markdown(f"### Accuracy (field)\n<div class='val'>{m.get('field_acc_cnn', 0.75):.3f}</div>\nHeld-out field")
                    with gr.Column(elem_classes="metric"):
                        gr.Markdown(f"### Top-3\n<div class='val'>{m.get('field_top3', 0.966):.3f}</div>\nECE {m.get('field_ece', 0.05):.3f}")
                    with gr.Column(elem_classes="metric"):
                        gr.Markdown(f"### Lab Val F1\n<div class='val'>{m.get('lab_val_macro_f1', 0.997):.4f}</div>\nPlantVillage val (optimistic)")

                gr.Markdown("#### Confusion Matrix (TTA+MS+Restricted, 236 field images)")
                cm_path = ROOT / "report" / "confusion_matrix.png"
                if cm_path.exists():
                    gr.Image(value=str(cm_path), label="Confusion matrix", show_label=False, height=520)
                else:
                    gr.Markdown("*confusion_matrix.png missing — add from model/* to report/* after training*")

                gr.Markdown("#### Per-class report")
                pcr = ROOT / "report" / "per_class_report.txt"
                if pcr.exists():
                    gr.Code(value=pcr.read_text(encoding="utf-8")[:12000], language="text", label="per_class_report.txt")
                else:
                    gr.Markdown("*per_class_report.txt not found*")

                gr.Markdown("#### Model report (Section 7.3)")
                mr = ROOT / "report" / "model_report.md"
                if mr.exists():
                    gr.Markdown(value=mr.read_text(encoding="utf-8"))
                else:
                    gr.Markdown("*report/model_report.md missing*")

                with gr.Accordion("Advice dictionary (38 classes)", open=False):
                    adv = ROOT / "model" / "advice.json"
                    if adv.exists():
                        gr.JSON(value=json.loads(adv.read_text(encoding="utf-8")))
        gr.Markdown(f"<center style='opacity:0.6; font-size:0.85rem;'>HF Space: <code>DakshBhavsar007/agrismart-crop-disease</code> • Weights via <code>huggingface_hub</code> (repo_type=space) • ONNX stale warning if mismatched • <code>python model/predict.py --image path</code></center>")
    return demo

if __name__ == "__main__":
    demo = build_demo()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
