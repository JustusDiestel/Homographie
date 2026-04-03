# Homework #2 – Homography of a Circular Painting

## Overview

This project reconstructs a **front view of a circular painting** using homography.
Two input images are used, where one image is warped into the perspective of the other.
Occlusions (people) are removed by combining complementary regions from both images.
Finally, the result is mapped into a **perfect circular domain**.

---

## Methodology

## Results Visualization

The following figure shows intermediate and final outputs of the pipeline:

![Result Visualization](OutputImagesOk/plot_2026-04-03 18-05-55_6.png)

The visualization includes:
- the original images
- the warped (aligned) image
- the merged result after occlusion removal
- the final circular extraction

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

#### Challenges in Circle Estimation

Estimating the circle from manually selected points introduces several sources of error:

- **Imperfect point selection**: Even small inaccuracies in clicking points lead to deviations in the fitted circle.
- **Perspective distortion**: The circle appears as an ellipse in one image, so selected points are not perfectly circular in image space.
- **Numerical approximation**: Least-squares fitting minimizes overall error but does not guarantee a perfect geometric circle.

These factors cause slight discrepancies between the estimated circle and the true boundary of the painting.

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

#### Implementation Details

The occlusion (person) is removed by combining complementary regions from both images:

- One image serves as the base (reference view)
- The warped image provides missing regions where the person is present
- A region split is defined relative to the circle center

This approach avoids blending artifacts and produces a clean reconstruction without ghosting.

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

## Discussion

The main difficulty in this task lies in the interplay between homography accuracy and geometric consistency:

- If corresponding points are not selected in the correct order or position, the homography becomes unstable.
- Small errors in homography propagate into misalignment, which affects both occlusion removal and circle fitting.
- The circle fitting step is particularly sensitive, as it assumes that selected points lie on a perfect circle, which is not strictly true under perspective distortion.

As a result, minor discrepancies between the reconstructed image and the ideal ground truth are expected. However, the overall structure and geometry remain correct.

---

## Prozess in Pictures 

![Result Visualization](OutputImagesOk/plot_2026-04-03 18-05-55_1.png)
![Result Visualization](OutputImagesOk/plot_2026-04-03 18-05-55_2.png)
![Result Visualization](OutputImagesOk/plot_2026-04-03 18-05-55_3.png)
![Result Visualization](OutputImagesOk/plot_2026-04-03 18-05-55_4.png)
![Result Visualization](OutputImagesOk/plot_2026-04-03 18-05-55_5.png)
![Result Visualization](OutputImagesOk/plot_2026-04-03 18-05-55_6.png)