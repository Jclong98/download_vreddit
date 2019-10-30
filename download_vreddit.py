import json
import os
import subprocess
from tempfile import TemporaryDirectory

import requests


def download_vreddit(url, output_path=None):
    """
    takes a reddit link, downloads the vreddit inside it.
    
    url: a link to a vreddit video

    output_path: a path to where you want the video saved

    """

    # opening a temporary directory so that ffmpeg can output and work with files
    with TemporaryDirectory() as temp_dir:

        # getting vreddit.son from a reddit url
        # User-agent is there to get around a 429 too many requests error
        try:
            r = requests.get(url, headers={'User-agent': 'vreddit downloader'})
        except requests.exceptions.MissingSchema as e:
            print(e)
            return

        try:
            json_url = r.url + ".json"
            r2 = requests.get(json_url, headers={'User-agent': 'vreddit downloader'})
            r_dict = json.loads(r2.text)

            # finding the video and audio urls to download
            video_url = r_dict[0]['data']['children'][0]['data']['secure_media']['reddit_video']['fallback_url']
            audio_url = r_dict[0]['data']['children'][0]['data']['url'] + "/audio"

        except KeyError as e:
            # if the keys for the media urls cannot be found, then it probably isnt a vreddit
            print(e)
            return

        except Exception as e:
            # if the page cannot be parsed as json, it might not be what we are looking for
            print(e)
            return

        print("getting video and audio for vreddit")

        # getting video and downloading it
        video_request = requests.get(video_url)
        with open(os.path.join(temp_dir ,'video.mp4'), 'wb') as f:
            f.write(video_request.content)

        # getting audio and downloading it
        audio_request = requests.get(audio_url)
        with open(os.path.join(temp_dir ,'audio.mp4'), 'wb') as f:
            f.write(audio_request.content)

        # combining audio and video into one file
        print("combining audio and video into one file")
        uncompressed_path = os.path.join(temp_dir, 'uncompressed.mp4')
        subprocess.call(f"ffmpeg.exe -i {os.path.join(temp_dir ,'video.mp4')} -i {os.path.join(temp_dir ,'audio.mp4')} -c copy {uncompressed_path}", shell=True)

        # compressing the video
        print("compressing the video")
        compressed_path = os.path.join(temp_dir, 'compressed.mp4')
        subprocess.call(f"ffmpeg.exe -i {uncompressed_path} -crf 30 {compressed_path}", shell=True)

        if output_path:
            video_bytes = open(compressed_path, 'rb').read()
            with open(output_path, 'wb') as f:
                f.write(video_bytes)

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser('downloads a vreddit from a link')

    # url = "https://www.reddit.com/r/RocketLeague/comments/doo4jw/i_went_afk_for_5_seconds/" # vreddit without sound
    # url = "https://www.reddit.com/r/ShitPostCrusaders/comments/d8nh9r/niasan/"
    # video_bytes = download_vreddit(url, './test.mp4')

    parser.add_argument('-u', '--url', help="a url that contains a vreddit video", required=True)
    parser.add_argument('-f', '--filename', help="The path/filename you want to save the file to", required=True)

    # parsing cmd args
    args = parser.parse_args()

    video_bytes = download_vreddit(args.url, args.filename)