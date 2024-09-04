import streamlit as st
import zipfile
import os
from PyPDF2 import PdfMerger
from io import BytesIO
import PyPDF2

# Display the banner image at the top
st.image("banner3.png", use_column_width=True)

# Create a folder to store extracted files
output_dir = "zip_data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

st.title("Keyword-Driven Merging")

# List of keywords
keywords_list = [
    "Truck", "LKW", "Trailer", "truck", "FTL trucks", "safety ropes", 
    "belt- adjustment links", "vehicle", "carton", "wood", "quad boxes", 
    "returnable container", "package", "Pallet", "EU14", "Estate car", 
    "Bus", "Van", "Box", "Jumbo truck", "Double decker truck", 
    "Cooling truck", "Box semitrailer", "EMEA", "Bosch", "Anhänger", 
    "Carrier", "Frachtführer", "plant", "LSP", "EU", "Delivery place", 
    "15 ton", "45 m 3", "18 EU", "9000 kg", "91 m 3", "33 EU", "26", 
    "24000 kg", "18 ton", "48 m 3", "10000 kg", "24 ton", "101 m 3", 
    "33", "120 m 3", "38 EU", "28", "24.000 kg", "2021", "CP/LOG-T", 
    "Robert Bosch GmbH"
]

# Multi-select input with "All" option
selected_keywords = st.multiselect(
    "Select Keywords to Match in PDFs (Choose 'All' to select all keywords)", 
    options=["All"] + keywords_list, 
    default=["All"]
)

if "All" in selected_keywords:
    selected_keywords = keywords_list  # If "All" is selected, select all keywords

# Threshold slider
threshold = st.slider("Set Threshold Percentage for Matching", min_value=0, max_value=100, value=50)

# Upload ZIP file
uploaded_file = st.file_uploader("Upload a ZIP file containing PDFs", type="zip")

if uploaded_file:
    # Extract ZIP file
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall(output_dir)

    # Get list of PDF files in extracted directory
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    
    if pdf_files:
        st.write(f"Found {len(pdf_files)} PDF files.")
        
        # Prepare for merging PDFs
        merger = PdfMerger()
        valid_pdfs = 0
        merge_info = []

        # Process each PDF file
        for pdf in pdf_files:
            pdf_path = os.path.join(output_dir, pdf)
            matched_keywords = []

            # Read PDF content
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                text = text.lower()  # Convert text to lowercase for comparison

            # Count matches and collect matched keywords
            for keyword in selected_keywords:
                if keyword.lower() in text:
                    matched_keywords.append(keyword)

            # Calculate match percentage
            match_percentage = (len(matched_keywords) / len(selected_keywords)) * 100

            if match_percentage >= threshold:
                merger.append(pdf_path)  # Merge only if match percentage >= threshold
                valid_pdfs += 1
                merge_info.append((pdf, matched_keywords, len(matched_keywords), len(selected_keywords), match_percentage))

        if valid_pdfs > 0:
            # Display PDFs to merge and matched keywords
            st.write("### PDFs to Merge and Their Matched Keywords:")
            for pdf, keywords, match_count, total_keywords, percentage in merge_info:
                st.markdown(
                    f"""
                    <b><span style="color:red;">**{pdf}**%</span><b> - {match_count}/{total_keywords} - {percentage:.2f}
                    \n**Keywords:** {', '.join(keywords)}
                    \n---""",
                    unsafe_allow_html=True
                )

            # Output combined PDF to a BytesIO object
            combined_pdf = BytesIO()
            merger.write(combined_pdf)
            merger.close()
            combined_pdf.seek(0)

            # Provide download link for the combined PDF
            st.download_button(
                label="Download Combined PDF",
                data=combined_pdf,
                file_name="combined.pdf",
                mime="application/pdf"
            )
        else:
            st.write("No PDFs matched the criteria.")
    else:
        st.write("No PDF files found in the uploaded ZIP.")
