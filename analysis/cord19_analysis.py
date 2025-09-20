import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from datetime import datetime

# Define a variable for the chunk size
CHUNK_SIZE = 100

# Helper function to infer optimal data types
def get_optimal_dtypes(df):
    """Infer optimal data types to reduce memory usage."""
    # This is a simplified approach; in a real-world scenario, you might analyze
    # string columns to determine if they can be 'category' types.
    return {col: 'category' for col in df.select_dtypes(include='object').columns}

# Load the data
def load_data(file_path):
    """Load the metadata.csv file using an absolute path and return an iterator."""
    
    print(f"Looking for file at: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find the file at {file_path}")

    # Get optimal dtypes from a sample to reduce memory usage for the full load
    try:
        sample_df = pd.read_csv(file_path, nrows=10000, low_memory=False)
        optimal_dtypes = get_optimal_dtypes(sample_df)
    except Exception as e:
        print(f"Could not infer optimal dtypes from a sample. Proceeding without dtype optimization. Error: {e}")
        optimal_dtypes = None

    # Convert string dtypes to numpy dtypes
    if optimal_dtypes:
        for col, dtype_str in optimal_dtypes.items():
            try:
                optimal_dtypes[col] = str(pd.api.types.pandas_dtype(dtype_str))
            except TypeError as e:
                print(f"Could not convert dtype for column {col}: {e}. Skipping dtype conversion.")
                del optimal_dtypes[col]

    # Return an iterator for chunked reading
    return pd.read_csv(file_path, chunksize=CHUNK_SIZE, dtype=optimal_dtypes)

# Basic exploration (on a sample chunk)
def explore_data(df_chunk):
    """Perform basic data exploration on a single chunk."""
    print("Exploring a sample chunk of the dataset...")
    print("Dataset dimensions (chunk):", df_chunk.shape)
    print("\nColumn names and data types (chunk):")
    print(df_chunk.dtypes)
    print("\nMissing values per column (chunk):")
    print(df_chunk.isnull().sum())
    print("\nBasic statistics for numerical columns (chunk):")
    print(df_chunk.describe(include='all'))
    return df_chunk

# Data cleaning functions
def clean_data(df):
    """Clean and prepare a chunk of the dataset for analysis."""
    df_clean = df.copy()

    # Convert publish_time to datetime
    df_clean['publish_time'] = pd.to_datetime(df_clean['publish_time'], errors='coerce')

    # Extract year from publication date
    df_clean['year'] = df_clean['publish_time'].dt.year

    # Create abstract word count column
    df_clean['abstract_word_count'] = df_clean['abstract'].apply(
        lambda x: len(str(x).split()) if pd.notnull(x) else 0
    )

    # Handle missing values in important columns
    # This is the corrected section to handle the 'Categorical' type error
    if 'journal' in df_clean.columns and isinstance(df_clean['journal'].dtype, pd.CategoricalDtype):
        if 'Unknown' not in df_clean['journal'].cat.categories:
            df_clean['journal'] = df_clean['journal'].cat.add_categories('Unknown')
    
    df_clean['journal'] = df_clean['journal'].fillna('Unknown')
    
    return df_clean

def handle_missing_values_chunked(file_path):
    """Analyze missing values by processing the file in chunks."""
    missing_data_total = pd.Series(dtype=int)
    total_rows = 0
    
    try:
        chunk_iterator = pd.read_csv(file_path, chunksize=CHUNK_SIZE)
        for chunk in chunk_iterator:
            total_rows += len(chunk)
            missing_data_total = missing_data_total.add(chunk.isnull().sum(), fill_value=0)
            
        missing_percent = (missing_data_total / total_rows) * 100
        
        missing_info = pd.DataFrame({
            'Missing Values': missing_data_total,
            'Percentage': missing_percent
        }).sort_values('Percentage', ascending=False)
        
        print("\nMissing values information (Full Dataset):")
        print(missing_info.head(10))
        return missing_info
        
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

