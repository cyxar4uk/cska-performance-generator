#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test generation"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from services.image_library import ImageLibrary
    from utils.seats_loader import SeatsLoader
    from utils.image_mapper import ImageMapper

    print("[OK] Imports successful")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    seats_loader = SeatsLoader()
    seats_path = seats_loader.seats_file

    print(f"[OK] Seats path: {seats_path}")
    print(f"[OK] File exists: {os.path.exists(seats_path)}")

    seats_loader.load()
    print(f"[OK] Loaded seats: {len(seats_loader.all_seats)}")

    image_library = ImageLibrary()
    print(f"[OK] Images in library: {len(image_library.list_images())}")

    image = image_library.get_image('cska_logo')
    print(f"[OK] Image loaded: {image.size}")

    seats = seats_loader.all_seats
    arena_width, arena_height = seats_loader.get_arena_dimensions()
    print(f"[OK] Arena dimensions: {arena_width}x{arena_height}")

    mapper = ImageMapper(seats, arena_width, arena_height)
    seat_colors = mapper.map_image_to_seats(image, 0.8)
    print(f"[OK] Mapping done: {len(seat_colors)} seats")

    print("\n[SUCCESS] ALL TESTS PASSED!")

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
