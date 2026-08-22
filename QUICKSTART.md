# ⚡ Nexia Quick Start (2 Minutes)

## 🚀 Install (30 seconds)

```bash
git clone https://github.com/aatizaz/nexia.git
cd nexia
```

## ⚙️ Setup (30 seconds)

```bash
python nexia-index.py --build --input ./docs
```

Creates `.nexia/index.json` (persistent, never rebuild).

## 🎉 Done!

Agent automatically knows what to do from `.nexia-config`.

---

## 🤖 How It Works

**Session 1:**
```
You: "Build auth endpoint"
Nexia: Reads .nexia-config → "I'll use Nexia"
Nexia: Queries only auth docs
Nexia: Builds endpoint
Nexia: Saves to memory
```

**Session 2:**
```
You: "Build payments"
Nexia: Checks memory → "Auth already built!"
Nexia: Reuses auth code
Nexia: Builds payments (75% fewer tokens!)
```

---

## 💰 Results

| Metric | Before | After |
|--------|--------|-------|
| Tokens/session | 245,992 | 74,049 |
| Cost/session | $0.98 | $0.03 |
| 100 features | $96 | $24 |

**Saves $72 per 100 features built** 🎯

---

## 📚 Learn More

- Full guide: `GUIDE.md`
- GitHub info: `GITHUB.md`
- This README: `README.md`

---

**That's it. Start building!** 🚀
