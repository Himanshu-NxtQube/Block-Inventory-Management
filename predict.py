from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Load model
model = YOLO("models/block_sticker.pt")

# Read image
image_path = "testing images/debug/DJI_0057.JPG"
image = cv2.imread(image_path)

# Run inference
results = model(image)

# Draw predictions using built-in plot() method
for r in results:
    plotted_img = r.plot()  # returns image with boxes, labels, etc.

# Convert from BGR (OpenCV) to RGB (matplotlib)
plotted_img = cv2.cvtColor(plotted_img, cv2.COLOR_BGR2RGB)

# Show the image
plt.imshow(plotted_img)
plt.axis("off")
plt.show()
