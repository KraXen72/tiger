import tkinter as tk # for thumbnail gui
from PIL import ImageTk, Image, ImageOps
import tkinterDnD

thumb_mode = "center"
margin = 20 # margin from the side
wsize = 640 # window size
wbox = wsize - (2 * margin) # e.g. 600
current_pil_img = ""

current_image_path = ""
current_padding_color = (0, 0, 0)

instruct_image_h = 230

oob_hint = "(out of bounds) click on the image to pick padding color"

# utils
def setup_cropped_image(path):
    pil_img = Image.open(path)
    width, height = pil_img.size
    coefficient = wbox / width # get scale coefficient, for example 0.46 to scale image height also
    new_height = int(round(height * coefficient))
    pil_img = pil_img.resize((wbox, new_height))
    #print("image size: ", pil_img.size)

    global current_pil_img
    current_pil_img = pil_img

    thumb_photoimg = ImageTk.PhotoImage(pil_img)
    return thumb_photoimg, new_height

def get_ext(fn):
    return "." + fn.split(".")[-1]

# https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter#51592104
def _from_rgb(rgb):
    """
    translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb 

def _opposite_color(r,g,b):
    return (255 - r, 255 - g, 255 - b)

"""
creates a tkinter gui, then uses the arrow keys to select thumbnail mode. enter is submit
"""
def pick_thumb_mode(thumb_fullpath):
    global root
    root = tkinterDnD.Tk()
    root.title("Thumbnail to Album Art editor v2")

    global canvas
    canvas = tk.Canvas(root, width=wsize, height=wsize + instruct_image_h, borderwidth=0, highlightthickness=0, bg="white")

    global thumb_photoimg
    global new_height
    thumb_photoimg, new_height = setup_cropped_image(thumb_fullpath)

    global current_image_path
    current_image_path = thumb_fullpath # update the global path refrence

    global canvas_image
    canvas_image = canvas.create_image(wsize/2, wsize/2, image=thumb_photoimg)

    global top_offset
    global rsize
    rsize = new_height
    top_offset = ( wsize / 2 )-( new_height / 2 )

    global crop_rect
    startx = (wsize/2) - (rsize/2)
    crop_rect = canvas.create_rectangle(startx, top_offset, startx + rsize, rsize + top_offset, outline="black", width=5)

    # instructions 0.359375 is to get 230 px
    instruct_pil_img = Image.open("instructions.png")
    instruct_imagetk = ImageTk.PhotoImage(instruct_pil_img)
    canvas.create_image(wsize/2, (wsize + instruct_image_h) - (instruct_image_h / 2), image=instruct_imagetk)

    canvas.bind_all("<Left>", left)
    canvas.bind_all("<Down>", center)
    canvas.bind_all("<Up>", padded)
    canvas.bind_all("<Right>", right)
    canvas.bind_all("<Return>", submit)

    canvas.register_drop_target("*")
    canvas.bind("<<Drop>>", drop)

    canvas.bind('<Button-1>', click)
    canvas.bind("<Button-2>", right_click)
    canvas.bind("<Button-3>", right_click)

    canvas.pack()
    root.mainloop()

    global thumb_mode
    # print(">>> pick_thumb_mode is returning:", thumb_mode)
    return thumb_mode

# helper functions for the tkinter gui
def left(e):
    canvas.coords(crop_rect, margin, top_offset, rsize, rsize + top_offset)
    global thumb_mode
    thumb_mode = "left"

def center(e):
    startx = (wsize/2) - (rsize/2)
    canvas.coords(crop_rect, startx, top_offset, startx + rsize, rsize + top_offset)
    global thumb_mode
    thumb_mode = "center"

def right(e):
    startx = (wsize - margin) - rsize
    canvas.coords(crop_rect, startx, top_offset, startx + rsize, rsize + top_offset)
    global thumb_mode
    thumb_mode = "right"

def padded(e):
    canvas.coords(crop_rect, margin, margin, wsize-margin, wsize-margin)
    global thumb_mode
    thumb_mode = "padded"

def submit(e):
    global thumb_mode
    global root
    # print(thumb_mode)
    root.quit()
    root.destroy()

def drop(e):
    path = str(e.data)

    if path[0] == "{":
        path = path[1:]
    if path[-1] == "}":
        path = path[:-1]

    global thumb_mode
    print("loaded image: ", path)
    if ".jpg" in path or ".png" in path:
        global dropped_image # when an image is drag-n-dropped into the gui, update it
         
        global new_height
        dropped_image, new_height = setup_cropped_image(path) # this also updates new_height, which is used when calculating image offset
        # print(dropped_image) # tkinter PhotoImage

        # global thumb_photoimg
        # thumb_photoimg = dropped_image # update PIL image object so we can reference it when picking color
        # ^ is probably not needed since we only care about current_pil_img (PIL object)

        global current_image_path
        current_image_path = path # update the global path refrence according to the dropped image

        canvas.itemconfig(canvas_image, image=dropped_image)

def click(e):
    # set a custom padding color
    x, y = e.x, e.y
    img_top_offset = (wsize - new_height) / 2
    img_left_offset = (wsize - wbox) / 2
    print("offset (left, top): ", (img_left_offset, img_top_offset), x, y)

    img_x, img_y = int(round(x - img_left_offset)), int(round(y - img_top_offset))

    if img_x > 0 and img_y > 0:
        try:
            getpixel = current_pil_img.getpixel((img_x, img_y))
            # print("getpixel: ", getpixel)
            if len(getpixel) == 3:
                r,g,b = getpixel
            elif len(getpixel) == 4:
                r,g,b,alpha = getpixel
            # opposite_color = _opposite_color(r,g,b)
            # print("> picked: ", (r, g, b), "opposite: ", opposite_color)
            
            canvas.config(bg=_from_rgb((r,g,b)))
            # canvas.itemconfig(text1, fill=_from_rgb(opposite_color))
            # canvas.itemconfig(text2, fill=_from_rgb(opposite_color))
            # canvas.itemconfig(crop_rect, outline=_from_rgb(opposite_color))

            global current_padding_color
            current_padding_color = (r,g,b)
        except:
            print(oob_hint)
    else:
        print(oob_hint)
    
def right_click(e):
    # reset the custom padding color
    canvas.config(bg="white")
    # canvas.itemconfig(text1, fill="gray")
    # canvas.itemconfig(text2, fill="gray")

    global current_padding_color
    current_padding_color = (0, 0, 0)

"""
wrapper for pick_thumb_mode. calls it recursively if a new thumbnail is dropped in the gui
"""
def thumb_gui(thumb_fullpath):
    mode = pick_thumb_mode(thumb_fullpath)

    if ".png" in mode or ".jpg" in mode:
        return thumb_gui(mode)
    else:
        return mode

def crop_image(imgpath, mode, savepath):
    pil_img = Image.open(imgpath)
    print("> cropping image. size: ", pil_img.size)
    width, height = pil_img.size

    match mode:
        case "left":
            pil_img = pil_img.crop((0, 0, height, height))
        case "right":
            pil_img = pil_img.crop((width - height, 0, width, height))
        case "center":
            img_half = width / 2
            rect_half = height / 2
            pil_img = pil_img.crop((img_half - rect_half, 0, img_half + rect_half, height))
        case "padded":
            pil_img = ImageOps.pad(pil_img, (width, width), color=current_padding_color, centering=(0.5, 0.5))

    if not pil_img.mode == 'RGB':
        pil_img = pil_img.convert('RGB')
    
    if ".png" in savepath:
        savepath = savepath.replace(".png", ".jpg")

    # ensure png images are jpg
    current_image_path = savepath
    pil_img.save(savepath)
      

"""
use thumb_gui to defnitevly get mode and then crop latest image accordingly
"""
def thumb_gui_crop(thumb_fullpath):
    mode = thumb_gui(thumb_fullpath)
    print("> resulting cover mode is: ", mode)
    global root
    try:
        root.quit()
        root.destroy()
    except:
        pass
    crop_image(current_image_path, mode, "musicdl_assets\\out" + get_ext(current_image_path.split("\\")[-1])) 
    print("Focus / Go back to the terminal to continue")
    print()



if __name__=="__main__":
    thumb_fullpath = "musicdl_assets\\thumb[YBHxSFI_Q3Q].jpg"
    thumb_gui_crop(thumb_fullpath)
    # mode = thumb_gui(thumb_fullpath)
    # print("after exit the thing is:", mode)