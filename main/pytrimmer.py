import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sv_ttk, os, subprocess, mpv, time

def get_video_duration(video_path):
    result = subprocess.run(['ffprobe', '-i', video_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    duration = float(result.stdout)
    return duration

def browse_video_file():
    video_file_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"),
                                                              ("MKV files", "*.mkv"),
                                                              ("AVI files", "*.avi"),
                                                              ("MOV files", "*.mov"),
                                                              ("FLV files", "*.flv"),
                                                              ("WMV files", "*.wmv"),
                                                              ("All files", "*.*")])
    if video_file_path:
        video_path_var.set(video_file_path)
        player.command('loadfile', video_file_path)
        player.loop_playlist = 'inf'
        global original_video_path
        original_video_path = video_file_path

def show_original():
    player.command('loadfile', original_video_path)
    player.loop_playlist = 'inf'

def show_output():
    output_file_path = "output" + os.path.splitext(os.path.basename(video_path_var.get()))[0] + os.path.splitext(video_path_var.get())[1]
    player.command('loadfile', output_file_path)
    player.loop_playlist = 'inf'


def cut_video():
    start_time = start_var.get()
    end_time = end_var.get()
    input_file = video_path_var.get()
    output_file = "output" + os.path.splitext(os.path.basename(input_file))[0] + os.path.splitext(input_file)[1]

    if start_time and end_time:
        cmd = ['ffmpeg']
        if cuda_checkbox_var.get():
            cmd += ['-hwaccel', 'cuda']
        elif vulkan_checkbox_var.get():
            cmd += ['-hwaccel', 'vulkan']
        cmd += ['-ss', start_time, '-i', input_file, '-to', end_time, '-c', 'copy', '-copyts', output_file]
        subprocess.run(cmd)

        player.command('loadfile', output_file)
        player.loop_playlist = 'inf'
        global cut_output_file_path
        cut_output_file_path = output_file
        #print(cmd)



def on_slider_move(event):
    global slider_moving
    canvas_item = event.widget.find_withtag(tk.CURRENT)[0]
    x = event.x
    if x < 0:
        x = 0
    elif x > canvas_width - 10:
        x = canvas_width - 10
    canvas.coords(canvas_item, x, 0, x + 10, canvas_height)
    start_pos = canvas.coords(slider1)[0] / (canvas_width - 10)
    end_pos = canvas.coords(slider2)[0] / (canvas_width - 10)
    start_var.set(round(video_duration * start_pos, 2))
    end_var.set(round(video_duration * end_pos, 2))


root = tk.Tk()
root.title("PyTrimmer")
root.geometry("500x500")

script_dir = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(script_dir, 'PyTrimmer.png')
icon = tk.PhotoImage(file=icon_path)
root.iconphoto(True, icon)


sv_ttk.set_theme("light")
button = ttk.Button(root, text="Toggle theme", command=sv_ttk.toggle_theme)
button.pack()

style = ttk.Style(root)
style.configure(".", font=("Helvetica", 12))

frame = ttk.Frame(root, padding=20)
frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

video_path_var = tk.StringVar()
start_var = tk.StringVar()
end_var = tk.StringVar()

# Define global variables for the checkboxes
global cuda_checkbox_var
global vulkan_checkbox_var

# Create frames for the checkboxes
cuda_frame = ttk.LabelFrame(frame, text='Hardware acceleration')
cuda_frame.grid(column=3, row=0, padx=10, pady=10)

vulkan_frame = ttk.LabelFrame(frame, text='Hardware acceleration')
vulkan_frame.grid(column=3, row=1, padx=10, pady=10)

# Create the CUDA checkbox
cuda_checkbox_var = tk.BooleanVar()
cuda_checkbox = ttk.Checkbutton(cuda_frame, text="CUDA", variable=cuda_checkbox_var)
cuda_checkbox.grid(column=0, row=0, sticky=tk.W)

# Create the Vulkan checkbox
vulkan_checkbox_var = tk.BooleanVar()
vulkan_checkbox = ttk.Checkbutton(vulkan_frame, text="Vulkan", variable=vulkan_checkbox_var)
vulkan_checkbox.grid(column=0, row=0, sticky=tk.W)


