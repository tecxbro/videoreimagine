#!/usr/bin/env python3
"""
Video Scene Detection and Splitting Module

A self-contained module for detecting scene boundaries in videos using PySceneDetect
and splitting them into individual clip files using FFmpeg.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Tuple, Union

try:
    from scenedetect import detect, AdaptiveDetector, split_video_ffmpeg
    from scenedetect.video_manager import VideoManager
    from scenedetect.scene_manager import SceneManager
    from scenedetect.frame_timecode import FrameTimecode
    import cv2
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install scenedetect[opencv] rich")
    sys.exit(3)

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

__all__ = ['detect_scenes', 'split_video', 'detect_and_split']


def detect_scenes(
    video_path: str,
    adaptive_threshold: float = 2.0,
    min_scene_len: int = 15,
    window: int = 20
) -> List[Tuple[float, float]]:
    """
    Detect scene boundaries in a video using PySceneDetect's AdaptiveDetector.
    
    Args:
        video_path: Path to the input video file
        adaptive_threshold: Ratio threshold for scene detection (default: 2.0)
        min_scene_len: Minimum scene length in frames (default: 15)
        window: Rolling average window size in frames (default: 20)
    
    Returns:
        List of tuples containing (start_sec, end_sec) for each scene
        
    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video file is invalid or corrupted
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    logger.info(f"Detecting scenes in {video_path}")
    logger.debug(f"Parameters: threshold={adaptive_threshold}, min_len={min_scene_len}, window={window}")
    
    try:
        # Create adaptive detector with specified parameters
        detector = AdaptiveDetector(
            adaptive_threshold=adaptive_threshold,
            min_scene_len=min_scene_len,
            window=window
        )
        
        # Detect scenes using PySceneDetect
        scene_list = detect(
            str(video_path),
            detector,
            show_progress=False  # We'll handle progress ourselves
        )
        
        # Convert FrameTimecode objects to float seconds
        scenes = []
        for start, end in scene_list:
            start_sec = start.get_seconds()
            end_sec = end.get_seconds()
            scenes.append((start_sec, end_sec))
        
        logger.info(f"Detected {len(scenes)} scenes")
        return scenes
        
    except Exception as e:
        logger.error(f"Error detecting scenes: {e}")
        raise ValueError(f"Failed to process video: {e}")


