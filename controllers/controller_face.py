import os
import cv2
import numpy as np
from tkinter import messagebox

import sys

if getattr(sys, 'frozen', False):
    # PyInstaller environment: read-only assets in _MEIPASS, persistent files in executable directory
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    EXE_DIR = os.path.dirname(sys.executable)
    FACES_DIR = os.path.join(EXE_DIR, "faces")
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FACES_DIR = os.path.join(BASE_DIR, "faces")

MODEL_PATH = os.path.join(FACES_DIR, "trained_model.yml")

# Ensure faces directory exists
os.makedirs(FACES_DIR, exist_ok=True)

def get_cascade_path():
    """Ensure Haar Cascade XML file is available and return its path"""
    local_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
    if os.path.exists(local_path):
        return local_path
    
    faces_path = os.path.join(FACES_DIR, "haarcascade_frontalface_default.xml")
    if os.path.exists(faces_path):
        return faces_path
        
    # Download if not exists
    import urllib.request
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    try:
        urllib.request.urlretrieve(url, local_path)
        return local_path
    except Exception as e:
        print(f"Error downloading cascade: {e}")
        return cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

class FaceController:
    @staticmethod
    def is_face_registered(user_id):
        """Check if user has registered face photos"""
        if not os.path.exists(FACES_DIR):
            return False
        for file in os.listdir(FACES_DIR):
            if file.startswith(f"user_{user_id}_") and file.endswith(".jpg"):
                return True
        return False

    @staticmethod
    def train_model():
        """Train the LBPH Face Recognizer using registered face photos"""
        if not os.path.exists(FACES_DIR):
            return False

        face_samples = []
        ids = []

        # Load Haar Cascade
        cascade_path = get_cascade_path()
        face_cascade = cv2.CascadeClassifier(cascade_path)

        for file in os.listdir(FACES_DIR):
            if file.startswith("user_") and file.endswith(".jpg"):
                # Filename format: user_{user_id}_{index}.jpg
                parts = file.split("_")
                if len(parts) >= 3:
                    try:
                        user_id = int(parts[1])
                        img_path = os.path.join(FACES_DIR, file)
                        
                        # Load image in grayscale
                        gray_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                        if gray_img is None:
                            continue
                            
                        # Detect faces just to be sure we get the cropped face
                        faces = face_cascade.detectMultiScale(gray_img, 1.3, 5)
                        
                        if len(faces) > 0:
                            for (x, y, w, h) in faces:
                                crop_face = gray_img[y:y+h, x:x+w]
                                crop_face = cv2.resize(crop_face, (200, 200))
                                face_samples.append(crop_face)
                                ids.append(user_id)
                        else:
                            # Fallback: if no face detected now but the image itself is cropped face
                            resized = cv2.resize(gray_img, (200, 200))
                            face_samples.append(resized)
                            ids.append(user_id)
                    except ValueError:
                        continue

        if not face_samples:
            # If model path exists, delete it because there are no images
            if os.path.exists(MODEL_PATH):
                try:
                    os.remove(MODEL_PATH)
                except:
                    pass
            return False

        try:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(face_samples, np.array(ids))
            recognizer.write(MODEL_PATH)
            return True
        except Exception as e:
            print(f"Error training model: {e}")
            return False

    @staticmethod
    def register_face(user_id, name):
        """Capture face samples from webcam and save them for training"""
        # Load Haar Cascade
        cascade_path = get_cascade_path()
        face_cascade = cv2.CascadeClassifier(cascade_path)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error Kamera", "Tidak dapat membuka kamera web. Pastikan kamera terhubung dan tidak digunakan aplikasi lain.")
            return False

        # Clear existing samples for this user
        for file in os.listdir(FACES_DIR):
            if file.startswith(f"user_{user_id}_") and file.endswith(".jpg"):
                try:
                    os.remove(os.path.join(FACES_DIR, file))
                except Exception as e:
                    print(f"Failed to remove {file}: {e}")

        count = 0
        max_samples = 20
        messagebox.showinfo("Registrasi Wajah", "Kamera akan terbuka.\nHarap menghadap ke kamera, posisikan wajah Anda di tengah kotak, dan ubah sedikit ekspresi/posisi kepala Anda secara perlahan.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Mirror frame for easier alignment
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # UI Text on video
            cv2.putText(frame, f"Registrasi: {name}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f"Progress: {count}/{max_samples}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, "Tekan 'q' untuk Batal", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            for (x, y, w, h) in faces:
                # Draw box around face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 120, 0), 2)
                
                # Capture frame every 5 iterations to get variation
                if count < max_samples:
                    # Save cropped grayscale face
                    face_img = gray[y:y+h, x:x+w]
                    face_img = cv2.resize(face_img, (200, 200))
                    
                    img_name = f"user_{user_id}_{count}.jpg"
                    cv2.imwrite(os.path.join(FACES_DIR, img_name), face_img)
                    count += 1
                    
                    # Flash effect on the box
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

            cv2.imshow("Registrasi Wajah (Face Recognition)", frame)

            # Auto close if captured enough
            if count >= max_samples:
                break

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Clean up partially captured samples
                for file in os.listdir(FACES_DIR):
                    if file.startswith(f"user_{user_id}_") and file.endswith(".jpg"):
                        try:
                            os.remove(os.path.join(FACES_DIR, file))
                        except:
                            pass
                cap.release()
                cv2.destroyAllWindows()
                messagebox.showwarning("Registrasi Dibatalkan", "Registrasi wajah dibatalkan.")
                return False

        cap.release()
        cv2.destroyAllWindows()

        # Train the model with new face
        if count >= max_samples:
            messagebox.showinfo("Memproses", "Melatih model pengenalan wajah. Harap tunggu...")
            if FaceController.train_model():
                messagebox.showinfo("Sukses", "Registrasi wajah berhasil dilakukan dan database wajah telah diperbarui!")
                return True
            else:
                messagebox.showerror("Error", "Gagal melatih model pengenalan wajah.")
                return False
        return False

    @staticmethod
    def verify_face(user_id, name):
        """Open webcam and verify if the person matches user_id"""
        # Ensure model exists
        if not os.path.exists(MODEL_PATH):
            # Try to train if we have images
            trained = FaceController.train_model()
            if not trained:
                messagebox.showerror("Error Verifikasi", "Model pengenalan wajah belum siap. Harap daftarkan wajah Anda terlebih dahulu.")
                return False

        # Load recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            recognizer.read(MODEL_PATH)
        except Exception as e:
            messagebox.showerror("Error Verifikasi", f"Gagal membaca model wajah: {e}")
            return False

        # Load Haar Cascade
        cascade_path = get_cascade_path()
        face_cascade = cv2.CascadeClassifier(cascade_path)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error Kamera", "Tidak dapat membuka kamera web.")
            return False

        # Verification variables
        verified = False
        consecutive_matches = 0
        required_matches = 8  # Require 8 matching frames to verify
        timeout_frames = 200   # Max frames to try (approx 10-15 seconds)
        frame_count = 0

        messagebox.showinfo("Verifikasi Kehadiran", "Kamera akan terbuka.\nHarap menghadap ke kamera untuk verifikasi wajah.")

        while frame_count < timeout_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            # Mirror frame
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # UI text
            cv2.putText(frame, f"Mencari Wajah: {name}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, f"Kecocokan: {consecutive_matches}/{required_matches}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(frame, "Tekan 'q' untuk Batal", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            for (x, y, w, h) in faces:
                # Target face area
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))

                # Predict face
                pred_id, confidence = recognizer.predict(face_img)
                
                # Calculate similarity (distance is closer to 0 for better match)
                # For LBPH, confidence <= 75 is typically a good match
                match = (pred_id == user_id) and (confidence <= 75.0)
                
                if match:
                    consecutive_matches += 1
                    # Green box for match
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    similarity = max(0, int(100 - (confidence * 0.8)))
                    cv2.putText(frame, f"VERIFIED: {similarity}%", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    consecutive_matches = max(0, consecutive_matches - 1)
                    # Red box for mismatch
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, "UNKNOWN / NOT MATCH", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow("Verifikasi Wajah (Face Recognition)", frame)

            if consecutive_matches >= required_matches:
                verified = True
                # Visual confirmation
                for i in range(5):
                    # Show green frame flashing quickly
                    cv2.putText(frame, "VERIFIKASI BERHASIL!", (frame.shape[1]//2 - 150, frame.shape[0]//2), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
                    cv2.imshow("Verifikasi Wajah (Face Recognition)", frame)
                    cv2.waitKey(100)
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if verified:
            messagebox.showinfo("Verifikasi Berhasil", f"Wajah terverifikasi sebagai {name}!")
            return True
        else:
            messagebox.showerror("Verifikasi Gagal", "Wajah tidak dikenali atau verifikasi dibatalkan/habis waktu.")
            return False
