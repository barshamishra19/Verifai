class MetadataDetector:
    def check_metadata(self, video_path):
        # Simplified logic: If video has no camera/source metadata, it's suspicious
        # Real production would use ffprobe here
        return 0.0 # Default confidence (no metadata found)