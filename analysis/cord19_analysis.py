# analysis_simple.py
import pandas as pd
import matplotlib.pyplot as plt
import re
import os

def run_simple_analysis():
    """Run a simple analysis on a small sample"""
    file_path = "data/small_metadata.csv"
    
    if not os.path.exists(file_path):
        print("Small sample not found. Please run create_small_sample.py first.")
        return
    
    # Load the small sample
    df = pd.read_csv(file_path)
    
    # Basic cleaning
    df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
    df['year'] = df['publish_time'].dt.year
    df['journal'] = df['journal'].fillna('Unknown')
    
    # Ensure directories exist
    os.makedirs('images', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    # Simple analysis 1: Publications by year
    yearly_counts = df['year'].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    yearly_counts.plot(kind='bar')
    plt.title('Number of Publications by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('images/publications_by_year.png')
    plt.close()
    
    # Simple analysis 2: Top journals
    top_journals = df['journal'].value_counts().head(10)
    plt.figure(figsize=(12, 6))
    top_journals.plot(kind='bar')
    plt.title('Top 10 Journals by Publication Count')
    plt.xlabel('Journal')
    plt.ylabel('Number of Publications')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('images/top_journals.png')
    plt.close()
    
    # Save results
    yearly_counts.to_csv('results/yearly_counts.csv')
    top_journals.to_csv('results/top_journals.csv')
    
    print("Simple analysis complete! Results saved to images/ and results/ directories.")

if __name__ == "__main__":
    run_simple_analysis()