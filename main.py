from pointer import get_points


def main():
    pts_img1 = get_points("1.jpg", "Bild 1")
    pts_img2 = get_points("2.jpg", "Bild 2")

    print("Bild1:", pts_img1)
    print("Bild2:", pts_img2)




if __name__ == "__main__":
    main()