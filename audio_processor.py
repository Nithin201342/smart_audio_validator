import librosa
import numpy as np

def analyze_audio(original_path, user_path):
    try:
        # 1. Load the audio files
        y_orig, sr_orig = librosa.load(original_path, sr=None)
        y_user, sr_user = librosa.load(user_path, sr=None)

        # Trim silence
        y_orig, _ = librosa.effects.trim(y_orig, top_db=30)
        y_user, _ = librosa.effects.trim(y_user, top_db=30)

        if len(y_orig) == 0 or len(y_user) == 0:
             return {"status": "error", "message": "Audio contains only silence."}

        # MODULE A: PITCH ACCURACY 
        chroma_orig = np.nan_to_num(librosa.feature.chroma_stft(y=y_orig, sr=sr_orig))
        chroma_user = np.nan_to_num(librosa.feature.chroma_stft(y=y_user, sr=sr_user))
        D_pitch, wp_pitch = librosa.sequence.dtw(X=chroma_orig, Y=chroma_user)
        pitch_score = (D_pitch[-1, -1] / len(wp_pitch)) * 100

        # MODULE B: RHYTHMIC TIMING 
        onset_orig = np.nan_to_num(librosa.onset.onset_strength(y=y_orig, sr=sr_orig)).reshape(1, -1)
        onset_user = np.nan_to_num(librosa.onset.onset_strength(y=y_user, sr=sr_user)).reshape(1, -1)
        D_rhythm, wp_rhythm = librosa.sequence.dtw(X=onset_orig, Y=onset_user)
        rhythm_score = (D_rhythm[-1, -1] / len(wp_rhythm)) * 100

        # MODULE C: COMPARATIVE ANALYSIS
        dur_orig = librosa.get_duration(y=y_orig, sr=sr_orig)
        dur_user = librosa.get_duration(y=y_user, sr=sr_user)
        dur_diff = dur_user - dur_orig

        if dur_diff > 2: pacing_diff = f"You sang noticeably slower, adding {abs(round(dur_diff, 1))} seconds."
        elif dur_diff < -2: pacing_diff = f"You rushed the performance, finishing {abs(round(dur_diff, 1))} seconds faster."
        else: pacing_diff = "Your overall pacing matched the original perfectly."

        rms_orig = librosa.feature.rms(y=y_orig)[0]
        rms_user = librosa.feature.rms(y=y_user)[0]
        var_orig = np.var(rms_orig / (np.max(rms_orig) + 1e-6))
        var_user = np.var(rms_user / (np.max(rms_user) + 1e-6))

        if var_user > var_orig * 1.5: energy_diff = "Your recording had heavy volume fluctuations."
        elif var_user < var_orig * 0.5: energy_diff = "Your recording lacked dynamic range (it was very flat)."
        else: energy_diff = "Your volume control and vocal dynamics closely mirrored the professional track."

        # ==========================================
        # MODULE D: THE "TROUBLE SPOT" LOCATOR
        # ==========================================
        # Calculate the absolute difference in pitch at every single aligned frame
        frame_differences = np.sum(np.abs(chroma_orig[:, wp_pitch[:, 0]] - chroma_user[:, wp_pitch[:, 1]]), axis=0)
        
        # Find the index of the worst mistake
        worst_step = np.argmax(frame_differences)
        worst_frame_in_original = wp_pitch[worst_step, 0]
        
        # Convert that specific frame back into a timestamp (seconds)
        trouble_time_sec = float(librosa.frames_to_time(worst_frame_in_original, sr=sr_orig))
        
        # Format it nicely for the UI (MM:SS)
        mins = int(trouble_time_sec // 60)
        secs = int(trouble_time_sec % 60)
        trouble_spot_formatted = f"{mins:02d}:{secs:02d}"

        # MODULE E: GRADING
        # Wrap the math in float() to prevent FastAPI JSON serialization errors
        pitch_score = float((D_pitch[-1, -1] / len(wp_pitch)) * 100)
        rhythm_score = float((D_rhythm[-1, -1] / len(wp_rhythm)) * 100)
        
        overall_score = round((pitch_score + rhythm_score) / 2, 2)
        pitch_score = round(pitch_score, 2)
        rhythm_score = round(rhythm_score, 2)

        if pitch_score < 15: pitch_tips = "Excellent pitch! You hit the notes perfectly."
        elif pitch_score < 30: pitch_tips = "Good pitch. A few wavering notes, but solid overall."
        elif pitch_score < 50: pitch_tips = "Average pitch. You are drifting off-key. Focus on breath support."
        else: pitch_tips = "Poor pitch. You are singing flat/sharp. Try practicing scales."

        if rhythm_score < 15: rhythm_tips = "Perfect timing! You are locked into the groove."
        elif rhythm_score < 30: rhythm_tips = "Good rhythm, but you rushed a few transitions."
        elif rhythm_score < 50: rhythm_tips = "Average timing. You are dragging behind the beat."
        else: rhythm_tips = "Poor timing. You are out of sync with the track."

        return {
            "status": "success",
            "overall_score": overall_score,
            "pitch_feedback": pitch_tips,
            "rhythm_feedback": rhythm_tips,
            "pacing_diff": pacing_diff,
            "energy_diff": energy_diff,
            "trouble_time_sec": trouble_time_sec,          # NEW: Raw seconds for the audio player
            "trouble_spot_formatted": trouble_spot_formatted # NEW: Formatted string for text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}