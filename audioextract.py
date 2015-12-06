#!/usr/bin/env python3
import sys
import signal
import os
from gi.repository import Gtk, GObject
import threading

# Function to extract the audio from all the files of a folder which is passed as parameter
def extractfromFolder(folder):
    for file in os.listdir(folder):
        if file.endswith(".mp4"):
            vid = file[:-4]
            from subprocess import call
            # Execute avconv -i file -acodec mp3 -vn file.mp3
            call(["avconv", "-i", folder+"/"+file, "-y", "-acodec", "mp3", "-vn", vid+".mp3"])

# Function to extract the audio from a specific file passed as parameter
def extractfromFile(video):
    from subprocess import call
    vid = video[:-4]
    # Execute avconv -i file -acodec mp3 -vn file.mp3
    call(["avconv", "-i", video, "-y", "-acodec", "mp3", "-vn", vid+".mp3"])

# Main window class
class MyWindow(Gtk.Window):
    # Global variables
    # jenga is for getting the name of the file/folder in on_file_selected/on_folder_selected and use it in on_run_clicked
    jenga = 0
    # f is to know which option has been chosen file/folder
    f = 0
    # t1 is to create a thread in on_run_clicked which would execute extractfromFolder or extractfromFile and to check if it is executing in on_timeout
    t1 = False
    # button is to set the sensitivity of the "Run" button to false when the conversion is executing, becoming true when it is finished
    button = 0

    # Function which initializes the gtk window and all the widgets
    def __init__(self):
        Gtk.Window.__init__(self, title="Extractipy")
        self.set_border_width(5)
        self.set_resizable(False)
        box = Gtk.Box(spacing=6)
        self.add(box)
        button1 = Gtk.Button("Choose File")
        button1.connect("clicked", self.on_file_clicked)
        box.add(button1)

        button2 = Gtk.Button("Choose Folder")
        button2.connect("clicked", self.on_folder_clicked)
        box.add(button2)

        global button
        button = Gtk.Button(label="Run")
        button.connect("clicked", self.on_run_clicked)
        box.add(button)
        self.progressbar = Gtk.ProgressBar()
        box.pack_start(self.progressbar, True, True, 0)

    # Function to select a file
    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        global f
        f = 0

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            global jenga
            jenga = dialog.get_filename()
            print("Folder selected: " + jenga)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    # Function to set the kind of files which are going to be selected in on_file_clicked
    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("mp4 files")
        filter_text.add_mime_type("video/mp4")
        dialog.add_filter(filter_text)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
    
    # Function to select a folder
    def on_folder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a folder", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        global f
        f = 1

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            global jenga
            jenga = dialog.get_filename()
            print("Folder selected: " + jenga)
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
    # Function to run the conversion
    def on_run_clicked(self, widget):
        global jenga
        global t1
        global f
        self.progressbar.set_fraction(0)
        self.progressbar.set_text(None)
        
        if f == 0 and jenga:
            t1 = threading.Thread(target=extractfromFile, args=(jenga,))
            t1.start()
                
            self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)
        elif f == 1 and jenga:
            t1 = threading.Thread(target=extractfromFolder, args=(jenga,))
            t1.start()
                
            self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)
        else:
            print ("Hello World")

    # Function to make the progressbar pulse while the conversion is performed. If so, it returns True so that it continues to get called
    def on_timeout(self, user_data):
        global button
        global t1
        if t1.isAlive():
            button.set_sensitive(False)
            self.progressbar.set_show_text(False)
            self.progressbar.pulse()
            return True
        else:
            button.set_sensitive(True)
            self.progressbar.set_fraction(1)
            self.progressbar.set_show_text(True)
            self.progressbar.set_text("Done, check your folder")
            return False

# Instance of the main window
win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
# Main loop
Gtk.main()
