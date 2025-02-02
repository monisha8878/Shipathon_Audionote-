


# Load the .env file
#load_dotenv()





import os
import soundfile as sf
from groq import Groq
import math
import tempfile
from reportlab.pdfgen import canvas
from textwrap import wrap



def txt_to_pdf(txt_file, pdf_file):
    c = canvas.Canvas(pdf_file)
    with open(txt_file, "r") as f:
        text = f.read()

    # Configure text object
    textobject = c.beginText(50, 750)  # Initial position: (x, y)
    textobject.setFont("Helvetica", 12)
    line_height = 14
    max_chars_per_line = 90  # Adjust for the page width and font size

    for line in text.splitlines():
        words = line.split()  # Split the line into words
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                # Add the word to the current line
                if current_line:
                    current_line += " "
                current_line += word
            else:
                # Add the current line to the text object
                textobject.textLine(current_line)
                if textobject.getY() < 50:  # If bottom margin is reached
                    c.drawText(textobject)
                    c.showPage()  # Create a new page
                    textobject = c.beginText(50, 750)  # Reset position for new page
                    textobject.setFont("Helvetica", 12)
                current_line = word  # Start a new line with the current word

        # Add the last line in the paragraph
        if current_line:
            textobject.textLine(current_line)
            if textobject.getY() < 50:  # If bottom margin is reached
                c.drawText(textobject)
                c.showPage()  # Create a new page
                textobject = c.beginText(50, 750)  # Reset position for new page
                textobject.setFont("Helvetica", 12)

    # Draw remaining text and save
    c.drawText(textobject)
    c.save()



class AudioTranscriber:
    def __init__(self, groq_api_key):
        """Initialize with Groq API key"""
        self.client = Groq(api_key=groq_api_key)
        self.chunk_duration = 5 * 60  # 5 minutes in seconds (roughly 800 words)

    def split_audio(self, audio_path):
        """Split audio file into manageable chunks"""
        # Load audio file
        
        data, samplerate = sf.read(audio_path)
        
        chunks = []

        # Create temporary directory for chunks
        temp_dir = tempfile.mkdtemp()

        # Calculate samples per chunk
        samples_per_chunk = int(self.chunk_duration * samplerate)

        # Split audio into 5-minute chunks
        for i in range(0, len(data), samples_per_chunk):
            chunk = data[i:min(i + samples_per_chunk, len(data))]
            chunk_path = os.path.join(temp_dir, f"chunk_{i//samples_per_chunk}.wav")
            sf.write(chunk_path, chunk, samplerate)
            chunks.append(chunk_path)
        #print(1)
        return chunks, temp_dir
    

    def transcribe_audio(self, filename):
        """Transcribe audio file with chunking support"""
        if not os.path.exists(filename):
            print(f"Error: File not found at {filename}. Please check the path and filename.")
            return None

        # Split audio into chunks
        print(filename)
        chunks, temp_dir = self.split_audio(filename)
        full_transcription = ""

        # Process each chunk
        #print(chunks)
        for chunk_path in chunks:
            try:
                with open(chunk_path, "rb") as file:
                    transcription = self.client.audio.transcriptions.create(
                        file=(chunk_path, file.read()),
                        model="whisper-large-v3-turbo",
                        response_format="json"
                    )
                    full_transcription += transcription.text + " "
            except Exception as e:
                print(f"Error processing chunk {chunk_path}: {str(e)}")

        # Cleanup temporary files
        for chunk_path in chunks:
            os.remove(chunk_path)
        os.rmdir(temp_dir)
       #print(2)
        return full_transcription.strip()

    def generate_notes(self, transcription, course_name, output_file):
        """Generate notes from transcription using Groq API and save to file"""
        prompt = (
            "You are a Note making model. You need to make notes out of the given audio transcript in English. "
            "Omit unnecessary information. "
            f"The heading should contain the name of the course: **{course_name}**, subheadings, and provide clear meanings. "
            "Create notes with suitable headings, heading should contain name of course, subheadings and provide clear meanings. "
            f"\n\n{transcription}"
        )

        completion = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None
        )
        print (3)

        # Stream directly to file instead of printing
        with open(output_file, "w", encoding="utf-8") as f:
            for chunk in completion:
                chunk_content = chunk.choices[0].delta.content or ""
                f.write(chunk_content)
                f.flush()  # Ensure content is written immediately
        print(4)


def main(course_name,groq_api_key):
    # Initialize transcriber with your API key
    transcriber = AudioTranscriber(groq_api_key)
    print(5)
    # Specify the path to the audio file
    filename = r"temp_audio.mpeg"

    # Replace with your audio file!
    print(6)
    # Get transcription
    transcription = transcriber.transcribe_audio(filename)
    print(7)
    if transcription:
       

        # Save transcription
        with open("transcription.txt", "w", encoding="utf-8") as f:
            f.write(transcription)
        print("start")
        # Generate and save notes without printing
        transcriber.generate_notes(transcription, course_name, "notes.txt")
        print("Notes have been saved to 'notes.txt'")
        txt_to_pdf("notes.txt", "notes.pdf")





