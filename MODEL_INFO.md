# Model Files Information

## rf_model.pkl (NOT in GitHub)

**File Size:** 95.54 MB

**Location:** This file is generated locally on your machine and NOT tracked in this repository.

### How to Get the Model

**Option A: Generate Locally (Recommended)**
```bash
python train_model.py
```
This will train a new Random Forest model using the balanced dataset.

**Option B: Download Pre-trained Model**
- Contact the development team
- Or download from: [Model Storage Link - TBD]
- Place in: `./rf_model.pkl`

### Model Information

- **Type:** Random Forest Classifier (100 trees)
- **Data:** 117,280 balanced samples (12.5% per major)
- **Accuracy:** 90.83% (on test set)
- **Features:** 9 academic subjects (Toán, Lý, Hóa, Sinh, Văn, Anh, Lịch sử, Địa lý, Tin học)
- **Classes:** 8 majors (IT, Kinh tế, Y khoa, Kỹ thuật, Nông-Lâm, Sư phạm, Luật, Du lịch)

### Using the Model

**To Run the App:**
```bash
streamlit run app.py
```
If `rf_model.pkl` doesn't exist, the app will automatically train it on first run.

**To Evaluate the Model:**
```bash
python evaluate_model.py
```

---

*Last Updated: 05/04/2026*
