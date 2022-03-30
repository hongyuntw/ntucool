from __future__ import unicode_literals
from pydub import AudioSegment
import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
import argparse
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
import sys
def download_wav(video_url, output_name=None):
    ## download youtube

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    if output_name:
        ydl_opts['outtmpl'] =  f'./outputs/{output_name}.wav'
        

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', None)
        print(video_title)
        ydl.download([video_url])
        return output_name

def get_transcript(video_id, transcript_language):
    
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    print(transcript_list)
    transcript = transcript_list.find_manually_created_transcript([transcript_language,])
    texts = transcript.fetch()
    return texts


def split_wav_script(scripts, output_name):
    output_name = os.path.join('./outputs', output_name)
    os.makedirs(output_name, exist_ok=True)
    wav_name = f"{output_name}.wav"
    print(wav_name)
    audio = AudioSegment.from_file(wav_name)
    cur_audio = AudioSegment.empty()
    cur_sec = 0.0
    cur_script = ''
    wav_id = 0
    single_wav_sec = 8.0
    print(len(audio))

    for i, script in enumerate(scripts):
        text = script['text']
        start = float(script['start'])
        duration = float(script['duration'])
        end = start + duration

        start *= 1000
        end *= 1000
        cur_audio += audio[start:end]
        cur_script += ' ' + text
        cur_sec += duration

        if cur_sec >= single_wav_sec:
            file_name = str(wav_id).zfill(4)
            cur_audio.export(f'{output_name}/{file_name}.wav', format="wav")
            fp = open(f'{output_name}/{file_name}.txt', 'w', encoding='utf-8')
            print(cur_script, file=fp)
            fp.close()
            wav_id += 1
            print(cur_script)

            cur_audio = AudioSegment.empty()
            cur_sec = 0.0
            cur_script = ''
        
    if cur_script != '':
        file_name = str(wav_id).zfill(4)
        cur_audio.export(f'{output_name}/{file_name}.wav', format="wav")
        fp = open(f'{output_name}/{file_name}.txt', 'w', encoding='utf-8')
        print(text, file=fp)



if __name__ == '__main__':
    # video_url = 'https://www.youtube.com/watch?v=wWV0NCPD050&ab_channel=IrisYu'
    # video_url = 'https://www.youtube.com/watch?v=Lm4vgG-0loo&ab_channel=TEDxTaipei'
    # transcript_language = 'zh-TW'

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", dest="url", help="youtube video url", type=str)
    parser.add_argument("--lan", dest="lan", help="youtube video transcript language", type=str)
    args = parser.parse_args()

    video_url = args.url
    transcript_language = args.lan
    if not (video_url and transcript_language):
        sys.exit('[ERROR] url and transcript language are necessary')



    if not os.path.exists('./outputs'):
        os.makedirs('./outputs')


    parsed_url = urlparse(video_url)
    video_id = parse_qs(parsed_url.query)['v'][0]    
    output_name = f'{video_id}_{transcript_language}'

    download_wav(video_url, output_name)
    scripts = get_transcript(output_name, transcript_language)
    split_wav_script(scripts, output_name)