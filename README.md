# CORD-19 Dataset Analysis  

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)  
[![Streamlit](https://img.shields.io/badge/Streamlit-Enabled-brightgreen.svg)](https://streamlit.io/)  
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  

## 📌 Project Overview  

This project provides a comprehensive analysis of the **CORD-19 dataset**, which contains metadata about COVID-19 research papers. It includes both analysis scripts and an **interactive Streamlit web application** for data exploration.  

The implementation is **optimized for systems with limited memory (4GB RAM)** by using chunked data processing, selective column loading, and small-sample datasets for quick testing.  

---

## 📂 Project Structure  

```

Frameworks_Assignment/
├── data/
│   ├── metadata.csv           # Original dataset (excluded from repo)
│   └── small_metadata.csv     # Sample dataset (2000 rows)
├── analysis/
│   ├── cord19_analysis.py     # Original full analysis script
│   ├── simple_analysis.py     # Simplified analysis for small datasets
│   └── create_small_sample.py # Script to generate small dataset sample
├── images/                    # Generated visualizations
├── results/                   # Saved analysis results
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation

````

---

## ⚙️ Installation and Setup  

### ✅ Prerequisites  

- Python **3.7+**  
- At least **4GB RAM**  

### 🚀 Step-by-Step Setup  

1. **Clone the repository**  

   ```bash
   git clone <your-repo-url>
   cd Frameworks_Assignment

    ````

2. **Create and activate a virtual environment**

   ```bash
   python -m venv myenv
   source myenv/bin/activate  # Linux/Mac
   myenv\Scripts\activate     # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Download and prepare data**

   - Download `metadata.csv` from Kaggle
   - Place it inside the `data/` directory
   - Generate a smaller dataset (2000 rows):

     ```bash
     python create_small_sample.py
     ```

---

## 📊 Usage

### ▶️ Running the Analysis

```bash
python analysis/analysis_simple.py
```

### 🌐 Launching the Web Application

```bash
streamlit run app.py
```

---

## ✨ Key Features

### 🛠 Data Optimization

- **Memory-efficient processing**: chunked reading & sampling
- **Small sample mode**: lightweight analysis for 4GB RAM systems
- **Selective column loading**: only necessary fields are processed

### 🔎 Interactive Exploration

- **Temporal filtering**: explore publications by year range
- **Journal analysis**: identify top publishing venues
- **Text analysis**: word frequency in titles & abstracts
- **Data sampling**: interactively browse filtered results

### 📈 Visualization Capabilities

- Publication trends over time
- Journal publication rankings
- Word frequency distributions
- Optional **word cloud generation**

---

## 📑 Key Findings

- **Temporal patterns**: COVID-19 publications surged dramatically in **2020**
- **Journal distribution**: top publishers include *BMJ*, *Lancet*, and other medical journals
- **Terminology analysis**: frequent terms include *covid*, *pandemic*, *sars*, *coronavirus*
- **Temporal concentration**: majority of papers were published in **2020–2021**

---

## 🔧 Technical Implementation

### Optimization Strategies

- **Chunked processing** for large files
- **Memory-aware data types** to reduce RAM footprint
- **Selective loading** of essential columns
- **Progress indicators** for user feedback

### Performance Considerations

- Defaults to **small sample mode** for better performance
- **Word cloud generation optional** (memory-heavy)
- Full dataset analysis available (requires longer runtime)

### Challenges & Solutions

| Challenge             | Solution                                 |
| --------------------- | ---------------------------------------- |
| Memory limitations    | Implemented chunked reading & sampling   |
| Long processing time  | Created smaller sample datasets          |
| Dependency issues     | Removed unnecessary packages             |
| Large text processing | Limited sampling & efficient word counts |

---

## 💡 Development Experience

Through this project, the following skills were applied and enhanced:

- Data processing under **memory constraints**
- Exploratory analysis of **large datasets**
- Visualization with **matplotlib** & **seaborn**
- Interactive dashboards with **Streamlit**
- Resource optimization techniques

---

## 🔮 Future Enhancements

- Advanced NLP (sentiment analysis, topic modeling)
- Database integration for faster querying
- Recommendation features (paper similarity search)
- Cloud deployment for full dataset analysis

---
