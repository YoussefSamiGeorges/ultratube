import os
import yt_dlp
from yt_dlp.utils import DownloadError


def main():
    print("YouTube Media Downloader")
    print("========================")

    while True:
        try:
            # Content type selection
            content_type = input("\nChoose content type:\n1. Audio\n2. Video\n> ").strip()
            if content_type not in ['1', '2']:
                print("Invalid choice. Please enter 1 or 2.")
                continue

            # Common inputs
            url = input("\nEnter YouTube URL: ").strip()
            download_dir = input("Enter download directory: ").strip()
            os.makedirs(download_dir, exist_ok=True)

            if content_type == '1':
                download_audio(url, download_dir)
            else:
                # Video quality selection
                quality = input("\nChoose video quality:\n"
                                "1. Highest Quality\n"
                                "2. 1080p\n"
                                "3. 720p\n"
                                "4. 480p\n"
                                "5. 360p\n"
                                "6. 240p\n> ").strip()

                quality_map = {
                    '1': 'highest',
                    '2': '1080p',
                    '3': '720p',
                    '4': '480p',
                    '5': '360p',
                    '6': '240p'
                }
                selected_quality = quality_map.get(quality, 'highest')

                # Metadata selection
                metadata = input("\nInclude metadata:\n1. Thumbnail\n2. Chapters\n3. Both\n4. None\n> ").strip()
                metadata_map = {
                    '1': {'thumbnail': True, 'chapters': False},
                    '2': {'thumbnail': False, 'chapters': True},
                    '3': {'thumbnail': True, 'chapters': True},
                    '4': {'thumbnail': False, 'chapters': False}
                }
                metadata = metadata_map.get(metadata, {'thumbnail': False, 'chapters': False})

                download_video(url, download_dir, selected_quality, metadata)

            if input("\nAnother download? (y/n): ").lower() != 'y':
                break

        except DownloadError as e:
            print(f"\nDownload error: {str(e)}")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")


def download_audio(url, download_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
        'writethumbnail': True,
        'verbose': False,
        'ignoreerrors': False,
    }

    print("\nDownloading audio...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Audio download complete!")


def download_video(url, download_dir, quality, metadata):
    format_selector = {
        'highest': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]',
        '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]',
        '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]',
        '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]',
        '240p': 'bestvideo[height<=240][ext=mp4]+bestaudio[ext=m4a]/best[height<=240][ext=mp4]'
    }.get(quality, 'best')

    ydl_opts = {
        'format': format_selector,
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'writethumbnail': metadata['thumbnail'],
        'embedthumbnail': metadata['thumbnail'],
        'writeautomaticsub': False,
        'embedsubtitles': False,
        'embedchapters': metadata['chapters'],
        'merge_output_format': 'mp4',
        'postprocessors': [
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ],
        'verbose': False,
        'ignoreerrors': False,
    }

    print(f"\nDownloading {quality} video...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Video download complete!")


if __name__ == "__main__":
    main()