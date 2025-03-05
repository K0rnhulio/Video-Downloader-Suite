import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import threading
import io
import codecs
import logging
import datetime

# Import the YouTube and Twitter downloader functions directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from youtube_downloader_hq import download_youtube_video, validate_youtube_url
from twitter_downloader import download_twitter_video, validate_twitter_url
from facebook_downloader import download_facebook_video, is_valid_facebook_url
from instagram_downloader import download_instagram_video, is_valid_instagram_url
from tiktok_downloader import download_tiktok_video, is_valid_tiktok_url

# Set up logging
log_dir = os.path.join(os.path.expanduser("~"), "Downloads", "VideoDownloader_Logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"downloader_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('VideoDownloaderGUI')
logger.info(f"Starting Video Downloader GUI. Log file: {log_file}")

class VideoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader Suite")
        self.root.geometry("600x450")
        self.root.configure(bg='#f0f0f0')
        
        # Configure custom styles
        self.setup_styles()
        
        # Create main frame
        main_frame = ttk.Frame(root, style='Main.TFrame', padding="20 20 20 20")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Video Downloader Suite",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Platform selection frame
        platform_frame = ttk.LabelFrame(
            main_frame,
            text="Select Platform",
            style='Card.TLabelframe',
            padding="10 10 10 10"
        )
        platform_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        self.platform_var = tk.StringVar()
        self.platform_combo = ttk.Combobox(
            platform_frame,
            textvariable=self.platform_var,
            state="readonly",
            style='Custom.TCombobox'
        )
        self.platform_combo['values'] = ('YouTube', 'Facebook', 'Instagram', 'TikTok', 'Twitter')
        self.platform_combo.current(0)
        self.platform_combo.pack(fill='x', padx=5, pady=5)
        self.platform_combo.bind("<<ComboboxSelected>>", self.on_platform_change)
        
        # URL input frame
        url_frame = ttk.LabelFrame(
            main_frame,
            text="Video URL",
            style='Card.TLabelframe',
            padding="10 10 10 10"
        )
        url_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        self.url_entry = ttk.Entry(
            url_frame,
            style='Custom.TEntry',
            font=('Segoe UI', 10)
        )
        self.url_entry.pack(fill='x', padx=5, pady=5)
        
        # Quality selection frame
        quality_frame = ttk.LabelFrame(
            main_frame,
            text="Quality Settings",
            style='Card.TLabelframe',
            padding="10 10 10 10"
        )
        quality_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        
        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.quality_var,
            state="readonly",
            style='Custom.TCombobox'
        )
        self.quality_combo['values'] = ('Maximum Quality', 'High Quality', 'Medium Quality')
        self.quality_combo.current(0)
        self.quality_combo.pack(fill='x', padx=5, pady=5)
        
        # Download button
        self.download_btn = ttk.Button(
            main_frame,
            text="Download Video",
            style='Action.TButton',
            command=self.start_download
        )
        self.download_btn.grid(row=4, column=0, columnspan=2, pady=(0, 15))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            orient='horizontal',
            mode='indeterminate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        self.progress.grid_remove()
        
        # Status message
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            style='Status.TLabel',
            wraplength=560
        )
        self.status_label.grid(row=6, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Log file info
        log_label = ttk.Label(
            main_frame,
            text=f"Log file: {log_file}",
            style='Info.TLabel'
        )
        log_label.grid(row=7, column=0, columnspan=2, sticky='ew')
        
        logger.info("GUI initialization complete with modern styling")

    def setup_styles(self):
        style = ttk.Style()
        
        # Configure colors
        style.configure('.',
            background='#f0f0f0',
            foreground='#333333',
            font=('Segoe UI', 10)
        )
        
        # Title style
        style.configure('Title.TLabel',
            font=('Segoe UI', 16, 'bold'),
            foreground='#2c3e50',
            padding=10
        )
        
        # Card frame style
        style.configure('Card.TLabelframe',
            background='#ffffff',
            relief='solid'
        )
        style.configure('Card.TLabelframe.Label',
            font=('Segoe UI', 10, 'bold'),
            foreground='#2c3e50',
            background='#ffffff'
        )
        
        # Button styles
        style.configure('Action.TButton',
            font=('Segoe UI', 11, 'bold'),
            padding=10
        )
        style.map('Action.TButton',
            background=[('active', '#2980b9'), ('!active', '#3498db')],
            foreground=[('active', 'white'), ('!active', 'white')]
        )
        
        # Status label style
        style.configure('Status.TLabel',
            font=('Segoe UI', 10),
            foreground='#27ae60'
        )
        
        # Info label style
        style.configure('Info.TLabel',
            font=('Segoe UI', 8),
            foreground='#7f8c8d'
        )
        
        # Progress bar style
        style.configure('Custom.Horizontal.TProgressbar',
            troughcolor='#f0f0f0',
            background='#3498db',
            thickness=10
        )
        
    def on_platform_change(self, event):
        """Update GUI elements based on selected platform"""
        platform = self.platform_var.get()
        logger.info(f"Platform changed to: {platform}")
        
        # Show/hide quality selector based on platform
        if platform in ['YouTube', 'Twitter', 'Facebook', 'Instagram', 'TikTok']:
            self.quality_combo.pack(fill='x', padx=5, pady=5)
            
            # Update quality options based on platform
            if platform == 'YouTube':
                self.quality_combo['values'] = ('Maximum Quality', 'High Quality', 'Medium Quality')
            elif platform == 'Twitter':
                self.quality_combo['values'] = ('Best Quality', 'Medium Quality', 'Worst Quality')
            elif platform == 'Facebook':
                self.quality_combo['values'] = ('Best Quality', 'Medium Quality', 'Worst Quality')
            elif platform == 'Instagram':
                self.quality_combo['values'] = ('Best Quality', 'Medium Quality', 'Worst Quality')
            elif platform == 'TikTok':
                self.quality_combo['values'] = ('Best Quality', 'Medium Quality', 'Worst Quality')
            
            self.quality_combo.current(0)
            logger.debug(f"Quality options updated for {platform}")
        else:
            self.quality_combo.pack_forget()
    
    def download_thread(self, platform, url, quality_format):
        """Run download in a separate thread to keep GUI responsive"""
        try:
            logger.info(f"Starting download thread for {platform}: {url}")
            logger.info(f"Selected quality: {quality_format}")
            
            if platform == 'YouTube':
                # Directly call the YouTube downloader function
                if not validate_youtube_url(url):
                    logger.error(f"Invalid YouTube URL: {url}")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Invalid YouTube URL"))
                    return
                
                # Set output directory
                output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube_Videos_HQ")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                logger.info(f"YouTube output directory: {output_dir}")
                
                # Call the download function directly with the quality settings
                logger.debug(f"Calling YouTube downloader with quality: {quality_format}")
                result = download_youtube_video(
                    url, 
                    output_dir, 
                    force_high_quality=True, 
                    quality=quality_format, 
                    non_interactive=True
                )
                
                logger.info(f"YouTube download result: {result}")
                self.root.after(0, lambda: self.status_var.set(result))
                self.root.after(0, lambda: messagebox.showinfo('Success', 'Download completed successfully!'))
            
            elif platform == 'Twitter':
                # Directly call the Twitter downloader function
                if not validate_twitter_url(url):
                    logger.error(f"Invalid Twitter URL: {url}")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Invalid Twitter URL"))
                    return
                
                # Set output directory
                output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Twitter_Videos")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                logger.info(f"Twitter output directory: {output_dir}")
                
                # Check if directory is writable
                try:
                    test_file = os.path.join(output_dir, "test_write.txt")
                    with open(test_file, 'w') as f:
                        f.write("Test")
                    os.remove(test_file)
                    logger.info(f"Output directory is writable: {output_dir}")
                except Exception as e:
                    logger.error(f"Output directory is not writable: {output_dir}, Error: {str(e)}")
                
                # Map quality selection to Twitter quality options
                twitter_quality = {
                    'Best Quality': 'best',
                    'Medium Quality': 'medium',
                    'Worst Quality': 'worst'
                }.get(quality_format, 'best')
                
                logger.info(f"Mapped Twitter quality: {quality_format} -> {twitter_quality}")
                
                try:
                    # Call the download function directly with error handling for encoding issues
                    logger.debug(f"Calling Twitter downloader with quality: {twitter_quality}")
                    result = download_twitter_video(url, output_dir, twitter_quality)
                    logger.info(f"Twitter download raw result: {result}")
                    
                    # Check if the file exists in the output directory
                    files_before_download = set(os.listdir(output_dir))
                    logger.debug(f"Files in output directory before download: {files_before_download}")
                    
                    # Check again after download
                    files_after_download = set(os.listdir(output_dir))
                    logger.debug(f"Files in output directory after download: {files_after_download}")
                    
                    # Find new files
                    new_files = files_after_download - files_before_download
                    logger.info(f"New files created: {new_files}")
                    
                    # Ensure the result is properly encoded
                    if isinstance(result, str):
                        # Replace any problematic characters
                        try:
                            result = result.encode('ascii', 'replace').decode('ascii')
                        except Exception as e:
                            logger.error(f"Error encoding result: {str(e)}")
                            result = "Download completed successfully, but couldn't display full details"
                    
                    self.root.after(0, lambda: self.status_var.set(result))
                    if isinstance(result, str) and "Success" in result:
                        logger.info("Twitter download reported success")
                        self.root.after(0, lambda: messagebox.showinfo('Success', 'Twitter video downloaded successfully!'))
                    else:
                        logger.error(f"Twitter download failed: {result}")
                        self.root.after(0, lambda: messagebox.showerror('Error', str(result)))
                except Exception as e:
                    # Handle all exceptions
                    logger.exception(f"Exception during Twitter download: {str(e)}")
                    safe_message = f"Error during download: {str(e)}"
                    self.root.after(0, lambda: self.status_var.set(safe_message))
                    self.root.after(0, lambda: messagebox.showerror('Error', safe_message))
            
            elif platform == 'Facebook':
                # Directly call the Facebook downloader function
                if not is_valid_facebook_url(url):
                    logger.error(f"Invalid Facebook URL: {url}")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Invalid Facebook URL"))
                    return
                
                # Set output directory
                output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Facebook_Videos")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                logger.info(f"Facebook output directory: {output_dir}")
                
                # Check if directory is writable
                try:
                    test_file = os.path.join(output_dir, "test_write.txt")
                    with open(test_file, 'w') as f:
                        f.write("Test")
                    os.remove(test_file)
                    logger.info(f"Output directory is writable: {output_dir}")
                except Exception as e:
                    logger.error(f"Output directory is not writable: {output_dir}, Error: {str(e)}")
                
                # Map quality selection to Facebook quality options
                facebook_quality = {
                    'Best Quality': 'best',
                    'Medium Quality': 'medium',
                    'Worst Quality': 'worst'
                }.get(quality_format, 'best')
                
                logger.info(f"Mapped Facebook quality: {quality_format} -> {facebook_quality}")
                
                try:
                    # Call the download function directly with error handling
                    logger.debug(f"Calling Facebook downloader with quality: {facebook_quality}")
                    
                    # Record files before download to detect new files
                    files_before_download = set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
                    logger.debug(f"Files in output directory before download: {files_before_download}")
                    
                    # Call the Facebook downloader
                    result = download_facebook_video(url, facebook_quality, output_dir)
                    logger.info(f"Facebook download result: {result}")
                    
                    # Check again after download
                    files_after_download = set(os.listdir(output_dir))
                    logger.debug(f"Files in output directory after download: {files_after_download}")
                    
                    # Find new files
                    new_files = files_after_download - files_before_download
                    logger.info(f"New files created: {new_files}")
                    
                    if result:
                        success_message = "Facebook video downloaded successfully!"
                        logger.info(success_message)
                        self.root.after(0, lambda: self.status_var.set(success_message))
                        self.root.after(0, lambda: messagebox.showinfo('Success', success_message))
                    else:
                        error_message = "Failed to download Facebook video. Check the log for details."
                        logger.error(error_message)
                        self.root.after(0, lambda: self.status_var.set(error_message))
                        self.root.after(0, lambda: messagebox.showerror('Error', error_message))
                except Exception as e:
                    # Handle all exceptions
                    logger.exception(f"Exception during Facebook download: {str(e)}")
                    safe_message = f"Error during download: {str(e)}"
                    self.root.after(0, lambda: self.status_var.set(safe_message))
                    self.root.after(0, lambda: messagebox.showerror('Error', safe_message))
            
            elif platform == 'Instagram':
                # Directly call the Instagram downloader function
                if not is_valid_instagram_url(url):
                    logger.error(f"Invalid Instagram URL: {url}")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Invalid Instagram URL"))
                    return
                
                # Set output directory
                output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "Instagram_Videos")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                logger.info(f"Instagram output directory: {output_dir}")
                
                # Check if directory is writable
                try:
                    test_file = os.path.join(output_dir, "test_write.txt")
                    with open(test_file, 'w') as f:
                        f.write("Test")
                    os.remove(test_file)
                    logger.info(f"Output directory is writable: {output_dir}")
                except Exception as e:
                    logger.error(f"Output directory is not writable: {output_dir}, Error: {str(e)}")
                
                # Map quality selection to Instagram quality options
                instagram_quality = {
                    'Best Quality': 'best',
                    'Medium Quality': 'medium',
                    'Worst Quality': 'worst'
                }.get(quality_format, 'best')
                
                logger.info(f"Mapped Instagram quality: {quality_format} -> {instagram_quality}")
                
                try:
                    # Record files before download to detect new files
                    files_before_download = set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
                    logger.debug(f"Files in output directory before download: {files_before_download}")
                    
                    # Call the Instagram downloader
                    logger.debug(f"Calling Instagram downloader with quality: {instagram_quality}")
                    result = download_instagram_video(url, instagram_quality, output_dir)
                    logger.info(f"Instagram download result: {result}")
                    
                    # Check again after download
                    files_after_download = set(os.listdir(output_dir))
                    logger.debug(f"Files in output directory after download: {files_after_download}")
                    
                    # Find new files
                    new_files = files_after_download - files_before_download
                    logger.info(f"New files created: {new_files}")
                    
                    if result:
                        success_message = "Instagram video downloaded successfully!"
                        logger.info(success_message)
                        self.root.after(0, lambda: self.status_var.set(success_message))
                        self.root.after(0, lambda: messagebox.showinfo('Success', success_message))
                    else:
                        error_message = "Failed to download Instagram video. Check the log for details."
                        logger.error(error_message)
                        self.root.after(0, lambda: self.status_var.set(error_message))
                        self.root.after(0, lambda: messagebox.showerror('Error', error_message))
                except Exception as e:
                    # Handle all exceptions
                    logger.exception(f"Exception during Instagram download: {str(e)}")
                    safe_message = f"Error during download: {str(e)}"
                    self.root.after(0, lambda: self.status_var.set(safe_message))
                    self.root.after(0, lambda: messagebox.showerror('Error', safe_message))
            
            elif platform == 'TikTok':
                # Directly call the TikTok downloader function
                if not is_valid_tiktok_url(url):
                    logger.error(f"Invalid TikTok URL: {url}")
                    self.root.after(0, lambda: messagebox.showerror("Error", "Invalid TikTok URL"))
                    return
                
                # Set output directory
                output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "TikTok_Videos")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                logger.info(f"TikTok output directory: {output_dir}")
                
                # Check if directory is writable
                try:
                    test_file = os.path.join(output_dir, "test_write.txt")
                    with open(test_file, 'w') as f:
                        f.write("Test")
                    os.remove(test_file)
                    logger.info(f"Output directory is writable: {output_dir}")
                except Exception as e:
                    logger.error(f"Output directory is not writable: {output_dir}, Error: {str(e)}")
                
                # Map quality selection to TikTok quality options
                tiktok_quality = {
                    'Best Quality': 'best',
                    'Medium Quality': 'medium',
                    'Worst Quality': 'worst'
                }.get(quality_format, 'best')
                
                logger.info(f"Mapped TikTok quality: {quality_format} -> {tiktok_quality}")
                
                try:
                    # Record files before download to detect new files
                    files_before_download = set(os.listdir(output_dir)) if os.path.exists(output_dir) else set()
                    logger.debug(f"Files in output directory before download: {files_before_download}")
                    
                    # Call the TikTok downloader
                    logger.debug(f"Calling TikTok downloader with quality: {tiktok_quality}")
                    result = download_tiktok_video(url, tiktok_quality, output_dir)
                    logger.info(f"TikTok download result: {result}")
                    
                    # Check again after download
                    files_after_download = set(os.listdir(output_dir))
                    logger.debug(f"Files in output directory after download: {files_after_download}")
                    
                    # Find new files
                    new_files = files_after_download - files_before_download
                    logger.info(f"New files created: {new_files}")
                    
                    if result:
                        success_message = "TikTok video downloaded successfully!"
                        logger.info(success_message)
                        self.root.after(0, lambda: self.status_var.set(success_message))
                        self.root.after(0, lambda: messagebox.showinfo('Success', success_message))
                    else:
                        error_message = "Failed to download TikTok video. Check the log for details."
                        logger.error(error_message)
                        self.root.after(0, lambda: self.status_var.set(error_message))
                        self.root.after(0, lambda: messagebox.showerror('Error', error_message))
                except Exception as e:
                    # Handle all exceptions
                    logger.exception(f"Exception during TikTok download: {str(e)}")
                    safe_message = f"Error during download: {str(e)}"
                    self.root.after(0, lambda: self.status_var.set(safe_message))
                    self.root.after(0, lambda: messagebox.showerror('Error', safe_message))
            
            else:
                # Other downloaders still use the temporary script approach
                scripts = {
                    # 'TikTok': 'tiktok_downloader.py',
                }
                
                logger.info(f"Using temporary script approach for {platform}")
                
                temp_script = f"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from {scripts[platform][:-3]} import download_{platform.lower()}_video

