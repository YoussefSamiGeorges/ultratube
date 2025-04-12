"""
YouTubeExtractor: Main facade that coordinates the services for YouTube downloading.
"""
import os
from typing import List, Dict, Optional, Any, Tuple

from metadata_service import MetadataService
from download_service import DownloadService, DownloadOptions
from file_service import FileService, ProcessOptions
from models import AudioTrack, Subtitle


class UltraTubeExtractor:
    """Main facade for the YouTube downloader."""

    def __init__(self):
        """Initialize the YouTube extractor with its required services."""
        self.metadata_service = MetadataService()
        self.download_service = DownloadService(self.metadata_service)
        self.file_service = FileService()

    def get_audio_tracks(self, url: str) -> List[AudioTrack]:
        """
        Get available audio tracks for a YouTube video.
        
        Args:
            url: The YouTube URL
            
        Returns:
            A list of AudioTrack objects
        """
        return self.metadata_service.get_audio_tracks(url)

    def get_available_subtitles(self, url: str) -> Dict[str, List[Subtitle]]:
        """
        Get available subtitles for a YouTube video.
        
        Args:
            url: The YouTube URL
            
        Returns:
            A dictionary of subtitle language codes to Subtitle objects
        """
        return self.metadata_service.get_available_subtitles(url)

    def download_audio(
        self, 
        url: str, 
        download_dir: str,
        audio_format_id: Optional[str] = None,
        subtitle_ids: Optional[List[str]] = None,
        include_metadata: bool = True,
        include_thumbnail: bool = True
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download audio from a YouTube URL.
        
        Args:
            url: YouTube URL to download from
            download_dir: Directory to save the downloaded audio
            audio_format_id: Specific audio format to download
            subtitle_ids: List of subtitle language codes to download
            include_metadata: Whether to include metadata in the download
            include_thumbnail: Whether to include the thumbnail in the download
            
        Returns:
            Tuple containing (path to downloaded audio file, list of subtitle file paths)
        """
        options = DownloadOptions(
            output_directory=download_dir,
            include_metadata=include_metadata,
            include_thumbnail=include_thumbnail,
            include_chapters=True,
            audio_format_id=audio_format_id,
            subtitle_ids=subtitle_ids or []
        )
        
        return self.download_service.download_audio(url, options)

    def download_video(
        self,
        url: str,
        download_dir: str,
        quality: str,
        audio_format_id: Optional[str] = None,
        subtitle_ids: Optional[List[str]] = None,
        include_metadata: bool = True,
        include_thumbnail: bool = True,
        include_chapters: bool = True
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download video from a YouTube URL.
        
        Args:
            url: YouTube URL to download from
            download_dir: Directory to save the downloaded video
            quality: Desired video quality (e.g. 'highest', '1080p')
            audio_format_id: Specific audio format to download
            subtitle_ids: List of subtitle language codes to download
            include_metadata: Whether to include metadata in the download
            include_thumbnail: Whether to include the thumbnail in the download
            include_chapters: Whether to include chapters in the download
            
        Returns:
            Tuple containing (path to downloaded video file, list of subtitle file paths)
        """
        options = DownloadOptions(
            output_directory=download_dir,
            include_metadata=include_metadata,
            include_thumbnail=include_thumbnail,
            include_chapters=include_chapters,
            audio_format_id=audio_format_id,
            subtitle_ids=subtitle_ids or []
        )
        
        return self.download_service.download_video(url, quality, options)

    def merge_subtitles(
        self, 
        media_file: str, 
        subtitle_files: List[str], 
        output_file: Optional[str] = None
    ) -> str:
        """
        Merge subtitles into a media file.
        
        Args:
            media_file: Path to the media file
            subtitle_files: List of subtitle file paths
            output_file: Path to save the merged file (optional)
            
        Returns:
            Path to the merged file
        """
        if not output_file:
            # Generate output file name if not provided
            base_name = os.path.splitext(os.path.basename(media_file))[0]
            directory = os.path.dirname(media_file)
            output_file = os.path.join(directory, f"{base_name}_with_subs.mp4")
        
        return self.file_service.merge_subtitles(media_file, subtitle_files, output_file)
