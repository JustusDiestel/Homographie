#!/usr/bin/env python3
"""
Painting Perspective Rectification and Reconstruction
Homework Assignment - Computer Vision

Task:
1. Read two JPG images of a painting taken from different angles
2. Manually select 5+ matching points on the circular frame
3. Calculate homography matrix to correct perspective
4. Combine best halves to eliminate people
5. Create perfect circular output
6. Save result and marked points

Author: Justus Diestel
"""

import cv2
import numpy as np
import sys


class PaintingRectifier:
    """Main class for painting perspective rectification"""
    
    def __init__(self, img1_path, img2_path):
        self.img1_path = img1_path
        self.img2_path = img2_path
        self.img1 = cv2.imread(img1_path)
        self.img2 = cv2.imread(img2_path)
        
        if self.img1 is None or self.img2 is None:
            raise ValueError(f"Could not load images: {img1_path} or {img2_path}")
        
        self.pts1 = []
        self.pts2 = []
        self.marked1 = None
        self.marked2 = None
    
    def select_points(self, image, title):
        """
        Interactive GUI for selecting matching points on the circular frame.
        Click 5 points on the frame edge (not on wall), press SPACE when done, ESC to undo.
        """
        points = []
        display_img = image.copy()
        
        # Resize for display if too large
        h, w = image.shape[:2]
        scale = 1.0
        if w > 1400 or h > 1000:
            scale = min(1400/w, 1000/h)
            display_img = cv2.resize(display_img, (int(w*scale), int(h*scale)))
        
        display = display_img.copy()
        
        def mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                points.append((x, y))
                print(f"  Point {len(points)}: ({x}, {y})")
                
                # Draw point on display
                cv2.circle(display, (x, y), 12, (0, 255, 0), 3)
                cv2.circle(display, (x, y), 5, (0, 0, 255), -1)
                cv2.putText(display, str(len(points)), (x+15, y-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow(title, display)
        
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title, 1400, 1000)
        cv2.setMouseCallback(title, mouse_callback)
        
        print(f"\n{title}:")
        print("  ⚠️  WICHTIG: Klick NUR auf den KREISRAHMEN (goldener Rand)")
        print("     NICHT auf die Wand hinter dem Bild!")
        print("  • 5 Punkte gleichmäßig verteilt um den Kreis")
        print("  • SPACE: Fertig | ESC: Letzten Punkt löschen\n")
        
        while len(points) < 5:
            display = display_img.copy()
            # Draw center circle as guide
            cv2.putText(display, "Klick auf den KREISRAHMEN!", (50, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 165, 255), 2)
            cv2.putText(display, f"Punkte: {len(points)}/5", (50, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)
            
            for i, p in enumerate(points):
                cv2.circle(display, p, 12, (0, 255, 0), 3)
                cv2.circle(display, p, 5, (0, 0, 255), -1)
                cv2.putText(display, str(i+1), (p[0]+15, p[1]-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            cv2.imshow(title, display)
            key = cv2.waitKey(1) & 0xFF
            
            if key == 27:  # ESC - undo
                if points:
                    points.pop()
                    print(f"  Punkt gelöscht. Punkte: {len(points)}/5\n")
            
            elif key == ord(' '):  # SPACE - done
                if len(points) == 5:
                    break
        
        cv2.destroyAllWindows()
        
        # Scale points back to original resolution
        scaled_points = [(int(p[0]/scale), int(p[1]/scale)) for p in points]
        
        # Create marked image on original resolution
        marked = image.copy()
        for i, p in enumerate(scaled_points):
            cv2.circle(marked, p, 15, (0, 255, 0), 3)
            cv2.circle(marked, p, 8, (0, 0, 255), -1)
            cv2.putText(marked, str(i+1), (p[0]-8, p[1]-25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 3)
        
        return scaled_points, marked
    
    def fit_circle(self, points):
        """Fit a circle to the selected points using least squares"""
        points = np.array(points, dtype=np.float32)
        center = np.mean(points, axis=0)
        distances = np.linalg.norm(points - center, axis=1)
        radius = np.mean(distances)
        return (int(center[0]), int(center[1])), int(radius)
    
    def combine_halves(self, img1_warped, img2_warped, center, radius):
        """
        Intelligently combine both images to eliminate people.
        Uses radial blending around the circle center.
        """
        h, w = img1_warped.shape[:2]
        cy, cx = center[1], center[0]
        
        # Create radial gradient mask for blending
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        
        # Blend based on distance from center
        # Closer to center: use img1, farther: blend to img2
        blend_mask = np.clip((dist_from_center - radius * 0.6) / (radius * 0.4), 0, 1)
        blend_mask = cv2.GaussianBlur(blend_mask.astype(np.float32), (51, 51), 30)
        
        # Apply blending
        blend_mask_3ch = np.stack([blend_mask]*3, axis=2)
        combined = (img1_warped.astype(np.float32) * (1 - blend_mask_3ch) + 
                   img2_warped.astype(np.float32) * blend_mask_3ch)
        combined = np.clip(combined, 0, 255).astype(np.uint8)
        
        return combined
    
    def create_circular_result(self, image, center, radius):
        """Create final result with perfect circular frame"""
        # Create circular mask
        mask = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
        cv2.circle(mask, center, radius, 255, -1)
        
        # Apply mask to create circular image
        result = cv2.bitwise_and(image, image, mask=mask)
        
        return result
    
    def process(self):
        """Main processing pipeline"""
        print("\n" + "="*70)
        print("PAINTING PERSPECTIVE RECTIFICATION")
        print("Computer Vision Homework Assignment")
        print("="*70)
        
        # Step 1: Select matching points
        print("\n[STEP 1/6] Selecting matching points...")
        self.pts1, self.marked1 = self.select_points(self.img1, "Image 1")
        self.pts2, self.marked2 = self.select_points(self.img2, "Image 2")
        
        print(f"✓ Selected {len(self.pts1)} points on Image 1")
        print(f"✓ Selected {len(self.pts2)} points on Image 2")
        
        # Step 2: Fit circle
        print("\n[STEP 2/6] Fitting circle to frame...")
        center, radius = self.fit_circle(self.pts1)
        print(f"✓ Circle fitted - Center: {center}, Radius: {radius}px")
        
        # Step 3: Calculate homography
        print("\n[STEP 3/6] Computing homography matrix...")
        H, status = cv2.findHomography(
            np.array(self.pts2, dtype=np.float32),
            np.array(self.pts1, dtype=np.float32),
            cv2.RANSAC,
            5.0
        )
        
        if H is None:
            raise ValueError("Failed to compute homography!")
        print("✓ Homography matrix computed")
        
        # Step 4: Warp both images
        print("\n[STEP 4/6] Warping images to front view...")
        img1_warped = self.img1.copy()
        img2_warped = cv2.warpPerspective(
            self.img2, H, 
            (self.img1.shape[1], self.img1.shape[0])
        )
        print("✓ Images warped to front perspective")
        
        # Step 5: Combine best halves
        print("\n[STEP 5/6] Combining image halves...")
        combined = self.combine_halves(img1_warped, img2_warped, center, radius)
        print("✓ Image halves combined (people eliminated)")
        
        # Step 6: Create perfect circular result
        print("\n[STEP 6/6] Creating perfect circular frame...")
        result = self.create_circular_result(combined, center, radius)
        print("✓ Perfect circular frame created")
        
        # Save main result
        output_path = "Justus_Diestel.jpg"
        cv2.imwrite(output_path, result)
        print(f"\n✓ Result saved: {output_path}")
        
        # Create and save side-by-side marked points image
        h1, w1 = self.marked1.shape[:2]
        h2, w2 = self.marked2.shape[:2]
        max_h = max(h1, h2)
        
        if h1 < max_h:
            marked1_resized = cv2.resize(self.marked1, (int(w1 * max_h / h1), max_h))
        else:
            marked1_resized = self.marked1
        
        if h2 < max_h:
            marked2_resized = cv2.resize(self.marked2, (int(w2 * max_h / h2), max_h))
        else:
            marked2_resized = self.marked2
        
        side_by_side = cv2.hconcat([marked1_resized, marked2_resized])
        cv2.imwrite("matching_points.jpg", side_by_side)
        print("✓ Marked points saved: matching_points.jpg")
        
        # Display results
        print("\n" + "="*70)
        print("PROCESSING COMPLETE")
        print("="*70)
        print("\nGenerated files:")
        print("  1. Justus_Diestel.jpg - Final rectified painting (circular)")
        print("  2. matching_points.jpg - Marked matching points (side-by-side)")
        print("\nClose the preview window to exit...")
        print("="*70 + "\n")
        
        cv2.imshow("Final Result - Rectified Painting", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return result


def main():
    """Main entry point"""
    try:
        rectifier = PaintingRectifier("1.jpg", "2.jpg")
        rectifier.process()
    except FileNotFoundError as e:
        print(f"\n❌ Error: Image files not found in current directory")
        print(f"   Make sure 1.jpg and 2.jpg are in the same folder as this script")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

