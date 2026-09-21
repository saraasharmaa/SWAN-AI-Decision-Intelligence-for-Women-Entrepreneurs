# How to Run NDAP Platform in VS Code

## Step-by-Step Guide (10 minutes)

### **Step 1: Open Project in VS Code**

```bash
# Open VS Code
open -a "Visual Studio Code" /Users/sarasharma/Downloads/womens_economic_empowerment_vscode
```

Or manually:
1. Open VS Code
2. File → Open Folder
3. Navigate to: `/Users/sarasharma/Downloads/womens_economic_empowerment_vscode`
4. Click "Open"

---

### **Step 2: Open Terminal in VS Code**

In VS Code menu:
- **View → Terminal** (or press `Ctrl + ~`)

Terminal should open at the bottom showing:
```
womens_economic_empowerment_vscode %
```

---

### **Step 3: Create Virtual Environment**

In the VS Code terminal, type:

```bash
python3 -m venv .venv
```

**Wait 30-60 seconds** for the virtual environment to be created.

You'll see a new `.venv` folder appear in the file explorer on the left.

---

### **Step 4: Activate Virtual Environment**

In VS Code terminal, type:

```bash
source .venv/bin/activate
```

After running, your terminal prompt should change to:
```
(.venv) womens_economic_empowerment_vscode %
```

The `(.venv)` prefix means the virtual environment is **active** ✅

---

### **Step 5: Install Dependencies**

In VS Code terminal, type:

```bash
pip install -r requirements.txt
```

**This will download and install:**
- pandas
- numpy
- matplotlib
- scikit-learn
- joblib
- flask
- flask-cors
- python-dotenv

**Wait 2-5 minutes** for installation to complete. You'll see:
```
Successfully installed [all packages]
```

---

### **Step 6: Select Python Interpreter (Important!)**

1. Press: `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows/Linux)
2. Type: `Python: Select Interpreter`
3. Choose: `./.venv/bin/python` (the one with .venv path)

You should see in the bottom-right of VS Code:
```
./.venv/bin/python (the one you selected)
```

---

### **Step 7: Run the Flask Server**

In VS Code terminal, type:

```bash
python ndap_app.py
```

You'll see:
```
╔════════════════════════════════════════════════════════════════════════════╗
║                 NDAP INTELLIGENCE PLATFORM                                 ║
║         Decision Support System for Women Entrepreneurs                    ║
╚════════════════════════════════════════════════════════════════════════════╝

🚀 Starting Flask Server...

📊 Available Endpoints:
   - GET  /                    → Dashboard UI
   - POST /api/recommend       → Generate recommendations
   - GET  /api/states          → List states
   - GET  /api/sectors         → List sectors
   - GET  /api/health          → Health check
   - POST /api/compare         → Compare profiles
   - POST /api/export/<format> → Export

🌐 Open in browser: http://localhost:5000

📁 Datasets loaded: PMMY, PLFS, Wages, Industry, Education, UDYAM
🔧 ML Engine: Initialized and ready
```

**The server is running!** ✅

---

### **Step 8: Open the Dashboard in Browser**

Click on the link or manually open:

```
http://localhost:5000
```

The NDAP dashboard will load with:
- Beautiful form on the left
- Dashboard preview on the right
- All 8 animated charts ready

---

### **Step 9: Test with Sample Data**

Fill in the form with Priya's profile:

```
Name: Priya Sharma
Age: 28
State: Rajasthan
City: Jaipur
Education: 10th Pass
Sector: Textile & Apparel
Employment: Self-Employed
Skills: Textile weaving & design
Income: 240000
Debt: 0
Loan Status: Disbursed
Loan Amount: 75000
Repayment: Perfect (100%)
Documents: Complete (All docs ready)
Household: 4 members, 2 children
```

Click: **"Generate Recommendation"**

**Wait 2-3 seconds** → All 8 charts animate and generate! 🎉

---

## ⏹️ Stop the Server

In VS Code terminal, press:
```
Ctrl + C
```

The server will stop. Terminal will show:
```
KeyboardInterrupt
(.venv) womens_economic_empowerment_vscode %
```

---

## 🔄 Restart the Server

After stopping, you can start again:

```bash
python ndap_app.py
```

---

## 📝 Common Issues & Fixes

### **Issue 1: "python3 command not found"**

**Solution:**
```bash
# Check if Python 3 is installed
python --version

# If that works, use:
python -m venv .venv
```

---

### **Issue 2: "Virtual environment not activating"**

**Check if (.venv) appears in prompt:**
```bash
# If not, try:
source .venv/bin/activate

# On Windows, use:
.venv\Scripts\activate
```

---

### **Issue 3: "Port 5000 already in use"**

**Solution - Use different port:**
```bash
# Edit the last line of ndap_app.py from:
app.run(debug=True, port=5000, host='0.0.0.0')

# To:
app.run(debug=True, port=5001, host='0.0.0.0')

