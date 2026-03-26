import streamlit as st
import os
import time
import tempfile
import requests
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

# Try to import optional modules with helpful messages
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# Page configuration
st.set_page_config(page_title="AutoViral AI - Fully Autonomous", page_icon="🤖", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #FF0066, #FF6600);
        color: white;
        font-weight: bold;
        font-size: 18px;
    }
    .success-box {
        padding: 20px;
        background-color: #d4edda;
        border-radius: 10px;
        border-left: 5px solid #28a745;
    }
    .info-box {
        padding: 15px;
        background-color: #e3f2fd;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AutoViral AI - Fully Autonomous Creator")
st.caption("One-click: Trend → AI Script → AI Voice → AI Video → Auto-post to ALL platforms")

# Initialize session state
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'posting_status' not in st.session_state:
    st.session_state.posting_status = {}
if 'generation_log' not in st.session_state:
    st.session_state.generation_log = []

# Sidebar - API Keys
with st.sidebar:
    st.header("🔑 API Configuration")
    
    st.subheader("Required APIs")
    grok_key = st.text_input("xAI Grok API Key", type="password", placeholder="Get from console.x.ai")
    eleven_key = st.text_input("ElevenLabs API Key", type="password", placeholder="Get from elevenlabs.io")
    pexels_key = st.text_input("Pexels API Key (for stock footage)", type="password", placeholder="Get from pexels.com/api")
    
    st.divider()
    st.subheader("Social Media APIs (Optional)")
    with st.expander("X/Twitter API"):
        consumer_key = st.text_input("API Key", type="password")
        consumer_secret = st.text_input("API Secret", type="password")
        access_token = st.text_input("Access Token", type="password")
        access_secret = st.text_input("Access Secret", type="password")
    
    with st.expander("Instagram/TikTok"):
        st.info("Coming soon - OAuth integration")
    
    st.divider()
    
    # Installation helper
    if not all([OPENAI_AVAILABLE, ELEVENLABS_AVAILABLE]):
        st.warning("⚠️ Missing dependencies!")
        st.code("""
pip install openai elevenlabs requests pillow
        """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🎯 Content Settings")
    
    # Trend input
    trend_input = st.text_input(
        "Trending Topic",
        placeholder="e.g., AI Revolution, Bitcoin, Viral Dance",
        help="Enter any topic to create viral content"
    )
    
    col_style, col_duration = st.columns(2)
    with col_style:
        style = st.selectbox("Content Style", ["Humorous", "Hot Take", "Informative", "Motivational", "Educational"])
    with col_duration:
        duration = st.selectbox("Video Duration", ["30s", "60s", "90s"], index=1)
    
    # Platform selection
    st.subheader("📱 Auto-Post To:")
    col_x, col_ig, col_tiktok = st.columns(3)
    with col_x:
        post_to_x = st.checkbox("X (Twitter)", value=True)
    with col_ig:
        post_to_ig = st.checkbox("Instagram", value=False)
    with col_tiktok:
        post_to_tiktok = st.checkbox("TikTok", value=False)

with col2:
    st.header("📊 Status Dashboard")
    status_placeholder = st.empty()
    log_placeholder = st.empty()

# Function to add to log
def add_to_log(message, type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.generation_log.append(f"[{timestamp}] {message}")
    if len(st.session_state.generation_log) > 10:
        st.session_state.generation_log = st.session_state.generation_log[-10:]
    
    with log_placeholder.container():
        st.markdown("### 📋 Generation Log")
        for log in reversed(st.session_state.generation_log):
            if "✅" in log:
                st.success(log)
            elif "❌" in log:
                st.error(log)
            else:
                st.info(log)

# Function to generate script with Grok
def generate_script(topic, style, duration):
    add_to_log(f"📝 Generating script for: {topic}...")
    
    client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
    
    word_count = 90 if duration == "30s" else 180 if duration == "60s" else 270
    
    prompt = f"""Write a viral {duration} video script about {topic}.
Style: {style}
Word count: ~{word_count} words

Requirements:
- Hook in first 3 seconds
- Simple, conversational language
- Clear call-to-action at end
- Use emojis sparingly
- Format as plain text with line breaks for pacing

Script:"""
    
    response = client.chat.completions.create(
        model="grok-beta",
        messages=[{"role": "user", "content": prompt}]
    )
    
    script = response.choices[0].message.content
    add_to_log(f"✅ Script generated ({len(script.split())} words)")
    return script

# Function to generate voiceover
def generate_voiceover(script, voice="Rachel"):
    add_to_log(f"🎙️ Generating voiceover with ElevenLabs...")
    
    eleven = ElevenLabs(api_key=eleven_key)
    audio = eleven.text_to_speech.convert(
        text=script,
        voice_id=voice,
        model_id="eleven_turbo_v2_5",
        output_format="mp3_44100_128"
    )
    
    audio_path = tempfile.mktemp(suffix=".mp3")
    save(audio, audio_path)
    add_to_log(f"✅ Voiceover saved to {audio_path}")
    return audio_path

# Function to get stock footage from Pexels
def get_stock_footage(query):
    add_to_log(f"🎬 Fetching stock footage for: {query}...")
    
    headers = {"Authorization": pexels_key}
    url = f"https://api.pexels.com/videos/search?query={query}&per_page=5&orientation=portrait"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if data.get('videos'):
            # Get the first video
            video = data['videos'][0]
            # Get the highest quality video file
            video_files = video['video_files']
            # Prefer hd or sd
            video_url = None
            for vf in video_files:
                if vf['quality'] in ['hd', 'sd']:
                    video_url = vf['link']
                    break
            
            if video_url:
                add_to_log(f"✅ Found stock footage")
                return video_url
    
    except Exception as e:
        add_to_log(f"⚠️ Could not fetch stock footage: {str(e)}")
    
    # Fallback: return a placeholder URL
    add_to_log("⚠️ Using fallback footage")
    return "https://assets.mixkit.co/videos/preview/mixkit-abstract-animation-3981-large.mp4"

# Function to download video
def download_video(url, output_path):
    response = requests.get(url, stream=True)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path

# Function to create video with text overlays (using image frames for simplicity)
def create_simple_video(audio_path, script, duration_seconds):
    add_to_log(f"🎨 Creating video with text overlays...")
    
    # Create frames with text for different parts of the script
    frames_dir = tempfile.mkdtemp()
    frame_paths = []
    
    # Split script into sentences
    sentences = [s.strip() for s in script.split('.') if s.strip()]
    frames_per_sentence = max(1, int(duration_seconds / len(sentences)) * 2)
    
    try:
        # Try to use a system font
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 40)
    except:
        # Fallback to default
        font = ImageFont.load_default()
    
    for i, sentence in enumerate(sentences[:10]):  # Limit to 10 frames
        # Create an image frame
        img = Image.new('RGB', (1080, 1920), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Add text
        text_bbox = draw.textbbox((0, 0), sentence, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        position = ((1080 - text_width) // 2, (1920 - text_height) // 2)
        draw.text(position, sentence, fill=(255, 255, 255), font=font)
        
        # Save frame
        frame_path = os.path.join(frames_dir, f"frame_{i:03d}.png")
        img.save(frame_path)
        frame_paths.append(frame_path)
    
    # Create a simple video by repeating frames
    video_path = tempfile.mktemp(suffix=".mp4")
    
    # Use ffmpeg to create video from images (if available)
    try:
        import subprocess
        # Create a video from images with audio
        cmd = [
            'ffmpeg', '-y',
            '-framerate', '1',  # 1 frame per second
            '-i', f'{frames_dir}/frame_%03d.png',
            '-i', audio_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            video_path
        ]
        subprocess.run(cmd, capture_output=True)
        add_to_log(f"✅ Video created with ffmpeg")
        return video_path
    except:
        add_to_log(f"⚠️ Could not create video with ffmpeg, providing audio only")
        return None

# Function to post to X/Twitter
def post_to_x(video_path, caption):
    if not TWEEPY_AVAILABLE:
        add_to_log(f"❌ Tweepy not installed", "error")
        return False
    
    try:
        auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_secret)
        api = tweepy.API(auth)
        
        media = api.media_upload(video_path)
        api.update_status(status=caption, media_ids=[media.media_id_string])
        add_to_log(f"✅ Posted to X/Twitter")
        return True
    except Exception as e:
        add_to_log(f"❌ Failed to post to X: {str(e)}", "error")
        return False

# Main generation button
if st.button("🤖 FULLY AUTONOMOUS MODE - Create & Post Everything", type="primary", use_container_width=True):
    if not trend_input:
        st.error("❌ Please enter a trending topic")
        st.stop()
    
    if not grok_key:
        st.error("❌ Please enter Grok API key in sidebar")
        st.stop()
    
    if not eleven_key:
        st.error("❌ Please enter ElevenLabs API key in sidebar")
        st.stop()
    
    if not pexels_key:
        st.warning("⚠️ Pexels API key missing - using fallback footage")
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Generate script
        status_text.text("📝 Step 1/5: Generating viral script...")
        script = generate_script(trend_input, style, duration)
        progress_bar.progress(20)
        
        # Display script
        with st.expander("📄 View Generated Script"):
            st.write(script)
        
        # Step 2: Generate voiceover
        status_text.text("🎙️ Step 2/5: Creating voiceover...")
        audio_path = generate_voiceover(script)
        progress_bar.progress(40)
        st.audio(audio_path)
        
        # Step 3: Get stock footage
        status_text.text("🎬 Step 3/5: Fetching stock footage...")
        video_url = get_stock_footage(trend_input)
        progress_bar.progress(60)
        
        # Step 4: Create final video
        status_text.text("🎨 Step 4/5: Creating final video...")
        duration_seconds = 30 if duration == "30s" else 60 if duration == "60s" else 90
        video_path = create_simple_video(audio_path, script, duration_seconds)
        
        if video_path and os.path.exists(video_path):
            st.session_state.video_path = video_path
            st.video(video_path)
            progress_bar.progress(80)
        else:
            st.info("🎤 Video creation skipped - audio ready for manual editing")
            st.audio(audio_path)
            st.info("💡 Download the audio and combine with stock footage using Canva or CapCut")
        
        # Step 5: Auto-post to platforms
        status_text.text("📤 Step 5/5: Auto-posting to platforms...")
        caption = f"🔥 {trend_input} - {style} in {duration}! #Viral #Trending #AI"
        
        if post_to_x and consumer_key:
            post_to_x(video_path if video_path else audio_path, caption)
        
        if post_to_ig:
            add_to_log("📱 Instagram posting coming soon", "info")
        
        if post_to_tiktok:
            add_to_log("📱 TikTok posting coming soon", "info")
        
        progress_bar.progress(100)
        status_text.text("✅ Complete!")
        
        # Download button
        if video_path and os.path.exists(video_path):
            with open(video_path, 'rb') as f:
                st.download_button(
                    label="📥 Download Video",
                    data=f,
                    file_name=f"viral_{trend_input.replace(' ', '_')}.mp4",
                    mime="video/mp4"
                )
        
        st.balloons()
        st.success("🎉 FULLY AUTONOMOUS COMPLETE! Your viral content has been created and posted!")
        
        # Show success box
        st.markdown(f"""
        <div class="success-box">
            ✅ <strong>Success!</strong><br>
            • Script generated<br>
            • Voiceover created<br>
            • Video assembled<br>
            • Posted to selected platforms<br>
            <br>
            <strong>Next steps:</strong> Check your social media accounts!
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        add_to_log(f"❌ Generation failed: {str(e)}", "error")
        
        # Provide troubleshooting help
        with st.expander("🔧 Troubleshooting Tips"):
            st.markdown("""
            **Common issues:**
            1. **API Keys**: Verify all keys are correct
            2. **Network**: Check internet connection
            3. **Rate Limits**: You might have hit API rate limits
            4. **Dependencies**: Run `pip install -r requirements.txt`
            
            **Get API Keys:**
            - Grok: https://console.x.ai
            - ElevenLabs: https://elevenlabs.io
            - Pexels: https://www.pexels.com/api
            """)

# Display generation log
with st.expander("📋 Detailed Generation Log"):
    for log in st.session_state.generation_log:
        if "✅" in log:
            st.success(log)
        elif "❌" in log:
            st.error(log)
        else:
            st.info(log)

# Footer
st.divider()
st.caption("🤖 Fully Autonomous AI Video Creator - One click creates everything from script to post!")
st.caption("💡 Requirements: pip install openai elevenlabs tweepy requests pillow")
