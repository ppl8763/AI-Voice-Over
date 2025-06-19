import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
import whisper
from gtts import gTTS
from pydub import AudioSegment
import os

# Function to extract audio from video
def extract_audio(video_path):
    try:
        video = VideoFileClip(video_path)
        audio_path = "extracted_audio.wav"
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        return audio_path
    except Exception as e:
        st.error(f"❌ Error extracting audio: {e}")
        return None

# Function to transcribe audio using Whisper
def transcribe_audio(audio_path, language="en"):
    try:
        model = whisper.load_model("small")
        result = model.transcribe(audio_path, language=language)
        transcript_text = result.get("text", "").strip()
        return transcript_text
    except Exception as e:
        st.error(f"❌ Error transcribing audio: {e}")
        return None

# Function to generate AI voice using gTTS
def generate_ai_voice(text, language="en"):
    try:
        tts = gTTS(text, lang=language)
        audio_path = "ai_audio.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"❌ Error generating AI voice: {e}")
        return None

# Function to adjust audio length to sync with original
def adjust_audio_length(original_audio_path, generated_audio_path):
    try:
        original_audio = AudioSegment.from_file(original_audio_path)
        generated_audio = AudioSegment.from_file(generated_audio_path)

        if len(original_audio) > len(generated_audio):
            silence = AudioSegment.silent(duration=(len(original_audio) - len(generated_audio)))
            adjusted_audio = generated_audio + silence
        else:
            adjusted_audio = generated_audio[:len(original_audio)]

        adjusted_path = "adjusted_ai_audio.wav"
        adjusted_audio.export(adjusted_path, format="wav")
        return adjusted_path
    except Exception as e:
        st.error(f"❌ Error adjusting audio: {e}")
        return None

# Function to replace audio in video
def replace_audio(video_path, new_audio_path, output_path):
    try:
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(new_audio_path)
        video = video.set_audio(new_audio)
        video.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    except Exception as e:
        st.error(f"❌ Error replacing audio: {e}")

# Streamlit UI
st.set_page_config(page_title="AI Voice Over", layout="centered")
st.title("🎙️ AI Voice Over for Videos")
st.markdown("""
Upload a video and let AI:
1. Extract and transcribe the audio 🎧  
2. Generate a new voiceover 🗣️  
3. Replace the original voice in the video 🎬  
""")

# Upload section
uploaded_file = st.file_uploader("📤 Upload a video file", type=["mp4", "avi", "mov"])

language_options = {"English": "en", "Spanish": "es", "French": "fr", "Hindi": "hi"}
selected_language = st.selectbox("🌐 Select language", list(language_options.keys()))

# If file uploaded
if uploaded_file:
    video_path = "uploaded_video.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    st.video(video_path)

    if st.button("🚀 Process Video"):
        with st.spinner("Processing..."):
            try:
                # Step 1: Extract audio
                st.info("🔍 Extracting audio...")
                audio_path = extract_audio(video_path)
                if not audio_path:
                    st.stop()

                # Step 2: Transcribe
                st.info("📝 Transcribing audio...")
                transcript = transcribe_audio(audio_path, language_options[selected_language])
                if not transcript:
                    st.stop()
                st.success("🗒️ Transcription Complete!")
                st.write(f"**Transcript:** {transcript}")

                # Step 3: Generate AI Voice
                st.info("🧠 Generating AI Voice...")
                ai_audio_path = generate_ai_voice(transcript, language_options[selected_language])
                if not ai_audio_path:
                    st.stop()

                # Step 4: Sync audio
                st.info("⏱️ Adjusting Audio Length...")
                adjusted_ai_audio_path = adjust_audio_length(audio_path, ai_audio_path)
                if not adjusted_ai_audio_path:
                    st.stop()

                # Step 5: Replace Audio in Video
                st.info("🎥 Replacing original audio...")
                output_path = "output_video.mp4"
                replace_audio(video_path, adjusted_ai_audio_path, output_path)

                # Step 6: Show output
                st.success("✅ Done! Here's your modified video:")
                st.video(output_path)
                with open(output_path, "rb") as f:
                    st.download_button("⬇️ Download Modified Video", f, "modified_video.mp4")

            except Exception as e:
                st.error(f"🔥 Unexpected error: {e}")

            # Clean up
            finally:
                for file in [video_path, audio_path, ai_audio_path, adjusted_ai_audio_path, output_path]:
                    if file and os.path.exists(file):
                        os.remove(file)
