#!/usr/bin/env python3
"""
AgriSmart CLI — uv based, for judges (single image + batch dir + offline)
Usage:
  uv run agrismart predict --image leaf.jpg --topk 3
  uv run agrismart predict --dir images/ --out predictions.csv --topk 3
  uv run agrismart predict --image leaf.jpg --offline --json
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import track

# ensure repo root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from model.predict import predict_topk, ADVICE  # type: ignore

app = typer.Typer(add_completion=False, help="AgriSmart AI — Crop Disease CLI (ONNX Runtime -> HF -> heuristic)")
console = Console()

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

@app.command("predict")
def predict_cmd(
    image: Optional[Path] = typer.Option(None, "--image", "-i", help="Single image path"),
    dir: Optional[Path] = typer.Option(None, "--dir", "-d", help="Batch directory (scans all images recursively)"),
    topk: int = typer.Option(3, "--topk", "-k", min=1, max=5, help="Top-K predictions"),
    all_classes: bool = typer.Option(False, "--all-classes", help="Do not restrict to 28 shared classes"),
    offline: bool = typer.Option(False, "--offline", help="Do not download from HF Space"),
    json_out: bool = typer.Option(False, "--json", help="Output JSON to stdout"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="CSV output for batch mode"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose table"),
):
    if not image and not dir:
        console.print("[red]Provide --image or --dir[/red]")
        raise typer.Exit(2)
    if image and dir:
        console.print("[red]Use either --image or --dir, not both[/red]")
        raise typer.Exit(2)

    if image:
        if not image.exists():
            console.print(f"[red]Image not found: {image}[/red]")
            raise typer.Exit(1)
        top, engine = predict_topk(str(image), topk=topk, restrict=not all_classes, offline=offline)
        label = top[0][0]
        if json_out:
            console.print(json.dumps({"image": str(image), "prediction": label, "engine": engine, "topk": [{"label": l, "confidence": p} for l, p in top], "advice": ADVICE.get(label, "")}, indent=2))
        else:
            table = Table(title=f"AgriSmart — {image.name}  [engine: {engine}]", show_header=True)
            table.add_column("Rank", justify="right")
            table.add_column("Predicted Label", overflow="fold")
            table.add_column("Confidence", justify="right")
            for i, (l, p) in enumerate(top, 1):
                table.add_row(str(i), l, f"{p:.3f}" + f"  ({p:.1%})")
            console.print(table)
            if label in ADVICE:
                console.print(f"\n[bold]Advice:[/bold] {ADVICE[label]}")
            # last line must be bare label for pipe compatibility (SIH 4.1)
            console.print(label)
        return

    # batch mode
    assert dir is not None
    if not dir.exists():
        console.print(f"[red]Dir not found: {dir}[/red]")
        raise typer.Exit(1)
    images = [p for p in dir.rglob("*") if p.suffix.lower() in IMG_EXTS]
    if not images:
        console.print(f"[yellow]No images found in {dir}[/yellow]")
        raise typer.Exit(0)
    rows = []
    for p in track(images, description="Predicting..."):
        try:
            top, engine = predict_topk(str(p), topk=topk, restrict=not all_classes, offline=offline)
            rows.append({"image": str(p), "prediction": top[0][0], "confidence": f"{top[0][1]:.4f}", "engine": engine, "top3": json.dumps(top), "advice": ADVICE.get(top[0][0], "")})
        except Exception as e:
            rows.append({"image": str(p), "prediction": "ERROR", "confidence": "0", "engine": "error", "top3": str(e), "advice": ""})

    if json_out:
        console.print(json.dumps(rows, indent=2))
    else:
        table = Table(title=f"Batch — {len(rows)} images from {dir}", show_header=True)
        table.add_column("Image", overflow="fold", max_width=40)
        table.add_column("Prediction", overflow="fold")
        table.add_column("Conf", justify="right")
        table.add_column("Engine")
        for r in rows:
            table.add_row(Path(r["image"]).name, r["prediction"], r["confidence"], r["engine"])
        console.print(table)

    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["image", "prediction", "confidence", "engine", "advice"])
            w.writeheader()
            for r in rows:
                w.writerow({k: r[k] for k in ["image", "prediction", "confidence", "engine", "advice"]})
        console.print(f"[green]Wrote {len(rows)} rows to {out}[/green]")

@app.command("info")
def info():
    from model.predict import META, CLASSES, ALLOWED_CLASSES, IMG_SIZE
    console.print(f"[bold]Model:[/bold] {META.get('model')}")
    console.print(f"Classes: {len(CLASSES)} (allowed {len(ALLOWED_CLASSES)})  img_size={IMG_SIZE}  temp={META.get('temperature')}")
    console.print(f"HF Space: DakshBhavsar007/agrismart-crop-disease (repo_type=space)")
    console.print(f"Metrics: macro-F1 {META.get('metrics',{}).get('field_macro_f1_cnn')}  acc {META.get('metrics',{}).get('field_acc_cnn')}")

if __name__ == "__main__":
    app()
