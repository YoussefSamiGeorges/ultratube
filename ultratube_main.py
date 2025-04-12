"""
UltraTube: A YouTube Media Downloader with CLI

This script provides a command-line interface for downloading YouTube videos and audio
with various options such as quality selection, subtitle downloading, and more.
"""
import os
import sys
import time
from typing import List, Dict, Optional, Tuple, Any

from ultratube_extractor import UltraTubeExtractor
from models import AudioTrack, DownloadOptions, ProcessOptions


def display_header() -> None:
    """Display the application header."""
    print("🎵🎥 UltraTube - YouTube Media Downloader")
    print()


def display_audio_track_options(extractor: UltraTubeExtractor, url: str) -> Optional[str]:
    """
    Display available audio tracks and allow user to select one.

    Args:
        extractor: The YouTube extractor instance
        url: YouTube URL

    Returns:
        Selected audio format ID or None
    """
    print("ℹ️ Fetching available audio tracks...")
    tracks = extractor.get_audio_tracks(url)

    if not tracks:
        print("⚠️ No separate audio tracks found.")
        return None

    # Print audio tracks as a simple table
    print("Available Audio Tracks:")
    print("-" * 80)
    print(f"{'#':<3} {'Language':<15} {'Format ID':<10} {'Quality':<10} {'Codec':<10}")
    print("-" * 80)

    for i, track in enumerate(tracks, 1):
        # Format bitrate
        bitrate = f"{track.bitrate}k" if track.bitrate else "N/A"

        print(f"{i:<3} {track.language:<15} {track.format_id:<10} {bitrate:<10} {track.codec or 'Unknown':<10}")

    print("-" * 80)

    choice = input("🔊 Select audio track (or Enter for default): ")

    if not choice:
        print("ℹ️ Using default audio track.")
        return None

    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(tracks):
            print(f"✅ Selected: {tracks[choice_idx].description}")
            return tracks[choice_idx].format_id
        else:
            print("⚠️ Invalid selection. Using default audio.")
            return None
    except ValueError:
        print("⚠️ Invalid input. Using default audio.")
        return None


def display_subtitle_options(extractor: UltraTubeExtractor, url: str, prompt_text: str) -> Optional[str]:
    """
    Display available subtitles and allow user to select one.

    Args:
        extractor: The YouTube extractor instance
        url: YouTube URL
        prompt_text: Text to display when prompting for selection

    Returns:
        Selected subtitle language code or None
    """
    print("ℹ️ Checking available subtitles...")
    subtitles = extractor.get_available_subtitles(url)

    if not subtitles:
        print("⚠️ No subtitles available for this video.")
        return None

    # Print subtitles as a simple table
    print("Available Subtitles:")
    print("-" * 70)
    print(f"{'#':<3} {'Language':<20} {'Code':<10} {'Auto-Generated'}")
    print("-" * 70)

    # Convert dictionary to list for display
    subtitle_languages = []
    for lang_code, subs in subtitles.items():
        if subs:  # Check if there are subtitles for this language
            subtitle_languages.append((lang_code, subs[0]))

    for i, (lang_code, subtitle) in enumerate(subtitle_languages, 1):
        auto_gen = "Yes ⚙️" if subtitle.is_auto_generated else "No"
        print(f"{i:<3} {subtitle.language:<20} {lang_code:<10} {auto_gen}")

    print("-" * 70)

    choice = input(f"📝 {prompt_text}: ")

    if not choice:
        return None

    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(subtitle_languages):
            selected = subtitle_languages[choice_idx]
            print(f"✅ Selected: {selected[1].language} ({selected[0]})")
            return subtitle_languages[choice_idx][0]  # Return language code
        else:
            print("⚠️ Invalid selection. No subtitles selected.")
            return None
    except ValueError:
        print("⚠️ Invalid input. No subtitles selected.")
        return None


def download_with_progress(
    extractor: UltraTubeExtractor,
    url: str,
    download_dir: str,
    is_audio: bool,
    quality: Optional[str] = None,
    audio_format_id: Optional[str] = None,
    subtitle_ids: Optional[List[str]] = None,
    include_metadata: bool = True,
    include_thumbnail: bool = True,
    include_chapters: bool = True
) -> Tuple[Optional[str], List[str]]:
    """
    Download media with a progress display.

    Args:
        extractor: The YouTube extractor instance
        url: YouTube URL
        download_dir: Directory to save downloads
        is_audio: Whether to download audio (True) or video (False)
        quality: Video quality (only for video downloads)
        audio_format_id: Specific audio format ID
        subtitle_ids: List of subtitle language codes
        include_metadata: Whether to include metadata
        include_thumbnail: Whether to include thumbnail
        include_chapters: Whether to include chapters

    Returns:
        Tuple of (media file path, list of subtitle file paths)
    """
    media_file = None
    subtitle_files = []
    start_time = time.time()

    # Prepare download options
    options = DownloadOptions(
        output_directory=download_dir,
        include_metadata=include_metadata,
        include_thumbnail=include_thumbnail,
        include_chapters=include_chapters,
        audio_format_id=audio_format_id,
        subtitle_ids=subtitle_ids or []
    )

    # Simple progress feedback
    content_type = "Audio" if is_audio else f"Video ({quality})"
    print(f"⏬ Downloading {content_type}...")

    try:
        # Perform the actual download
        if is_audio:
            media_file, subtitle_files = extractor.download_audio(
                url,
                download_dir,
                audio_format_id,
                subtitle_ids,
                include_metadata,
                include_thumbnail
            )
        else:
            media_file, subtitle_files = extractor.download_video(
                url,
                download_dir,
                quality or "highest",
                audio_format_id,
                subtitle_ids,
                include_metadata,
                include_thumbnail,
                include_chapters
            )

    except Exception as e:
        print(f"❌ Failed to download: {str(e)}")

    # Calculate download time
    elapsed_time = time.time() - start_time

    if media_file:
        print(f"✅ Download completed in {elapsed_time:.1f}s")
        print(f"💾 Media file: {media_file}")

    if subtitle_files:
        print(f"📝 Subtitles downloaded: {len(subtitle_files)}")

    return media_file, subtitle_files


