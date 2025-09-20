# create_small_sample.py
import pandas as pd
import os

def create_small_sample(input_path, output_path, sample_size=2000):
    """Create a small sample of the metadata file"""
    print(f"Creating small sample with {sample_size} rows...")
    
    # Read the first few chunks and sample from them
    chunks = pd.read_csv(input_path, chunksize=5000)
    
    # Collect a diverse sample
    sample_chunks = []
    for i, chunk in enumerate(chunks):
        if i >= 4:  # Only read first 4 chunks (20,000 rows)
            break
        # Take a portion from each chunk
        sample = chunk.sample(n=min(500, len(chunk)), random_state=42)
        sample_chunks.append(sample)
    
    # Combine and ensure exact sample size
    sample_df = pd.concat(sample_chunks, ignore_index=True)
    sample_df = sample_df.head(sample_size)
    
    sample_df.to_csv(output_path, index=False)
    print(f"Small sample saved to {output_path} with {len(sample_df)} rows")
    
    return sample_df

if __name__ == "__main__":
    input_file = "data/metadata.csv"
    output_file = "data/small_metadata.csv"
    
    if os.path.exists(input_file):
        create_small_sample(input_file, output_file, sample_size=2000)
    else:
        print(f"Input file {input_file} not found!")