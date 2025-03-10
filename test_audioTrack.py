import os
import yt_dlp
from yt_dlp.utils import DownloadError


def get_audio_tracks(url):
    """
    Fetches and returns all available webm audio tracks for a YouTube video.

    Args:
        url (str): YouTube URL to check for audio tracks

    Returns:
        list: List of dictionaries containing audio track information
            Each dictionary contains:
            - 'language': Language code or name of the audio track
            - 'format_id': Format ID for use with yt-dlp
            - 'description': Human-readable description of the audio track
    """
    audio_tracks = []
    processed_languages = set()  # Track languages we've already processed

    # Configure yt-dlp to only extract format information without downloading
    ydl_opts = {
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
            info = ydl.extract_info(url, download=False)

            # Loop through all formats
            for format in info.get('formats', []):
                # Filter for audio-only webm formats
                if (format.get('vcodec') == 'none' and
                        format.get('acodec') != 'none' and
                        format.get('ext') == 'webm'):

                    format_id = format.get('format_id')

                    # Extract language information from format_note if available
                    format_note = format.get('format_note', '')
                    language_name = None

                    # Check for language in format_note (typically formatted as "Language, quality")
                    if format_note:
                        # Split by comma and get the first part (language name)
                        parts = format_note.split(',', 1)
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
                    abr = format.get('abr', 'unknown')

                    # Is this the default track?
                    is_default = 'default' in format_note.lower()

                    # Create a user-friendly description
                    description = f"{language_name} (webm, {abr}k)"
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


def display_audio_track_options(url):
    """
    Displays available audio tracks for a YouTube video and allows user to select one.

    Args:
        url (str): YouTube URL to check for audio tracks

    Returns:
        str: Format ID of the selected audio track, or None if no selection made
    """
    tracks = get_audio_tracks(url)

    if len(tracks) <= 1:
        print("No separate audio tracks found or unable to retrieve track information.")
        return None

    print("\nAvailable audio tracks:")
    for i, track in enumerate(tracks, 1):
        print(f"{i}. {track['description']}")

    try:
        choice = input("\nSelect audio track (or press Enter for default): ").strip()
        if not choice:
            return None

        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(tracks):
            return tracks[choice_idx]['format_id']
        else:
            print("Invalid selection. Using default audio.")
            return None
    except ValueError:
        print("Invalid input. Using default audio.")
        return None

display_audio_track_options("https://www.youtube.com/watch?v=NDsO1LT_0lw")