# Analysis functions (updated for chunking)
def analyze_publications_by_year(file_path):
    """Analyze publications by year using a chunked approach."""
    yearly_counts = pd.Series(dtype=int)
    chunk_iterator = load_data(file_path)
    for chunk in chunk_iterator:
        df_clean = clean_data(chunk.copy())
        yearly_counts = yearly_counts.add(df_clean['year'].value_counts(), fill_value=0)
    
    plt.figure(figsize=(10, 6))
    yearly_counts.sort_index().plot(kind='bar')
    plt.title('Number of Publications by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('../images/publications_by_year.png')
    plt.close()
    
    return yearly_counts.sort_index()

def analyze_top_journals(file_path, top_n=10):
    """Analyze top journals by publication count using a chunked approach."""
    journal_counts = pd.Series(dtype=int)
    chunk_iterator = load_data(file_path)
    for chunk in chunk_iterator:
        df_clean = clean_data(chunk.copy())
        journal_counts = journal_counts.add(df_clean['journal'].value_counts(), fill_value=0)
        
    plt.figure(figsize=(12, 6))
    journal_counts.nlargest(top_n).plot(kind='bar')
    plt.title(f'Top {top_n} Journals by Publication Count')
    plt.xlabel('Journal')
    plt.ylabel('Number of Publications')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('../images/top_journals.png')
    plt.close()
    
    return journal_counts.nlargest(top_n)

def analyze_word_frequency(file_path, column='title', top_n=20):
    """Analyze word frequency in titles or abstracts using an incremental approach."""
    all_words = []
    chunk_iterator = load_data(file_path)
    for chunk in chunk_iterator:
        df_clean = clean_data(chunk.copy())
        all_text = ' '.join(df_clean[column].dropna().astype(str))
        words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
        stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'for', 'on', 'with', 'by', 
                      'an', 'as', 'at', 'from', 'is', 'that', 'this', 'are', 'be', 'was'}
        words = [word for word in words if word not in stop_words and len(word) > 2]
        all_words.extend(words)
        
    word_freq = pd.Series(all_words).value_counts().head(top_n)
    
    plt.figure(figsize=(12, 6))
    word_freq.plot(kind='bar')
    plt.title(f'Top {top_n} Words in {column.capitalize()}s')
    plt.xlabel('Word')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'../images/top_words_{column}.png')
    plt.close()
    
    return word_freq

def analyze_sources(file_path, top_n=10):
    """Analyze paper counts by source using a chunked approach."""
    source_counts = pd.Series(dtype=int)
    chunk_iterator = load_data(file_path)
    for chunk in chunk_iterator:
        df_clean = clean_data(chunk.copy())
        source_counts = source_counts.add(df_clean['source_x'].value_counts(), fill_value=0)
        
    plt.figure(figsize=(12, 6))
    source_counts.nlargest(top_n).plot(kind='bar')
    plt.title(f'Top {top_n} Sources by Publication Count')
    plt.xlabel('Source')
    plt.ylabel('Number of Publications')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('../images/top_sources.png')
    plt.close()
    
    return source_counts.nlargest(top_n)

if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('../images', exist_ok=True)
    os.makedirs('../results', exist_ok=True)
    
    # Get the file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', 'data', 'metadata.csv')
    
    # Basic exploration on a sample chunk
    try:
        sample_chunk = next(pd.read_csv(file_path, chunksize=CHUNK_SIZE))
        explore_data(sample_chunk)
    except Exception as e:
        print(f"Could not perform basic exploration on a sample chunk. Error: {e}")

    # Handle missing values
    missing_info = handle_missing_values_chunked(file_path)
    
    # Perform analyses using the chunking functions
    print("Starting analysis of the full dataset...")
    
    yearly_counts = analyze_publications_by_year(file_path)
    top_journals = analyze_top_journals(file_path)
    title_word_freq = analyze_word_frequency(file_path, 'title')
    abstract_word_freq = analyze_word_frequency(file_path, 'abstract')
    top_sources = analyze_sources(file_path)
    
    # Save results to CSV
    yearly_counts.to_csv('../results/yearly_counts.csv')
    top_journals.to_csv('../results/top_journals.csv')
    title_word_freq.to_csv('../results/title_word_freq.csv')
    abstract_word_freq.to_csv('../results/abstract_word_freq.csv')
    top_sources.to_csv('../results/top_sources.csv')
    
    print("Analysis complete! Results saved to results/ directory.")