"""Image processing utilities for WiiVC Injector."""
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageOps


class ImageProcessor:
    """Handle image processing and conversion."""

    # Standard sizes for WiiVC images
    ICON_SIZE = (128, 128)
    BANNER_SIZE = (1280, 720)  # HD banner
    DRC_SIZE = (854, 480)      # GamePad screen
    LOGO_SIZE = (170, 42)

    @staticmethod
    def resize_image(
        input_path: Path,
        output_path: Path,
        target_size: Tuple[int, int],
        keep_aspect: bool = True
    ) -> bool:
        """
        Resize image to target size.

        Args:
            input_path: Input image path
            output_path: Output image path
            target_size: Target (width, height)
            keep_aspect: Maintain aspect ratio

        Returns:
            True if successful
        """
        try:
            with Image.open(input_path) as img:
                # Convert to RGBA if needed
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                if keep_aspect:
                    # Fit image within target size, maintaining aspect ratio
                    img.thumbnail(target_size, Image.Resampling.LANCZOS)

                    # Create new image with target size and paste centered
                    new_img = Image.new('RGBA', target_size, (0, 0, 0, 0))
                    paste_x = (target_size[0] - img.width) // 2
                    paste_y = (target_size[1] - img.height) // 2
                    new_img.paste(img, (paste_x, paste_y))
                    img = new_img
                else:
                    # Stretch to exact size
                    img = img.resize(target_size, Image.Resampling.LANCZOS)

                # Save as PNG
                img.save(output_path, 'PNG')
                return True

        except Exception as e:
            print(f"Error resizing image: {e}")
            return False

    @staticmethod
    def process_icon(input_path: Path, output_path: Path) -> bool:
        """
        Process icon image (128x128).

        Args:
            input_path: Input image
            output_path: Output PNG path

        Returns:
            True if successful
        """
        return ImageProcessor.resize_image(
            input_path,
            output_path,
            ImageProcessor.ICON_SIZE,
            keep_aspect=True
        )

    @staticmethod
    def process_banner(input_path: Path, output_path: Path) -> bool:
        """
        Process banner image (1280x720).

        Args:
            input_path: Input image
            output_path: Output PNG path

        Returns:
            True if successful
        """
        return ImageProcessor.resize_image(
            input_path,
            output_path,
            ImageProcessor.BANNER_SIZE,
            keep_aspect=False
        )

    @staticmethod
    def process_drc(input_path: Path, output_path: Path) -> bool:
        """
        Process DRC/GamePad image (854x480).

        Args:
            input_path: Input image
            output_path: Output PNG path

        Returns:
            True if successful
        """
        return ImageProcessor.resize_image(
            input_path,
            output_path,
            ImageProcessor.DRC_SIZE,
            keep_aspect=False
        )

    @staticmethod
    def process_logo(input_path: Path, output_path: Path) -> bool:
        """
        Process logo image (170x42).

        Args:
            input_path: Input image
            output_path: Output PNG path

        Returns:
            True if successful
        """
        return ImageProcessor.resize_image(
            input_path,
            output_path,
            ImageProcessor.LOGO_SIZE,
            keep_aspect=True
        )

    @staticmethod
    def create_thumbnail(input_path: Path, max_size: int = 256) -> Optional[Image.Image]:
        """
        Create thumbnail for preview.

        Args:
            input_path: Input image path
            max_size: Maximum width/height

        Returns:
            PIL Image or None
        """
        try:
            with Image.open(input_path) as img:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                return img.copy()
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return None

    @staticmethod
    def validate_image(path: Path) -> bool:
        """
        Check if file is a valid image.

        Args:
            path: Image path

        Returns:
            True if valid image
        """
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except Exception:
            return False


# Convenience instance
image_processor = ImageProcessor()
