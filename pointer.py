import cv2

mouse_pos = (0, 0)

def mouse_callback(event, x, y, flags, param):
    global mouse_pos
    mouse_pos = (x, y)


def get_points(image_path, window_name):
    global mouse_pos

    points = []
    img = cv2.imread(image_path)
    clone = img.copy()

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    print(f"{window_name}: Wähle 5 Punkte (P drücken)")

    while len(points) < 5:
        display = clone.copy()

        # Maus-Vorschau
        cv2.circle(display, mouse_pos, 5, (0, 255, 0), -1)

        cv2.imshow(window_name, display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('p'):
            points.append(mouse_pos)
            print(f"{window_name} Punkt: {mouse_pos}")
            cv2.circle(clone, mouse_pos, 5, (0, 0, 255), -1)

        elif key == ord('z') and points:
            points.pop()
            clone = img.copy()
            for p in points:
                cv2.circle(clone, p, 5, (0, 0, 255), -1)

        elif key == 27:
            break

    cv2.imwrite(f'{window_name}_pts.png', clone)
    cv2.destroyAllWindows()
    return points

