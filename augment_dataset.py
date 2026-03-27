import librosa
import soundfile as sf
import numpy as np
import os

# Notice the 'r' placed directly before the quotation mark here
file_path = r"C:\Users\NIthin Mathew Thomas\Downloads\Poomuthole_Lyric_Video_Joseph_Malayalam_Movie_Ranjin_Raj_Joju_George_M_Padmakumar_256KBPS,Entam[...]\Chaiyya_Chaiyya_Full_Lyrical_Video_Dil_Se_Melody_Maker_-_A.R_Rahman_256kbps.wav"

def generate_test_samples(file_path):
    """
    Takes a perfect isolated vocal track and generates flawed versions 
    for testing an audio validation system.
    """
    if not os.path.exists(file_path):
        print(f"Error: Could not find the file at {file_path}.")
        print("Please double-check the path.")
        return

    print(f"Loading baseline track: {file_path}...")
    # Load the audio. sr=None preserves the original sample rate.
    try:
        y, sr = librosa.load(file_path, sr=None)
    except Exception as e:
        print(f"\nError taking to load the audio file: {e}")
        print("This usually happens when the audio file is not a valid WAV file (it could be an MP3 or WebM file renamed to .wav),")
        print("or if 'ffmpeg' is not installed on your system to decode other audio formats.")
        print("-> Please use an actual .wav file, or install ffmpeg to proceed.")
        return

    # ---------------------------------------------------------
    # 1. Generate the "Average" Recording
    # Flaw: Sings slightly flat and drags the beat a tiny bit.
    # ---------------------------------------------------------
    print("Generating 'Average' recording...")
    # Shift pitch down by 0.5 semitones
    y_avg_pitch = librosa.effects.pitch_shift(y, sr=sr, n_steps=-0.5)
    # Slow down tempo by 5% (rate < 1.0 slows it down)
    y_avg_final = librosa.effects.time_stretch(y_avg_pitch, rate=0.95)
    
    sf.write("sample_average.wav", y_avg_final, sr)
    print(" -> Saved sample_average.wav")

    # ---------------------------------------------------------
    # 2. Generate the "Terrible" Recording
    # Flaw: Sings completely off-key (sharp) and heavily rushes the beat.
    # ---------------------------------------------------------
    print("Generating 'Terrible' recording...")
    # Shift pitch up by 3 full semitones (very noticeable)
    y_bad_pitch = librosa.effects.pitch_shift(y, sr=sr, n_steps=3.0)
    # Speed up tempo by 15% (rate > 1.0 speeds it up)
    y_bad_final = librosa.effects.time_stretch(y_bad_pitch, rate=1.15)
    
    sf.write("sample_terrible.wav", y_bad_final, sr)
    print(" -> Saved sample_terrible.wav")

    print("\nDataset generation complete!")

if __name__ == "__main__":
    # Now we pass the variable from the top directly into the function
    generate_test_samples(file_path)