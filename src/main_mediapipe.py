import cv2
import time
import threading
import tkinter as tk
from tkinter import ttk
import mediapipe as mp
import numpy as np

is_compact = False  # state awal

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
        self.geometry("480x680")
        self.configure(bg="#f0f2f5")
        self.popup_shown = False 

        self.running = False
        self.start_time = time.time()
        
        # Variabel baru untuk counting
        self.drowsy_count = 0
        self.last_face_detected_time = time.time()
        self.face_detected = False
        self.was_sleepy = False  # Untuk mencegah multiple counting
        self.popup = None
        self.popup_close_time = None
        self.is_compact = False

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
        ttk.Label(self, text="Drowsiness Monitor System", font=("Segoe UI", 16, "bold")).pack(pady=15)

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
        
        # Tambahan: Waktu reset tanpa wajah
        ttk.Label(form, text="Reset Timeout (detik):").grid(row=4, column=0)
        self.reset_timeout = tk.DoubleVar(value=5.0)
        ttk.Entry(form, textvariable=self.reset_timeout, width=14).grid(row=4, column=1, padx=5, pady=4)

        # Status Indicator
        self.status_label = tk.Label(self, text="Status: NORMAL", bg="green", fg="white", font=("Segoe UI", 16), width=20)
        self.status_label.pack(pady=10)

        # Timer dan Counter
        timer_counter_frame = tk.Frame(self, bg="#f0f2f5")
        timer_counter_frame.pack(pady=10)
        
        self.timer_label = tk.Label(timer_counter_frame, text="00:00:00", font=("Segoe UI", 20, "bold"), bg="#f0f2f5")
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        self.counter_label = tk.Label(timer_counter_frame, text="Kantuk: 0", font=("Segoe UI", 16, "bold"), 
                                     bg="#ff6b6b", fg="white", width=12, height=2)
        self.counter_label.pack(side=tk.LEFT, padx=20)

        # Buttons
        button_frame = tk.Frame(self, bg="#f0f2f5")
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="▶ Mulai", command=self.start_thread).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="⏹ Stop", command=self.stop_detection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔄 Reset Counter", command=self.reset_counter).pack(side=tk.LEFT, padx=5)

        # Log Box
        self.log_box = tk.Text(self, height=8, width=50, bg="white")
        self.log_box.pack(pady=8)
        self.log("[INFO] Sistem siap digunakan.")

                        # Simpan widget UI yang akan disembunyikan saat compact
        self.compact_hide_widgets = [
            form, 
            timer_counter_frame,
            button_frame,
            self.log_box
        ]

        # Tombol toggle ukuran window
        self.toggle_btn = tk.Button(self, text="↔", command=self.toggle_window_size, bg="#d9d9d9")
        self.toggle_btn.place(x=440, y=5)

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
    # COUNTER MANAGEMENT
    # ==========================
    def reset_counter(self):
        self.drowsy_count = 0
        self.counter_label.config(text="Kantuk: 0")
        self.log("[INFO] Counter direset ke 0")

    def update_counter(self):
        self.drowsy_count += 1
        self.counter_label.config(text=f"Kantuk: {self.drowsy_count}")
        self.log(f"[COUNT] Kantuk terdeteksi! Total: {self.drowsy_count}")

    def check_face_timeout(self):
        """Reset counter jika wajah tidak terdeteksi dalam waktu tertentu"""
        if self.face_detected:
            self.last_face_detected_time = time.time()
            self.face_detected = False
        else:
            time_since_last_face = time.time() - self.last_face_detected_time
            if time_since_last_face > self.reset_timeout.get() and self.drowsy_count > 0:
                self.log(f"[RESET] Counter direset karena tidak ada wajah terdeteksi selama {self.reset_timeout.get()} detik")
                self.reset_counter()

    # ==========================
    # START / STOP
    # ==========================
    def start_thread(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True
            threading.Thread(target=self.detect_loop, daemon=True).start()
            self.log("[INFO] Deteksi dimulai...")
        if not self.is_compact and self.mode.get() == "User":
            self.toggle_window_size()

    def stop_detection(self):
        self.running = False
        cv2.destroyAllWindows()
        self.log("[INFO] Deteksi dihentikan.")

    def show_popup(self):
        if self.popup is not None:
            return  # Jangan buat popup baru kalau sudah ada

        self.popup = tk.Toplevel(self)
        self.popup.title("⚠ PERINGATAN KELELAHAN")
        self.popup.geometry("720x220")  # << Perbesar ukuran popup
        self.popup.configure(bg="#ff4f4f")  # Merah lembut biar warning nyaman

        # Judul Besar
        tk.Label(
            self.popup,
            text="⚠ Harap Beristirahat!",
            font=("Segoe UI", 26, "bold"),   # << Font lebih besar
            fg="white",
            bg="#ff4f4f"
        ).pack(pady=20)

        # Info jumlah kantuk
        tk.Label(
            self.popup,
            text=f"Kamu terdeteksi mengantuk sebanyak: {self.drowsy_count} kali",
            font=("Segoe UI", 18),           # << Lebih jelas
            fg="white",
            bg="#ff4f4f"
        ).pack(pady=5)

        # Pesan tambahan santai
        tk.Label(
            self.popup,
            text="Cobalah tarik napas, minum air, Wudhu, atau pejamkan mata sebentar.",
            font=("Segoe UI", 12),
            fg="white",
            bg="#ff4f4f"
        ).pack(pady=10)

        # Disable close manual
        self.popup.protocol("WM_DELETE_WINDOW", lambda: None)

    def close_popup(self):
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None

    def toggle_window_size(self):
        global is_compact

        if not is_compact:
            # Masuk mode kecil
            self.normal_geometry = self.geometry()
            self.geometry("500x100")

            # Sembunyikan semua UI kecuali status dan toggle
            for w in self.compact_hide_widgets:
                w.pack_forget()

            self.toggle_btn.config(text="▣")  # ikon restore
            is_compact = True
        else:
            # Kembali normal
            self.geometry(self.normal_geometry)

            # Tampilkan kembali UI
            for w in self.compact_hide_widgets:
                w.pack(pady=10)

            self.toggle_btn.config(text="↔")
            is_compact = False


    # ==========================
    # MAIN DETECTION LOOP
    # ==========================
    def detect_loop(self):
        width, height = RESOLUSI[self.res_var.get()]
        cap = cv2.VideoCapture(0)
        cap.set(3, width)
        cap.set(4, height)

        closed_counter = 0
        self.face_detected = False

        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            ear = 1.0
            face_found = False
            
            if results.multi_face_landmarks:
                face_found = True
                self.face_detected = True
                lm = results.multi_face_landmarks[0].landmark
                left_idx = [33, 160, 158, 133, 153, 144]
                right_idx = [263, 387, 385, 362, 380, 373]
                left_eye = np.array([(lm[i].x, lm[i].y) for i in left_idx])
                right_eye = np.array([(lm[i].x, lm[i].y) for i in right_idx])
                ear = (calculate_EAR(left_eye) + calculate_EAR(right_eye)) / 2.0

            # Check for face timeout
            self.check_face_timeout()

            if face_found:
                if ear < self.ear_threshold.get():
                    closed_counter += 1
                else:
                    closed_counter = 0

                sleepy = closed_counter * 0.033 > self.sleep_time_set.get()

                # ===== DROWSINESS COUNTING =====
                if sleepy and not self.was_sleepy:
                    self.update_counter()
                    self.was_sleepy = True

                    # === Tampil POPUP (Mode User saja) ===
                    if self.mode.get() == "User":
                        self.show_popup()

                elif not sleepy:
                    # Mata sudah kembali terbuka
                    if self.was_sleepy:
                        # Set waktu kapan popup boleh ditutup
                        if self.popup is not None and self.popup_close_time is None:
                            self.popup_close_time = time.time() + 5  # Delay 5 detik
                    self.was_sleepy = False

                # Tutup popup setelah 2 detik mata normal
                if self.popup is not None and self.popup_close_time is not None:
                    if time.time() >= self.popup_close_time:
                        self.close_popup()
                        self.popup_close_time = None

                # ===== STATUS LABEL =====
                if sleepy:
                    self.status_label.config(text="⚠ MENGANTUK!", bg="red")
                else:
                    self.status_label.config(text="Status: NORMAL", bg="green")
            else:
                # No face detected
                closed_counter = 0
                self.status_label.config(text="WAJAH TIDAK TERDETEKSI", bg="orange")
                self.was_sleepy = False

            # ===== MODE ENGINEER =====
            if self.mode.get() == "Engineer":
                if face_found:
                    # draw mesh
                    self.mp_drawing.draw_landmarks(
                        frame,
                        results.multi_face_landmarks[0],
                        self.mp_face_mesh.FACEMESH_CONTOURS,
                        self.drawing_spec,
                        self.drawing_spec,
                    )

                    # draw eye bounding boxes safely
                    if 'left_eye' in locals() and 'right_eye' in locals() and left_eye.size > 0 and right_eye.size > 0:
                        lx, ly, lw, lh = cv2.boundingRect((left_eye * [width, height]).astype(np.int32))
                        rx, ry, rw, rh = cv2.boundingRect((right_eye * [width, height]).astype(np.int32))

                        cv2.rectangle(frame, (lx, ly), (lx+lw, ly+lh), (255, 0, 0), 2)
                        cv2.rectangle(frame, (rx, ry), (rx+rw, ry+rh), (255, 0, 0), 2)

                    if sleepy:
                        cv2.putText(frame, "⚠ DROWSY!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
                
                # Display counter on engineer mode
                cv2.putText(frame, f"Drowsy Count: {self.drowsy_count}", (50, height - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

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