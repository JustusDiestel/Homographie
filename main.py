import cv2
from pointer import get_points


def main():
    pts_img1 = get_points("1.jpg", "Bild 1")
    pts_img2 = get_points("2.jpg", "Bild 2")

    # OPTIONAL: nur anzeigen wenn Datei existiert
    img1 = cv2.imread("Bild1_pts.png")
    img2 = cv2.imread("Bild2_pts.png")

    if img1 is not None:
        cv2.imshow("Bild 1", img1)

    if img2 is not None:
        cv2.imshow("Bild 2", img2)

    print("Bild1:", pts_img1)
    print("Bild2:", pts_img2)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()