import os

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Load processed projects data
def load_processed_projects():
    return pd.read_csv("data/processed/processed_projects.csv")

# Generate word cloud for a given year
def generate_word_cloud(year):
    #df = load_processed_projects()

    font_paths = [
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\Arial.ttf",
    ]

    font_path = next((f for f in font_paths if os.path.exists(f)), None)


    test_df = pd.DataFrame({
        'year': [2020, 2020, 2021, 2021],
        'clean_text': ['data science machine learning', 'deep learning ai', 'data analysis visualization', 'machine learning ai']
    })
    df=test_df

    year_df = df[df["year"] == year]

    # Join all cleaned text from that year into one big string
    text = " ".join(year_df["clean_text"].fillna("")) #or whatever column has the cleaned texts

    stopwords = set(WordCloud().stopwords)
    # Remove stopwords and very short words
    text = ' '.join(word for word in text.split() if word not in stopwords and len(word) > 2)

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color="white", font_path=font_path).generate(text)

    # Display the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"Word Cloud for Year {year}")
    plt.show()

if "__main__" == __name__:
    generate_word_cloud(2020)