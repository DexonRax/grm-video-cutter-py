from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import cv2

class VideoCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GRM Video Cutter v0.1")

        self.video_path = ""
        self.start_time = 0
        self.end_time = 0
        self.current_time = 0
        self.is_playing = True  # Track play/pause state

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Select Video File:").pack(pady=10)

        tk.Button(self.root, text="Browse", command=self.browse_file).pack(pady=10)

        tk.Label(self.root, text="Start Time (seconds):").pack(pady=5)
        self.start_entry = tk.Entry(self.root)
        self.start_entry.pack(pady=5)

        tk.Label(self.root, text="End Time (seconds):").pack(pady=5)
        self.end_entry = tk.Entry(self.root)
        self.end_entry.pack(pady=5)

        tk.Button(self.root, text="Cut Video", command=self.cut_video).pack(pady=10)

        self.slider_label = tk.Label(self.root, text="Selected Time: 0 seconds")
        self.slider_label.pack(pady=5)

        self.slider = tk.Scale(self.root, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, length=400,
                               command=self.update_preview)
        self.slider.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=640, height=360)
        self.canvas.pack(pady=10)

        # Bind spacebar key event to toggle play/pause
        self.root.bind("<space>", self.toggle_play_pause)

    def browse_file(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
        if self.video_path:
            self.load_preview()

    def cut_video(self):
        try:
            self.start_time = float(self.start_entry.get())
            self.end_time = float(self.end_entry.get())

            if not self.video_path:
                messagebox.showerror("Error", "Please select a video file.")
                return

            clip = VideoFileClip(self.video_path).subclip(self.start_time, self.end_time)
            output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])

            if output_path:
                clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                messagebox.showinfo("Success", "Video has been cut successfully.")
            else:
                messagebox.showinfo("Info", "Operation canceled.")
        except ValueError:
            messagebox.showerror("Error", "Invalid input for start/end time. Please enter numeric values.")

    def load_preview(self):
        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.slider.config(to=total_frames / cap.get(cv2.CAP_PROP_FPS))

        self.current_time = 0
        self.slider.set(self.current_time)

        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 360))
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)
            self.canvas.config(width=image.width(), height=image.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
            self.canvas.image = image

    def update_preview(self, value):
        self.current_time = float(value)
        self.slider_label.config(text=f"Selected Time: {self.current_time:.2f} seconds")
        cap = cv2.VideoCapture(self.video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.current_time * cap.get(cv2.CAP_PROP_FPS)))
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 360))
            image = Image.fromarray(frame)
            image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
            self.canvas.image = image

    def toggle_play_pause(self, event):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_video()
        else:
            self.pause_video()

    def play_video(self):
        self.root.after(0, self.play_video_frame)

    def play_video_frame(self):
        if self.is_playing:
            self.current_time = self.slider.get()
            self.slider.set(self.current_time + 0.06)  # Increment slider by a small amount
            self.root.after(30, self.play_video_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoCutterApp(root)
    root.mainloop()
