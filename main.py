import pyautogui
import time
import asyncio
import winrt.windows.media.control as media
import tkinter as tk
from tkinter import font as tkfont
import numpy as np
import soundfile as sf
import subprocess
import os
import keyboard

PAUSE_BUTTON = "space"

class Bluetooth():
    def __init__(self, root):
        self.root = root

        self.previous_session = None
        self.init_time = time.time()
        self.audio_process = None

        if not os.path.exists("audio.wav"):
            self.create_silent_audio("audio.wav")
        
        self.audio_process = subprocess.Popen(["start", "audio.wav"], shell=True)
        
        self.active = False

        self.bluetooth_icon = tk.PhotoImage(file="bluetooth-icon.png")
        self.toggle_button = tk.Button(self.root, image=self.bluetooth_icon, command=self.toggle)
        self.toggle_button.pack()

        self.root.after(100, self.bluetoothCheck)

        self.pause_button_var = tk.StringVar()
        self.pause_button_var.set(PAUSE_BUTTON)

        bold_font = tkfont.Font(family="Helvetica", size=12, weight="bold")
        self.pause_button_label = tk.Label(self.root, text=f"Pause button: {PAUSE_BUTTON}", font=bold_font)
        self.pause_button_label.pack()

        self.pause_button_label.bind("<Button-1>", self.edit_pause_button)
        self.pause_button_entry = None

    def toggle(self):
        self.active = not self.active
        self.update_button_state()

    def update_button_state(self):
        relief = "sunken" if self.active else "raised"
        self.toggle_button.config(relief=relief)

    def create_silent_audio(self, filename):
        sample_rate = 48000
        duration = 600
        num_samples = int(sample_rate * duration)
        silent_audio = np.zeros(num_samples, dtype=np.float32)

        sf.write(filename, silent_audio, sample_rate)

    def bluetoothCheck(self):
        current_time = time.time()
        
        if self.active and current_time - self.init_time > 0.5:
            asyncio.run(self.asyncBluetoothCheck())
            current_time = self.init_time

        self.root.after(100, self.bluetoothCheck)

    async def asyncBluetoothCheck(self):
        try:
            gs = media.GlobalSystemMediaTransportControlsSessionManager
            session_manager = await gs.request_async()
            current_session = session_manager.get_current_session()
            current_playback_status = current_session.get_playback_info().playback_status
                    
            if not self.previous_session:
                self.previous_session = current_playback_status
            else:
                if current_playback_status != self.previous_session:
                    self.previous_session = current_playback_status
                    pyautogui.hotkey("alt", "tab")
                    pyautogui.press(PAUSE_BUTTON)
                    pyautogui.hotkey("alt", "tab")
        except Exception as e:
            print(f"Error: {str(e)}")

    def edit_pause_button(self, event):
        self.pause_button_entry = tk.Entry(self.root, textvariable=self.pause_button_var)
        self.pause_button_entry.pack()
        self.pause_button_entry.bind("<Return>", self.update_pause_button)

        self.pause_button_entry.focus_set()
        self.pause_button_entry.icursor(tk.END)

        self.pause_button_label.pack_forget()

    def update_pause_button(self, event):
        new_pause_button = self.pause_button_var.get()

        global PAUSE_BUTTON
        try:
            keyboard.press_and_release(new_pause_button)

            self.pause_button_var.set(new_pause_button)
            PAUSE_BUTTON = self.pause_button_var.get()
        except Exception as e:
            self.pause_button_var.set("space")
            PAUSE_BUTTON = "space"

        self.pause_button_label.config(text=f"Pause button: {PAUSE_BUTTON}")
        self.pause_button_label.pack()

        if self.pause_button_entry:
            self.pause_button_entry.destroy()
            self.pause_button_entry = None

if __name__ == "__main__":
    root = tk.Tk()
    bluet = Bluetooth(root)
    root.mainloop()