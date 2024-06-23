import pytesseract
import cv2
from PIL import Image
import numpy as np
import os
import csv
from fuzzywuzzy import process
import logging

# Tesseract location for MacOS when installed through brew
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

logging.basicConfig(filename='ocr_log.txt', level=logging.INFO)

def preprocess_image(image, roi):
    x, y, w, h = roi
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

def preprocess_for_names(roi_image):
    gray_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    resized_image = cv2.resize(gray_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized_image

def preprocess_for_characters(roi_image):
    gray_image = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray_image, (3, 3), 0)
    thresholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    inverted_image = cv2.bitwise_not(thresholded)
    resized_image = cv2.resize(inverted_image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized_image

def correct_character_name(ocr_result):
    valid_characters = ["Beef", "Pork", "Onion", "Garlic", "Rice", "Noodle"]
    corrected_name, score = process.extractOne(ocr_result, valid_characters)
    return corrected_name if score > 60 else "Unknown"

def extract_player_info(image_path):
    try:
        image = cv2.imread(image_path)
        extracted_info = {}

        roi_characters = {
            "player_1_character": (305, 110, 60, 19),
            "player_2_character": (1096, 109, 60, 22),
        }

        roi_names = {
            "player_1_name": (291, 657, 228, 34), 
            "player_2_name": (939, 658, 227, 32),
        }

        for key, roi in roi_names.items():
            preprocessed_roi = preprocess_image(image, roi)
            preprocessed_ocr = preprocess_for_names(preprocessed_roi)
            roi_image = Image.fromarray(preprocessed_ocr)
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890 "'
            text = pytesseract.image_to_string(roi_image, config=custom_config)
            extracted_info[key] = text.strip()

        for key, roi in roi_characters.items():
            preprocessed_roi = preprocess_image(image, roi)
            preprocessed_ocr = preprocess_for_characters(preprocessed_roi)
            roi_image = Image.fromarray(preprocessed_ocr)
            custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist="BeefPorkOnionGarlicRiceNoodle"'
            text = pytesseract.image_to_string(roi_image, config=custom_config)
            extracted_info[key] = correct_character_name(text.strip())

        return extracted_info

    except Exception as e:
        logging.error(f"Error processing {image_path}: {str(e)}")
        return None

def process_frames(frames_folder, output_csv):
    data = []

    for i in range(2000, 592000, 2000):  # Adjust range as needed
        frame_path = os.path.join(frames_folder, f"frame_{i}.jpg")
        if os.path.exists(frame_path):
            player_info = extract_player_info(frame_path)
            if player_info:
                data.append({
                    "frame": frame_path,
                    "player_1_name": player_info["player_1_name"],
                    "player_1_character": player_info["player_1_character"],
                    "player_2_name": player_info["player_2_name"],
                    "player_2_character": player_info["player_2_character"]
                })

    # Write to CSV
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = ["frame", "player_1_name", "player_1_character", "player_2_name", "player_2_character"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    # Path to the video
    video_path = 'output_video.mp4'
    frames_folder = 'frames_folder'

    process_frames(frames_folder, "output.csv")
