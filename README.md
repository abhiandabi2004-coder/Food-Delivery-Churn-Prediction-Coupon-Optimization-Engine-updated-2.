# 📊 Customer Value Intelligence Platform Using RFM Analytics

## 📌 Business Context

In competitive consumer businesses such as food delivery platforms, understanding customer behavior is critical for retention and revenue growth.

Traditional dashboards often fail to segment customers meaningfully.  
This project builds a percentile-based RFM (Recency, Frequency, Monetary) intelligence engine to identify high-value customers, churn risk users, and behavioral segments.

---

## 🎯 Objective

To design an interactive, executive-ready customer analytics dashboard that:

- Performs percentile-based RFM scoring
- Segments customers into meaningful business groups
- Identifies most preferred products per segment
- Tracks revenue trends over time
- Enables data-driven marketing decisions

---

## 🧠 Methodology

### 1️⃣ RFM Calculation

- **Recency** – Days since last purchase
- **Frequency** – Total number of purchases
- **Monetary** – Total revenue contribution

---

### 2️⃣ Percentile-Based Scoring

**Recency (Reverse Scoring)**  
- 20th percentile → 5  
- 40th percentile → 4  
- 60th percentile → 3  
- 80th percentile → 2  
- 100th percentile → 1  

(Lower recency is better, hence reverse scoring)

**Frequency & Monetary (Normal Scoring)**  
- 20th percentile → 1  
- 40th percentile → 2  
- 60th percentile → 3  
- 80th percentile → 4  
- 100th percentile → 5  

(Higher values indicate stronger engagement)

---

### 3️⃣ Combined RFM Score

Each customer receives a 3-digit score.

Example:

Recency = 5  
Frequency = 4  
Monetary = 3  

Final RFM Score = 543

This allows precise behavioral segmentation.

---

## 👥 Customer Segments

Customers are grouped into five actionable segments:

1. Champion Customer  
2. Loyal Customer  
3. Fence Sitter  
4. At Risk Customer  
5. Churned Customer  

Segmentation is based on RFM score patterns and behavioral strength.

---

## 📊 Dashboard Features

### 🔹 KPI Overview
- Total Customers
- Total Revenue
- Champion Customers
- At Risk Customers
- Last Updated Timestamp

### 🔹 Customer Segment Distribution
Visual breakdown of all five segments.

### 🔹 Monthly Revenue Trend
Line chart showing revenue performance across the year.

### 🔹 Recency & Frequency Comparison
Bar chart comparing behavioral patterns across segments.

### 🔹 Most Preferred Product by Segment
Identifies dominant product preference per customer group.

### 🔹 Detailed RFM Table
Customer-level scoring and segmentation.

---

## 📂 Dataset

- 1200 unique customers
- Full 1-year transactional data (Jan–Dec)
- 5–25 orders per customer
- Multiple product categories
- Suitable for percentile-based segmentation

---

## 🛠 Tech Stack

- Python
- Pandas
- NumPy
- Plotly
- Streamlit

---

## 🚀 How to Run Locally

pip install -r requirements.txt  
streamlit run app.py

---

## 💡 Business Impact

This dashboard enables:

- Identification of high-value customers
- Early detection of churn risk
- Targeted marketing interventions
- Product preference analysis by segment
- Strategic revenue monitoring

Designed with clarity, prioritization, and executive usability in mind.

---

## 📈 Use Case Applications

- Food Delivery Platforms
- E-commerce Businesses
- Retail Customer Analytics
- Subscription-Based Businesses
