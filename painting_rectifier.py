#!/usr/bin/env python3
"""
Painting Perspective Rectification and Cleaning
- Find matching points on circular painting frames
- Calculate homography to correct perspective
- Remove people and create clean circular image
"""

import cv2
import numpy as np
from pathlib import Path


class PaintingRectifier:
    def __init__(self, img1_path, img2_path):
        self.img1_path = img1_path
        self.img2_path = img2_path
        self.img1 = cv2.imread(img1_path)
        self.img2 = cv2.imread(img2_path)
        
        if self.img1 is None or self.img2 is None:
            raise ValueError("Could not load images")
        
        self.pts1 = []
        self.pts2 = []
        
    def select_points(self, image, title):
        """Interactive point selection on image"""
        points = []
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                print(f"{title} - Point {len(points)}: ({x}, {y})")
                
                # Draw point
                cv2.circle(display, (x, y), 8, (0, 0, 255), -1)
                cv2.circle(display, (x, y), 8, (255, 255, 255), 2)
                cv2.putText(display, str(len(points)), (x - 5, y - 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.imshow(title, display)
        
        # Resize for display if too large
        h, w = image.shape[:2]
        scale = 1.0
        if w > 1400 or h > 1000:
            scale = min(1400/w, 1000/h)
            display_img = cv2.resize(image, (int(w*scale), int(h*scale)))
        else:
            display_img = image.copy()
            scale = 1.0
        
        display = display_img.copy()
        
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title, 1400, 1000)
        cv2.setMouseCallback(title, mouse_callback)
        
        print(f"\n{title}: Click on 5 points around the circular frame")
        print("Press SPACE when done, ESC to clear last point\n")
        
        while len(points) < 5:
            cv2.imshow(title, display)
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC - remove last point
                if points:
                    points.pop()
                    display = display_img.copy()
                    for i, p in enumerate(points):
                        cv2.circle(display, p, 8, (0, 0, 255), -1)
                        cv2.circle(display, p, 8, (255, 255, 255), 2)
                        cv2.putText(display, str(i+1), (p[0]-5, p[1]-15),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    print(f"Removed last point. Points: {len(points)}/5")
            
            elif key == ord(' '):  # SPACE - done
                if len(points) >= 5:
                    break
        
        cv2.destroyAllWindows()
        
        # Scale points back to original image size
        scaled_points = [(int(p[0]/scale), int(p[1]/scale)) for p in points]
        
        # Save marked image
        marked = image.copy()
        for i, p in enumerate(scaled_points):
            cv2.circle(marked, p, 12, (0, 0, 255), -1)
            cv2.circle(marked, p, 12, (255, 255, 255), 2)
            cv2.putText(marked, str(i+1), (p[0]-8, p[1]-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)
        
        return scaled_points, marked
    
    def fit_circle(self, points):
        """Fit a circle to the points"""
        points = np.array(points, dtype=np.float32)
        center = np.mean(points, axis=0)
        distances = np.linalg.norm(points - center, axis=1)
        radius = np.mean(distances)
        # Convert to int tuple to avoid numpy.int64 issues
        return (int(center[0]), int(center[1])), int(radius)
    
    def create_mask_outside_circle(self, shape, center, radius):
        """Create mask for areas outside circle (people)"""
        mask = np.zeros(shape[:2], dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, -1)
        # Return inverse - True where people are (outside circle)
        return 255 - mask
    
    def remove_people(self, image, people_mask, center, radius):
        """Remove people using inpainting"""
        # Dilate to extend removal area smoothly
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        people_mask_dilated = cv2.dilate(people_mask, kernel, iterations=3)
        
        # Ensure it's uint8
        inpaint_mask = people_mask_dilated.astype(np.uint8)
        inpaint_mask = np.where(inpaint_mask > 128, 255, 0).astype(np.uint8)
        
        # Inpaint the image
        result = cv2.inpaint(image, inpaint_mask, 7, cv2.INPAINT_TELEA)
        
        return result
    
    def process(self):
        """Main processing pipeline"""
        print("\n" + "="*60)
        print("PAINTING RECTIFICATION TOOL")
        print("="*60)
        
        # Step 1: Select points
        print("\nSTEP 1: Selecting matching points...")
        self.pts1, marked1 = self.select_points(self.img1, "Image 1")
        self.pts2, marked2 = self.select_points(self.img2, "Image 2")
        
        # Save marked images
        cv2.imwrite("Bild_1_marked.png", marked1)
        cv2.imwrite("Bild_2_marked.png", marked2)
        
        # Create side-by-side marked image
        h1, w1 = marked1.shape[:2]
        h2, w2 = marked2.shape[:2]
        max_h = max(h1, h2)
        
        if h1 < max_h:
            marked1 = cv2.resize(marked1, (int(w1 * max_h / h1), max_h))
        if h2 < max_h:
            marked2 = cv2.resize(marked2, (int(w2 * max_h / h2), max_h))
        
        side_by_side = cv2.hconcat([marked1, marked2])
        cv2.imwrite("matching_points.jpg", side_by_side)
        print(f"✓ Matched points saved: matching_points.jpg")
        
        # Step 2: Fit circle
        print("\nSTEP 2: Fitting circle...")
        center, radius = self.fit_circle(self.pts1)
        print(f"✓ Circle detected - Center: {center}, Radius: {radius}")
        
        # Step 3: Calculate homography
        print("\nSTEP 3: Calculating homography...")
        H, mask = cv2.findHomography(
            np.array(self.pts2, dtype=np.float32),
            np.array(self.pts1, dtype=np.float32),
            cv2.RANSAC,
            5.0
        )
        
        if H is None:
            raise ValueError("Could not compute homography")
        print("✓ Homography matrix computed")
        
        # Step 4: Warp image
        print("\nSTEP 4: Warping image to front view...")
        warped = cv2.warpPerspective(self.img2, H, 
                                     (self.img1.shape[1], self.img1.shape[0]))
        print("✓ Image warped")
        
        # Step 5: Remove people
        print("\nSTEP 5: Removing people...")
        people_mask = self.create_mask_outside_circle(warped, center, radius)
        warped_clean = self.remove_people(warped, people_mask, center, radius)
        print("✓ People removed")
        
        # Step 6: Create perfect circle
        print("\nSTEP 6: Creating perfect circular frame...")
        # Create circular mask
        circle_mask = np.zeros((warped.shape[0], warped.shape[1]), dtype=np.uint8)
        cv2.circle(circle_mask, center, radius, 255, -1)
        
        # Keep only circle area from cleaned image
        result_full = cv2.bitwise_and(warped_clean, warped_clean, mask=circle_mask)
        
        print("✓ Perfect circular frame created")
        
        # Step 7: Save result
        print("\nSTEP 7: Saving result...")
        output_path = "Justus_Diestel.jpg"
        cv2.imwrite(output_path, result_full)
        print(f"✓ Result saved: {output_path}")
        
        # Display results
        print("\nDone! Press any key to close windows...")
        
        cv2.imshow("Final Result", result_full)
        cv2.imshow("Marked Points (Side by Side)", side_by_side)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        print("\n" + "="*60)
        print("FILES CREATED:")
        print("  - Justus_Diestel.jpg (main result)")
        print("  - matching_points.jpg (marked points)")
        print("="*60 + "\n")


if __name__ == "__main__":
    try:
        rectifier = PaintingRectifier("1.jpg", "2.jpg")
        rectifier.process()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

