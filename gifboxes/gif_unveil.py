#!/usr/bin/env python3
"""
GIF Unveil - Creates a 10-frame GIF that progressively unveils an image.

Given a PNG or JPG image and a permutation of numbers 1-9, this program creates
a GIF that starts with a fully grey frame and reveals one ninth of the image
(in a 3x3 grid) per frame according to the given permutation.
"""

import argparse
import sys
from pathlib import Path
from PIL import Image, ImageDraw


def validate_permutation(perm_str: str) -> list[int]:
    """Validate and parse the permutation string."""
    try:
        perm = [int(x) for x in perm_str.split(',') if x.strip()]
        if len(perm) != 9:
            raise ValueError("Permutation must contain exactly 9 numbers")
        if set(perm) != set(range(1, 10)):
            raise ValueError("Permutation must contain numbers 1-9 exactly once each")
        return perm
    except ValueError as e:
        print(f"Error parsing permutation: {e}")
        sys.exit(1)


def get_grid_coordinates(width: int, height: int) -> list[tuple[int, int, int, int]]:
    """Get the bounding box coordinates for each cell in a 3x3 grid."""
    cell_width = width // 3
    cell_height = height // 3
    
    coordinates = []
    for row in range(3):
        for col in range(3):
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width if col < 2 else width
            y2 = y1 + cell_height if row < 2 else height
            coordinates.append((x1, y1, x2, y2))
    
    return coordinates


def create_gray_frame(width: int, height: int) -> Image.Image:
    """Create a fully gray frame."""
    return Image.new('RGB', (width, height), color=(128, 128, 128))


def create_unveil_gif(image_path: str, permutation: list[int], output_path: str):
    """Create the unveiling GIF animation."""
    try:
        original_img = Image.open(image_path)
        if original_img.mode != 'RGB':
            original_img = original_img.convert('RGB')
        
        width, height = original_img.size
        grid_coords = get_grid_coordinates(width, height)
        
        frames = []
        
        # Frame 0: Fully gray
        frames.append(create_gray_frame(width, height))
        
        # Frames 1-9: Progressive unveiling
        for frame_num in range(1, 10):
            frame = create_gray_frame(width, height)
            
            # Reveal cells according to permutation up to current frame
            for i in range(frame_num):
                cell_index = permutation[i] - 1  # Convert to 0-based index
                x1, y1, x2, y2 = grid_coords[cell_index]
                
                # Copy the region from original image to current frame
                region = original_img.crop((x1, y1, x2, y2))
                frame.paste(region, (x1, y1))
            
            frames.append(frame)
        
        # Save as GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=500,  # 500ms per frame
            loop=0
        )
        
        print(f"GIF created successfully: {output_path}")
        
    except Exception as e:
        print(f"Error creating GIF: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Create a progressive unveiling GIF from an image')
    parser.add_argument('image', help='Path to input PNG or JPG image')
    parser.add_argument('permutation', help='Comma-separated permutation of numbers 1-9 (e.g., "1,2,3,4,5,6,7,8,9")')
    parser.add_argument('-o', '--output', help='Output GIF path (default: output.gif)', default='output.gif')
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.image).exists():
        print(f"Error: Image file '{args.image}' not found")
        sys.exit(1)
    
    # Validate and parse permutation
    permutation = validate_permutation(args.permutation)
    
    # Create the GIF
    create_unveil_gif(args.image, permutation, args.output)


if __name__ == '__main__':
    main()