---

# 🧠 Drawio Diagram Generator

Generate structured Draw.io diagrams from YAML and CSV inputs using Python. This tool automates layout based on your manually refined design, making it scalable and reproducible.

---

## 📦 Features

- ✅ Converts CSV data into hierarchical diagrams
- ✅ Configurable shape styles and layout via YAML
- ✅ Deterministic positioning based on header/subheader/item logic
- ✅ Outputs `.drawio` XML compatible with [Draw.io](https://app.diagrams.net/)
- ✅ Git-integrated workflow for version control on Ubuntu

---

## 📁 Input Files

### 1. `config.yaml` — Page, Shape & Layout Configuration

```yaml
page:
  width: 1200           # width of page in points
  height: 800           # height of page in points
  background: "#ffffff" # background color of page
  grid: 1               # show grid (1 = true, 0 = false)
  gridSize: 10          # size of grid squares
  guides: 1             # show alignment guides
  tooltips: 1           # show tooltips
  connect: 1            # enable connector snapping
  arrows: 1             # show arrows on connectors
  fold: 1               # allow folding of groups
  pageScale: 1          # scale factor for page
  pageWidth: 1200       # width of printable page
  pageHeight: 800       # height of printable page

shape:
  header:
    style: "rounded=1;fillColor=#dae8fc"
    width: 140
    height: 40
  subheader:
    style: "rounded=1;fillColor=#d5e8d4"
    width: 120
    height: 40
  item:
    style: "rounded=1;fillColor=#fff2cc"
    width: 100
    height: 25

layout:
  header_x: 40                # starting x position for header
  header_y: 40                # starting y position for header
  subheader_x: 40             # fixed x position for subheaders
  subheader_spacing_y: 40     # vertical spacing between subheaders
  item_spacing_x: 40          # horizontal spacing between subheader and item
  item_spacing_y: 35          # vertical spacing between items
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

## 🧩 Layout Logic

- **Header** starts at `(40, 40)` — top-left corner.
- **Subheaders** stack vertically down the left, spaced by header height and `subheader_spacing_y`.
- **Items** align to the right of subheaders, spaced horizontally by `item_spacing_x` and vertically by `item_spacing_y`.

This layout matches your manually refined diagram and scales cleanly across multiple headers and subheaders.

---

## 🚀 Usage

```bash
python generate_diagram.py
```

This will:

- Load `config.yaml` and `data.csv`
- Generate a `.drawio` XML file
- Save it as `diagram.drawio`

Open it in [Draw.io](https://app.diagrams.net/) via **File → Import from Device**.

---

## 🛠 Requirements

- Python 3.7+
- `pyyaml`

Install dependencies:

```bash
pip install pyyaml
```

---

## 🧪 Git Workflow on Ubuntu Dev Server

To version control your diagram generator:

### 1. Initialize Git repo

```bash
git init
git remote add origin git@github.com:yourusername/yourrepo.git
```

### 2. Stage and commit changes

```bash
git add .
git commit -m "Initial commit with layout logic and config"
```

### 3. Push to GitHub

```bash
git push -u origin main
```

### 4. Pull updates from GitHub

```bash
git pull origin main
```

### 5. Check status and log

```bash
git status
git log --oneline
```

---

## 📄 License

MIT — feel free to use, modify, and share.

---
