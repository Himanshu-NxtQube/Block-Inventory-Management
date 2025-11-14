import cv2
import io
from google.cloud import vision
import os

# Set up credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./models/GoogleVisionCredential.json"

# Initialize client
client = vision.ImageAnnotatorClient()

# Load image
image_path = "./testing images/debug/DJI_0336.JPG"
with io.open(image_path, 'rb') as image_file:
    content = image_file.read()

image = vision.Image(content=content)

# Perform OCR
response = client.document_text_detection(image=image)  # better than text_detection for structured OCR

# Load image using OpenCV
img = cv2.imread(image_path)

# Loop through blocks/paragraphs/words to get confidence
for page in response.full_text_annotation.pages:
    for block in page.blocks:
        for paragraph in block.paragraphs:
            for word in paragraph.words:
                word_text = "".join([symbol.text for symbol in word.symbols])
                confidence = word.confidence

                # Get bounding box
                vertices = [(v.x, v.y) for v in word.bounding_box.vertices]
                pts = vertices + [vertices[0]]
                for j in range(len(pts) - 1):
                    cv2.line(img, pts[j], pts[j + 1], (255, 0, 0), 2)

                # Put text with confidence
                x, y = vertices[0]
                
                print(f"{word_text} - {confidence:.2f}")
                cv2.putText(
                    img,
                    f"{word_text}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1
                )

# Optional reference line
cv2.line(img, (0, 2570), (500, 2570), (0, 0, 255), 5)

# Save output
cv2.imwrite("annotations.png", img)
