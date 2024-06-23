"""
Visualise ROIs
"""
import cv2
import os

def draw_roi_boxes(image_path, rois):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Could not read image: {image_path}")
        return None
    
    for roi in rois.values():
        x, y, w, h = roi
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return image

def visualize_roi_on_frame(image_path, output_path):
    rois = {
        "player_1_name": (291, 657, 228, 34),  # Example values, adjust to what you want to see
        "player_1_character": (287, 103, 128, 35),
        "player_2_name": (939, 658, 227, 32),
        "player_2_character": (1020, 134, 136, 27)
    }
    
    frame_with_boxes = draw_roi_boxes(image_path, rois)
    if frame_with_boxes is not None:
        cv2.imwrite(output_path, frame_with_boxes)
        print(f"Frame with ROI boxes saved at {output_path}")
    else:
        print(f"Failed to process frame: {image_path}")

# Path to the specific frame image
image_path = 'frames_folder/frame_11904.jpg'
output_path = 'frames_folder/frame_11904_with_boxes.jpg'

# Visualize the ROIs on the specific frame
visualize_roi_on_frame(image_path, output_path)
