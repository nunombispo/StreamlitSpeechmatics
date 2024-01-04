from decouple import config
from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from httpx import HTTPStatusError


# API key and language
AUTH_TOKEN = config("SPEECHMATICS_API_KEY")
LANGUAGE = "en"

# API Settings
settings = ConnectionSettings(
    url="https://asr.api.speechmatics.com/v2",
    auth_token=AUTH_TOKEN,
)

# Define transcription parameters
conf = {
    "type": "transcription",
    "transcription_config": {
        "language": LANGUAGE,
        "diarization": "speaker"
    },
    "summarization_config": {
        "content_type": "informative",
        "summary_length": "detailed",
        "summary_type": "paragraphs"
      },
    "auto_chapters_config": {}
}


# Transcribe the audio file
def transcribe(file_path):
    # Open the client using a context manager
    with BatchClient(settings) as client:
        try:
            # Submit the job
            job_id = client.submit_job(
                audio=file_path,
                transcription_config=conf,
            )
            print(f"job {job_id} submitted successfully, waiting for transcript")
            # Wait for the job to complete
            transcription = client.wait_for_completion(job_id, transcription_format="json")
            summary = transcription["summary"]["content"]
            chapters = transcription["chapters"]
            transcript = transcription["results"]
            # Return the transcript, summary and chapters
            return transcript, summary, chapters
        except HTTPStatusError:
            print("Invalid API key")


# Format the chapters
def format_chapters(chapters):
    chapter_list = []
    for chapter in chapters:
        start_time = chapter['start_time']
        end_time = chapter['end_time']
        title = chapter['title']
        chapter_summary = chapter['summary']
        start_time_minutes_seconds = f"{start_time // 60:02.0f}:{start_time % 60:02.0f}"
        end_time_minutes_seconds = f"{end_time // 60:02.0f}:{end_time % 60:02.0f}"
        chapter_list.append({
            "start": start_time_minutes_seconds,
            "end": end_time_minutes_seconds,
            "title": title,
            "summary": chapter_summary
        })
    return chapter_list


# Format the transcript
def format_transcript(transcript):
    transcript_list = []
    current_speaker = None
    content = ''
    for alternatives in transcript:
        alternative = alternatives['alternatives'][0]
        # Get the speaker
        speaker = alternative['speaker']
        if current_speaker is None:
            current_speaker = speaker
        # Get the text and type and end of sentence
        text = alternative['content']
        type_text = alternatives['type']
        end_of_sentence = False
        if 'is_eos' in alternatives:
            end_of_sentence = alternatives['is_eos']
        # If the speaker is the same, append the text
        if current_speaker == speaker:
            if type_text != 'punctuation':
                content += ' '
            content += text
            if end_of_sentence:
                # If the sentence ends, append the text to the transcript list
                content += '\n\n'
        else:
            # If the speaker is different, append the text to the transcript list
            transcript_list.append({
                "speaker": current_speaker.replace('S', 'SPEAKER '),
                "text": content
            })
            # Reset the content and speaker
            content = text
            current_speaker = None
    return transcript_list
