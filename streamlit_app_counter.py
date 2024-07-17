import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import zipfile
import io

# Function to check if a pixel is within a specified color range
def is_pixel_in_range(pixel, color_range):
    (r_min, g_min, b_min), (r_max, g_max, b_max) = color_range
    r, g, b = pixel
    return (r_min <= r <= r_max) and (g_min <= g <= g_max) and (b_min <= b <= b_max)

# Function to count pixels of each color category in an image
def count_pixels(image, color_ranges):
    image = image.convert('RGB')
    pixel_data = np.array(image)
    height, width, _ = pixel_data.shape

    color_counts = {color: 0 for color in color_ranges}

    for row in pixel_data:
        for pixel in row:
            for color, (color_min, color_max) in color_ranges.items():
                if is_pixel_in_range(pixel, (color_min, color_max)):
                    color_counts[color] += 1
                    break  # Move to the next pixel

    return color_counts, height * width

# Function to process uploaded files and calculate counts and percentages
def process_files(files, color_ranges):
    results = []

    for file in files:
        image = Image.open(file)
        color_counts, num_pixels = count_pixels(image, color_ranges)
        
        # Calculate total calculated pixels for this file
        total_calculated_pixels = sum(color_counts.values())

        # Calculate percentages using total calculated pixels
        percentages = {color: (count / total_calculated_pixels) * 100 if total_calculated_pixels > 0 else 0 for color, count in color_counts.items()}
        
        result = {
            'Image': file.name,
            'Total Pixels': num_pixels,
            'Total Calculated Pixels': total_calculated_pixels,
            **{f'Count {color}': count for color, count in color_counts.items()},
            **{f'Percentage {color}': percentages[color] for color in color_ranges}
        }
        results.append(result)

    return results

# Streamlit app code
def main():
    st.title('Image Processing App')

    # Upload folder
    uploaded_files = st.file_uploader('Upload Image Files', type=['tif'], accept_multiple_files=True)
    
    if uploaded_files:
        # Color range inputs
        st.subheader('Color Ranges')
        color_ranges = {}
        for label in ['Residential', 'Open Spaces', 'Commercial', 'PSP', 'Transportation & Utility']:
            st.subheader(label)
            min_rgb_hex = st.color_picker(f'{label} Min RGB')
            max_rgb_hex = st.color_picker(f'{label} Max RGB')

            # Convert hex to RGB integer tuple
            min_rgb = tuple(int(min_rgb_hex[i:i+2], 16) for i in (1, 3, 5))
            max_rgb = tuple(int(max_rgb_hex[i:i+2], 16) for i in (1, 3, 5))

            # Convert RGB values to numpy.uint8
            color_min = np.uint8(min_rgb)
            color_max = np.uint8(max_rgb)

            color_ranges[label] = (color_min, color_max)

        # Process folder button
        if st.button('Process Files'):
            results = process_files(uploaded_files, color_ranges)
            df = pd.DataFrame(results)
            
            # Format percentage columns to two decimal places
            df = df.style.format({
                'Percentage Residential': '{:.2f}%',
                'Percentage Open Spaces': '{:.2f}%',
                'Percentage Commercial': '{:.2f}%',
                'Percentage PSP': '{:.2f}%',
                'Percentage Transportation & Utility': '{:.2f}%'
            })

            st.subheader('Processed Results')
            st.write(df)

if __name__ == '__main__':
    main()
