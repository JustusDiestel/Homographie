import cv2
import numpy as np

mouse_pos = (0, 0)
zoom_level = 1.0
pan_x = 0
pan_y = 0

def mouse_callback(event, x, y, flags, param):
    global mouse_pos, zoom_level, pan_x, pan_y
    
    # Rückrechnung auf Original-Koordinaten bei Zoom
    mouse_pos = (int(x / zoom_level + pan_x), int(y / zoom_level + pan_y))


def get_points(image_path, window_name):
    global mouse_pos, zoom_level, pan_x, pan_y
    
    points = []
    img = cv2.imread(image_path)
    
    if img is None:
        print(f"Fehler: {image_path} konnte nicht geladen werden!")
        return points
    
    clone = img.copy()
    h, w = img.shape[:2]
    
    # Skaliere Bild wenn zu groß
    scale = 1.0
    if w > 1200 or h > 900:
        scale = min(1200 / w, 900 / h)
        img = cv2.resize(img, (int(w * scale), int(h * scale)))
        clone = img.copy()
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 900)
    cv2.setMouseCallback(window_name, mouse_callback)
    
    print(f"\n{window_name}:")
    print(f"  P = Punkt setzen")
    print(f"  Z = Letzten Punkt löschen")
    print(f"  +/- = Zoom")
    print(f"  Pfeiltasten = Verschieben")
    print(f"  ESC = Fertig")
    print(f"\nWähle 5 Punkte auf dem Kreisrahmen...")
    
    while len(points) < 5:
        display = clone.copy()
        
        # Zeichne Grid/Overlay
        h_d, w_d = display.shape[:2]
        
        # Vertikale und horizontale Linien (Hilfslinien)
        cv2.line(display, (w_d // 2, 0), (w_d // 2, h_d), (100, 100, 100), 1)
        cv2.line(display, (0, h_d // 2), (w_d, h_d // 2), (100, 100, 100), 1)
        
        # Maus-Vorschau mit großem Kreis
        cv2.circle(display, mouse_pos, 15, (0, 255, 0), 2)
        cv2.circle(display, mouse_pos, 3, (0, 255, 0), -1)
        
        # Text mit Koordinaten
        text = f"Maus: {mouse_pos} | Punkte: {len(points)}/5"
        cv2.putText(display, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Zeichne bereits gesetzte Punkte
        for i, p in enumerate(points):
            cv2.circle(display, p, 10, (0, 0, 255), 2)
            cv2.putText(display, str(i + 1), (p[0] - 5, p[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        cv2.imshow(window_name, display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('p') or key == ord('P'):
            # Rückrechnung auf Original-Koordinaten
            orig_pos = (int(mouse_pos[0] / scale), int(mouse_pos[1] / scale))
            points.append(orig_pos)
            print(f"  Punkt {len(points)}: {orig_pos}")
            cv2.circle(clone, mouse_pos, 10, (0, 0, 255), 2)
        
        elif key == ord('z') or key == ord('Z'):
            if points:
                removed = points.pop()
                print(f"  Punkt gelöscht: {removed}")
                clone = img.copy()
                for i, p in enumerate(points):
                    cv2.circle(clone, p, 10, (0, 0, 255), 2)
        
        elif key == 27:  # ESC
            break
    
    # Speichern mit original Größe
    if scale < 1.0:
        save_img = cv2.resize(clone, (w, h))
    else:
        save_img = clone
    
    cv2.imwrite(f'{window_name}_pts.png', save_img)
    cv2.destroyAllWindows()
    return points

