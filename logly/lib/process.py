import cv2 

class processor: 
    
    def __init__(self):
        pass
    
    def process(self, image_path):
        # Read the image
        image = cv2.imread(image_path)

        # Convert to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur (optional)
        # blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

        # Apply simple binary thresholding (optional)
        _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)


        return binary_image