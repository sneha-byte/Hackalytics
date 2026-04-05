# Hackalytics 

 **Live App:** https://hackalytics-eq2iqkxqwylq3pzbp9vf7b.streamlit.app  

Hackalytics is an interactive data dashboard that analyzes hackathon trends from **2009 → 2025** using real project data. It helps answer a simple but powerful question:

> *What are hackers building, using, and focusing on over time?*

---

##  What It Does

Hackalytics breaks down hackathon trends into three core insights:

### 1. What problems are hackers focused on?
We analyze project descriptions to surface recurring themes and keywords.

- Word cloud of common ideas  
- Theme trends over time  

**Example (2025):**  
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/392fa722-99a8-40d8-a6ec-c80dc4227701" />
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/afcf1f0d-836d-4a3e-96c1-0e299fc71cf7" />

---

### 2. What tools are hackers using?
We track the technologies used in projects across years.

- Bar chart of most-used tools  
- Distribution breakdown of tech stacks  

**Example (2025):**  
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/2ca6d9e6-3d74-46ca-bb63-60cd2482c557" />

---

### 3. Where are hackathons being held?
We visualize global hackathon distribution using location data.

- Interactive map  
- Top locations by year  

**Example:**  
<img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/d40c4672-2067-4ee6-bb56-153cdce61e7b" />

---

##  How It Works

- Cleaned and processed hackathon + project datasets  
- Extracted:
  - Themes  
  - Tools ("built with")  
  - Locations  
- Aggregated trends by year  
- Built an interactive dashboard using **Streamlit**

To improve performance, we used caching so data only loads once instead of reprocessing on every interaction.

---

##  Tech Stack

- **Python**
- **Pandas**
- **Streamlit**
- **PyDeck**
- **Matplotlib**
- **WordCloud**

---

##  How to Run Locally

1. Clone the repository:
```bash
git clone https://github.com/sneha-byte/Hackalytics.git
cd Hackalytics
```

2. Set up python virtual environment and install dependencies
3. Scrape data
```bash
  cd scraping
  python3 scrape_hackathons.py
  python3 run_chunks 0 9
  scrapy crawl HackathonLocationSpider -O ../data/locations.csv -a dataset="../data/hackathons.csv"
```
5. Process data.
  - Set up .env file for geocoding
     ```.env
      GOOGLE_MAPS_API_KEY=<your key>
     ```
  - Run process.ipynb
  - Run analysis.ipynb
5. Deplot streamlit dashboard
```bash
  cd app
  streamlit run Home.py
 ```
