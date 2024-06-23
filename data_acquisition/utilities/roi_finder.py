
"""
Can be run to find what values would work for OCR ROIs

Change image_path to the frame you want to check
"""
import cv2

# Load the image
image_path = 'frames_folder/frame_51216.jpg'
image = cv2.imread(image_path)

# Function to draw rectangle
def draw_rectangle(event, x, y, flags, param):
    global x1, y1, drawing, roi
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x1, y1 = x, y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = image.copy()
            cv2.rectangle(img_copy, (x1, y1), (x, y), (0, 255, 0), 2)
            cv2.imshow('Select ROI', img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        roi = (x1, y1, x - x1, y - y1)
        img_copy = image.copy()
        cv2.rectangle(img_copy, (x1, y1), (x, y), (0, 255, 0), 2)
        cv2.imshow('Select ROI', img_copy)

# Initialize global variables
x1, y1 = 0, 0
drawing = False
roi = (0, 0, 0, 0)

# Create a window and set the mouse callback
cv2.namedWindow('Select ROI')
cv2.setMouseCallback('Select ROI', draw_rectangle)

# Display the image and wait for a key press
cv2.imshow('Select ROI', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Print the selected ROI coordinates
print("Selected ROI:", roi)

player_1_character = (287, 103, 128, 35)
player_2_character = (1157, 110, -111, 24)
player_1_name = (291, 657, 228, 34)
player_2_name = (939, 658, 227, 32)

x, y, w, h = 748, 192, 474, 210  # Adjusted values

#     # Define ROIs for characters
#     roi_characters = {
#         "player_1_character": (305, 110, 60, 19),
#         "player_2_character": (1096, 109, 60, 22),
#     }