def split_video(
    video_path: str,
    scene_list: List[Tuple[float, float]],
    output_dir: Union[str, Path] = "clips"
) -> None:
    """
    Split a video into individual clip files based on scene boundaries.
    
    Args:
        video_path: Path to the input video file
        scene_list: List of (start_sec, end_sec) tuples for scene boundaries
        output_dir: Directory to save output clips (default: "clips")
        
    Raises:
        FileNotFoundError: If video file doesn't exist
        OSError: If output directory cannot be created
        RuntimeError: If FFmpeg splitting fails
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Splitting video into {len(scene_list)} clips")
    logger.info(f"Output directory: {output_dir}")
    
    try:
        # Get FPS once via OpenCV
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        cap.release()
        
        # Convert seconds → FrameTimecode tuples
        scenes_ftc = [
            (FrameTimecode(start_sec, fps=fps),
             FrameTimecode(end_sec, fps=fps))
            for start_sec, end_sec in scene_list
        ]
        
        # Split video using FFmpeg
        split_video_ffmpeg(
            str(video_path),
            scenes_ftc,
            str(output_dir),
            suppress_output=True
        )
        
        logger.info("Video splitting completed successfully")
        
    except Exception as e:
        logger.error(f"Error splitting video: {e}")
        raise RuntimeError(f"Failed to split video: {e}")


def detect_and_split(video_path: str, **kwargs) -> List[Path]:
    """
    Convenience wrapper: detect scenes then split video into clips.
    
    Args:
        video_path: Path to the input video file
        **kwargs: Additional arguments passed to detect_scenes and split_video
        
    Returns:
        List of Path objects pointing to the created clip files
        
    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video processing fails
    """
    # Extract parameters for detect_scenes
    adaptive_threshold = kwargs.get('adaptive_threshold', 2.0)
    min_scene_len = kwargs.get('min_scene_len', 15)
    window = kwargs.get('window', 20)
    output_dir = kwargs.get('output_dir', 'clips')
    
    # Detect scenes
    scenes = detect_scenes(
        video_path,
        adaptive_threshold=adaptive_threshold,
        min_scene_len=min_scene_len,
        window=window
    )
    
    # Split video
    split_video(video_path, scenes, output_dir)
    
    # Return list of created clip files
    output_path = Path(output_dir)
    clip_files = sorted(output_path.glob("*.mp4"))
    
    logger.info(f"Created {len(clip_files)} clip files")
    return clip_files


def create_stats_table(scenes: List[Tuple[float, float]], video_path: str) -> Table:
    """Create a rich table showing scene statistics."""
    if not RICH_AVAILABLE:
        return None
    
    table = Table(title=f"Scene Analysis: {Path(video_path).name}")
    table.add_column("Scene", style="cyan", no_wrap=True)
    table.add_column("Start (s)", style="green")
    table.add_column("End (s)", style="green")
    table.add_column("Duration (s)", style="yellow")
    
    for i, (start, end) in enumerate(scenes, 1):
        duration = end - start
        table.add_row(
            f"Scene {i:02d}",
            f"{start:.2f}",
            f"{end:.2f}",
            f"{duration:.2f}"
        )
    
    return table


def save_stats_csv(scenes: List[Tuple[float, float]], stats_file: str) -> None:
    """Save scene statistics to a CSV file."""
    import csv
    
    with open(stats_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Scene', 'Start_Seconds', 'End_Seconds', 'Duration_Seconds'])
        
        for i, (start, end) in enumerate(scenes, 1):
            duration = end - start
            writer.writerow([f"Scene_{i:02d}", start, end, duration])
    
    logger.info(f"Statistics saved to {stats_file}")


def main() -> int:
    """CLI entry point for the scene detection and splitting tool."""
    parser = argparse.ArgumentParser(
        description="Detect and split video scenes using PySceneDetect",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python splitter.py -i video.mp4
  python splitter.py -i video.mp4 -t 1.5 -m 10 -o my_clips/
  python splitter.py -i video.mp4 --dry-run --stats-file stats.csv
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input video file path'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=2.0,
        help='Adaptive threshold for scene detection (default: 2.0)'
    )
    
    parser.add_argument(
        '-m', '--min-len',
        type=int,
        default=15,
        help='Minimum scene length in frames (default: 15)'
    )
    
    parser.add_argument(
        '-w', '--window',
        type=int,
        default=20,
        help='Rolling average window size in frames (default: 20)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='clips',
        help='Output directory for clips (default: clips/)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Detect scenes but do not split video'
    )
    
    parser.add_argument(
        '--stats-file',
        help='Save scene statistics to CSV file'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate input file
    if not Path(args.input).exists():
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    try:
        # Detect scenes
        scenes = detect_scenes(
            args.input,
            adaptive_threshold=args.threshold,
            min_scene_len=args.min_len,
            window=args.window
        )
        
        # Display results
        if RICH_AVAILABLE:
            console = Console()
            console.print(f"\n[bold green]✓[/bold green] Detected {len(scenes)} scenes in {Path(args.input).name}")
            
            table = create_stats_table(scenes, args.input)
            if table:
                console.print(table)
        else:
            logger.info(f"Detected {len(scenes)} scenes")
            for i, (start, end) in enumerate(scenes, 1):
                duration = end - start
                logger.info(f"Scene {i:02d}: {start:.2f}s - {end:.2f}s (duration: {duration:.2f}s)")
        
        # Save statistics if requested or auto-save on dry run
        if args.stats_file:
            save_stats_csv(scenes, args.stats_file)
        elif args.dry_run:
            # Auto-name CSV file for dry run
            video_name = Path(args.input).stem
            auto_stats_file = f"{video_name}-scenes.csv"
            save_stats_csv(scenes, auto_stats_file)
        
        # Split video unless dry run
        if not args.dry_run:
            split_video(args.input, scenes, args.output)
            
            if RICH_AVAILABLE:
                console.print(f"\n[bold green]✓[/bold green] Video split into clips in '{args.output}/'")
        
        return 0
        
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Processing error: {e}")
        return 2
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main()) 