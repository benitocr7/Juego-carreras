import wave
import math
import struct
import random
import os

def generate_sound(filename, duration, freq_start, freq_end, volume=0.5, wave_type='sine'):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            
            # Frequency modulation
            if freq_start != freq_end:
                progress = i / n_samples
                freq = freq_start + (freq_end - freq_start) * progress
            else:
                freq = freq_start
                
            # Waveform generation
            if wave_type == 'sine':
                value = math.sin(2 * math.pi * freq * t)
            elif wave_type == 'noise':
                value = random.uniform(-1, 1)
            elif wave_type == 'square':
                value = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            elif wave_type == 'sawtooth':
                value = 2 * (t * freq - math.floor(t * freq + 0.5))
            else:
                value = 0
                
            # Envelope (Attack/Decay)
            if i < 1000: # Attack
                env = i / 1000
            elif i > n_samples - 1000: # Decay
                env = (n_samples - i) / 1000
            else:
                env = 1.0
                
            data = int(value * volume * env * 32767)
            wav_file.writeframes(struct.pack('<h', data))
            
    print(f"Generated {filename}")

if __name__ == "__main__":
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    # Crash: Noise, 0.5s, High to Low freq (simulated by noise filter?) No, just noise.
    generate_sound(os.path.join(assets_dir, "crash.wav"), 0.5, 100, 50, 0.8, 'noise')
    
    # Coin: Sine, 0.1s, 1000Hz to 1500Hz (Ding!)
    generate_sound(os.path.join(assets_dir, "coin.wav"), 0.1, 1000, 1500, 0.6, 'sine')
    
    # Turbo: Square, 1.0s, 200Hz to 600Hz (Rising engine)
    generate_sound(os.path.join(assets_dir, "turbo.wav"), 1.0, 200, 600, 0.5, 'square')
    
    # Near Miss: Sine, 0.15s, 800Hz rapid 
    generate_sound(os.path.join(assets_dir, "whoosh.wav"), 0.15, 600, 300, 0.7, 'noise') # Whoosh is more like filtered noise but noise will do
    
    print("All sounds generated.")
