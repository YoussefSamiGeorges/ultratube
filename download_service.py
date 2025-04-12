"""
DownloadService: Handles downloading of YouTube media.
"""
import os
from typing import List, Dict, Optional, Any, Tuple, Union

import yt_dlp
from yt_dlp.utils import DownloadError

from metadata_service import MetadataService
from models import DownloadOptions


class DownloadService:
    """Service for downloading media from YouTube."""
    
    def __init__(self, metadata_service: MetadataService):
        """
        Initialize the download service.
        
        Args:
            metadata_service: Service for retrieving video metadata
        """
        self.metadata_service = metadata_service
    
    def download_audio(
        self, 
        url: str, 
        options: DownloadOptions
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download audio from a YouTube URL.
        
        Args:
            url: YouTube URL to download from
            options: Download options
            
        Returns:
            Tuple containing (path to downloaded audio file, list of subtitle file paths)
        """
        # Ensure the output directory exists
        os.makedirs(options.output_directory, exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': options.audio_format_id or 'bestaudio/best',
            'outtmpl': os.path.join(options.output_directory, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
            ],
            'verbose': False,
            'ignoreerrors': False,
        }
        
        # Add optional postprocessors
        if options.include_thumbnail:
            ydl_opts['writethumbnail'] = True
            ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})
            
        if options.include_metadata:
            ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata'})
        
        # Download the audio
        print("\nDownloading audio...")
        audio_file_path = None
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    title = info.get('title', 'audio')
                    # Normalize the title to a safe filename
                    safe_title = "".join(c if c.isalnum() or c in " -_." else "_" for c in title)
                    audio_file_path = os.path.join(options.output_directory, f"{safe_title}.mp3")
            
            print("Audio download complete!")
        except DownloadError as e:
            print(f"Error downloading audio: {str(e)}")
            return None, []
        
        # Download subtitles if requested
        subtitle_files = []
        if options.subtitle_ids:
            print("\nDownloading subtitles...")
            subtitle_files = self.download_subtitles(url, options.subtitle_ids, options.output_directory)
        
        return audio_file_path, subtitle_files
    
    def download_video(
        self, 
        url: str, 
        quality: str, 
        options: DownloadOptions
    ) -> Tuple[Optional[str], List[str]]:
        """
        Download video from a YouTube URL.
        
        Args:
            url: YouTube URL to download from
            quality: Desired video quality
            options: Download options
            
        Returns:
            Tuple containing (path to downloaded video file, list of subtitle file paths)
        """
        # Ensure the output directory exists
        os.makedirs(options.output_directory, exist_ok=True)
        
        # Map quality to format selector
        format_map = {
            'highest': 'bestvideo[ext=mp4]',
            '1080p': 'bestvideo[height<=1080][ext=mp4]',
            '720p': 'bestvideo[height<=720][ext=mp4]',
            '480p': 'bestvideo[height<=480][ext=mp4]',
            '360p': 'bestvideo[height<=360][ext=mp4]',
            '240p': 'bestvideo[height<=240][ext=mp4]'
        }
        format_selector = format_map.get(quality, 'bestvideo[ext=mp4]')
        
        # Append audio format if specified, otherwise use best audio
        if options.audio_format_id:
            format_selector += f"+{options.audio_format_id}"
        else:
            format_selector += "+bestaudio[ext=m4a]"
        
        # Add fallback option
        height = quality[:-1] if quality.endswith('p') and quality[:-1].isdigit() else '1080'
        format_selector += f"/best[height<={height}][ext=mp4]/best"
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': format_selector,
            'outtmpl': os.path.join(options.output_directory, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'postprocessors': [],
            'verbose': False,
            'ignoreerrors': False,
        }
        
        # Add optional features
        if options.include_thumbnail:
            ydl_opts['writethumbnail'] = True
            ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})
        
        if options.include_metadata:
            ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata'})
        
        if options.include_chapters:
            ydl_opts['embedchapters'] = True
        
        # Download the video
        print(f"\nDownloading {quality} video...")
        video_file_path = None
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    title = info.get('title', 'video')
                    # Normalize the title to a safe filename
                    safe_title = "".join(c if c.isalnum() or c in " -_." else "_" for c in title)
                    video_file_path = os.path.join(options.output_directory, f"{safe_title}.mp4")
            
            print("Video download complete!")
        except DownloadError as e:
            print(f"Error downloading video: {str(e)}")
            return None, []
        
        # Download subtitles if requested
        subtitle_files = []
        if options.subtitle_ids:
            print("\nDownloading subtitles...")
            subtitle_files = self.download_subtitles(url, options.subtitle_ids, options.output_directory)
        
        return video_file_path, subtitle_files
    
    def download_subtitles(
        self, 
        url: str, 
        subtitle_ids: List[str], 
        output_dir: str
    ) -> List[str]:
        """
        Download subtitles as .vtt files for a given YouTube video.
        
        Args:
            url: YouTube video URL
            subtitle_ids: List of subtitle language codes to download
            output_dir: Directory to save the downloaded subtitles
            
        Returns:
            List of paths to downloaded subtitle files
        """
        if not subtitle_ids:
            return []
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Configure yt-dlp options
        ydl_opts = {
            'writesubtitles': True,
            'subtitleslangs': subtitle_ids,
            'subtitlesformat': 'vtt',
            'skip_download': True,
            'quiet': True,
            'outtmpl': os.path.join(output_dir, '%(title)s'),
        }
        
        subtitle_files = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_title = info.get('title', 'video')
                # Normalize the title to a safe filename
                safe_title = "".join(c if c.isalnum() or c in " -_." else "_" for c in video_title)
                base_path = os.path.join(output_dir, safe_title)
                
                # Construct the expected subtitle file paths
                for lang in subtitle_ids:
                    sub_path = f"{base_path}.{lang}.vtt"
                    if os.path.exists(sub_path):
                        subtitle_files.append(sub_path)
                        print(f"Downloaded subtitle: {sub_path}")
        
        except Exception as e:
            print(f"Error downloading subtitles: {str(e)}")
        
        return subtitle_files
