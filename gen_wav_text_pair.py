from __future__ import unicode_literals
from pydub import AudioSegment
import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
import argparse
from yt_dlp import YoutubeDL
from youtube_transcript_api import YouTubeTranscriptApi
import sys
import pysrt



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

def get_transcript(video_id):
    
    valid_lan_list = ['zh-TW', 'en']
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    results = []
    for transcript in transcript_list:
        if transcript.is_generated or transcript.language_code not in valid_lan_list:
            continue
        texts = transcript.fetch()
        results.append({
            'lang' : transcript.language_code,
            'scripts': texts,
        })
 
    return results


def split_wav_script(scripts, wav_name, output_folder):
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
            cur_audio.export(f'{output_folder}/{file_name}.wav', format="wav")
            fp = open(f'{output_folder}/{file_name}.txt', 'w', encoding='utf-8')
            cur_script = cur_script.strip()
            print(cur_script, file=fp)
            fp.close()
            wav_id += 1
            print(cur_script)

            cur_audio = AudioSegment.empty()
            cur_sec = 0.0
            cur_script = ''
        
    if cur_script != '':
        file_name = str(wav_id).zfill(4)
        cur_audio.export(f'{output_folder}/{file_name}.wav', format="wav")
        fp = open(f'{output_folder}/{file_name}.txt', 'w', encoding='utf-8')
        cur_script = cur_script.strip()
        print(cur_script, file=fp)




def conver_to_seconds(h, m, s, ms):
    m += h * 60
    s += m * 60
    s = s + ms / 1000.0
    return s


def convert_srt(srt_path):
    subs = pysrt.open(srt_path, encoding='utf-8')
    scripts = []
    for sub in subs:
        print(sub.start)
        start_sec = conver_to_seconds(sub.start.hours, sub.start.minutes, sub.start.seconds , sub.start.milliseconds)
        end_sec = conver_to_seconds(sub.end.hours, sub.end.minutes, sub.end.seconds , sub.end.milliseconds)
        duration = end_sec - start_sec
        print(start_sec, end_sec, duration)
        scripts.append({
            'text' : sub.text,
            'start' : start_sec,
            'duration' : duration
        })

    return scripts




if __name__ == '__main__':
    # video_url = 'https://www.youtube.com/watch?v=wWV0NCPD050&ab_channel=IrisYu'
    # video_url = 'https://www.youtube.com/watch?v=Lm4vgG-0loo&ab_channel=TEDxTaipei'
    # video_url = 'https://www.youtube.com/watch?v=wWV0NCPD050&ab_channel=IrisYu'
    # video_url = 'https://www.youtube.com/watch?v=6XhJtJU1rz4&ab_channel=webspeedyweb'


    # srt_path = './tsai_yin_wen_bbc.srt'
    # scripts = convert_srt(srt_path)
    # exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", dest="url", help="youtube video url", type=str)
    args = parser.parse_args()

    video_url = args.url
    if not video_url:
        sys.exit('[ERROR] url and transcript language are necessary')



    if not os.path.exists('./outputs'):
        os.makedirs('./outputs')


    parsed_url = urlparse(video_url)
    video_id = parse_qs(parsed_url.query)['v'][0]    
    scripts = get_transcript(video_id)
    # output_name = f'{video_id}'
    if len(scripts) == 0:
        # need ocr to build srt file
        print('no manually cc script found, need to use ocr')
        pass
    else:
        download_wav(video_url, video_id)
        for item in scripts:
            lang = item['lang']
            scripts = item['scripts']
            output_folder = os.path.join('./outputs', f'{video_id}_{lang}')
            os.makedirs(output_folder, exist_ok=True)
            split_wav_script(scripts, wav_name=f'./outputs/{video_id}.wav', output_folder=output_folder)

    


    

    
    
    