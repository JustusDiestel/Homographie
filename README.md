Homework: 2 Justus Diestel 

1. Choice of Points:
- I chose points on the distorted circle because they have geometric value

2. How to run the program:
- Activate the virtual environment: source .venv/bin/activate
- Run the script: python homework2.py
- Select 5 points on the distorted circle in image 1 by clicking.
- Select 5 corresponding points on the distorted circle in image 2.
- The program will compute homographies, warp the images to a front view with a perfect circle, combine them to eliminate people (by averaging), and save the result as Justus_Diestel.jpg
- Also saves marked_points.jpg with the selected points marked side-by-side.

3. Libraries used:
- OpenCV for image processing and homography calculation.
- NumPy for array operations.

4. Approach:
- Manually select at least 5 matching points on the circles in both images.
- Compute homography to map to a perfect circle.
- Warp both images to the front view.
- Combine by averaging to clean the painting.
- Mask to perfect circle.
