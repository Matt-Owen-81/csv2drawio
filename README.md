# 🧠 Drawio Diagram Generator

Generate structured Draw.io diagrams from YAML and CSV inputs using Python. This tool is perfect for visualizing hierarchical relationships like headers, sub-headers, and items in a clean, automated layout.

---

## 📦 Features

- ✅ Converts CSV data into a hierarchical diagram
- ✅ Configurable shape styles and layout via YAML
- ✅ Outputs `.drawio` XML compatible with [Draw.io](https://app.diagrams.net/)
- ✅ Simple, extensible Python script

---

## 📁 Input Files

### 1. `config.yaml` — Diagram & Shape Configuration

```yaml
page:
  width: 800
  height: 600
  background: "#ffffff"

shape:
  header:
    style: "rounded=1;fillColor=#dae8fc"
    width: 120
    height: 40
  subheader:
    style: "rounded=1;fillColor=#d5e8d4"
    width: 100
    height: 30
  item:
    style: "rounded=1;fillColor=#fff2cc"
    width: 80
    height: 25
```

### 2. `data.csv` — Hierarchical Data

```csv
Header,Sub-Header,Item
ABC,EDF,123
ABC,EDF,456
ABC,GHI,789
ABC,GHI,101112
ABC,GHI,131415
```

---

## 🚀 Usage

```bash
python generate_diagram.py
```

This will:

- Load `config.yaml` and `data.csv`
- Generate a `.drawio` XML file
- Save it as `diagram.drawio`

You can then open it in [Draw.io](https://app.diagrams.net/) via **File → Import from Device**.

---

## 🛠 Requirements

- Python 3.7+
- `pyyaml`

Install dependencies:

```bash
pip install pyyaml
```

---

## 🧩 Diagram Structure

```
[Header]
 └─ [Sub-Header]
      ├─ [Item]
      ├─ [Item]
```

Each header links to its sub-headers, which link to their respective items.

---

## 📌 Customization

- Modify `config.yaml` to change styles, dimensions, or layout.
- Extend the Python script to support multiple headers, dynamic spacing, or additional metadata.

---

## 📄 License

MIT — feel free to use, modify, and share.

---
