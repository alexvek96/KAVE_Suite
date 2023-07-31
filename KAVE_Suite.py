# import all the required libraries
# obviously, pip install anything you are missing...
from cryptography.fernet import Fernet
from tkinter import *
from PIL import ImageTk, Image
import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import os
import docx2txt
import textwrap

# function that acquires the name of a file from its path
def get_filename_from_path(file_path):
    return os.path.basename(file_path)

# function that acquires the name of a file without its extension, given the file in a file path
def get_filename_without_extension(file_path):
    filename, file_extension = os.path.splitext(file_path)
    return filename

# image using cv2.imshow() thus use this import
def messageToBinary(message):

    if type(message) == str:
        return ''.join([format(ord(i), "08b") for i in message])
    elif type(message) == bytes or type(message) == np.ndarray:
        return [format(i, "08b") for i in message]
    elif type(message) == int or type(message) == np.uint8:
        return format(message, "08b")
    else:
        raise TypeError("Input type not supported")

# Function to hide the secret message into the image
def hideData(image, secret_message):

    secret_message += "#####"  # you can use any string as the delimeter
    data_index = 0
    # convert input data to binary format using messageToBinary() function
    binary_secret_msg = messageToBinary(secret_message)

    data_len = len(binary_secret_msg)  # Find the length of data that needs to be hidden
    for values in image:
        for pixel in values:
            # convert RGB values to binary format
            r, g, b = messageToBinary(pixel)
            # modify the least significant bit only if there is still data to store
            if data_index < data_len:
                # hide the data into least significant bit of red pixel
                pixel[0] = int(r[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # hide the data into least significant bit of green pixel
                pixel[1] = int(g[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            if data_index < data_len:
                # hide the data into least significant bit of  blue pixel
                pixel[2] = int(b[:-1] + binary_secret_msg[data_index], 2)
                data_index += 1
            # if data is encoded, just break out of the loop
            if data_index >= data_len:
                break

    return image

# conversion function
def showData(image):

    binary_data = ""
    for values in image:
        for pixel in values:
            r, g, b = messageToBinary(pixel)  # convert the red,green and blue values into binary format
            binary_data += r[-1]  # extracting data from the least significant bit of red pixel
            binary_data += g[-1]  # extracting data from the least significant bit of red pixel
            binary_data += b[-1]  # extracting data from the least significant bit of red pixel
    # split by 8-bits
    all_bytes = [binary_data[i: i + 8] for i in range(0, len(binary_data), 8)]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "#####":  # check if we have reached the delimeter which is "#####"
            break

    return decoded_data[:-5]  # remove the delimeter to show the original hidden message

# function to create button for uploading your image
def button_Upload_1():
    newButton = tk.Button(window, text='Upload PNG image', command=encode_text).place(x=152, y=40)

# function to create button for uploading your image containing a hidden text
def button_Upload_2():
    newButton = tk.Button(window, text='Upload PNG image', command=decode_text).place(x=652, y=40)

# function to upload a .key file, to be able to decrypt the steganographed text in the image
def upload_key_file():
    global filename_of_key
    filename_of_key = filedialog.askopenfilename()
    k = Label(window, width=100).place(x=652, y=300)
    l = tk.Label(window, text="Chosen .key file: " + filename_of_key).place(x=652, y=300)

# function to print label in GUI window (encode section)
def print_label_1(name, img):
    l2 = tk.Label(window, text="Chosen image: " + " " + name).place(x=10, y=90)
    # this creates a new label to the GUI
    (a, b, c) = img.shape
    l3 = tk.Label(window, text="The dimensions of the image are: [" + str(a) + ", " + str(b) + ", " + str(c) + " ]").place(x=10, y=125)
    global total_encr_char_capacity
    total_encr_char_capacity = ((a * b * c * 3) // 8) - 5       # we have to keep in mind of the delimeter
    # total_encr_char_capacity indicates how many encrypted bytes we can hide in the image file
    l4 = tk.Label(window, text="Encrypted bytes capacity of the image: " + str(total_encr_char_capacity) + " Bs").place(x=10, y=150)

# function to print label in GUI window (decode section)
def print_label_2(name, img):

    l2 = tk.Label(window, text="Chosen image: " + name).place(x=650, y=90)
    # this creates a new label to the GUI
    (a, b, c) = img.shape
    l3 = tk.Label(window, text="The dimensions of the image are: [" + str(a) + ", " + str(b) + ", " + str(c) + " ]").place(x=650, y=120)

# function to print logo in GUI window
def print_logo(name):

    # Create a photoimage object of the logo in the path
    test = ImageTk.PhotoImage(name)
    label1 = tk.Label(image=test)
    label1.image = test
    # Position logo
    label1.place(x=1100, y=627)

# function to print image in GUI window (encode section)
def print_image_1(name):

    # Create a photoimage object of the image in the path
    test = ImageTk.PhotoImage(name)
    label1 = tk.Label(image=test)
    label1.image = test

    # Position image
    label1.place(x=400, y=50)

# function to print image in GUI window (decode section)
def print_image_2(name):

    # Create a photoimage object of the image in the path
    test = ImageTk.PhotoImage(name)
    label1 = tk.Label(image=test)
    label1.image = test

    # Position image
    label1.place(x=1050, y=50)

global user_text_to_hide
global text_to_hide

# function for the user to upload a file, from which we attain text data for encryption
def Upload_file():

    def finish_get_file():

        filename = text3.get()

        if (len(filename) == 0):
            er1 = Label(window, bg="red", text="  FAILURE!  ").place(x=380, y=603)
            er2 = Label(window, text="(Name your new file!)").place(x=450, y=603)
            raise ValueError('New file name is empty.')
        elif (os.path.exists('filekey.key') == 0):
            l5 = Label(window, width=35).place(x=380, y=603)
            Upload_file()
        old_name = key_file
        new_name = 'filekey_for_' + filename + '.key'
        os.rename(old_name, new_name)
        encoded_image_from_file = hideData(image, text_to_hide)  # call the hideData function to hide the secret message into the selected image
        cv2.imwrite(filename, encoded_image_from_file)
        l5 = Label(window, bg="lawn green", text="  SUCCESS! ").place(x=380, y=603)
        er3 = Label(window, text="                                                         ").place(x=450, y=603)

    # key generation
    global key
    key = Fernet.generate_key()
    global key_file
    key_file = 'filekey.key'
    # string the key in a file
    with open(key_file, 'wb') as filekey:
        filekey.write(key)

    # opening the key
    with open(key_file, 'rb') as filekey:
        key = filekey.read()

    # using the generated key
    global fernet
    fernet = Fernet(key)

    txt_data = UploadAction()
    l = tk.Label(window, text="Chosen file: " + txt_data).place(x=10, y=530)
    file_extension = os.path.splitext(txt_data)[1]
    # if-structure to handle .doc and .docx files
    if ( (file_extension == ".doc") or (file_extension == ".docx") ):

        text_to_hide = docx2txt.process(txt_data, os.getcwd())
        temp_text_to_hide = textwrap.fill(text_to_hide, 70)

        # opening the original file to encrypt
        with open('helper.txt', encoding='utf-8', mode='w') as file:
            file.write(temp_text_to_hide)
            file.close()
        with open('helper.txt', 'rb') as file:
            plain_text = file.read()
            # encrypting the file
            encrypted_text = fernet.encrypt(plain_text)
            text_to_hide = encrypted_text.decode()

        os.remove('helper.txt')

    else:
        messageToBinary(txt_data)
        with open(txt_data, 'rb') as f:
            plain_text = f.read()
            f.close()
            # encrypting the file
        encrypted_text = fernet.encrypt(plain_text)
        text_to_hide = encrypted_text.decode()

    if ((len(text_to_hide) <= total_encr_char_capacity) and ((file_extension == ".doc") or (file_extension == ".docx") or (file_extension == ".txt")) ):
        global text3
        text3 = StringVar()
        blank1 = Label(window, width=88).place(x=10, y=530)
        blank2 = Label(window, width=88).place(x=10, y=555)
        l = tk.Label(window, text="Chosen file: " + txt_data).place(x=10, y=530)
        e3 = Entry(window, width=50, textvariable=text3).place(x=300, y=557)
        l1 = Label(window, text="Name your new encrypted image (with extension): ").place(x=10, y=555)
        OK_Button = Button(window, width=10, text=' OK ', command=finish_get_file).place(x=285, y=600)
    else:
        blank1 = Label(window, width=88).place(x=10, y=530)
        blank2 = Label(window, width=88).place(x=10, y=555)
        l = tk.Label(window, text="Chosen file: " + txt_data).place(x=10, y=530)
        l2 = Label(window, bg='orange', text=" Error (!)").place(x=10, y=555)
        l3 = Label(window, text="Data size extends the image capacity or wrong input file format! Retry.").place(x=65, y=555)
    tk.mainloop()

# function to acquire data when user gives data through the keyboard
def get_text():

    def finish_get_text():

        h1 = text1.get()
        filename = text2.get()

        # opening the original file to encrypt
        with open('helper2.txt', encoding='utf-8', mode='w') as file:
            file.write(h1)
            file.close()
        with open('helper2.txt', 'rb') as file:
            plain_text = file.read()
            # encrypting the file
            encrypted_text = fernet.encrypt(plain_text)
            user_text_to_hide = encrypted_text.decode()

        os.remove('helper2.txt')


        if (len(h1) == 0):
            er1 = Label(window, bg="red", text="  FAILURE!  ").place(x=380, y=383)
            er2 = Label(window, text="(Data is empty! Retry.)").place(x=455, y=382)
            # delete previous key
            os.remove('filekey.key')
            # with same image, generate a new key
            get_text()
            raise ValueError('Data is empty.')
        elif (len(filename) == 0):
            er1 = Label(window, bg="red", text="  FAILURE!  ").place(x=380, y=383)
            er2 = Label(window, text="(Name your new file!)").place(x=455, y=382)
            # delete previous key
            os.remove('filekey.key')
            # with same image, generate a new key
            get_text()
            raise ValueError('File name is empty.')
        else:
            encoded_image = hideData(image, user_text_to_hide)  # call the hideData function to hide the secret message into the selected image
            cv2.imwrite(filename, encoded_image)
            old_name = key_file
            new_name = 'filekey_for_'+filename+'.key'
            os.rename(old_name, new_name)
            l5 = Label(window, bg="lawn green", text="  SUCCESS! ").place(x=380, y=383)
            er3 = Label(window, text="                                                         ").place(x=450, y=383)

    # key generation
    global key
    key = Fernet.generate_key()
    global key_file
    key_file = 'filekey.key'
    # string the key in a file
    with open(key_file, 'wb') as filekey:
        filekey.write(key)

    # opening the key
    with open(key_file, 'rb') as filekey:
        key = filekey.read()

    # using the generated key
    global fernet
    fernet = Fernet(key)

    global text1
    text1 = StringVar()
    e1 = Entry(window, width=80, textvariable=text1).place(x=118, y=310)
    l4 = Label(window, text="Insert text to hide: ").place(x=10, y=310)

    global text2
    text2 = StringVar()
    e2 = Entry(window, width=51, textvariable=text2).place(x=294, y=348)
    l5 = Label(window, text="Name your new encrypted image (with extension): ").place(x=10, y=348)
    OK_Button = Button(window, width=10, text=' OK ', command=finish_get_text).place(x=285, y=380)
    tk.mainloop()

# Encode data into image
def encode_text():

    image_name = UploadAction()
    global image
    image = cv2.imread(image_name)
    # Read the input image using OpenCV-Python.
    # It is a library of Python bindings designed to solve computer vision problems.
    print_label_1(image_name, image)
    img = Image.open(image_name)
    resized_image = img.resize((200, 200))
    print_image_1(resized_image)

    global Encode_text
    global Encode_txt_file
    Encode_text = Button(window, text="Encode text from user input", width=22, command=get_text).place(x=240, y=270)
    Encode_txt_file = Button(window, text="Encode text from text / word file", width=26, command=Upload_file).place(x=226, y=465)
    w.create_line(4, 435, 638, 435, dash=(4, 2))

# Decode the data in the image
def decode_text():

    global text

    def decrypt_image():

        text = showData(image)

        # creating a temporary file to write the encrypted text of the image
        with open('temp.txt', 'w') as f:
            f.write(text)
            f.close()

        # reading the encrypted text as binary
        with open('temp.txt', 'rb') as f:
            text_to_decrypt = f.read()
        os.remove('temp.txt')
        # initializing the decryption key the user uploaded
        with open(filename_of_key, 'rb') as v:
            decryption_key = Fernet(v.read())

        # decrypting the encrypted text and presenting it into a new text file
        image_filename = get_filename_from_path(image_path)
        raw_image_filename = get_filename_without_extension(image_filename)
        result_file_name = "result_of_image_" + raw_image_filename + ".txt"
        with open(result_file_name + ".txt", encoding='utf-8', mode='w') as j:
            result = decryption_key.decrypt(text_to_decrypt)
            res = result.decode('utf-8', 'ignore')
            j.write(res)

        path = os.getcwd()
        l6 = Label(window, bg="lawn green", text=" SUCCESS! ").place(x=750, y=402)
        l7 = Label(window, text="The hidden text is at:     " + path + "\\" + result_file_name).place(x=650, y=450)

    # read the image that contains the hidden text
    image_path = UploadAction()
    image = cv2.imread(image_path)
    # Read the input image using OpenCV-Python.
    # It is a library of Python bindings designed to solve computer vision problems.
    print_label_2(image_path, image)
    img = Image.open(image_path)
    resized_image = img.resize((200, 200))
    print_image_2(resized_image)
    Button1 = tk.Button(window, text='Upload .key file', command=upload_key_file).place(x=652, y=260)
    Button2 = tk.Button(window, text='Decrypt text', command=decrypt_image).place(x=652, y=400)
    tk.mainloop()

# function to upload your image through File Explorer
def UploadAction():
    filename = filedialog.askopenfilename()
    return filename

# function to close GUI
def close_window():
    window.destroy()
    exit()


# window object creation
window = Tk()

# window dimensions
window_height = 700
window_width = 1300

# get the screen dimension
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# find the center point of the screen
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2 - 40)

# set the position of the window to the center of the screen
window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# window logo
window.iconbitmap('eye.ico')

# fixed window size
window.resizable(0, 0)

# window title
window.title("KAVE Suite")

# Buttons and lines definition
w = Canvas(window, width=1300, height=700)
w.create_line(638, 0, 638, 650)
w.create_line(0, 35, 1300, 35)
w.pack()

b1 = Button(window, text="Encode text", width=15, command=button_Upload_1)
b1.place(x=150, y=5)
l1 = Label(window, text="Choose action:")
l1.place(x=30, y=7)
b2 = Button(window, text="Decode image", width=15, command=button_Upload_2)
b2.place(x=650, y=5)
b3 = Button(window, text="Exit", width=10, command=close_window)
b3.place(x=600, y=660)

logo_name = 'Logo Art.png'
logo = cv2.imread(logo_name)
# Read the input image using OpenCV-Python.
# It is a library of Python bindings designed to solve computer vision problems.
log = Image.open(logo_name)
resized_image = log.resize((200, 60))
print_logo(resized_image)

window.mainloop()