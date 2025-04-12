"""
MetadataService: Handles extraction and caching of YouTube video metadata.
"""
import time
from typing import List, Dict, Optional, Any

import yt_dlp
from yt_dlp.utils import DownloadError

from models import VideoInfo, AudioTrack, Subtitle


class MetadataService:
    """Service for extracting and caching metadata from YouTube videos."""
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize the metadata service.
        
        Args:
            cache_ttl: Time-to-live for cached metadata in seconds (default: 1 hour)
        """
        self._video_info_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl = cache_ttl
    
    def get_video_info(self, url: str) -> VideoInfo:
        """
        Get video information for a YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            VideoInfo object with video metadata
        """
        # Check cache first
        current_time = time.time()
        if url in self._video_info_cache:
            cache_time = self._cache_timestamps.get(url, 0)
            if current_time - cache_time < self._cache_ttl:
                info = self._video_info_cache[url]
                return self._create_video_info(info)
        
        # Cache miss or expired, extract info
        info = self._extract_video_info(url)
        
        # Update cache
        self._video_info_cache[url] = info
        self._cache_timestamps[url] = current_time
        
        return self._create_video_info(info)
    
    def get_audio_tracks(self, url: str) -> List[AudioTrack]:
        """
        Get available audio tracks for a YouTube video.
        
        Args:
            url: YouTube URL
            
        Returns:
            List of AudioTrack objects
        """
        info = self.get_video_info(url)
        audio_tracks: List[AudioTrack] = []
        processed_languages = set()
        
        for format in info.formats:
            # Filter for audio-only formats
            if (format.get('vcodec') == 'none' and 
                    format.get('acodec') != 'none' or 
                    format.get('resolution') == 'audio only'):
                
                format_id = format.get('format_id')
                
                # Extract language information
                language_name = None
                format_note = format.get('format_note', '')
                
                if format_note:
                    language_name = format_note.split(' - ')[0] if ' - ' in format_note else format_note
                
                if not language_name and format.get('language'):
                    language_name = format.get('language')
                
                if not language_name:
                    language_name = format.get('language') or 'default'
                
                # Skip if we've already processed this language
                if language_name.lower() in processed_languages:
                    continue
                
                # Get audio format details
                audio_ext = format.get('ext', '')
                protocol = format.get('protocol', '')
                abr = format.get('abr')
                
                # Create description
                description = f"{language_name} ({audio_ext}"
                if protocol and protocol not in ['http', 'https']:
                    description += f", {protocol}"
                if abr:
                    description += f", {abr}k"
                description += ")"
                
                if 'dubbed' in format_note.lower():
                    description += " [dubbed]"
                
                # Create audio track object
                audio_tracks.append(AudioTrack(
                    language=language_name,
                    format_id=format_id,
                    description=description,
                    codec=format.get('acodec'),
                    bitrate=format.get('abr')
                ))
                
                processed_languages.add(language_name.lower())
        
        return audio_tracks
    
    def get_available_subtitles(self, url: str) -> Dict[str, List[Subtitle]]:
        """
        Get available subtitles for a YouTube video.
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary of language codes to lists of Subtitle objects
        """
        info = self.get_video_info(url)
        subtitles: Dict[str, List[Subtitle]] = {}
        
        for lang_code, sub_list in info.subtitles.items():
            if not sub_list:
                continue
                
            subtitles[lang_code] = []
            for sub in sub_list:
                # Create subtitle object
                subtitle = Subtitle(
                    language=sub.get('name', lang_code),
                    language_code=lang_code,
                    format_id=sub.get('format_id', ''),
                    is_auto_generated='auto' in sub.get('name', '').lower()
                )
                subtitles[lang_code].append(subtitle)
        
        return subtitles
    
    def _extract_video_info(self, url: str) -> Dict[str, Any]:
        """
        Extract information from a YouTube URL using yt-dlp.
        
        Args:
            url: YouTube URL
            
        Returns:
            Raw video information dictionary
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'no_format_sort': True,
            'dump_single_json': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except DownloadError as e:
            raise ValueError(f"Failed to extract video information: {str(e)}")
    
    def _create_video_info(self, raw_info: Dict[str, Any]) -> VideoInfo:
        """
        Create a VideoInfo object from raw yt-dlp data.
        
        Args:
            raw_info: Raw video information from yt-dlp
            
        Returns:
            VideoInfo object
        """
        return VideoInfo(
            id=raw_info.get('id', ''),
            title=raw_info.get('title', 'Untitled'),
            formats=raw_info.get('formats', []),
            subtitles=raw_info.get('subtitles', {}),
            duration=raw_info.get('duration'),
            thumbnail_url=raw_info.get('thumbnail'),
            description=raw_info.get('description')
        )
