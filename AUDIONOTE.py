



import streamlit as st
import main as my
import os

from reportlab.pdfgen import canvas
from groq import Groq


groq_api_key = st.secrets['GROQ_API_KEY']

client=Groq(api_key=groq_api_key)






st.title('Welcome To Audionote! 😊')
st.write("Transform your audio into clear, structured notes effortlessly! Whether you're recording lectures, meetings, or brainstorming sessions, this app converts spoken content into accurate text notes in seconds. Perfect for students, professionals, and anyone who wants to save time and stay organized.")
st.write("Made By Monisha Bangar-2025")
st.header("Key Features:")
st.write("""
         1. Speech-to-Text Conversion: Convert audio files into detailed, editable text notes with high accuracy.\n
    2. Multiple Formats: Upload audio in popular formats like MP3, MPEG,MP4 . \n
    3. Smart Structuring: Automatically organizes notes into headings, bullet points, and paragraphs for readability.\n
    4. Multi-Language Support: Transcribe audio in various languages with ease.\n
    """)

audio_file = st.file_uploader("Upload your audio file", type=["mp3", "wav", "m4a", "mpeg"])

if audio_file is not None:
    # Save the uploaded file temporarily
    with open("temp_audio.mpeg", "wb") as f:
        f.write(audio_file.getbuffer())
    
    # Get course name
    course_name = st.text_input("Please enter the course name:")
    
    if course_name:
        if st.button("Process Audio"):
            with st.spinner("Processing audio and generating notes..."):
                # Process the audio file
                my.main(course_name,groq_api_key)
                print(1)
                # Check if PDF was generated
                if  os.path.exists("notes.pdf"):
                    # Read the generated PDF
                    with open("notes.pdf", "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    # Display PDF
                    st.success("Notes generated successfully!")
                    # st.pdf(pdf_bytes)
                    
                    # Add download button
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        
                        file_name="notes.pdf",
                        mime="application/pdf"
                    )
                    
                    # Clean up temporary files
                    os.remove("temp_audio.mpeg")
                else:
                    st.error("Error generating PDF. Please try again.")

# Clean up temporary files when the app is clos ed
if os.path.exists("temp_audio.mpeg"):
    os.remove("temp_audio.mpeg")
