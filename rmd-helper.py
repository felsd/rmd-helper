import os
import subprocess
from datetime import datetime
from pathlib import Path
from shutil import which
from threading import Thread

import click
import psutil

import wx

global c1, c2
c1 = None
c2 = None


class RectangleSelectionFrame(wx.Frame):
    def __init__(self, parent=None, id=wx.ID_ANY, title=""):
        wx.Frame.__init__(self, parent, id, title, size=wx.DisplaySize())
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.panel.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.panel.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyUp)
        self.panel.SetFocus()

        self.ShowFullScreen(True)
        self.SetTransparent(100)
        self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
        self.Show()

    def OnKeyUp(self, event):
        if event.KeyCode == wx.WXK_ESCAPE:
            self.Destroy()

    def OnMouseDown(self, event):
        global c1
        c1 = event.GetPosition()

    def OnMouseMove(self, event):
        if event.Dragging() and event.LeftIsDown():
            global c2
            c2 = event.GetPosition()
            self.Refresh()

    def OnMouseUp(self, event):
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.Destroy()

    def OnPaint(self, event):
        global c1, c2
        if c1 is None or c2 is None:
            return

        dc = wx.PaintDC(self.panel)
        dc.SetPen(wx.Pen("red", 1))
        dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0), wx.TRANSPARENT))

        dc.DrawRectangle(c1.x, c1.y, c2.x - c1.x, c2.y - c1.y)


class RecordMyDesktopHelper(wx.App):
    def OnInit(self):
        RectangleSelectionFrame()
        return True


def get_active_screen_offset():
    """Returns 0 if 1st screen is active, 1920 if 2nd screen is active"""
    active_window_info = (
        subprocess.check_output("xwininfo -id $(xdotool getactivewindow)", shell=True,)
        .decode("utf-8")
        .split("\n")
    )
    for line in active_window_info:
        if "Absolute upper-left X" in line:
            x = int(line.split(":")[1].strip())
            return 0 if x < 1920 else 1920
    raise Exception("Could not determine active screen")


def launch_and_notify(cmd):
    subprocess.call(cmd)
    subprocess.call(["notify-send", "RecordMyDesktop", "Recording finished"])


@click.command()
@click.option("--rect", is_flag=True, help="Select a rectangle for capture (default)")
@click.option("--screen", is_flag=True, help="Capture active screen")
def main(screen, rect):
    """Minimalistic wrapper for recordmydesktop that makes recording of the
    currently active screen or a region easier.
    Designed for single or dual monitor setup, with a resolution of 1920x1080.
    Execution while recordmydesktop is running will stop the current recording
    by sending SIGTERM."""
    if which("recordmydesktop") is None:
        raise Exception("recordmydesktop is not present")
    if "recordmydesktop" in [p.name() for p in psutil.process_iter()]:
        subprocess.call(["killall", "-s", "SIGTERM", "recordmydesktop"])
        os._exit(0)

    cmd = []
    if screen:
        cmd.append("recordmydesktop")
        if get_active_screen_offset() > 0:
            cmd.append("-x")
            cmd.append("1920")
        cmd.append("-width")
        cmd.append("1920")
        cmd.append("-height")
        cmd.append("1080")
    else:
        app = RecordMyDesktopHelper(redirect=False)
        app.MainLoop()
        if c1 is None or c2 is None:
            os._exit(0)
        cmd.append("recordmydesktop")
        cmd.append("-x")
        cmd.append(str(c1.x + get_active_screen_offset()))
        cmd.append("-y")
        cmd.append(str(c1.y))
        cmd.append("-width")
        cmd.append(str(abs(c2.x - c1.x)))
        cmd.append("-height")
        cmd.append(str(abs(c2.y - c1.y)))
    cmd.append("-o")
    cmd.append(
        os.path.join(
            str(Path.home()),
            f"recordmydesktop{datetime.now().strftime('_%Y-%m-%d_%H-%m-%S')}",
        )
    )
    thread = Thread(target=launch_and_notify, args=(cmd,))
    thread.start()
    thread.join()


if __name__ == "__main__":
    main()
