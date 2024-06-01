from tkinter import filedialog
from convertors import (
    flac_to_mp3, flac_to_wav, flac_to_wma, mp3_to_flac,
    mp3_to_wav, mp3_to_wma, wav_to_flac, wav_to_mp3,
    wav_to_wma, wma_to_flac, wma_to_mp3, wma_to_wav
)

# Generic Function that runs all the audio convertors with same information #
def convert_audio_file(filetypes, conversion_function):
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select Audio File",
        filetypes=filetypes
    )
    if filename:
        conversion_function(filename)

# Function to convert FLAC to MP3 #
def convert_flac_to_mp3():
    convert_audio_file([("Audio files", "*.flac"), ("all files", "*.*")], flac_to_mp3.convert)

# Function to convert FLAC to WAV #
def convert_flac_to_wav():
    convert_audio_file([("Audio files", "*.flac"), ("all files", "*.*")], flac_to_wav.convert)

# Function to convert FLAC to WMA #
def convert_flac_to_wma():
    convert_audio_file([("Audio files", "*.flac"), ("all files", "*.*")], flac_to_wma.convert)

# Function to convert MP3 to FLAC #
def convert_mp3_to_flac():
    convert_audio_file([("Audio files", "*.mp3"), ("all files", "*.*")], mp3_to_flac.convert)

# Function to convert MP3 to WAV #
def convert_mp3_to_wav():
    convert_audio_file([("Audio files", "*.mp3"), ("all files", "*.*")], mp3_to_wav.convert)

# Function to convert MP3 to WMA #
def convert_mp3_to_wma():
    convert_audio_file([("Audio files", "*.mp3"), ("all files", "*.*")], mp3_to_wma.convert)

# Function to convert WAV to FLAC #
def convert_wav_to_flac():
    convert_audio_file([("Audio files", "*.wav"), ("all files", "*.*")], wav_to_flac.convert)

# Function to convert WAV to MP3 #
def convert_wav_to_mp3():
    convert_audio_file([("Audio files", "*.wav"), ("all files", "*.*")], wav_to_mp3.convert)

# Function to convert WAV to WMA #
def convert_wav_to_wma():
    convert_audio_file([("Audio files", "*.wav"), ("all files", "*.*")], wav_to_wma.convert)

# Function to convert WMA to FLAC #
def convert_wma_to_flac():
    convert_audio_file([("Audio files", "*.wma"), ("all files", "*.*")], wma_to_flac.convert)

# Function to convert WMA to MP3 #
def convert_wma_to_mp3():
    convert_audio_file([("Audio files", "*.wma"), ("all files", "*.*")], wma_to_mp3.convert)

# Function to convert WMA to WAV #
def convert_wma_to_wav():
    convert_audio_file([("Audio files", "*.wma"), ("all files", "*.*")], wma_to_wav.convert)