ttk.Label(frame, text="Video file:").grid(column=0, row=0, sticky=tk.W)
ttk.Entry(frame, textvariable=video_path_var).grid(column=1, row=0, sticky=(tk.W, tk.E))
ttk.Button(frame, text="Browse", command=browse_video_file).grid(column=2, row=0)

ttk.Label(frame, text="Start time (seconds):").grid(column=0, row=1, sticky=tk.W)
ttk.Entry(frame, textvariable=start_var).grid(column=1, row=1, sticky=(tk.W, tk.E))

ttk.Label(frame, text="End time (seconds):").grid(column=0, row=2, sticky=tk.W)
ttk.Entry(frame, textvariable=end_var).grid(column=1, row=2, sticky=(tk.W, tk.E))

ttk.Button(frame, text="Cut Video", command=cut_video).grid(column=1, row=3, pady=20)

ttk.Button(frame, text="Show Original", command=show_original).grid(column=2, row=3, pady=20)
ttk.Button(frame, text="Show Output", command=show_output).grid(column=0, row=3, pady=20)

# Add the video player
player_container = ttk.Frame(frame)
player_container.grid(column=0, row=4, columnspan=3, pady=20, sticky=(tk.W, tk.E, tk.N, tk.S))

player = mpv.MPV(wid=str(player_container.winfo_id()), osc=True, input_default_bindings=True, pause=False, keep_open=True, aspect=16/9)

def on_slider_move(event):
    global slider_moving

    # Get the current width of the canvas
    canvas_width = canvas.winfo_width()

    canvas_item = event.widget.find_withtag(tk.CURRENT)[0]
    x = event.x

    if x < 0:
        x = 0
    elif x > canvas_width - 10:
        x = canvas_width - 10

    canvas.coords(canvas_item, x, 0, x + 10, canvas_height)

    # Get the current positions of both sliders
    slider1_pos = canvas.coords(slider1)[0]
    slider2_pos = canvas.coords(slider2)[0]

    start_pos = slider1_pos / (canvas_width - 10)
    end_pos = slider2_pos / (canvas_width - 10)

    start_var.set(round(video_duration * start_pos, 2))
    end_var.set(round(video_duration * end_pos, 2))

def resize_canvas(event):
    # Get the current width of the window
    window_width = event.width

    global end_width
    end_width = root.winfo_width()
    #print(" Resize Window width:", end_width)

    if(root.winfo_width() == 1):
        canvas_width = 460

    # Set the new width and height of the canvas
    canvas.config(width=window_width, height=canvas_height)

    # Set the new position of slider1 based on the new canvas width
    slider1_width = int(window_width * 0.01)
    slider2_width = int(end_width*0.90)
    canvas.coords(slider1, slider1_width, 0, slider1_width + 10, canvas_height)
    canvas.coords(slider2, slider2_width - 10, 0, slider2_width, canvas_height)
    #print(" Slider2 width", slider2_width)

# Add the custom dual-slider
video_duration = 100  # Replace with actual video duration
canvas_height = 20

canvas_frame = ttk.Frame(frame)
canvas_frame.grid(column=0, row=5, columnspan=9, pady=(10, 20), sticky=(tk.W, tk.E))

canvas = tk.Canvas(canvas_frame, height=canvas_height, bg='white')
canvas.pack(fill=tk.BOTH, expand=True)

global end_width

if(root.winfo_width() != 1):
    canvas_width = end_width
    #print(canvas_width)
else:
    canvas_width = 710

slider1_width = int(root.winfo_width() * 0.01)
slider2_width = int(canvas_width)
#print(slider2_width)
slider1 = canvas.create_rectangle(slider1_width, 0, slider1_width + 10, canvas_height, fill='blue')
slider2 = canvas.create_rectangle(slider2_width - 10, 0, slider2_width, canvas_height, fill='blue')

canvas.tag_bind(slider1, '<B1-Motion>', on_slider_move)
canvas.tag_bind(slider2, '<B1-Motion>', on_slider_move)

# Configure the row containing the canvas to have a fixed height
canvas_frame.rowconfigure(0, weight=1, minsize=canvas_height)

# Bind the resize_canvas function to the <Configure> event of the root window
root.bind('<Configure>', resize_canvas)

frame.columnconfigure(1, weight=1)
frame.rowconfigure(4, weight=1)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

root.mainloop()
