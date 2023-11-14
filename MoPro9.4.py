import wx
import os
import sys
import shutil
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64

class LogTextHandler(logging.Handler):
    def __init__(self, log_text_ctrl):
        logging.Handler.__init__(self)
        self.log_text_ctrl = log_text_ctrl

    def emit(self, record):
        log_message = self.format(record)
        wx.CallAfter(self.log_text_ctrl.AppendText, log_message + '\n')

class FolderManagementApp(wx.Frame):
    def __init__(self, parent, title):
        super(FolderManagementApp, self).__init__(parent, title=title, size=(800, 600))

        # Create the main panel
        self.panel = wx.Panel(self)

        # Create a border sizer for the app window
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        border_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add extra spacing after the border
        border_sizer.AddSpacer(5)

        # Create a nested sizer inside the border sizer
        nested_sizer = wx.BoxSizer(wx.VERTICAL)
        nested_sizer.Add(self.panel, 1, wx.EXPAND)  # Add the panel to the nested sizer

        # Add the nested sizer to the border sizer
        border_sizer.Add(nested_sizer, 1, wx.EXPAND)

        # Add the border sizer to the main sizer
        main_sizer.Add(border_sizer, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        # Create the log text control
        self.log_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.log_text.SetMinSize((600, 200))  # Set the size of the log text control

        # Create the log handler to redirect logging output to the log text control
        log_handler = LogTextHandler(self.log_text)
        log_handler.setLevel(logging.DEBUG)  # Set the log level
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(log_formatter)

        # Create a logger and add the log handler
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(log_handler)

        # Create the widgets
        new_path_label = wx.StaticText(self.panel, label="  New Path:")
        self.new_path_entry = wx.TextCtrl(self.panel)
        browse_new_path_button = wx.Button(self.panel, label="Browse")
        browse_new_path_button.Bind(wx.EVT_BUTTON, self.on_browse_new_path)

        copy_folders_button = wx.Button(self.panel, label="Copy Folders")
        copy_folders_button.Bind(wx.EVT_BUTTON, self.on_copy_folders)
        self.override = wx.CheckBox(self.panel, label="Override")

        folders_label = wx.StaticText(self.panel, label="  Selected Folders:")
        self.folders_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.HSCROLL)
        browse_folders_button = wx.Button(self.panel, label="Browse")
        browse_folders_button.Bind(wx.EVT_BUTTON, self.on_browse_folders)

        files_label = wx.StaticText(self.panel, label="  Selected Files:")
        self.files_text = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.HSCROLL)
        import_from_file_button = wx.Button(self.panel, label="Import from File")
        import_from_file_button.Bind(wx.EVT_BUTTON, self.on_import_from_file)

        self.progress_bar = wx.Gauge(self.panel)

        self.delete_source = wx.CheckBox(self.panel, label="Delete source after copy")
        self.skip_existing = wx.CheckBox(self.panel, label="Skipping Existing Files")
        self.skip_errors = wx.CheckBox(self.panel, label="Error Handling - Skip Errors")
        self.force_copy = wx.CheckBox(self.panel, label="Force Copy (Overwrite files)")

        clear_button = wx.Button(self.panel, label="Clear")
        clear_button.Bind(wx.EVT_BUTTON, self.on_clear_inputs)

        # Create the sizer and add the widgets
        sizer = wx.GridBagSizer(5, 5)
        sizer.Add(new_path_label, pos=(0, 0), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.new_path_entry, pos=(0, 1), span=(1, 2), flag=wx.EXPAND)
        sizer.Add(browse_new_path_button, pos=(0, 3), flag=wx.ALIGN_RIGHT)

        sizer.Add(copy_folders_button, pos=(1, 0), flag=wx.EXPAND)
        sizer.Add(self.override, pos=(1, 1), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.force_copy, pos=(1, 2), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(folders_label, pos=(2, 0), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.folders_text, pos=(2, 1), span=(1, 3), flag=wx.EXPAND)
        sizer.Add(browse_folders_button, pos=(2, 4), flag=wx.ALIGN_RIGHT)

        sizer.Add(files_label, pos=(3, 0), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.files_text, pos=(3, 1), span=(1, 3), flag=wx.EXPAND)
        sizer.Add(import_from_file_button, pos=(3, 4), flag=wx.ALIGN_RIGHT)

        sizer.Add(self.progress_bar, pos=(4, 0), span=(1, 5), flag=wx.EXPAND)

        sizer.Add(self.delete_source, pos=(5, 0), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.skip_existing, pos=(6, 0), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.skip_errors, pos=(7, 0), flag=wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(clear_button, pos=(8, 0), span=(1, 5), flag=wx.ALIGN_RIGHT)

        sizer.Add(self.log_text, pos=(9, 0), span=(1, 5), flag=wx.EXPAND)

        self.panel.SetSizerAndFit(sizer)

        # Set the icon for the application
        icon_data = """
            iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAIAAAD8GO2jAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJ
            TUUH5AoNEAEdGDzL2wAAAI9JREFUWMPt1zEKwkAMhC8z9P/AiyeKbWj5dCt6t/fN2i+9cdl0Lgr/Z
            7QwwvnWUh/MATGcMbCTYxRo4bCMZg/1Xo4iV2++zuA0AsQpyWBfWqCCEmUKMMFJLWMlU1EpJoDTCJ
            KNFguzk6CPE6WIgDBdW7mIKNRNSaGcZFI0UxYjiRQl2nJFLTYaLQQMcRRqJLBshgWpykS02LckDdF
            g+FQjCRSUgMkYhmcoiRwP0maTMmRKIoqQd0DIQUibIUNmkkihoyT9RQQ2DKMNCCCAjKkgMCxkkgqA
            BJrckS0AJBElyRDQhNNA
            """
        icon_data = base64.b64decode(icon_data)
        with open("MO_LOGO.png", "wb") as icon_file:
            icon_file.write(icon_data)

        icon_path = "MO_LOGO.png"
        icon = wx.Icon(icon_path, wx.BITMAP_TYPE_PNG)
        wx.Frame.SetIcon(self, icon)

        # Show the frame
        self.Show()


    def on_browse_new_path(self, event):
        dlg = wx.DirDialog(self, "Select Destination Path")
        if dlg.ShowModal() == wx.ID_OK:
            self.new_path_entry.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_browse_folders(self, event):
        dlg = wx.DirDialog(self, "Select Folder Path")
        if dlg.ShowModal() == wx.ID_OK:
            self.folders_text.AppendText(dlg.GetPath() + '\n')
        dlg.Destroy()

    def on_import_from_file(self, event):
        wildcard = "Text Files (*.txt)|*.txt"
        dlg = wx.FileDialog(self, "Select Text File", wildcard=wildcard, style=wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            file_path = dlg.GetPath()
            with open(file_path, "r") as file:
                lines = file.readlines()
                for line in lines:
                    line = line.strip()
                    if line:
                        if line.endswith(".txt") or line.endswith(".doc") or line.endswith(".pdf"):
                            self.files_text.AppendText(line + '\n')
                        else:
                            self.folders_text.AppendText(line + '\n')
        dlg.Destroy()

    def copy_files_recursive(self, src, dst, skip_existing=False, skip_errors=False, force_copy=False):
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            item_path = os.path.join(src, item)
            dst_item_path = os.path.join(dst, item)
            try:
                if os.path.isfile(item_path):
                    if skip_existing and os.path.exists(dst_item_path) and not force_copy:
                        self.logger.debug(f"Skipped copying file: {item_path}")
                        continue
                    if not os.path.exists(dst_item_path) or force_copy:
                        try:
                            shutil.copy2(item_path, dst_item_path, follow_symlinks=True)
                            self.logger.debug(f"Copied file: {item_path} to {dst_item_path}")
                        except shutil.Error as e:
                            logging.error(f"Error copying file: {item_path} - {e}", exc_info=True)
                            if not skip_errors:
                                wx.MessageBox(f"Error copying file: {item_path} - {e}", "Error", wx.OK | wx.ICON_ERROR)
                elif os.path.isdir(item_path):
                    new_dst_folder_path = os.path.join(dst, item)
                    self.copy_files_recursive(item_path, new_dst_folder_path, skip_existing, skip_errors, force_copy)
            except OSError as e:
                logging.error(f"Error copying file or folder: {item_path} - {e}", exc_info=True)
                if not skip_errors:
                    wx.MessageBox(f"Error copying file or folder: {item_path} - {e}", "Error", wx.OK | wx.ICON_ERROR)

    def are_all_files_exist(self, src, dst):
        src_files = set(str(file.relative_to(src)) for file in Path(src).rglob("*") if file.is_file())
        dst_files = set(str(file.relative_to(dst)) for file in Path(dst).rglob("*") if file.is_file())
        return src_files.issubset(dst_files)

    def on_clear_inputs(self, event):
        self.new_path_entry.Clear()
        self.folders_text.Clear()
        self.files_text.Clear()
        self.override.SetValue(False)
        self.skip_existing.SetValue(False)
        self.skip_errors.SetValue(False)
        self.delete_source.SetValue(False)
        self.force_copy.SetValue(False)

    def on_copy_folders(self, event):
        selected_folders = self.folders_text.GetValue().split('\n')
        destination_path = self.new_path_entry.GetValue()
        num_folders = len(selected_folders)

        self.progress_bar.SetRange(num_folders)
        self.progress_bar.SetValue(0)

        skip_existing = self.skip_existing.GetValue()
        skip_errors = self.skip_errors.GetValue()
        force_copy = self.force_copy.GetValue()

        for i, folder_path in enumerate(selected_folders, start=1):
            if folder_path and os.path.exists(folder_path):
                folder_name = os.path.basename(folder_path)
                parent_folder_name = os.path.basename(os.path.dirname(folder_path))
                new_folder_path = os.path.join(destination_path, parent_folder_name, folder_name)

                try:
                    if os.path.exists(new_folder_path):
                        if skip_existing:
                            if self.are_all_files_exist(folder_path, new_folder_path):
                                self.logger.debug(f"Skipped copying folder: {folder_path}")
                                continue

                    self.copy_files_recursive(folder_path, new_folder_path, skip_existing, skip_errors, force_copy)

                    if self.delete_source.GetValue():
                        shutil.rmtree(folder_path)

                    self.logger.debug(f"Copied folder: {folder_path} to {new_folder_path}")

                except shutil.Error as e:
                    logging.error(f"Error copying folder: {e}", exc_info=True)
                    if not skip_errors:
                        wx.MessageBox(f"Error copying folder: {e}", "Error", wx.OK | wx.ICON_ERROR)

            self.progress_bar.SetValue(i)

        wx.MessageBox("Folders copied successfully!")

app = wx.App()
FolderManagementApp(None, title="MOAZ Folder Management")
app.MainLoop()


app = wx.App()
FolderManagementApp(None, title="MOAZ Folder Management")
app.MainLoop()
