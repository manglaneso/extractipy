#!/usr/bin/env python3
import sys
import signal
import os
from gi.repository import Gtk, GObject
from subprocess import call
import threading
import ntpath

# Function to extract the audio from all the files of a folder which is passed as parameter
def extractfromFolder(folder):
    for file in os.listdir(folder):
        if file.endswith(".mp4"):
            vid = file[:-4]
            # Execute avconv -i file -acodec mp3 -vn file.mp3
            call(["avconv", "-i", folder+"/"+file, "-y", "-acodec", "mp3", "-vn", vid+".mp3"])

# Function to extract the audio from a specific file passed as parameter
def extractfromFile(video):
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

    filegrid = 0
    foldergrid = 0
    vbox = 0

    # Function which initializes the gtk window and all the widgets
    def __init__(self):
        global f
        global vbox
 
        f = 0
        label = 0
        Gtk.Window.__init__(self, title="Extractipy")
        self.set_border_width(5)
        self.set_resizable(False)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        hbox = Gtk.Box(spacing=6)
        self.add(vbox)
        vbox.add(hbox)

        button1 = Gtk.Button("Choose File")
        button1.connect("clicked", self.on_file_clicked)
        hbox.add(button1)

        button2 = Gtk.Button("Choose Folder")
        button2.connect("clicked", self.on_folder_clicked)
        hbox.add(button2)

        global button
        button = Gtk.Button(label="Run")
        button.connect("clicked", self.on_run_clicked)
        button.set_sensitive(False)
        hbox.add(button)

        self.progressbar = Gtk.ProgressBar()
        hbox.pack_start(self.progressbar, True, True, 0)

    # Function to select a file
    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        global f
        global foldergrid
        global filegrid
        global warninglabel
        f = 0

        if 'foldergrid' in globals():
            foldergrid.destroy()

        if 'filegrid' in globals():
            filegrid.destroy()

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            global jenga
            global button
            global vbox
            
            jenga = dialog.get_filename()
            filename = ntpath.basename(jenga)
            path = jenga[:-len(filename)]

            filegrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
            vbox.add(filegrid)
            label = Gtk.Label()
            label.set_markup("<b>File selected in " + path + ":</b>")
            l = Gtk.Label(filename)
            filegrid.add(label)
            filegrid.add(l)
            label.set_alignment(0, .5)
            l.set_alignment(0, .5)
            label.show()
            l.show()
            filegrid.show()

            button.set_sensitive(True)
            print("File selected: " + jenga)
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
        global foldergrid
        global filegrid
        f = 1

        if 'foldergrid' in globals():
            foldergrid.destroy()

        if 'filegrid' in globals():
            filegrid.destroy()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            global jenga
            global button
            global vbox
            jenga = dialog.get_filename()

            foldergrid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL)
            vbox.add(foldergrid)
            jenga = dialog.get_filename()
            label = Gtk.Label()
            label.set_markup("<b>Files selected in " + jenga + ":</b>")
            label.set_alignment(0, .5)
            foldergrid.add(label) 
            
            arefiles = 1
            for file in os.listdir(jenga):
                if file.endswith(".mp4"):
                    l = Gtk.Label(file)
                    l.set_alignment(0, .5)
                    foldergrid.add(l)
                    l.show()
                else:
                    l = Gtk.Label("Oops, no videos in here")
                    l.set_alignment(0, .5)
                    foldergrid.add(l)
                    l.show()
                    arefiles = 0
                    break

            if arefiles == 1:
                button.set_sensitive(True)
            label.show()
            foldergrid.show()


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
        if jenga:
            if f == 0:
                t1 = threading.Thread(target=extractfromFile, args=(jenga,))
                t1.start()
                    
                self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)
            elif f == 1:
                t1 = threading.Thread(target=extractfromFolder, args=(jenga,))
                t1.start()
                    
                self.timeout_id = GObject.timeout_add(50, self.on_timeout, None)
            else:
                # Error handling
                print("This is bad...")
        else:
            # Error handling
            print("This is bad...")


    # Function to make the progressbar pulse while the conversion is performed. If so, it returns True so that it continues to get called
    def on_timeout(self, user_data):
        global button
        global t1
        global f
        button.set_sensitive(False)
        
        if t1.isAlive():
            self.progressbar.set_show_text(False)
            self.progressbar.pulse()
            return True
        else:
            if f == 0:
                filegrid.destroy()
            elif f == 1:
                foldergrid.destroy()

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