# Then open:
http://localhost:5001
```

Or kill the process using port 5000:
```bash
lsof -i :5000
kill -9 <PID>
```

---

### **Issue 4: "Module not found" error**

**Solution - Reinstall dependencies:**
```bash
# Make sure virtual environment is active (check for .venv prefix)
pip install -r requirements.txt --force-reinstall
```

---

### **Issue 5: "Datasets not found"**

**Check that you have all 16 CSV files:**
```bash
ls -la data/raw/
```

You should see:
```
1.csv  2.csv  3.csv  4.csv  5.csv  6.csv  7.csv  8.csv
9.csv  10.csv 11.csv 12.csv 13.csv 14.csv 15.csv 16.csv
```

If missing, extract from `/Users/sarasharma/Desktop/DMA NITI.zip`

---

## 🛠️ Development Tips

### **Auto-reload on file changes**
Flask is already set to `debug=True`, so the server auto-reloads when you edit Python files.

### **Edit the HTML dashboard**
Edit: `ndap_prescriptive_dashboard.html`
- Refresh browser (Cmd+R) to see changes
- No server restart needed

### **Add new features**
Edit: `ndap_app.py` or `prescriptive_engine.py`
- Server auto-reloads
- Refresh browser

### **Debug mode**
Flask is running with `debug=True`, so:
- Detailed error messages in terminal
- Click "Traceback" in browser error for more info
- Check VS Code terminal for full stack trace

---

## 📊 Full Project Structure in VS Code

```
womens_economic_empowerment_vscode/
├── 📄 ndap_prescriptive_dashboard.html    ← Frontend (edit here)
├── 🐍 ndap_app.py                         ← Flask server (run this)
├── 🧠 prescriptive_engine.py              ← ML engine
├── 📂 data/
│   └── raw/
│       ├── 1.csv through 16.csv           ← Datasets
├── 📂 outputs/
│   └── (generated reports)
├── 📚 .venv/                              ← Virtual environment
├── 📋 requirements.txt                    ← Dependencies
├── 📖 RUN_IN_VSCODE.md                    ← This file
└── 📖 Other documentation files
```

---

## ✨ Full Workflow in VS Code

### **First Time Setup (5 minutes)**
1. Open project in VS Code
2. Open terminal (View → Terminal)
3. `python3 -m venv .venv`
4. `source .venv/bin/activate`
5. `pip install -r requirements.txt`
6. Select Python interpreter (Cmd+Shift+P)

### **Each Time You Use It (1 minute)**
1. Open VS Code project
2. Open terminal
3. `source .venv/bin/activate`
4. `python ndap_app.py`
5. Open `http://localhost:5000`

### **When You're Done**
1. In terminal: `Ctrl + C` (stop server)
2. Close VS Code
3. That's it!

---

## 🚀 Running Multiple Instances

Want to run two copies simultaneously?

**Terminal 1:**
```bash
source .venv/bin/activate
python ndap_app.py
# Runs on http://localhost:5000
```

**Open NEW terminal in VS Code** (Ctrl+Shift+`) then:

```bash
source .venv/bin/activate
python ndap_app.py  # But need to change port!
```

To avoid port conflict, edit line 2 of `ndap_app.py`:
```python
app.run(debug=True, port=5001, host='0.0.0.0')  # Different port
```

Then second copy runs on `http://localhost:5001`

---

## 📝 Using VS Code Extensions (Optional)

### **Recommended Extensions**
1. **Python** (by Microsoft) - Already installed likely
2. **Pylance** - Better Python IntelliSense
3. **Better Comments** - Color-code comments
4. **Thunder Client** - Test API endpoints without Postman

### **To test API endpoints in VS Code:**
1. Install "Thunder Client" extension
2. Open Thunder Client panel (left sidebar)
3. Create new request:
   - Method: POST
   - URL: `http://localhost:5000/api/recommend`
   - Body: JSON with woman's profile
   - Click Send

---

## 🔍 Debugging in VS Code

### **If something breaks:**

1. **Check VS Code terminal** for error messages
2. **Check browser console** (F12 → Console tab)
3. **Check Network tab** (F12 → Network) to see API responses
4. **Add print() statements** in Python to debug:

```python
# In ndap_app.py or prescriptive_engine.py
def my_function():
    print("Debug message here")  # This prints in VS Code terminal
    return result
```

5. **Restart the server** after making changes

---

## 💾 File Locations

When running from VS Code:

```
Current Working Directory: /Users/sarasharma/Downloads/womens_economic_empowerment_vscode

Data files load from:     ./data/raw/*.csv
Output files save to:     ./outputs/
Logs appear in:           VS Code Terminal
```

---

## 🎓 Quick Commands Reference

```bash
# Activate environment
source .venv/bin/activate

# Check Python version
python --version

# Check installed packages
pip list

# Install new package
pip install package_name

# Run the server
python ndap_app.py

# Run a Python script
python script_name.py

# Stop the server
Ctrl + C

# Exit virtual environment
deactivate
```

---

## ✅ Success Checklist

- [ ] Project opened in VS Code
- [ ] Terminal visible at bottom
- [ ] Virtual environment created (.venv folder visible)
- [ ] Virtual environment activated ((.venv) in prompt)
- [ ] Dependencies installed (pip install complete)
- [ ] Python interpreter selected (.venv/bin/python)
- [ ] Server running (Flask startup message visible)
- [ ] Browser opens to http://localhost:5000
- [ ] Dashboard visible with form and charts
- [ ] Sample data entered and recommendation generated
- [ ] All 8 charts animate and display

**If all checked ✅ → You're good to go!**

---

## 🎉 You're Ready!

The NDAP Platform is now running on your local machine via VS Code.

**You can now:**
- ✅ Enter woman entrepreneur profiles
- ✅ Get instant personalized recommendations
- ✅ View 8 beautiful animated charts
- ✅ Export recommendations
- ✅ Train field officers to use it

**Next Steps:**
1. Test with more profiles
2. Validate predictions against real outcomes
3. Train officers to use the dashboard
4. Deploy to districts

---

*Last Updated: September 2, 2026*
