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
# 5. Fit circle from points (BEST SOLUTION)
# -----------------------------

# Punkte extrahieren
x = pts_img2[:, 0]
y = pts_img2[:, 1]

# Kreis-Fit (Least Squares)
A = np.c_[2*x, 2*y, np.ones(len(x))]
b = x**2 + y**2

c, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)

cx, cy, c0 = c
center = (int(cx), int(cy))
radius = int(np.sqrt(c0 + cx**2 + cy**2))

print(f"Circle from points: center={center}, radius={radius}")

# Maske
circle_mask = np.zeros((h, w), dtype=np.uint8)
cv2.circle(circle_mask, center, radius, 255, -1)

# Debug
debug = img2.copy()
cv2.circle(debug, center, radius, (0,255,0), 2)
show(debug, "Fitted Circle")
# -----------------------------
# 5.5 Apply circle mask to both images (FIX)
# -----------------------------
masked_img2 = cv2.bitwise_and(img2, img2, mask=circle_mask)
masked_warped = cv2.bitwise_and(warped, warped, mask=circle_mask)

show(masked_img2, "Masked Image 2")
show(masked_warped, "Masked Warped Image")

# -----------------------------
# 6. Combine (vectorized version)
# -----------------------------
combined = masked_img2.copy()

offset = 20
x_split = center[0] + offset

# Maske für rechte Seite
right_mask = np.zeros_like(circle_mask)
right_mask[:, x_split:] = 255

# Nur innerhalb Kreis UND rechts ersetzen
mask_final = cv2.bitwise_and(circle_mask, right_mask)

combined[mask_final == 255] = masked_warped[mask_final == 255]

show(combined, "Combined Halves (vectorized)")

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
