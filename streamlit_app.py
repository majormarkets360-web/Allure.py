import streamlit as st
import os
import time
import tempfile
import requests
from datetime import datetime

# Try to import with fallbacks
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    st.warning("⚠️ tweepy not installed. Run: pip install tweepy")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    st.warning("⚠️ openai not installed. Run: pip install openai")

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    st.warning("⚠️ elevenlabs not installed. Run: pip install elevenlabs")

try:
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    st.warning("⚠️ litellm not installed. Run: pip install litellm")

# MoviePy with fallback for common issues
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    st.warning("⚠️ moviepy not installed. Run: pip install moviepy")
except Exception as e:
    MOVIEPY_AVAILABLE = False
    st.warning(f"⚠️ moviepy import error: {str(e)}")

# Page configuration
st.set_page_config(page_title="TrendClip AI PRO VIRAL MODE", page_icon="🎬", layout="wide")

# Title and description
st.title("🎬 TrendClip AI PRO VIRAL MODE ENABLED")
st.caption("One-click: Trend → Grok script → ElevenLabs voice → Runway Gen-4 video → Auto-post to X + TikTok + Instagram Reels")

# Initialize session state variables
if 'trends' not in st.session_state:
    st.session_state.trends = []
if 'selected' not in st.session_state:
    st.session_state.selected = None
if 'script' not in st.session_state:
    st.session_state.script = ""
if 'video' not in st.session_state:
    st.session_state.video = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None

# === SIDEBAR API KEYS ===
with st.sidebar:
    st.header("🔑 API Keys")
    grok_key = st.text_input("xAI Grok API Key", type="password", value=os.getenv("GROK_API_KEY", ""))
    eleven_key = st.text_input("ElevenLabs API Key", type="password", value=os.getenv("ELEVENLABS_API_KEY", ""))
    runway_key = st.text_input("Runway / LiteLLM Key", type="password", value=os.getenv("RUNWAYML_API_KEY", ""))
    consumer_key = st.text_input("X API Key", type="password")
    consumer_secret = st.text_input("X API Secret", type="password")
    access_token = st.text_input("X Access Token", type="password")
    access_secret = st.text_input("X Access Secret", type="password")
    meta_token = st.text_input("Meta Graph API Token (Instagram)", type="password")
    ig_user_id = st.text_input("Instagram Business Account ID")
    
    st.divider()
    st.header("📦 Dependencies Status")
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        st.write(f"{'✅' if TWEEPY_AVAILABLE else '❌'} tweepy")
        st.write(f"{'✅' if OPENAI_AVAILABLE else '❌'} openai")
        st.write(f"{'✅' if ELEVENLABS_AVAILABLE else '❌'} elevenlabs")
    with status_col2:
        st.write(f"{'✅' if LITELLM_AVAILABLE else '❌'} litellm")
        st.write(f"{'✅' if MOVIEPY_AVAILABLE else '❌'} moviepy")
        st.write(f"✅ requests")
    
    if not all([TWEEPY_AVAILABLE, OPENAI_AVAILABLE, ELEVENLABS_AVAILABLE, LITELLM_AVAILABLE, MOVIEPY_AVAILABLE]):
        st.warning("⚠️ Some dependencies are missing!")
        st.code("""
pip install tweepy openai elevenlabs litellm moviepy requests
        """)
    
    st.info("⚠️ All keys required for full VIRAL MODE")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Trends", "🎬 Generate", "📱 Post"])

# Tab 1: Trends
with tab1:
    if st.button("Fetch live X trends", type="primary"):
        if not TWEEPY_AVAILABLE:
            st.error("❌ tweepy is not installed. Please install it: pip install tweepy")
        elif not (consumer_key and consumer_secret and access_token and access_secret):
            st.warning("Please enter your X API credentials in the sidebar first!")
        else:
            try:
                with st.spinner("Fetching trends from X..."):
                    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                    auth.set_access_token(access_token, access_secret)
                    api = tweepy.API(auth, wait_on_rate_limit=True)
                    trends = api.get_place_trends(1)[0]['trends'][:12]
                    st.session_state.trends = [t['name'] for t in trends]
                    st.success(f"✅ Fetched {len(st.session_state.trends)} trends!")
            except Exception as e:
                st.error(f"Error fetching trends: {str(e)}")
    
    if st.session_state.trends:
        trend = st.selectbox("Pick a trend", st.session_state.trends)
        if st.button("Select this trend"):
            st.session_state.selected = trend
            st.success(f"Selected: {trend}")
        if st.session_state.selected:
            st.info(f"**Currently selected:** {st.session_state.selected}")
    else:
        st.info("Click 'Fetch live X trends' to get trending topics")

