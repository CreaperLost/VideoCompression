import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox
import os
from moviepy.editor import VideoFileClip
import multiprocessing
import cv2
import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD


class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text='', command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command

        if cornerradius > 0.5*width:
            cornerradius = 0.5*width
        if cornerradius > 0.5*height:
            cornerradius = 0.5*height

        self.shapes = []
        self.shapes.append(self.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,padding+cornerradius,padding,width-padding-cornerradius,padding,width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,width-padding-cornerradius,height-padding,padding+cornerradius,height-padding), fill=color, outline=color))

        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.textid = self.create_text(width/2, height/2, text=text, fill='white', font=("Helvetica", 10))


    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()


class VideoCompressorApp:
    def __init__(self, root):
        """self.root = root  # Root is correctly assigned
        self.root.title("Aero Compress")
        self.single_video_path = None  # Store the path of the dropped video file
        self.batch_dir = None  # Store the directory of batch videos
        self.create_main_menu()  # Ensure the main menu is created"""
        self.root = root
        self.root.title("Aero Compress")
        self.root.configure(bg="#1e1e1e")
        self.single_video_path = None
        self.batch_dir = None
        self.style = ttk.Style()
        self.setup_styles()
        self.create_main_menu()
    
    def setup_styles(self):
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", foreground="white", background="#1e1e1e", font=("Helvetica", 10))
        self.style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white", insertcolor="white", font=("Helvetica", 10))
        self.style.configure("Rounded.TEntry", borderwidth=0, relief="flat")
        self.style.layout("Rounded.TEntry",
                     [('Entry.plain.field', {'children': [(
                         'Entry.background', {'children': [(
                             'Entry.padding', {'children': [(
                                 'Entry.textarea', {'sticky': 'nswe'})],
                      'sticky': 'nswe'})], 'sticky': 'nswe'})],
                      'border':'2', 'sticky': 'nswe'})])
        self.style.configure('Wild.TRadiobutton',fieldbackground="#2e2e2e", background="#1e1e1e", foreground='white', font=("Helvetica", 10))        
        
    def create_rounded_frame(self, parent, color):
        frame = tk.Frame(parent, bg=color, bd=0, highlightthickness=0)
        frame.grid_propagate(False)
        return frame

    def clean_up(self):
            for widget in self.root.winfo_children():
                widget.destroy()

    def create_main_menu(self):
        self.clean_up()

        main_frame = self.create_rounded_frame(self.root, "#1e1e1e")
        main_frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)

        ttk.Label(main_frame, text="Select an Option", font=("Helvetica", 16, "bold")).pack(padx=20, pady=20)

        RoundedButton(main_frame, 200, 40, 20, 2, "#3e3e3e", text="One Video", command=self.open_single_video_menu).pack(padx=20, pady=10, expand=True, fill=tk.BOTH)
        RoundedButton(main_frame, 200, 40, 20, 2, "#3e3e3e", text="Batch of Videos", command=self.open_batch_video_menu).pack(padx=20, pady=10, expand=True, fill=tk.BOTH)


    def add_placeholders(self):

        ttk.Label(self.root, text="Compression", font=("Helvetica", 14)).pack(padx=20, pady=10)

        self.compression_var = tk.StringVar(self.root, value="High")

        for option in ["Low", "Medium", "High"]:
            ttk.Radiobutton(self.root, text=option, variable=self.compression_var, value=option, style='Wild.TRadiobutton').pack(padx=20, expand=True, fill=tk.BOTH, anchor=tk.W)

        ttk.Label(self.root, text="Output", font=("Helvetica", 16)).pack(padx=20, expand=True, fill=tk.BOTH, pady=10)
        self.output_dir = tk.StringVar(self.root)
        ttk.Entry(self.root, textvariable=self.output_dir, width=40, style="Rounded.TEntry").pack(padx=20, expand=True, fill=tk.BOTH, pady=5)
        RoundedButton(self.root, 200, 30, 15, 2, "#3e3e3e", text="Select Output Directory", command=self.select_output_directory).pack(padx=20, expand=True, fill=tk.BOTH, pady=5)

        RoundedButton(self.root, 120, 30, 15, 2, "#3e3e3e", text="Back", command=self.create_main_menu).pack(side=tk.LEFT, padx=20, pady=20, expand=True, fill=tk.BOTH)




    def open_single_video_menu(self):

        self.clean_up()

        ttk.Label(self.root, text="Drag clip here", font=("Helvetica", 16, "bold")).pack(padx=20, expand=True, fill=tk.BOTH, pady=20)

        drag_drop_area = tk.Label(self.root, text="Drop Video Here", relief="solid", width=40, height=10 )
        drag_drop_area.pack(padx=20, pady=20)

        drag_drop_area.drop_target_register(DND_FILES)
        drag_drop_area.dnd_bind('<<Drop>>', self.on_drop)

        self.add_placeholders()
        RoundedButton(self.root, 120, 30, 15, 2, "#3e3e3e", text="Render", command=self.render_single_video).pack(side=tk.RIGHT, padx=20, pady=20, expand=True, fill=tk.BOTH)



    def open_batch_video_menu(self):
        self.clean_up()

        ttk.Label(self.root, text="Select Batch Directory", font=("Helvetica", 16, "bold")).pack(padx=20, pady=20, expand=True, fill=tk.BOTH)
        self.batch_dir = tk.StringVar(self.root)
        ttk.Entry(self.root, textvariable=self.batch_dir, width=40, style="Rounded.TEntry").pack(padx=20, pady=5, expand=True, fill=tk.BOTH)
        RoundedButton(self.root, 200, 30, 15, 2, "#3e3e3e", text="Select Directory", command=self.select_batch_directory).pack(padx=20, pady=5, expand=True, fill=tk.BOTH)

        self.add_placeholders()
        RoundedButton(self.root, 120, 30, 15, 2, "#3e3e3e", text="Render", command=self.render_batch_videos).pack(side=tk.RIGHT, padx=20, pady=20, expand=True, fill=tk.BOTH)


    def on_drop(self, event):
        # Handle the dropped file and store its path
        file_path = event.data.strip('{}')  # Strip out curly braces around file path if any
        self.single_video_path = file_path
        print(f"File dropped: {file_path}")
        # Update the label with the dropped file name
        event.widget.config(text=f"Selected: {file_path.split('/')[-1]}")

   

    def select_output_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir.set(directory)

    def select_batch_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.batch_dir.set(directory)

    def render_single_video(self):
        # Implement your video compression logic here
        compression_level = self.compression_var.get()
        output_directory = self.output_dir.get()
        if self.single_video_path and output_directory:
            messagebox.showinfo("Render", f"Rendering {self.single_video_path} with {compression_level} compression to {output_directory}")
            
            input_basename = os.path.basename(self.single_video_path)
            output_filename = os.path.splitext(input_basename)[0] + "_compressed.mp4"
            
            # Combine the output directory with the output filename
            output_filepath = os.path.join(output_directory, output_filename)

            # Bitrate.
            original_bitrate = self.get_bitrate(self.single_video_path)
            new_bitrate = self.calculate_new_bitrate(original_bitrate, compression_level)
            new_bitrate_str = f"{new_bitrate}k"

            clip = VideoFileClip(self.single_video_path)
            # bitrate=new_bitrate,
            clip.write_videofile(
                filename= output_filepath,
                bitrate=new_bitrate_str,
                audio=True,
                preset=self.get_compression_preset(compression_level),
                codec="libx264",  # H.264 codec for MP4 files
                audio_codec="aac",  # AAC codec for audio
                threads=multiprocessing.cpu_count()  # Use the maximum number of threads available
            )
            messagebox.showinfo("Render", f"Video successfully rendered to {output_filepath} with {compression_level} compression.")
        else:
            messagebox.showwarning("Warning", "Please select a video file and an output directory!")

    def get_compression_preset(self, compression_level):
        if compression_level == 'Low':
            return 'veryfast'
        elif compression_level == 'Medium':
            return 'medium'
        else:
            return 'veryslow' 
        
    def get_bitrate(self, input_filepath):
        # Get the original video properties
        cap = cv2.VideoCapture(input_filepath)
        original_bitrate = int(cap.get(cv2.CAP_PROP_BITRATE))
        cap.release()
        return original_bitrate

    def calculate_new_bitrate(self, original_bitrate, compression_level):
        """
        Calculates the new bitrate based on the selected compression level.

        Args:
            original_bitrate (int): The original bitrate of the video.
            compression_level (str): The selected compression level ('Low', 'Medium', 'High').
        Returns:
            int: The new bitrate for the compressed video.
        """
        if compression_level == 'Low':
            return int(original_bitrate * 0.8)  # 80% of the original bitrate
        elif compression_level == 'Medium':
            return int(original_bitrate * 0.6)  # 60% of the original bitrate
        else:
            return int(original_bitrate * 0.4)  # 40% of the original bitrate

    
    def render_batch_videos(self):
        compression_level = self.compression_var.get()
        batch_directory = self.batch_dir.get()
        output_directory = self.output_dir.get()

        print(batch_directory, output_directory)
        if batch_directory and output_directory:
            messagebox.showinfo("Render", f"Rendering batch in {batch_directory} with {compression_level} compression to {output_directory}")

            # Loop through the files in the batch directory
            for file in os.listdir(batch_directory):
                print(file)
                # Check if the file is a video file
                if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    input_filepath = os.path.join(batch_directory, file)
                    input_basename = os.path.basename(input_filepath)
                    output_filename = os.path.splitext(input_basename)[0] + "_compressed.mp4"
                    output_filepath = os.path.join(output_directory, output_filename)

                    original_bitrate = self.get_bitrate(input_filepath)

                    new_bitrate = self.calculate_new_bitrate(original_bitrate, compression_level)
                    new_bitrate_str = f"{new_bitrate}k"

                    # Compress and render the video
                    clip = VideoFileClip(input_filepath)
                    clip.write_videofile(
                        filename=output_filepath,
                        bitrate=new_bitrate_str,
                        audio=True,
                        preset= self.get_compression_preset(compression_level),
                        codec="libx264",
                        audio_codec="aac",
                        threads=multiprocessing.cpu_count()
                    )

                    print(f"Rendered {input_basename} to {output_filename}")

            messagebox.showinfo("Render", f"Batch rendering complete.")
        else:
            messagebox.showwarning("Warning", "Please select a batch directory and an output directory!")

       

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Initialize the TkinterDnD window
    app = VideoCompressorApp(root)
    root.mainloop()
