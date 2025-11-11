import cv2
import winsound
import time

# load classifier wajah dan mata
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

cam = cv2.VideoCapture(0)

no_eye_start = None
last_beep_time = 0
alarm_delay = 3  # mata tertutup nya brp dtk
beep_interval = 1  # jeda antar beep nya brp dtk

while True:
    ret, frame = cam.read()
    if not ret:
        break

    # size frame
    frame = cv2.resize(frame, (360, 240))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # deteksi wajah
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    eyes_detected = False

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        if len(eyes) > 0:
            eyes_detected = True

    # logika alarm
    current_time = time.time()
    if not eyes_detected:
        if no_eye_start is None:
            no_eye_start = current_time
        elif current_time - no_eye_start > alarm_delay:
            # beep hanya kalau sudah lewat 1 dtk dari beep terakhir
            if current_time - last_beep_time >= beep_interval:
                winsound.Beep(1000, 700)  # frekuensi 1000Hz, durasi 0.7 dtk
                last_beep_time = current_time
                print("⚠️ KAMU NGANTUK BRO")
    else:
        no_eye_start = None  # reset
        last_beep_time = 0

    cv2.imshow('Deteksi Mata Ngantuk', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()