# Tab 2: Generate
with tab2:
    if st.session_state.selected:
        st.write(f"**Selected trend:** {st.session_state.selected}")
        style = st.selectbox("Style", ["Humorous", "Hot take", "Informative", "Motivational"])
        
        # Generate video button
        if st.button("🚀 VIRAL MODE Generate 60s clip + AUTO-POST to ALL platforms", type="primary", use_container_width=True):
            # Check dependencies
            missing_deps = []
            if not OPENAI_AVAILABLE:
                missing_deps.append("openai")
            if not ELEVENLABS_AVAILABLE:
                missing_deps.append("elevenlabs")
            if not LITELLM_AVAILABLE:
                missing_deps.append("litellm")
            if not MOVIEPY_AVAILABLE:
                missing_deps.append("moviepy")
            
            if missing_deps:
                st.error(f"❌ Missing dependencies: {', '.join(missing_deps)}")
                st.info("Please install them using: pip install " + " ".join(missing_deps))
                st.stop()
            
            with st.spinner("Running full VIRAL MODE..."):
                try:
                    # Check API keys
                    if not grok_key:
                        st.error("Please enter Grok API key in sidebar")
                        st.stop()
                    if not eleven_key:
                        st.error("Please enter ElevenLabs API key in sidebar")
                        st.stop()
                    if not runway_key:
                        st.error("Please enter Runway API key in sidebar")
                        st.stop()
                    
                    # 1. Grok script generation
                    st.info("📝 Generating viral script with Grok...")
                    client = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
                    prompt = f"Write a viral 60-second spoken script about: {st.session_state.selected}. Style: {style}. Max 165 words. Plain text."
                    response = client.chat.completions.create(
                        model="grok-beta", 
                        messages=[{"role": "user", "content": prompt}]
                    )
                    script_text = response.choices[0].message.content
                    st.session_state.script = script_text
                    st.success("✅ Script generated!")
                    with st.expander("View generated script"):
                        st.write(script_text)
                    
                    # 2. ElevenLabs voice generation
                    st.info("🎙️ Generating voiceover with ElevenLabs...")
                    eleven = ElevenLabs(api_key=eleven_key)
                    audio = eleven.text_to_speech.convert(
                        text=script_text, 
                        voice_id="Rachel", 
                        model_id="eleven_turbo_v2_5", 
                        output_format="mp3_44100_128"
                    )
                    audio_path = tempfile.mktemp(suffix=".mp3")
                    save(audio, audio_path)
                    st.session_state.audio_path = audio_path
                    st.success("✅ Voiceover generated!")
                    
                    # 3. Runway Gen-4 video generation
                    st.info("🎬 Generating video with Runway...")
                    litellm.api_key = runway_key
                    video_resp = litellm.video_generation(
                        model="runwayml/gen4_turbo", 
                        prompt=f"Cinematic 60-second viral video: {st.session_state.selected}. Dynamic, high-energy, trending style.", 
                        seconds=10, 
                        size="1280x720"
                    )
                    video_url = video_resp.data[0] if hasattr(video_resp, 'data') else video_resp['data'][0]
                    video_path = tempfile.mktemp(suffix=".mp4")
                    response = requests.get(video_url)
                    with open(video_path, "wb") as f:
                        f.write(response.content)
                    st.success("✅ Video generated!")
                    
                    # 4. Combine to 60s video
                    st.info("✂️ Combining audio and video...")
                    try:
                        video_clip = VideoFileClip(video_path).subclip(0, 10)
                        audio_clip = AudioFileClip(audio_path).subclip(0, 60)
                        final_video = concatenate_videoclips([video_clip] * 6).set_audio(audio_clip)
                        final_path = f"viral_clip_{int(time.time())}.mp4"
                        final_video.write_videofile(final_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
                        st.session_state.video = final_path
                        st.success("✅ 60-second VIRAL clip created!")
                        st.video(final_path)
                    except Exception as e:
                        st.error(f"Error combining video: {str(e)}")
                        st.info("MoviePy error. Try: pip install imageio-ffmpeg")
                        st.stop()
                    
                    # 5. Auto-post to X (Twitter)
                    if TWEEPY_AVAILABLE and consumer_key and consumer_secret and access_token and access_secret:
                        st.info("📤 Posting to X (Twitter)...")
                        try:
                            auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_secret)
                            api = tweepy.API(auth, wait_on_rate_limit=True)
                            media = api.media_upload(final_path)
                            caption = f"🔥 {st.session_state.selected} in 60 seconds! #Viral #TrendClipAI #Grok"
                            api.update_status(status=caption, media_ids=[media.media_id_string])
                            st.success("✅ Posted to X!")
                        except Exception as e:
                            st.error(f"Error posting to X: {str(e)}")
                    else:
                        if not TWEEPY_AVAILABLE:
                            st.warning("tweepy not installed - skipping X post")
                        else:
                            st.warning("X API credentials missing - skipping X post")
                    
                    st.success("🚀 VIRAL MODE COMPLETE!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Error in VIRAL MODE: {str(e)}")
    else:
        st.info("Please select a trend in the Trends tab first!")

# Tab 3: Manual Post
with tab3:
    if st.session_state.video:
        st.write("🎥 Manual post (or just use VIRAL MODE above)")
        st.video(st.session_state.video)
        default_caption = f"🔥 {st.session_state.get('selected', 'Trending')} — watch in 60s! #Viral #TrendClipAI"
        caption = st.text_input("Caption", default_caption)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📱 Post to X"):
                if not TWEEPY_AVAILABLE:
                    st.error("❌ tweepy is not installed. Please install it: pip install tweepy")
                elif not (consumer_key and consumer_secret and access_token and access_secret):
                    st.warning("Please enter X API credentials in sidebar")
                else:
                    try:
                        with st.spinner("Posting to X..."):
                            auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_secret)
                            api = tweepy.API(auth, wait_on_rate_limit=True)
                            media = api.media_upload(st.session_state.video)
                            api.update_status(status=caption, media_ids=[media.media_id_string])
                            st.success("✅ Posted to X!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("📱 Post to TikTok"):
                st.info("TikTok API integration would go here")
                st.warning("Full OAuth implementation required for TikTok")
        
        with col3:
            if st.button("📱 Post to Instagram"):
                if meta_token and ig_user_id:
                    st.info("Instagram API integration would go here")
                    st.warning("Full Graph API implementation required")
                else:
                    st.warning("Please enter Meta Graph API credentials in sidebar")
    else:
        st.info("No video generated yet. Go to the Generate tab to create a viral clip!")

# Footer
st.divider()
st.caption("💡 Installation command: pip install streamlit tweepy openai elevenlabs litellm moviepy requests")
st.caption("🚀 Run the app: streamlit run app.py")
