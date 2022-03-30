# ntucool


## Usage
```
python gen_wav_text_pair.py --url "[YOUTUBE_VIDEO_URL]"

example
python gen_wav_text_pair.py --url "https://www.youtube.com/watch?v=Lm4vgG-0loo&ab_channel=TEDxTaipei"
````
* YOUTUBE_VIDEO_URL = youtube url


Running ```gen_wav_text_pair.py``` will create a folder named ```outputs```, the folder structure will be like
```
.
|-- Lm4vgG-0loo_zh-TW ([video_ID]_[transcript_language])
|   |-- 0000.txt
|   |-- 0000.wav
|   |-- 0001.txt
|   |-- 0001.wav
      ...
|   |-- 0087.txt
|   `-- 0087.wav

Lm4vgG-0loo = video ID
zh-TW = transcript language
````
