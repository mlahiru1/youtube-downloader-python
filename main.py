import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import os
from urllib.parse import urlparse, parse_qs

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video/Audio Downloader")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL Entry
        ttk.Label(self.main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.main_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Download Location
        ttk.Label(self.main_frame, text="Save Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.location_entry = ttk.Entry(self.main_frame, textvariable=self.location_var, width=50)
        self.location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_location).grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        
        # Download Type Frame
        type_frame = ttk.LabelFrame(self.main_frame, text="Download Type", padding="5")
        type_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Download Type Selection
        self.download_type = tk.StringVar(value="video_audio")
        ttk.Radiobutton(type_frame, text="Video with Audio", variable=self.download_type, 
                       value="video_audio", command=self.update_quality_options).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Video Only", variable=self.download_type, 
                       value="video_only", command=self.update_quality_options).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="Audio Only", variable=self.download_type, 
                       value="audio_only", command=self.update_quality_options).pack(side=tk.LEFT, padx=5)
        
        # Quality Frame
        quality_frame = ttk.LabelFrame(self.main_frame, text="Quality Settings", padding="5")
        quality_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Video Quality
        self.video_quality_frame = ttk.Frame(quality_frame)
        self.video_quality_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.video_quality_frame, text="Video Quality:").pack(side=tk.LEFT, padx=5)
        self.video_quality_var = tk.StringVar(value="1080p")
        self.video_quality_combo = ttk.Combobox(self.video_quality_frame, textvariable=self.video_quality_var, width=20)
        self.video_quality_combo['values'] = ('2160p (4K)', '1440p (2K)', '1080p', '720p', '480p', '360p', 'best')
        self.video_quality_combo.pack(side=tk.LEFT, padx=5)
        
        # Audio Quality
        self.audio_quality_frame = ttk.Frame(quality_frame)
        self.audio_quality_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.audio_quality_frame, text="Audio Quality:").pack(side=tk.LEFT, padx=5)
        self.audio_quality_var = tk.StringVar(value="192")
        self.audio_quality_combo = ttk.Combobox(self.audio_quality_frame, textvariable=self.audio_quality_var, width=20)
        self.audio_quality_combo['values'] = ('320 kbps', '256 kbps', '192 kbps', '128 kbps', '96 kbps')
        self.audio_quality_combo.pack(side=tk.LEFT, padx=5)
        
        # Audio Format
        self.audio_format_frame = ttk.Frame(quality_frame)
        self.audio_format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.audio_format_frame, text="Audio Format:").pack(side=tk.LEFT, padx=5)
        self.audio_format_var = tk.StringVar(value="mp3")
        self.audio_format_combo = ttk.Combobox(self.audio_format_frame, textvariable=self.audio_format_var, width=20)
        self.audio_format_combo['values'] = ('mp3', 'm4a', 'wav', 'aac')
        self.audio_format_combo.pack(side=tk.LEFT, padx=5)
        
        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Download Button
        self.download_btn = ttk.Button(self.main_frame, text="Download", command=self.start_download)
        self.download_btn.grid(row=6, column=0, columnspan=3, pady=10)
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # Update quality options initially
        self.update_quality_options()
    
    def update_quality_options(self):
        download_type = self.download_type.get()
        
        # Show/hide quality options based on download type
        if download_type == "audio_only":
            self.video_quality_frame.pack_forget()
            self.audio_quality_frame.pack(fill=tk.X, pady=5)
            self.audio_format_frame.pack(fill=tk.X, pady=5)
        elif download_type == "video_only":
            self.video_quality_frame.pack(fill=tk.X, pady=5)
            self.audio_quality_frame.pack_forget()
            self.audio_format_frame.pack_forget()
        else:  # video_audio
            self.video_quality_frame.pack(fill=tk.X, pady=5)
            self.audio_quality_frame.pack(fill=tk.X, pady=5)
            self.audio_format_frame.pack_forget()
    
    def browse_location(self):
        directory = filedialog.askdirectory(initialdir=self.location_var.get())
        if directory:
            self.location_var.set(directory)
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Downloading... {progress:.1f}%")
            except:
                pass
        elif d['status'] == 'finished':
            self.status_var.set("Download completed!")
            self.progress_var.set(100)
            self.download_btn.config(state=tk.NORMAL)
    
    def get_video_info(self, url):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get('title', 'video')
        except:
            return 'video'
    
    def download_video(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        output_path = os.path.join(self.location_var.get(), '%(title)s.%(ext)s')
        download_type = self.download_type.get()
        
        try:
            if download_type == "audio_only":
                # Audio only download
                audio_quality = self.audio_quality_var.get().split()[0]  # Get just the number
                audio_format = self.audio_format_var.get()
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': audio_format,
                        'preferredquality': audio_quality,
                    }],
                    'progress_hooks': [self.progress_hook],
                    'outtmpl': output_path,
                }
            
            elif download_type == "video_only":
                # Video only download
                quality = self.video_quality_var.get().split()[0]  # Get just the resolution
                format_str = f'bestvideo[height<={quality[:-1]}][ext=mp4]'
                
                ydl_opts = {
                    'format': format_str,
                    'progress_hooks': [self.progress_hook],
                    'outtmpl': output_path,
                }
            
            else:  # video_audio
                # Video with audio download
                quality = self.video_quality_var.get().split()[0]
                if quality == 'best':
                    format_str = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                else:
                    format_str = f'bestvideo[height<={quality[:-1]}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                
                ydl_opts = {
                    'format': format_str,
                    'progress_hooks': [self.progress_hook],
                    'outtmpl': output_path,
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.status_var.set("Starting download...")
                ydl.download([url])
                
        except Exception as e:
            self.status_var.set("Download failed!")
            messagebox.showerror("Error", str(e))
            self.download_btn.config(state=tk.NORMAL)
    
    def start_download(self):
        self.download_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        thread = threading.Thread(target=self.download_video, daemon=True)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()