from cx_Freeze import setup, Executable
import sys

buildOptions = dict(packages = ["tkinter", "pydle", "serial", "queue", "threading", "asyncio"],  # 1
	excludes = [])

exe = [Executable("twitchCraneUi.py")]  # 2

# 3
setup(
    name='Twitch Crane for DDOL3',
    version = '0.1',
    author = "Kyoungkyu Park",
    description = "Twitch Crane! Wow!",
    options = dict(build_exe = buildOptions),
    executables = exe
)
