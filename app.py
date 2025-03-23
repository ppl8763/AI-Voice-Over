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
        st.error(f"Error extracting audio: {e}")
        return None

# Function to transcribe audio using Whisper
def transcribe_audio(audio_path, language="en"):
    try:
        model = whisper.load_model("small")
        result = model.transcribe(audio_path, language=language)
        transcript_text = result.get("text", "").strip()
        return transcript_text
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return None

# Function to generate AI voice using gTTS
def generate_ai_voice(text, language="en"):
    try:
        tts = gTTS(text, lang=language)
        audio_path = "ai_audio.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"Error generating AI voice: {e}")
        return None

# Function to adjust audio length
def adjust_audio_length(original_audio_path, generated_audio_path):
    original_audio = AudioSegment.from_wav(original_audio_path)
    generated_audio = AudioSegment.from_mp3(generated_audio_path)
    
    if len(original_audio) > len(generated_audio):
        silence = AudioSegment.silent(duration=(len(original_audio) - len(generated_audio)))
        adjusted_audio = generated_audio + silence
    else:
        adjusted_audio = generated_audio[:len(original_audio)]
    
    adjusted_audio_path = "adjusted_ai_audio.wav"
    adjusted_audio.export(adjusted_audio_path, format="wav")
    return adjusted_audio_path

# Function to replace audio in video
def replace_audio(video_path, new_audio_path, output_path):
    try:
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(new_audio_path)
        video = video.set_audio(new_audio)
        video.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    except Exception as e:
        st.error(f"Error replacing audio: {e}")

# Streamlit App UI
st.title("🎙️ Advanced AI Voice Over for Videos")
st.markdown(
    """
    Upload a video, and let AI:
    1. Extract and transcribe the audio.
    2. Generate a new AI voiceover.
    3. Replace the original audio in the video.
    """
)

# File uploader
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

# Language options
language_options = {"English": "en", "Spanish": "es", "French": "fr", "Hindi": "hi"}
selected_language = st.selectbox("Select language for transcription and AI voice", list(language_options.keys()))

if uploaded_file is not None:
    video_path = "uploaded_video.mp4"
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.video(video_path)

    if st.button("Process Video"):
        with st.spinner("Processing started..."):
            try:
                # Step 1: Extract audio
                st.info("Extracting audio from video...")
                audio_path = extract_audio(video_path)
                if not audio_path:
                    st.stop()

                # Step 2: Transcribe audio
                st.info("Transcribing audio...")
                transcript = transcribe_audio(audio_path, language_options[selected_language])
                if not transcript:
                    st.stop()
                st.write("**Transcribed Text:**")
                st.write(transcript)

                # Step 3: Generate AI voice
                st.info("Generating AI voice...")
                ai_audio_path = generate_ai_voice(transcript, language_options[selected_language])
                if not ai_audio_path:
                    st.stop()

                # Step 4: Adjust audio length
                st.info("Adjusting audio length for synchronization...")
                adjusted_ai_audio_path = adjust_audio_length(audio_path, ai_audio_path)

                # Step 5: Replace audio in video
                st.info("Replacing audio in the video...")
                output_video_path = "output_video.mp4"
                replace_audio(video_path, adjusted_ai_audio_path, output_video_path)

                # Step 6: Show and download the modified video
                st.success("✅ Audio has been replaced successfully!")
                st.video(output_video_path)

                with open(output_video_path, "rb") as f:
                    st.download_button("Download Modified Video", f, file_name="modified_video.mp4")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

            # Cleanup temporary files
            finally:
                try:
                    if os.path.exists(video_path):
                        os.remove(video_path)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                    if os.path.exists(ai_audio_path):
                        os.remove(ai_audio_path)
                    if os.path.exists(output_video_path):
                        os.remove(output_video_path)
                except Exception as cleanup_error:
                    st.warning(f"Cleanup issue: {cleanup_error}")
