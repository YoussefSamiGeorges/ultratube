import os
import subprocess
from typing import List, Dict, Optional, Union, Any, Tuple

import yt_dlp
from yt_dlp.utils import DownloadError


def get_audio_tracks(url: str) -> List[Dict[str, str]]:
    """
    Fetches and returns all available webm audio tracks for a YouTube video.

    Args:
        url (str): YouTube URL to check for audio tracks

    Returns:
        List[Dict[str, str]]: List of dictionaries containing audio track information
            Each dictionary contains:
            - 'language': Language code or name of the audio track
            - 'format_id': Format ID for use with yt-dlp
            - 'description': Human-readable description of the audio track
    """
    audio_tracks: List[Dict[str, str]] = []
    processed_languages: set[str] = set()  # Track languages we've already processed

    # Configure yt-dlp to only extract format information without downloading
    ydl_opts: Dict[str, Union[bool, str]] = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'no_format_sort': True,  # Prevents automatic format sorting
        'dump_single_json': True,  # Puts data into easily parseable JSON
    }

    try:
        # Create a YoutubeDL object to extract info
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract format information
            info: Dict[str, Any] = ydl.extract_info(url, download=False)

            # Loop through all formats
            for format in info.get('formats', []):
                # Filter for audio-only webm formats
                if (format.get('vcodec') == 'none' and
                        format.get('acodec') != 'none' and
                        format.get('ext') == 'webm'):

                    format_id: str = format.get('format_id', '')

                    # Extract language information from format_note if available
                    format_note: str = format.get('format_note', '')
                    language_name: Optional[str] = None

                    # Check for language in format_note (typically formatted as "Language, quality")
                    if format_note:
                        # Split by comma and get the first part (language name)
                        parts: List[str] = format_note.split(',', 1)
                        if parts:
                            language_name = parts[0].strip()

                    # If no format_note, try getting language from language field
                    if not language_name and format.get('language'):
                        language_name = format.get('language')

                    # Default to language code if available, otherwise "default"
                    if not language_name:
                        language_name = format.get('language') or 'default'

                    # Skip if we've already processed this language
                    if language_name.lower() in processed_languages:
                        continue

                    # Get audio bitrate for the description
                    abr: Union[str, float] = format.get('abr', 'unknown')

                    # Is this the default track?
                    is_default: bool = 'default' in format_note.lower()

                    # Create a user-friendly description
                    description: str = f"{language_name} (webm, {abr}k)"
                    if is_default:
                        description += " [default]"

                    # Add to our results and mark as processed
                    audio_tracks.append({
                        'language': language_name,
                        'format_id': format_id,
                        'description': description
                    })
                    processed_languages.add(language_name.lower())

    except Exception as e:
        print(f"Error retrieving audio tracks: {str(e)}")
        return []

    return audio_tracks


def display_audio_track_options(url: str) -> Optional[str]:
    """
    Displays available audio tracks for a YouTube video and allows user to select one.

    Args:
        url (str): YouTube URL to check for audio tracks

    Returns:
        Optional[str]: Format ID of the selected audio track, or None if no selection made
    """
    tracks: List[Dict[str, str]] = get_audio_tracks(url)

    if len(tracks) <= 1:
        print("No separate audio tracks found or unable to retrieve track information.")
        return None

    print("\nAvailable audio tracks:")
    for i, track in enumerate(tracks, 1):
        print(f"{i}. {track['description']}")

    try:
        choice: str = input("\nSelect audio track (or press Enter for default): ").strip()
        if not choice:
            return None

        choice_idx: int = int(choice) - 1
        if 0 <= choice_idx < len(tracks):
            return tracks[choice_idx]['format_id']
        else:
            print("Invalid selection. Using default audio.")
            return None
    except ValueError:
        print("Invalid input. Using default audio.")
        return None


