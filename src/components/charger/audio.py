import pyaudio
import wave

import os

# Determine the directory of the script
dir_path = os.path.dirname(os.path.realpath(__file__))
charging_completed_file = os.path.join(dir_path, "audio_files/charging_completed.wav")
charging_started_file = os.path.join(dir_path, "audio_files/charging_started.wav")


# Set chunk size of 1024 samples per data frame
chunk = 1024


def play_sound(filename):
    # Open the sound file
    wf = wave.open(filename, "rb")

    # Create an interface to PortAudio
    p = pyaudio.PyAudio()

    # Open a .Stream object to write the WAV file to
    # 'output = True' indicates that the sound will be played rather than recorded
    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
    )

    # Read data in chunks
    data = wf.readframes(chunk)

    # Play the sound by writing the audio data to the stream
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(chunk)

    # Close and terminate the stream
    stream.close()
    p.terminate()


def play_charging_completed_sound():
    play_sound(charging_completed_file)


def play_charging_started_sound():
    play_sound(charging_started_file)
