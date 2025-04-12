# UltraTube 📹
A powerful and feature-rich YouTube media downloader built in Python.

## 📋 Overview
UltraTube is a command-line application that allows users to download audio and video content from YouTube with advanced options like multiple audio track selection, subtitle support, and quality preferences. Built with Python and powered by yt-dlp, this tool offers functionality that goes beyond basic downloaders.

**UltraTube aims to bring the YouTube experience offline, allowing users to enjoy their favorite content without an internet connection while preserving the quality, audio options, and subtitles of the original media.**

## ✨ Key Features
* **Flexible Media Options**
   * Download video or audio-only content
   * Select specific audio tracks (including dubbed versions)
   * Choose from multiple video quality settings (240p to highest)
* **Comprehensive Subtitle Support**
   * Download subtitles in multiple languages
   * Support for dual subtitles
   * Option to embed subtitles directly into media files
* **Enhanced Metadata Handling**
   * Thumbnail embedding
   * Chapter information preservation
   * Proper metadata tagging
* **User-Friendly Interface**
   * Clear command-line prompts
   * Descriptive output messages
   * Error handling and recovery

## 🚀 Getting Started
### Prerequisites
* Python 3.6+
* FFmpeg (must be installed and in your PATH)
* Internet connection

### Installation
1. Clone the repository:

```bash
git clone https://github.com/your-username/ultratube.git
cd ultratube
```

2. Install required dependencies:

```bash
pip install yt-dlp
```

3. Ensure FFmpeg is installed:
   * **Windows**: Download from ffmpeg.org and add to PATH
   * **macOS**: `brew install ffmpeg`
   * **Linux**: `sudo apt install ffmpeg` or equivalent for your distribution

### Usage
Run the application:

```bash
python ultratube_main.py
```

Follow the interactive prompts to:
1. Choose between audio or video download
2. Enter the YouTube URL
3. Specify the download directory
4. Select preferred audio track (if multiple available)
5. Choose subtitle language(s)
6. Select video quality (for video downloads)
7. Configure metadata options

## 🧮 How It Works
UltraTube utilizes the powerful yt-dlp library to:
1. Extract metadata from YouTube videos
2. Identify available audio tracks and subtitles
3. Download the selected content with specified options
4. Process and merge components using FFmpeg

The modular design allows for clear separation of concerns:
* Media information extraction
* User interface handling
* Download process management
* Post-processing and merging

## 📊 Code Structure
```
ultratube/
├── ultratube_main.py          # Main application with CLI interface
├── ultratube_extractor.py     # Core facade for YouTube extraction
├── download_service.py        # Handles media downloading
├── file_service.py            # File operations and processing
├── metadata_service.py        # Video metadata handling
├── models.py                  # Data models
└── README.md                  # Project documentation
```

## 📊 UML Class Diagram
To understand the project architecture, you can use the following UML class diagram. Copy and paste the PlantUML code below into any PlantUML renderer (like [PlantUML Online Server](https://www.plantuml.com/plantuml/uml/) or VS Code with PlantUML extension).

```
@startuml UltraTube Architecture

' Style and layout options
skinparam backgroundColor white
skinparam packageStyle rectangle
skinparam classFontSize 14
skinparam classFontName Arial
skinparam classAttributeFontSize 12
skinparam classAttributeFontName Arial

' Title
title UltraTube - YouTube Media Downloader Architecture

' Packages and Classes
package "Main Application" {
  class UltraTubeMain {
    + display_header()
    + display_audio_track_options()
    + display_subtitle_options()
    + download_with_progress()
    + get_yes_no_input()
    + main()
  }
}

package "Core" {
  class UltraTubeExtractor {
    - metadata_service: MetadataService
    - download_service: DownloadService
    - file_service: FileService
    + get_audio_tracks()
    + get_available_subtitles()
    + download_audio()
    + download_video()
    + merge_subtitles()
  }
}

package "Services" {
  class DownloadService {
    - metadata_service: MetadataService
    + download_audio()
    + download_video()
    + download_subtitles()
  }

  class MetadataService {
    - _video_info_cache: Dict
    - _cache_timestamps: Dict
    - _cache_ttl: int
    + get_video_info()
    + get_audio_tracks()
    + get_available_subtitles()
    - _extract_video_info()
    - _create_video_info()
  }

  class FileService {
    + merge_subtitles()
    + process_download()
    + cleanup_temp_files()
    - _run_ffmpeg_command()
  }
}

package "Models" {
  class VideoInfo {
    + id: str
    + title: str
    + formats: List[Dict]
    + subtitles: Dict
    + duration: Optional[int]
    + thumbnail_url: Optional[str]
    + description: Optional[str]
    + filename_safe_title()
  }

  class AudioTrack {
    + language: str
    + format_id: str
    + description: str
    + codec: Optional[str]
    + bitrate: Optional[int]
  }

  class Subtitle {
    + language: str
    + language_code: str
    + format_id: str
    + is_auto_generated: bool
  }

  class DownloadOptions {
    + output_directory: str
    + include_metadata: bool
    + include_thumbnail: bool
    + include_chapters: bool
    + audio_format_id: Optional[str]
    + subtitle_ids: List[str]
  }

  class ProcessOptions {
    + keep_original: bool
    + output_format: str
    + quality_level: Optional[int]
  }
}

package "External Libraries" {
  class "yt_dlp" as ytdlp {
    + YoutubeDL
    + extract_info()
    + download()
  }

  class "ffmpeg" as ffmpeg {
    + process media files
    + merge subtitles
    + convert formats
  }
}

' Relationships

' Main relationships
UltraTubeMain --> UltraTubeExtractor: uses
UltraTubeExtractor --* DownloadService: contains
UltraTubeExtractor --* MetadataService: contains
UltraTubeExtractor --* FileService: contains

' Service relationships
DownloadService --> MetadataService: uses
DownloadService --> ytdlp: uses
FileService --> ffmpeg: uses via subprocess

' Model relationships
DownloadService --> DownloadOptions: uses
FileService --> ProcessOptions: uses
MetadataService --> VideoInfo: creates
MetadataService --> AudioTrack: creates
MetadataService --> Subtitle: creates

' Service-to-model relationships
UltraTubeExtractor --> AudioTrack: returns
UltraTubeExtractor --> Subtitle: returns
UltraTubeExtractor --> DownloadOptions: uses

@enduml
```

## 🔒 Privacy and Security
* UltraTube respects YouTube's terms of service by using the yt-dlp library
* The application performs all operations locally
* No user data or download history is stored or transmitted

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🔄 Future Improvements
* [ ] Graphical user interface (GUI)
* [ ] Batch download support
* [ ] Download speed optimization
* [ ] Playlist handling
* [ ] Custom FFmpeg filters
* [ ] Format conversion options
* [ ] Download resume capability
* [ ] Multi-language interface support
* [ ] Download queue management
* [ ] Extended error handling and reporting
