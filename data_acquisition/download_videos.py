"""
To be updated to include a sample of TLGs, majors, Roundhorsin
"""
import yt_dlp as youtube_dl

def download_videos(urls, output_dir):
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'merge_output_format': 'mp4'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)

urls = [
    'https://www.youtube.com/watch?v=gqHPRuo8Gmo',
    # Add more URLs here
]

output_dir = 'output_videos'
download_videos(urls, output_dir)
