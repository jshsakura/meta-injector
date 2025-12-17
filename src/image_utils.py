"""Image processing utilities for WiiVC Injector."""
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageOps, ImageDraw


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
    def add_gamepad_badge(img: Image.Image, badge_type: str = None) -> Image.Image:
        """
        Add gamepad badge to bottom-right corner of icon.

        Args:
            img: Input image (should be 128x128)
            badge_type: 'galaxy_allstars' (red) or 'galaxy_nvidia' (green) or None

        Returns:
            Image with badge overlay
        """
        if not badge_type or badge_type not in ['galaxy_allstars', 'galaxy_nvidia', 'gct']:
            return img

        # Create badge (36x28 for wider aspect ratio)
        badge_width = 36
        badge_height = 28
        badge = Image.new('RGBA', (badge_width, badge_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(badge)

        # Badge colors
        if badge_type == 'galaxy_allstars':
            # Red theme
            bg_color = (200, 40, 40, 240)
            dark_color = (140, 20, 20, 255)
            light_color = (255, 80, 80, 255)
        elif badge_type == 'galaxy_nvidia':
            # Green theme
            bg_color = (40, 180, 60, 240)
            dark_color = (20, 120, 40, 255)
            light_color = (80, 220, 100, 255)
        else:  # gct
            # Gray theme
            bg_color = (100, 100, 100, 240)
            dark_color = (60, 60, 60, 255)
            light_color = (160, 160, 160, 255)

        # Draw Wii U GamePad style controller (no background circle)
        # Main gamepad body (rounded rectangle)
        pad_left = 2
        pad_top = 3
        pad_right = badge_width - 2
        pad_bottom = badge_height - 3

        # Draw rounded body
        draw.rounded_rectangle(
            [pad_left, pad_top, pad_right, pad_bottom],
            radius=4,
            fill=bg_color,
            outline=dark_color,
            width=2
        )

        # Left grip
        draw.polygon([
            (pad_left, pad_top + 4),
            (pad_left - 2, pad_top + 6),
            (pad_left, pad_bottom - 2)
        ], fill=dark_color)

        # Right grip
        draw.polygon([
            (pad_right, pad_top + 4),
            (pad_right + 2, pad_top + 6),
            (pad_right, pad_bottom - 2)
        ], fill=dark_color)

        # Screen area (center)
        screen_left = pad_left + 6
        screen_top = pad_top + 2
        screen_right = pad_right - 6
        screen_bottom = pad_bottom - 2
        draw.rectangle([screen_left, screen_top, screen_right, screen_bottom],
                      fill=(40, 40, 60, 220), outline=light_color, width=1)

        # D-pad (left side) - slightly smaller
        dpad_x = pad_left + 3
        dpad_y = pad_top + 6
        # Horizontal bar
        draw.rectangle([dpad_x - 1.5, dpad_y - 0.8, dpad_x + 1.5, dpad_y + 0.8], fill=light_color)
        # Vertical bar
        draw.rectangle([dpad_x - 0.8, dpad_y - 1.5, dpad_x + 0.8, dpad_y + 1.5], fill=light_color)

        # Action buttons (right side) - smaller ABXY style
        btn_x = pad_right - 3.5
        btn_y = pad_top + 6
        btn_r = 1.0  # Reduced from 1.5
        # Four buttons in diamond pattern
        draw.ellipse([btn_x - btn_r, btn_y - 2.5 - btn_r, btn_x + btn_r, btn_y - 2.5 + btn_r], fill=light_color)  # Top
        draw.ellipse([btn_x - btn_r, btn_y + 2.5 - btn_r, btn_x + btn_r, btn_y + 2.5 + btn_r], fill=light_color)  # Bottom
        draw.ellipse([btn_x - 2.5 - btn_r, btn_y - btn_r, btn_x - 2.5 + btn_r, btn_y + btn_r], fill=light_color)  # Left
        draw.ellipse([btn_x + 2.5 - btn_r, btn_y - btn_r, btn_x + 2.5 + btn_r, btn_y + btn_r], fill=light_color)  # Right

        # Analog sticks (two small circles) - slightly smaller
        stick_y = pad_bottom - 1.5
        stick_r = 1.2
        # Left stick
        draw.ellipse([pad_left + 8 - stick_r, stick_y - stick_r, pad_left + 8 + stick_r, stick_y + stick_r],
                    fill=dark_color, outline=light_color, width=1)
        # Right stick
        draw.ellipse([pad_right - 8 - stick_r, stick_y - stick_r, pad_right - 8 + stick_r, stick_y + stick_r],
                    fill=dark_color, outline=light_color, width=1)

        # Paste badge to bottom-right corner
        img_with_badge = img.copy()
        badge_x = img.width - badge_width - 2
        badge_y = img.height - badge_height - 2
        img_with_badge.paste(badge, (badge_x, badge_y), badge)

        return img_with_badge

    @staticmethod
    def process_icon(input_path: Path, output_path: Path, badge_type: str = None) -> bool:
        """
        Process icon image (128x128) with optional gamepad badge.

        Args:
            input_path: Input image
            output_path: Output PNG path
            badge_type: Optional badge type ('galaxy_allstars' or 'galaxy_nvidia')

        Returns:
            True if successful
        """
        try:
            with Image.open(input_path) as img:
                # Convert to RGBA if needed
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')

                # Resize with aspect ratio
                img.thumbnail(ImageProcessor.ICON_SIZE, Image.Resampling.LANCZOS)

                # Create new image with target size and paste centered
                new_img = Image.new('RGBA', ImageProcessor.ICON_SIZE, (0, 0, 0, 0))
                paste_x = (ImageProcessor.ICON_SIZE[0] - img.width) // 2
                paste_y = (ImageProcessor.ICON_SIZE[1] - img.height) // 2
                new_img.paste(img, (paste_x, paste_y))

                # Add gamepad badge if specified (bottom-right)
                if badge_type:
                    new_img = ImageProcessor.add_gamepad_badge(new_img, badge_type)

                # Save as PNG
                new_img.save(output_path, 'PNG')
                return True

        except Exception as e:
            print(f"Error processing icon: {e}")
            return False

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
