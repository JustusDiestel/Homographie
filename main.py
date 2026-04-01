import cv2
import numpy as np
from pointer import get_points


def fit_circle(points):
    """Fit a circle to points using least squares"""
    points = np.array(points, dtype=np.float32)
    center = np.mean(points, axis=0)
    distances = np.linalg.norm(points - center, axis=1)
    radius = np.mean(distances)
    return tuple(center.astype(int)), int(radius)


def main():
    # Get matching points from user
    pts_img1 = get_points("1.jpg", "Bild 1")
    pts_img2 = get_points("2.jpg", "Bild 2")
    
    if len(pts_img1) < 4 or len(pts_img2) < 4:
        print("Fehler: Mindestens 4 Punkte notwendig!")
        return
    
    print(f"\n✓ Bild 1 Punkte: {pts_img1}")
    print(f"✓ Bild 2 Punkte: {pts_img2}\n")
    
    # Load images
    img1 = cv2.imread("1.jpg")
    img2 = cv2.imread("2.jpg")
    
    if img1 is None or img2 is None:
        print("Fehler: Bilder konnten nicht geladen werden!")
        return
    
    # Fit circle to points in img1
    center, radius = fit_circle(pts_img1)
    print(f"Kreis: Center {center}, Radius {radius}\n")
    
    # Compute homography from img2 to img1
    H, status = cv2.findHomography(np.array(pts_img2, dtype=np.float32), 
                                    np.array(pts_img1, dtype=np.float32), 
                                    cv2.RANSAC, 5.0)
    
    if H is None:
        print("Fehler: Homography konnte nicht berechnet werden!")
        return
    
    print("✓ Homography Matrix berechnet")
    
    # Warp img2 to img1's perspective
    warped = cv2.warpPerspective(img2, H, (img1.shape[1], img1.shape[0]))
    
    print("✓ Bild transformiert")
    
    # Save the full transformed image (no masking, just the clean warped result)
    result = warped
    cv2.imwrite("Justus_Diestel.jpg", result)
    print("✓ Resultat gespeichert: Justus_Diestel.jpg\n")
    
    # Create side-by-side image with markers
    img1_pts = cv2.imread("Bild 1_pts.png")
    img2_pts = cv2.imread("Bild 2_pts.png")
    if img1_pts is not None and img2_pts is not None:
        # Resize to same height for better side-by-side view
        h1, w1 = img1_pts.shape[:2]
        h2, w2 = img2_pts.shape[:2]
        max_h = max(h1, h2)
        
        if h1 != max_h:
            img1_pts = cv2.resize(img1_pts, (int(w1 * max_h / h1), max_h))
        if h2 != max_h:
            img2_pts = cv2.resize(img2_pts, (int(w2 * max_h / h2), max_h))
        
        combined = cv2.hconcat([img1_pts, img2_pts])
        cv2.imwrite("matching_points.jpg", combined)
        print("✓ Markierungspunkte gespeichert: matching_points.jpg\n")
    
    # Display results
    cv2.imshow("Transformiertes Bild", result)
    print("Drücke eine Taste zum Beenden...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()