# Call the download function directly
download_{platform.lower()}_video('{url}')
"""
                temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_download.py")
                with open(temp_file, 'w') as f:
                    f.write(temp_script)
                
                # Run the temporary script
                logger.debug(f"Running temporary script: {temp_file}")
                subprocess.run(['python', temp_file], check=True)
                
                # Clean up
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                
                logger.info(f"{platform} download completed via temporary script")
                self.root.after(0, lambda: self.status_var.set("Download completed successfully!"))
                self.root.after(0, lambda: messagebox.showinfo('Success', 'Download completed successfully!'))
        except Exception as e:
            logger.exception(f"Unhandled exception in download thread: {str(e)}")
            error_msg = f"Download failed: {str(e)}"
            self.root.after(0, lambda: self.status_var.set(error_msg))
            self.root.after(0, lambda: messagebox.showerror('Error', error_msg))
        finally:
            logger.info("Download thread completed")
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.grid_remove())
            self.root.after(0, lambda: self.download_btn.config(state='normal'))
    
    def start_download(self):
        """Start the download process"""
        platform = self.platform_var.get()
        url = self.url_entry.get().strip()
        
        logger.info(f"Starting download for {platform}: {url}")
        
        if not url:
            logger.warning("No URL provided")
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        # Disable download button during download
        self.download_btn.config(state='disabled')
        
        # Show progress bar
        self.status_var.set("Downloading... Please wait.")
        self.progress.grid()
        self.progress.start()
        
        # Get selected quality
        quality = self.quality_var.get()
        logger.info(f"Selected quality: {quality}")
        
        # Map quality selection to format string (for YouTube)
        if platform == 'YouTube':
            quality_formats = {
                'Maximum Quality': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                'High Quality': 'best',
                'Medium Quality': '18'  # 360p typically
            }
            format_string = quality_formats.get(quality, quality_formats['Maximum Quality'])
        else:
            # For other platforms, just pass the quality name
            format_string = quality
        
        logger.debug(f"Using format string: {format_string}")
        
        # Start download in a separate thread to keep GUI responsive
        download_thread = threading.Thread(
            target=self.download_thread,
            args=(platform, url, format_string)
        )
        download_thread.daemon = True
        download_thread.start()
        logger.info("Download thread started")

if __name__ == "__main__":
    try:
        logger.info("Starting main application")
        root = tk.Tk()
        app = VideoDownloaderGUI(root)
        root.mainloop()
    except Exception as e:
        logger.exception(f"Unhandled exception in main: {str(e)}")
        raise
