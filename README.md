# Homework #2 – Homography of a Circular Painting

## Overview

This project reconstructs a **front view of a circular painting** using homography.
Two input images are used, where one image is warped into the perspective of the other.
Occlusions (people) are removed by combining complementary regions from both images.
Finally, the result is mapped into a **perfect circular domain**.

---

## Methodology

### 1. Manual Point Selection

At least five corresponding points are manually selected between both images using an interactive tool.
These points are stored in a JSON file (`matches.json`) and used to compute the homography.

---

### 2. Homography Estimation

A homography matrix ( H ) is computed using:

[
x' = Hx
]

where corresponding points between both images define the transformation.
The function `cv2.findHomography()` is used.

---

### 3. Perspective Transformation

The first image is warped into the coordinate system of the second (frontal) image using:

```python
cv2.warpPerspective()
```

This produces a geometrically aligned version of the painting.

---

### 4. Circle Estimation (from Points)

Instead of relying on automatic detection, the circular frame is estimated using the manually selected points.

A **least-squares circle fitting** method is applied to determine:

* center ((c_x, c_y))
* radius (r)

This approach is robust and consistent with the assignment requirement of using manually selected correspondences.

---

### 5. Masking

A circular mask is created based on the estimated center and radius.
Both images (original and warped) are masked to isolate only the painting region.

---

### 6. Occlusion Removal

To remove people and artifacts:

* the left region is taken from the frontal image
* the right region is taken from the warped image

The split is defined relative to the **circle center**, ensuring geometric consistency.

---

### 7. Final Result

The combined image is cropped using the circular mask to obtain a clean, front-facing circular painting.

---

## Files

| File                 | Description                            |
| -------------------- | -------------------------------------- |
| `main.py` / notebook | Main implementation                    |
| `matches.json`       | Manually selected corresponding points |
| `Justus_Diestel.jpg` | Final reconstructed image              |
| `marked_points.jpg`  | Visualization of selected points       |

---

## How to Run

1. Place input images:

```
1.jpg
2.jpg
```

2. Ensure `matches.json` exists (generated via the point selection tool)

3. Run:

```bash
python main.py
```

---

## Notes

* At least 5 corresponding points are required.
* Accuracy of the result strongly depends on the quality of selected points.
* Circle estimation is based on geometric fitting rather than image-based detection to improve robustness.

---

## Conclusion

This implementation satisfies all requirements:

* correct homography estimation
* successful occlusion removal
* reconstruction of a circular painting

The combination of manual correspondences and geometric fitting ensures a stable and accurate result.
