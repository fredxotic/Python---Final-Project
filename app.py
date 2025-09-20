import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from datetime import datetime
import os

# Set page configuration
st.set_page_config(
    page_title="CORD-19 Data Explorer",
    page_icon=":microscope:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display loading message
st.sidebar.info("Loading data...")

# Load data with memory optimizations
@st.cache_data
def load_data(use_small_sample=True):
    """Load data with extreme memory optimizations"""
    if use_small_sample:
        file_path = "data/small_metadata.csv"
        if not os.path.exists(file_path):
            file_path = "data/sample_metadata.csv"
    else:
        file_path = "data/metadata.csv"
    
    if not os.path.exists(file_path):
        st.error(f"Data file not found at: {file_path}")
        st.info("Please make sure you've created a sample file first.")
        return None
    
    # Specify dtype to reduce memory usage - only essential columns
    dtype = {
        'title': 'string',
        'abstract': 'string',
        'publish_time': 'string',
        'journal': 'string'
    }
    
    # Only read necessary columns
    usecols = ['title', 'abstract', 'publish_time', 'journal']
    
    try:
        # For small sample, load directly
        if use_small_sample or "sample" in file_path or "small" in file_path:
            df = pd.read_csv(file_path, dtype=dtype, usecols=usecols)
        else:
            # For full dataset, load in chunks and sample
            chunk_list = []
            for chunk in pd.read_csv(file_path, dtype=dtype, usecols=usecols, chunksize=10000):
                chunk_list.append(chunk.sample(frac=0.1, random_state=42))  # 10% sample from each chunk
                if len(chunk_list) >= 5:  # Limit to 5 chunks
                    break
            df = pd.concat(chunk_list, ignore_index=True)
        
        # Convert publish_time to datetime
        df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
        
        # Extract year from publication date
        df['year'] = df['publish_time'].dt.year
        
        # Fill missing values
        df['journal'] = df['journal'].fillna('Unknown')
        df['abstract'] = df['abstract'].fillna('')
        
        # Create abstract word count column
        df['abstract_word_count'] = df['abstract'].apply(lambda x: len(str(x).split()))
        
        st.sidebar.success(f"Data loaded successfully! ({len(df)} rows)")
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Title and description
st.title("CORD-19 Data Explorer")
st.write("""
This application provides an interactive exploration of the CORD-19 dataset, 
which contains metadata about COVID-19 research papers.
""")

# Add option to use small sample data (default to True)
use_small_sample = st.sidebar.checkbox("Use small sample data (recommended for low memory)", value=True)

# Load the data with progress indicator
with st.spinner('Loading data... This may take a moment.'):
    df = load_data(use_small_sample=use_small_sample)

if df is None:
    st.error("Failed to load data. Please check if the data file exists.")
    st.info("""
    If you don't have a sample file yet, create one by running:
    ```bash
    python create_small_sample.py
    ```
    """)
    st.stop()

# Sidebar for filters
st.sidebar.header("Filters")

# Year filter - handle cases where year might be missing
if df['year'].isna().all():
    min_year, max_year = 2019, 2022
else:
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())

year_range = st.sidebar.slider(
    "Select year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Abstract length filter
min_abstract_length = st.sidebar.slider(
    "Minimum abstract word count",
    min_value=0,
    max_value=500,
    value=10
)

# Apply filters
filtered_df = df[
    (df['year'] >= year_range[0]) & 
    (df['year'] <= year_range[1]) &
    (df['abstract_word_count'] >= min_abstract_length)
].copy()

# Display dataset info
st.header("Dataset Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Papers", len(df))
col2.metric("Filtered Papers", len(filtered_df))
col3.metric("Date Range", f"{min_year} - {max_year}")

# Show simple memory info (no psutil needed)
if st.sidebar.checkbox("Show basic info", value=True):
    st.sidebar.info(f"Dataset size: {len(df)} rows")
    st.sidebar.info(f"Filtered to: {len(filtered_df)} rows")

# Tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs([
    "Publications Over Time", 
    "Journal Analysis", 
    "Word Analysis",
    "Sample Data"
])

with tab1:
    st.header("Publications Over Time")
    
    yearly_counts = filtered_df['year'].value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    yearly_counts.plot(kind='bar', ax=ax)
    ax.set_title('Number of Publications by Year')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Publications')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    st.write("""
    This chart shows the number of publications per year in the filtered dataset.
    COVID-19 research dramatically increased in 2020, as expected.
    """)

with tab2:
    st.header("Journal Analysis")
    
    top_n = st.slider("Number of top journals to show", 5, 20, 10, key="journal_slider")
    
    journal_counts = filtered_df['journal'].value_counts().head(top_n)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    journal_counts.plot(kind='bar', ax=ax)
    ax.set_title(f'Top {top_n} Journals by Publication Count')
    ax.set_xlabel('Journal')
    ax.set_ylabel('Number of Publications')
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)
    
    st.write(f"""
    This chart shows the top {top_n} journals publishing COVID-19 research.
    Many of these are prominent medical and scientific journals.
    """)

with tab3:
    st.header("Word Analysis")
    
    analysis_type = st.radio(
        "Choose text to analyze",
        ["Titles", "Abstracts"],
        horizontal=True
    )
    
    column = 'title' if analysis_type == "Titles" else 'abstract'
    top_n_words = st.slider("Number of top words to show", 10, 30, 15, key="word_slider")
    
    # Limit text processing to save memory
    sample_text = filtered_df[column].dropna().astype(str)
    if len(sample_text) > 1000:
        sample_text = sample_text.sample(1000, random_state=42)
    
    all_text = ' '.join(sample_text)
    
    words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
    
    stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'for', 'on', 'with', 'by', 
                 'an', 'as', 'at', 'from', 'is', 'that', 'this', 'are', 'be', 'was'}
    words = [word for word in words if word not in stop_words and len(word) > 2]
    
    word_freq = pd.Series(words).value_counts().head(top_n_words)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    word_freq.plot(kind='bar', ax=ax)
    ax.set_title(f'Top {top_n_words} Words in {analysis_type}')
    ax.set_xlabel('Word')
    ax.set_ylabel('Frequency')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Only generate word cloud if user explicitly requests it
    if st.checkbox("Generate Word Cloud (memory intensive)", value=False):
        st.subheader("Word Cloud")
        try:
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            ax.set_title(f'Word Cloud of {analysis_type}')
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Could not generate word cloud: {e}")
    
    st.write(f"""
    This analysis shows the most frequent words in paper {analysis_type.lower()}.
    Common COVID-19 related terms like 'covid', 'sars', 'coronavirus', and 'pandemic' 
    appear frequently, as expected.
    """)

with tab4:
    st.header("Sample Data")
    
    sample_size = st.slider("Number of rows to show", 5, 50, 10)
    
    st.dataframe(
        filtered_df[['title', 'journal', 'year', 'abstract_word_count']].head(sample_size),
        height=300
    )
    
    st.download_button(
        label="Download filtered data as CSV",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_cord19_data.csv",
        mime="text/csv"
    )

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    This app analyzes the CORD-19 dataset from Kaggle.
    Using small sample mode for better performance on low-memory devices.
    """
)