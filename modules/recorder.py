import queue, threading, time, sounddevice as sd, webrtcvad, wave

vad = webrtcvad.Vad(2)
q = queue.Queue()

def _callback(indata, frames, time_info, status):
    q.put(bytes(indata))

def record_until_silence(filename='data/audio/answer.wav', sample_rate=16000, silence_sec=4):
    q.queue.clear()
    sd.default.samplerate = sample_rate
    sd.default.channels = 1
    stream = sd.InputStream(callback=_callback)
    stream.start()

    frames = []
    silent_chunks = 0
    chunk_duration = 30  # ms per chunk
    chunk_size = int(sample_rate * chunk_duration / 1000)

    while True:
        data = q.get()
        frames.append(data)
        # VAD expects raw 16-bit PCM
        if vad.is_speech(data, sample_rate):
            silent_chunks = 0
        else:
            silent_chunks += 1
            if silent_chunks * (chunk_duration/1000) >= silence_sec:
                break

    stream.stop()
    # Save WAV
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    return filename
