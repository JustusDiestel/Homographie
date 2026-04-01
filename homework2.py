# =========================================
# Homework #2 - Homography Circular Painting
# =========================================

import cv2
import numpy as np
import matplotlib.pyplot as plt
import json


# -----------------------------
# Helper functions
# -----------------------------
def show(img, title="Image"):
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis('off')
    plt.show()


# -----------------------------
# 1. Load Images
# -----------------------------
img1 = cv2.imread("1.jpg")
img2 = cv2.imread("2.jpg")

show(img1, "Image 1")
show(img2, "Image 2")


# -----------------------------
# 2. Load matching points from JSON
# -----------------------------
with open("matches.json", "r") as f:
    data = json.load(f)

pts_img1 = np.float32(data["points_img1"])
pts_img2 = np.float32(data["points_img2"])


# -----------------------------
# 3. Compute Homography from img1 to img2 (since img2 is frontal)
# -----------------------------
H, status = cv2.findHomography(pts_img1, pts_img2)
print("Homography Matrix:\n", H)


# -----------------------------
# 4. Warp img1 into img2 plane
# -----------------------------
h, w = img2.shape[:2]
warped = cv2.warpPerspective(img1, H, (w, h))

show(warped, "Warped Image")


# -----------------------------
# 5. Mask both images to the circle
# -----------------------------
center = (w // 2, h // 2)
radius = min(center[0], center[1])

circle_mask = np.zeros((h, w), dtype=np.uint8)
cv2.circle(circle_mask, center, radius, 255, -1)

masked_img2 = cv2.bitwise_and(img2, img2, mask=circle_mask)
masked_warped = cv2.bitwise_and(warped, warped, mask=circle_mask)

show(masked_img2, "Masked Image 2")
show(masked_warped, "Masked Warped Image 1")


# -----------------------------
# 6. Combine the two halves to eliminate people
# -----------------------------
# Split a bit to the right of the half (adjust offset as needed)
offset = 50
x_split = w // 2 + offset

combined = masked_img2.copy()
combined[:, x_split:] = masked_warped[:, x_split:]

show(combined, "Combined Halves")

final = combined


# -----------------------------
# 7. Save output
# -----------------------------
cv2.imwrite("Justus_Diestel.jpg", final)
print("Saved as Justus_Diestel.jpg")


# -----------------------------
# 8. Create image with markers
# -----------------------------
# Mark points on img1
img1_marked = img1.copy()
for pt in pts_img1:
    cv2.circle(img1_marked, tuple(pt.astype(int)), 5, (0, 255, 0), -1)

# Mark points on img2
img2_marked = img2.copy()
for pt in pts_img2:
    cv2.circle(img2_marked, tuple(pt.astype(int)), 5, (0, 255, 0), -1)

# Side-by-side
marked_combined = np.concatenate((img1_marked, img2_marked), axis=1)
cv2.imwrite("marked_points.jpg", marked_combined)
print("Saved marked_points.jpg")
