"""
FileService: Handles file operations for the YouTube downloader.
"""
import os
import subprocess
from typing import List, Optional

from models import ProcessOptions


class FileService:
    """Service for file operations related to media processing."""
    
    def merge_subtitles(
        self, 
        media_file: str, 
        subtitle_files: List[str], 
        output_file: str
    ) -> str:
        """
        Merge subtitles into a media file using ffmpeg.
        
        Args:
            media_file: Path to the media file
            subtitle_files: List of subtitle file paths
            output_file: Path to save the merged file
            
        Returns:
            Path to the merged file
        """
        if not subtitle_files:
            print("No subtitle files to merge.")
            return media_file
        
        try:
            # Prepare FFmpeg command
            subtitle_args = []
            for sub in subtitle_files:
                subtitle_args.extend(["-i", sub])
            
            command = [
                "ffmpeg", "-i", media_file,
                *subtitle_args,
                "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text",
                output_file
            ]
            
            # Execute FFmpeg command
            self._run_ffmpeg_command(command)
            print(f"Successfully merged subtitles into {output_file}")
            
            return output_file
        
        except Exception as e:
            print(f"Error merging subtitles: {str(e)}")
            return media_file
    
    def process_download(
        self, 
        file_path: str, 
        options: ProcessOptions
    ) -> str:
        """
        Process a downloaded file according to the given options.
        
        Args:
            file_path: Path to the file to process
            options: Processing options
            
        Returns:
            Path to the processed file
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return file_path
        
        try:
            # Generate output file path
            directory = os.path.dirname(file_path)
            filename = os.path.basename(file_path)
            base_name, _ = os.path.splitext(filename)
            output_file = os.path.join(directory, f"{base_name}_processed.{options.output_format}")
            
            # Basic FFmpeg command with format conversion
            command = [
                "ffmpeg", "-i", file_path,
                "-c:v", "copy", "-c:a", "copy"
            ]
            
            # Add quality parameters if specified
            if options.quality_level:
                command.extend(["-crf", str(options.quality_level)])
            
            # Add output file
            command.append(output_file)
            
            # Execute FFmpeg command
            self._run_ffmpeg_command(command)
            print(f"Successfully processed file to {output_file}")
            
            # Delete original if not keeping it
            if not options.keep_original:
                os.remove(file_path)
                print(f"Deleted original file: {file_path}")
            
            return output_file
        
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return file_path
    
    def cleanup_temp_files(self, files: List[str]) -> None:
        """
        Clean up temporary files.
        
        Args:
            files: List of file paths to clean up
        """
        for file_path in files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Deleted temporary file: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {str(e)}")
    
    def _run_ffmpeg_command(self, command: List[str]) -> None:
        """
        Run an FFmpeg command.
        
        Args:
            command: FFmpeg command as a list of arguments
            
        Raises:
            RuntimeError: If the command fails
        """
        try:
            # Run the command and capture output
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return process.stdout
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg command failed: {e.stderr}")
