import time

import yt_dlp


def get_available_subtitles(url):
    """
    Fetches and returns all available subtitles for a YouTube video.

    Args:
        url (str): YouTube URL to check for subtitles

    Returns:
        dict: Dictionary containing available subtitles with language codes as keys
    """
    subtitles = {}

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'no_format_sort': True,  # Prevents automatic format sorting
        'dump_single_json': True,  # Puts data into easily parseable JSON
        'ext': 'json3',  # Only fetch subtitles in json3 format
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            subtitles = info.get('subtitles', {})  # Extract subtitle info
    except Exception as e:
        print(f"Error retrieving subtitles: {str(e)}")
        return {}

    return subtitles


def display_subtitle_options(url):
    """
    Displays available subtitles for a YouTube video and allows user selection.

    Args:
        url (str): YouTube URL to check for subtitles

    Returns:
        str: Selected subtitle language code or None if no selection made
    """
    subs = get_available_subtitles(url)
    if not subs:
        print("No subtitles available for this video.")
        return None

    print("\nAvailable subtitles:")
    languages = list(subs.keys())
    for i, lang in enumerate(languages, 1):
        print(f"{i}. {subs[lang][0]['name']}")

    try:
        choice = input("\nSelect subtitle language (or press Enter for none): ").strip()
        if not choice:
            return None

        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(languages):
            return languages[choice_idx]
        else:
            print("Invalid selection. No subtitles selected.")
            return None
    except ValueError:
        print("Invalid input. No subtitles selected.")
        return None


# Example usage
print(display_subtitle_options("https://www.youtube.com/watch?v=NDsO1LT_0lw"))