def get_yes_no_input(prompt: str, default: bool = True) -> bool:
    """
    Get a yes/no input from the user.

    Args:
        prompt: The prompt to display
        default: Default value (True for yes, False for no)

    Returns:
        Boolean representing user's choice
    """
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()

    if not response:
        return default
    return response[0] == 'y'


def main() -> None:
    """Main function to run the YouTube Media Downloader with CLI."""
    try:
        # Initialize the YouTube extractor
        extractor = UltraTubeExtractor()

        # Display header
        display_header()

        while True:
            # Content type selection
            print("===== Main Menu =====")
            print("1. 🎵 Download Audio")
            print("2. 🎥 Download Video")
            print("3. 🚪 Exit")
            print()

            content_type = input("Choose an option [1/2/3] (default: 1): ")
            if not content_type:
                content_type = "1"

            if content_type == "3":
                print("👋 Goodbye! Thanks for using UltraTube!")
                break

            is_audio = content_type == "1"

            # Get URL and download directory
            url = input("🌐 Enter YouTube URL: ")

            default_dir = os.path.expanduser("~/Downloads")
            download_dir = input(f"📁 Enter download directory (default: {default_dir}): ")
            if not download_dir:
                download_dir = default_dir

            # Check if directory exists, create if not
            if not os.path.exists(download_dir):
                print(f"⚠️ Directory not found! Creating...")
                os.makedirs(download_dir, exist_ok=True)
                print(f"✅ Created directory: {download_dir}")

            # Check for audio tracks and subtitles
            print("\n🔍 Checking available options...")

            # Get audio tracks
            audio_format_id = display_audio_track_options(extractor, url)

            # Get primary subtitle
            primary_subtitle = display_subtitle_options(
                extractor,
                url,
                "Select primary subtitle language (or press Enter for none)"
            )

            # Get secondary subtitle if primary was selected
            secondary_subtitle = None
            if primary_subtitle:
                secondary_subtitle = display_subtitle_options(
                    extractor,
                    url,
                    "Select secondary subtitle language (or press Enter for none)"
                )

            # Create list of subtitle IDs
            subtitle_ids = []
            if primary_subtitle:
                subtitle_ids.append(primary_subtitle)
            if secondary_subtitle:
                subtitle_ids.append(secondary_subtitle)

            # Configure metadata options
            include_metadata = get_yes_no_input("📀 Include metadata?", True)
            include_thumbnail = get_yes_no_input("🖼️ Include thumbnail?", True)

            if is_audio:
                # Download audio
                print("\n⏬ Starting audio download...")

                media_file, subtitle_files = download_with_progress(
                    extractor,
                    url,
                    download_dir,
                    True,
                    None,
                    audio_format_id,
                    subtitle_ids,
                    include_metadata,
                    include_thumbnail,
                    True
                )

            else:
                # Video quality selection
                print("===== Video Quality =====")
                print("1. highest")
                print("2. 1080p (Full HD)")
                print("3. 720p (HD)")
                print("4. 480p (SD)")
                print("5. 360p")
                print("6. 240p")

                quality_choices = {
                    "1": "highest",
                    "2": "1080p (Full HD)",
                    "3": "720p (HD)",
                    "4": "480p (SD)",
                    "5": "360p",
                    "6": "240p"
                }

                quality_choice = input("🎮 Select video quality [1-6] (default: 1): ")
                if not quality_choice or quality_choice not in quality_choices:
                    quality_choice = "1"

                selected_quality = quality_choices[quality_choice].split(" ")[0]  # Extract just the resolution part
                quality_name = quality_choices[quality_choice]
                print(f"✅ Selected: {quality_name}")

                include_chapters = get_yes_no_input("📑 Include chapters?", True)

                # Download video
                print(f"\n⏬ Starting video download ({quality_name})...")

                media_file, subtitle_files = download_with_progress(
                    extractor,
                    url,
                    download_dir,
                    False,
                    selected_quality,
                    audio_format_id,
                    subtitle_ids,
                    include_metadata,
                    include_thumbnail,
                    include_chapters
                )

            # Handle subtitle merging
            if subtitle_files and media_file:
                if get_yes_no_input("🔀 Merge subtitles with media file?", True):
                    print("🔄 Merging subtitles...")
                    output_file = extractor.merge_subtitles(media_file, subtitle_files)

                    if output_file:
                        print("✅ Successfully merged subtitles!")
                        print(f"📝 Merged file: {output_file}")
                    else:
                        print("❌ Failed to merge subtitles")

            # Offer to download another
            print("\n🎉 Download completed successfully!")

            if not get_yes_no_input("🔄 Download another?", True):
                print("🚀 Happy downloading! Thanks for using UltraTube!")
                break

    except KeyboardInterrupt:
        print("\n👋 Download canceled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()