import queue
import sounddevice as sd
import webrtcvad
import wave

vad = webrtcvad.Vad(2)
q = queue.Queue()

def _callback(indata, frames, time_info, status):
    try:
        q.put(indata.tobytes())
    except Exception as e:
        print(f"[Recorder] Callback error: {e}")

def record_until_silence(filename='data/audio/answer.wav', sample_rate=16000, silence_sec=2, min_speech_sec=2):
    q.queue.clear()

    try:
        stream = sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype='int16',
            blocksize=480,  # 30ms at 16kHz
            callback=_callback
        )
        stream.start()
        print("[Recorder] Audio stream started.")

        frames = []
        silent_chunks = 0
        speaking_duration = 0
        chunk_duration = 30  # ms

        while True:
            try:
                data = q.get(timeout=10)
            except queue.Empty:
                print("[Recorder] No audio input received — mic may be muted or blocked.")
                break

            if len(data) != 960:  # 480 samples * 2 bytes = 960 bytes
                print("[Recorder] Skipping invalid chunk.")
                continue

            frames.append(data)

            if vad.is_speech(data, sample_rate):
                silent_chunks = 0
                speaking_duration += chunk_duration / 1000
            else:
                silent_chunks += 1
                if (silent_chunks * chunk_duration / 1000 >= silence_sec) and (speaking_duration >= min_speech_sec):
                    print("[Recorder] Silence detected. Stopping recording.")
                    break

        stream.stop()
        stream.close()
        print("[Recorder] Audio stream stopped.")

        if not frames:
            print("[Recorder] No valid audio recorded.")
            return filename

        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))
        wf.close()
        return filename

    except Exception as e:
        print(f"[Recorder] Failed to start recording: {e}")
        return filename
