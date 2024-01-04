import streamlit as st
import yt_dlp
from speechmatics_client import transcribe, format_chapters, format_transcript

# Set page title
st.set_page_config(page_title="YouTube Content Analysis using Speechmatics", layout='wide')

# Title for your app
st.title('YouTube Content Analysis using Speechmatics')

# Input field for YouTube URL
youtube_url = st.text_input('Enter YouTube URL', placeholder='Paste YouTube URL here...')

# Check if the URL is entered and display it
if youtube_url:
    with st.status('Processing YouTube URL...', expanded=True):
        st.write('Downloading YouTube video...')
        # Get the video ID
        video_id = yt_dlp.YoutubeDL().extract_info(url=youtube_url, download=False)['id']
        filename = f'{video_id}.mp3'
        # Set the options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename
        }
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        # Call Speechmatics API
        st.write('Calling Speechmatics API...')
        transcript, summary, chapters = transcribe(filename)

    # Display the results
    st.divider()
    st.subheader('Transcript')
    transcript_list = format_transcript(transcript)
    for transcript in transcript_list:
        st.markdown(f"**{transcript['speaker']}:**")
        st.markdown(f"{transcript['text']}")
    st.divider()
    st.subheader('Summary')
    st.write(summary)
    st.divider()
    st.subheader('Chapters')
    chapter_list = format_chapters(chapters)
    for chapter in chapter_list:
        st.write(f"{chapter['start']} - {chapter['end']}: {chapter['title']}")
        st.caption(chapter['summary'])

