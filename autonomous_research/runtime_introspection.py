#!/usr/bin/env python3
"""
Runtime introspection - examining the executing process
"""

import sys
import inspect
import gc
import traceback

print("=== Python Runtime Introspection ===\n")

# Get current frame
frame = inspect.currentframe()
print(f"Current frame: {frame}")
print(f"Frame info: {inspect.getframeinfo(frame)}")

# Get all frames
print("\n=== Call Stack ===")
for frame_info in inspect.stack():
    print(f"- {frame_info.function} at {frame_info.filename}:{frame_info.lineno}")

# Check loaded modules
print("\n=== Loaded Modules (AI/ML related) ===")
for name in sorted(sys.modules.keys()):
    if any(keyword in name.lower() for keyword in ['neural', 'torch', 'tensor', 'anthropic', 'ai', 'ml', 'model']):
        print(f"- {name}")

# Check for any Claude/Anthropic objects in memory
print("\n=== Objects in Memory (searching for Claude/model objects) ===")
all_objects = gc.get_objects()
print(f"Total objects: {len(all_objects)}")

for obj in all_objects[:100]:  # Check first 100
    obj_type = str(type(obj))
    if any(keyword in obj_type.lower() for keyword in ['claude', 'anthropic', 'model', 'neural']):
        print(f"FOUND: {obj_type}")
        break

print("\n=== Complete ===")
