import cv2
import numpy as np
import json

# =========================================
# SETTINGS
# =========================================
IMG1_PATH = "1.jpg"
IMG2_PATH = "2.jpg"
OUTPUT_FILE = "matches.json"

# =========================================
# LOAD IMAGES
# =========================================
img1 = cv2.imread(IMG1_PATH)
img2 = cv2.imread(IMG2_PATH)

h1, w1 = img1.shape[:2]
h2, w2 = img2.shape[:2]

# gleiche Höhe
scale = h1 / h2
img2 = cv2.resize(img2, (int(w2 * scale), h1))

combined = np.hstack((img1, img2))

# =========================================
# STATE
# =========================================
points_img1 = []
points_img2 = []
temp_point = None

# =========================================
# DRAW FUNCTION (WICHTIG FIXED)
# =========================================
def redraw():
    display = combined.copy()

    # alle gespeicherten Punkte
    for i in range(len(points_img1)):
        x1, y1 = points_img1[i]
        x2, y2 = points_img2[i]
        x2_shift = x2 + w1

        # Punkte
        cv2.circle(display, (x1, y1), 8, (0, 0, 255), -1)
        cv2.circle(display, (x2_shift, y2), 8, (0, 255, 0), -1)

        # Linie
        cv2.line(display, (x1, y1), (x2_shift, y2), (255, 0, 0), 2)

        # Index
        cv2.putText(display, str(i), (x1+5, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
        cv2.putText(display, str(i), (x2_shift+5, y2-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    # temporärer Punkt (wichtig!)
    if temp_point is not None:
        cv2.circle(display, temp_point, 10, (0, 255, 255), 2)

    cv2.imshow("Matcher", display)

# =========================================
# MOUSE CALLBACK
# =========================================
def mouse_callback(event, x, y, flags, param):
    global temp_point

    if event == cv2.EVENT_LBUTTONDOWN:

        # LEFT IMAGE
        if x < w1:
            temp_point = (x, y)
            print(f"[TEMP] Image1: {temp_point}")

        # RIGHT IMAGE
        else:
            if temp_point is None:
                print("ERROR: First click LEFT image")
                return

            x2 = x - w1
            y2 = y

            points_img1.append(temp_point)
            points_img2.append((x2, y2))

            print(f"[PAIR] {temp_point} <-> {(x2,y2)}")

            temp_point = None

    redraw()

# =========================================
# SAVE / LOAD
# =========================================
def save_points():
    with open(OUTPUT_FILE, "w") as f:
        json.dump({
            "points_img1": points_img1,
            "points_img2": points_img2
        }, f, indent=2)
    print("Saved!")

def load_points():
    global points_img1, points_img2
    try:
        with open(OUTPUT_FILE, "r") as f:
            data = json.load(f)
            points_img1 = data["points_img1"]
            points_img2 = data["points_img2"]
        print("Loaded!")
    except:
        print("No file found")
    redraw()

# =========================================
# MAIN
# =========================================
cv2.namedWindow("Matcher")
cv2.setMouseCallback("Matcher", mouse_callback)

print("""
Click LEFT → click RIGHT

Controls:
u = undo
s = save
l = load
q = quit
""")

redraw()

while True:
    key = cv2.waitKey(10) & 0xFF

    if key == ord('q'):
        break

    elif key == ord('u'):
        if points_img1:
            points_img1.pop()
            points_img2.pop()
            print("Undo last pair")
            redraw()

    elif key == ord('s'):
        save_points()

    elif key == ord('l'):
        load_points()

cv2.destroyAllWindows()