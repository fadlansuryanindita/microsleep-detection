
import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk
import mediapipe as mp
import numpy as np

# ==========================
# RESOLUSI
# ==========================
RESOLUSI = {
    "240p": (320, 240),
    "360p": (480, 360),
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080)
}

# ==========================
# EAR FUNCTION
# ==========================
def calculate_EAR(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)


class FaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("👁️ Micro Break & Drowsiness Detection")
        self.geometry("480x620")
        self.configure(bg="#f0f2f5")

        self.running = False
        self.start_time = time.time()

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

        # Mediapipe Init
        self.mp_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_mesh.FaceMesh(refine_landmarks=True)

        # Build UI
        self.build_ui()

    # ==========================
    # UI BUILD
    # ==========================
    def build_ui(self):
        ttk.Label(self, text="👁️ Drowsiness Monitor System", font=("Segoe UI", 16, "bold")).pack(pady=15)

        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Mode Tampilan:").grid(row=0, column=0)
        self.mode = tk.StringVar(value="User")
        ttk.Combobox(form, textvariable=self.mode, values=["User", "Engineer"], width=14).grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form, text="Resolusi Kamera:").grid(row=1, column=0)
        self.res_var = tk.StringVar(value="480p")
        ttk.Combobox(form, textvariable=self.res_var, values=list(RESOLUSI.keys()), width=14).grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form, text="EAR Threshold:").grid(row=2, column=0)
        self.ear_threshold = tk.DoubleVar(value=0.23)
        ttk.Entry(form, textvariable=self.ear_threshold, width=14).grid(row=2, column=1, padx=5, pady=4)

        ttk.Label(form, text="Min Pejam (detik):").grid(row=3, column=0)
        self.sleep_time_set = tk.DoubleVar(value=1.2)
        ttk.Entry(form, textvariable=self.sleep_time_set, width=14).grid(row=3, column=1, padx=5, pady=4)

        # Status Indicator
        self.status_label = tk.Label(self, text="Status: NORMAL", bg="green", fg="white", font=("Segoe UI", 16), width=20)
        self.status_label.pack(pady=15)

        # Timer
        self.timer_label = tk.Label(self, text="00:00:00", font=("Segoe UI", 24, "bold"), bg="#f0f2f5")
        self.timer_label.pack(pady=10)

        # Buttons
        ttk.Button(self, text="▶ Mulai", command=self.start_thread).pack(pady=5)
        ttk.Button(self, text="⏹ Stop", command=self.stop_detection).pack(pady=5)

        # Log Box
        self.log_box = tk.Text(self, height=8, width=50, bg="white")
        self.log_box.pack(pady=8)
        self.log("[INFO] Sistem siap digunakan.")

        self.update_timer()

    # ==========================
    # LOG SYSTEM
    # ==========================
    def log(self, msg):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")

    # ==========================
    # TIMER SYSTEM
    # ==========================
    def update_timer(self):
        if self.running:
            elapsed = int(time.time() - self.start_time)
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            s = elapsed % 60
            self.timer_label.configure(text=f"{h:02}:{m:02}:{s:02}")
        self.after(1000, self.update_timer)

    # ==========================
    # START / STOP
    # ==========================
    def start_thread(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            threading.Thread(target=self.detect_loop, daemon=True).start()
            self.log("[INFO] Deteksi dimulai...")

    def stop_detection(self):
        self.running = False
        cv2.destroyAllWindows()
        self.log("[INFO] Deteksi dihentikan.")

    def play_alarm(self):
        print("[ALARM] Mata tertutup terlalu lama (suara dimatikan karena docker)")


    # ==========================
    # MAIN DETECTION LOOP
    # ==========================
    def detect_loop(self):
        width, height = RESOLUSI[self.res_var.get()]
        cap = cv2.VideoCapture(0)
        cap.set(3, width)
        cap.set(4, height)

        closed_counter = 0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            ear = 1.0
            if results.multi_face_landmarks:
                lm = results.multi_face_landmarks[0].landmark
                left_idx = [33, 160, 158, 133, 153, 144]
                right_idx = [263, 387, 385, 362, 380, 373]
                left_eye = np.array([(lm[i].x, lm[i].y) for i in left_idx])
                right_eye = np.array([(lm[i].x, lm[i].y) for i in right_idx])
                ear = (calculate_EAR(left_eye) + calculate_EAR(right_eye)) / 2.0

            if ear < self.ear_threshold.get():
                closed_counter += 1
            else:
                closed_counter = 0

            sleepy = closed_counter * 0.033 > self.sleep_time_set.get()

            # ===== STATUS LABEL =====
            if sleepy:
                self.status_label.config(text="⚠ MENGANTUK!", bg="red")
                self.play_alarm()
            else:
                self.status_label.config(text="Status: NORMAL", bg="green")

            # ===== MODE ENGINEER =====
            if self.mode.get() == "Engineer":
                if results.multi_face_landmarks:
                    # draw mesh
                    self.mp_drawing.draw_landmarks(
                        frame,
                        results.multi_face_landmarks[0],
                        self.mp_face_mesh.FACEMESH_CONTOURS,
                        self.drawing_spec,
                        self.drawing_spec,
                    )

                    # draw eye bounding boxes safely
                    if left_eye.size > 0 and right_eye.size > 0:
                        lx, ly, lw, lh = cv2.boundingRect((left_eye * [width, height]).astype(np.int32))
                        rx, ry, rw, rh = cv2.boundingRect((right_eye * [width, height]).astype(np.int32))

                        cv2.rectangle(frame, (lx, ly), (lx+lw, ly+lh), (255, 0, 0), 2)
                        cv2.rectangle(frame, (rx, ry), (rx+rw, ry+rh), (255, 0, 0), 2)

                    if sleepy:
                        cv2.putText(frame, "⚠ DROWSY!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)

                cv2.imshow("Drowsiness Monitor", frame)

            # ===== MODE USER (Tanpa window kamera) =====
            else:
                try:
                    cv2.destroyWindow("Drowsiness Monitor")
                except:
                    pass

            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.running = False


if __name__ == "__main__":
    app = FaceApp()
    app.mainloop()