def get_available_subtitles(url: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetches and returns all available subtitles for a YouTube video.

    Args:
        url (str): YouTube URL to check for subtitles

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary containing available subtitles with language codes as keys
    """
    subtitles: Dict[str, List[Dict[str, Any]]] = {}

    ydl_opts: Dict[str, Union[bool, str]] = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'no_format_sort': True,  # Prevents automatic format sorting
        'dump_single_json': True,  # Puts data into easily parseable JSON
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info: Dict[str, Any] = ydl.extract_info(url, download=False)
            subtitles = info.get('subtitles', {})  # Extract subtitle info
    except Exception as e:
        print(f"Error retrieving subtitles: {str(e)}")
        return {}

    return subtitles


def display_subtitle_options(url: str, prompt_text: str = "\nSelect subtitle language (or press Enter for none): ") -> \
Optional[str]:
    """
    Displays available subtitles for a YouTube video and allows user selection.

    Args:
        url (str): YouTube URL to check for subtitles
        prompt_text (str): Text to display when prompting for selection

    Returns:
        Optional[str]: Selected subtitle language code or None if no selection made
    """
    subs: Dict[str, List[Dict[str, Any]]] = get_available_subtitles(url)
    if not subs:
        print("No subtitles available for this video.")
        return None

    print("\nAvailable subtitles:")
    languages: List[str] = list(subs.keys())
    for i, lang in enumerate(languages, 1):
        print(f"{i}. {subs[lang][0].get('name', lang)}")

    try:
        choice: str = input(prompt_text).strip()
        if not choice:
            return None

        choice_idx: int = int(choice) - 1
        if 0 <= choice_idx < len(languages):
            return languages[choice_idx]
        else:
            print("Invalid selection. No subtitles selected.")
            return None
    except ValueError:
        print("Invalid input. No subtitles selected.")
        return None


def download_subtitles(url: str, subtitle_ids: List[str], download_dir: str) -> List[str]:
    """
    Downloads subtitles as .srt files for a given YouTube video.

    Args:
        url (str): YouTube video URL.
        subtitle_ids (List[str]): List of subtitle language codes to download.
        download_dir (str): Directory to save the downloaded subtitles.

    Returns:
        List[str]: List of paths to downloaded subtitle files.
    """
    if not subtitle_ids:
        return []

    ydl_opts: Dict[str, Union[bool, List[str], str]] = {
        'writesubtitles': True,
        'subtitleslangs': subtitle_ids,
        'subtitlesformat': 'vtt',
        'skip_download': True,
        'quiet': True,
        'outtmpl': os.path.join(download_dir, '%(title)s'),
    }

    subtitle_files: List[str] = []

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
            base_path = os.path.join(download_dir, video_title)

            # Construct the expected subtitle file paths
            for lang in subtitle_ids:
                sub_path = f"{base_path}.{lang}.vtt"
                if os.path.exists(sub_path):
                    subtitle_files.append(sub_path)
                    print(f"Downloaded subtitle: {sub_path}")

    except Exception as e:
        print(f"Error downloading subtitles: {str(e)}")

    return subtitle_files


def merge_subtitles(video_file: str, subtitle_files: List[str], output_file: str) -> None:
    """
    Merges subtitles into a video file using ffmpeg.

    Args:
        video_file (str): Path to the video or audio file.
        subtitle_files (List[str]): List of subtitle file paths.
        output_file (str): Path to save the merged file.
    """
    if not subtitle_files:
        print("No subtitle files to merge.")
        return

    try:
        subtitle_args: List[str] = []
        for sub in subtitle_files:
            subtitle_args.extend(["-i", sub])

        command: List[str] = [
            "ffmpeg", "-i", video_file,
            *subtitle_args,
            "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
            output_file
        ]

        subprocess.run(command, check=True)
        print(f"Successfully merged subtitles into {output_file}")
    except Exception as e:
        print(f"Error merging subtitles: {str(e)}")


def download_audio(
        url: str,
        download_dir: str,
        audio_format_id: Optional[str] = None,
        subtitle_ids: Optional[List[str]] = None
) -> Tuple[Optional[str], List[str]]:
    """
    Download audio from a YouTube URL.

    Args:
        url (str): YouTube URL to download from
        download_dir (str): Directory to save the downloaded audio
        audio_format_id (Optional[str], optional): Specific audio format to download. Defaults to None.
        subtitle_ids (Optional[List[str]], optional): List of subtitle language codes to download. Defaults to None.

    Returns:
        Tuple[Optional[str], List[str]]: Tuple containing (path to downloaded audio file, list of subtitle file paths)
    """
    ydl_opts: Dict[str, Union[str, bool, List[Dict[str, str]]]] = {
        'format': audio_format_id or 'bestaudio/best',
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
    audio_file_path: Optional[str] = None

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            title = info.get('title', 'audio')
            audio_file_path = os.path.join(download_dir, f"{title}.mp3")

    print("Audio download complete!")

    # Download subtitles if requested
    subtitle_files: List[str] = []
    if subtitle_ids:
        print("\nDownloading subtitles...")
        subtitle_files = download_subtitles(url, subtitle_ids, download_dir)

    return audio_file_path, subtitle_files


def download_video(
        url: str,
        download_dir: str,
        quality: str,
        metadata: Dict[str, bool],
        audio_format_id: Optional[str] = None,
        subtitle_ids: Optional[List[str]] = None
) -> Tuple[Optional[str], List[str]]:
    """
    Download video from a YouTube URL.

    Args:
        url (str): YouTube URL to download from
        download_dir (str): Directory to save the downloaded video
        quality (str): Desired video quality
        metadata (Dict[str, bool]): Metadata options for download
        audio_format_id (Optional[str], optional): Specific audio format to download. Defaults to None.
        subtitle_ids (Optional[List[str]], optional): List of subtitle language codes to download. Defaults to None.

    Returns:
        Tuple[Optional[str], List[str]]: Tuple containing (path to downloaded video file, list of subtitle file paths)
    """
    # Base format selector for video
    format_map: Dict[str, str] = {
        'highest': 'bestvideo[ext=mp4]',
        '1080p': 'bestvideo[height<=1080][ext=mp4]',
        '720p': 'bestvideo[height<=720][ext=mp4]',
        '480p': 'bestvideo[height<=480][ext=mp4]',
        '360p': 'bestvideo[height<=360][ext=mp4]',
        '240p': 'bestvideo[height<=240][ext=mp4]'
    }
    format_selector: str = format_map.get(quality, 'bestvideo[ext=mp4]')

    # Append audio format if specified, otherwise use best audio
    if audio_format_id:
        format_selector += f"+{audio_format_id}"
    else:
        format_selector += "+bestaudio[ext=m4a]"

    # Add fallback option
    format_selector += f"/best[height<={quality[:-1] if quality.endswith('p') else '1080'}][ext=mp4]/best"

    ydl_opts: Dict[str, Union[str, bool, List[Dict[str, str]]]] = {
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
    video_file_path: Optional[str] = None

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if info:
            title = info.get('title', 'video')
            video_file_path = os.path.join(download_dir, f"{title}.mp4")

    print("Video download complete!")

    # Download subtitles if requested
    subtitle_files: List[str] = []
    if subtitle_ids:
        print("\nDownloading subtitles...")
        subtitle_files = download_subtitles(url, subtitle_ids, download_dir)

    return video_file_path, subtitle_files


def main() -> None:
    """
    Main function to run the YouTube Media Downloader with subtitle support.
    """
    print("YouTube Media Downloader")
    print("========================")

    while True:
        try:
            # Content type selection
            content_type: str = input("\nChoose content type:\n1. Audio\n2. Video\n> ").strip()
            if content_type not in ['1', '2']:
                print("Invalid choice. Please enter 1 or 2.")
                continue

            # Common inputs
            url: str = input("\nEnter YouTube URL: ").strip()
            download_dir: str = input("Enter download directory: ").strip()
            os.makedirs(download_dir, exist_ok=True)

            # Check for audio tracks before downloading
            selected_audio_format: Optional[str] = display_audio_track_options(url)

            # Check for subtitles
            print("\nChecking for available subtitles...")
            primary_subtitle: Optional[str] = display_subtitle_options(url)

            # Check for a second subtitle if the first one was selected
            secondary_subtitle: Optional[str] = None
            if primary_subtitle:
                subs = get_available_subtitles(url)
                if len(subs) > 1:  # Only ask for second subtitle if multiple are available
                    print("\nSelect a second subtitle language (optional):")
                    secondary_subtitle = display_subtitle_options(url,
                                                                  "\nSelect second subtitle language (or press Enter for none): ")

            # Create a list of subtitle IDs to download
            subtitle_ids: List[str] = []
            if primary_subtitle:
                subtitle_ids.append(primary_subtitle)
            if secondary_subtitle:
                subtitle_ids.append(secondary_subtitle)

            if content_type == '1':
                # Download audio with selected options
                audio_file_path, subtitle_files = download_audio(
                    url,
                    download_dir,
                    selected_audio_format,
                    subtitle_ids
                )

                # Handle subtitle merging for audio
                if subtitle_files and audio_file_path:
                    merge_choice: str = input(
                        "\nDo you want to merge subtitles with the audio file? (y/n): ").strip().lower()
                    if merge_choice == 'y':
                        output_file = os.path.join(download_dir,
                                                   f"{os.path.splitext(os.path.basename(audio_file_path))[0]}_with_subs.mp4")
                        merge_subtitles(audio_file_path, subtitle_files, output_file)
            else:
                # Video quality selection
                quality: str = input("\nChoose video quality:\n"
                                     "1. Highest Quality\n"
                                     "2. 1080p\n"
                                     "3. 720p\n"
                                     "4. 480p\n"
                                     "5. 360p\n"
                                     "6. 240p\n> ").strip()

                quality_map: Dict[str, str] = {
                    '1': 'highest',
                    '2': '1080p',
                    '3': '720p',
                    '4': '480p',
                    '5': '360p',
                    '6': '240p'
                }
                selected_quality: str = quality_map.get(quality, 'highest')

                # Metadata selection
                metadata_input: str = input(
                    "\nInclude metadata:\n1. Thumbnail\n2. Chapters\n3. Both\n4. None\n> ").strip()
                metadata_map: Dict[str, Dict[str, bool]] = {
                    '1': {'thumbnail': True, 'chapters': False},
                    '2': {'thumbnail': False, 'chapters': True},
                    '3': {'thumbnail': True, 'chapters': True},
                    '4': {'thumbnail': False, 'chapters': False}
                }
                metadata: Dict[str, bool] = metadata_map.get(metadata_input, {'thumbnail': False, 'chapters': False})

                # Download video with selected options
                video_file_path, subtitle_files = download_video(
                    url,
                    download_dir,
                    selected_quality,
                    metadata,
                    selected_audio_format,
                    subtitle_ids
                )

                # Handle subtitle merging for video
                if subtitle_files and video_file_path:
                    merge_choice: str = input(
                        "\nDo you want to merge subtitles with the video file? (y/n): ").strip().lower()
                    if merge_choice == 'y':
                        output_file = os.path.join(download_dir,
                                                   f"{os.path.splitext(os.path.basename(video_file_path))[0]}_with_subs.mp4")
                        merge_subtitles(video_file_path, subtitle_files, output_file)

            if input("\nAnother download? (y/n): ").lower() != 'y':
                break

        except DownloadError as e:
            print(f"\nDownload error: {str(e)}")
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")


if __name__ == "__main__":
    main()