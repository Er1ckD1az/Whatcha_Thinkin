import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy import signal
import time
from collections import deque

#Serial port configuration
PORT = 'COM3' 
BAUD_RATE = 115200

#Buffer size for analysis
BUFFER_SIZE = 512  
EEG_buffer = deque(maxlen=BUFFER_SIZE)
time_buffer = deque(maxlen=BUFFER_SIZE)

#Sampling parameters - 250Hz to match Arduino's
sampling_rate = 250 
nyquist = sampling_rate / 2

#Frequency bands (Hz)
beta_band = [13, 30]    #Beta waves
gamma_band = [30, 45]   #Gamma waves

#Initialize plots
plt.style.use('dark_background')
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8))
fig.suptitle('Real-time EEG Analysis', fontsize=16)

#Line objects
line_time = ax1.plot([], [], 'c-', lw=1)[0]
line_fft = ax2.plot([], [], 'g-', lw=1)[0]

#Bar chart - using rect objects instead of bar container
beta_bar = ax3.bar(['Beta'], [0], color=['cyan'])[0]
gamma_bar = ax3.bar(['Gamma'], [0], color=['magenta'])[0]

#Configure subplot layouts
ax1.set_title('EEG Time Domain')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Amplitude (μV)')
ax1.set_ylim(-100, 150)
ax1.grid(True, alpha=0.3)

ax2.set_title('Frequency Spectrum')
ax2.set_xlabel('Frequency (Hz)')
ax2.set_ylabel('Power')
ax2.set_xlim(0, 50)
ax2.set_ylim(0, 1500)
ax2.grid(True, alpha=0.3)

ax3.set_title('Brain Wave Power')
ax3.set_ylim(0, 1000)
ax3.grid(True, alpha=0.3)

def apply_bandpass_filter(data, lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return signal.filtfilt(b, a, data)

def compute_band_power(data, fft_result, freqs, low, high):
    indices = np.where((freqs >= low) & (freqs <= high))[0]
    return np.sum(np.abs(fft_result[indices])**2) / len(indices) if len(indices) > 0 else 0

def init():
    return line_time, line_fft, beta_bar, gamma_bar

#Update plots
def update(frame): 
    current_time = time.time()
    data = np.array(list(EEG_buffer))
    times = np.array(list(time_buffer)) - current_time
    
    if len(data) < BUFFER_SIZE/4:  #Wait for sufficient data
        return line_time, line_fft, beta_bar, gamma_bar
    
    #Update time domain plot
    line_time.set_data(times, data)
    ax1.set_xlim(min(times), max(times))
    
    #Apply additional bandpass filtering for analysis 
    filtered_beta = apply_bandpass_filter(data, beta_band[0], beta_band[1], sampling_rate)
    filtered_gamma = apply_bandpass_filter(data, gamma_band[0], gamma_band[1], sampling_rate)
    
    #Perform FFT
    n = len(data)
    fft_data = np.fft.rfft(data * np.hanning(n))
    freqs = np.fft.rfftfreq(n, d=1.0/sampling_rate)
    
    
    line_fft.set_data(freqs, np.abs(fft_data))    #Update frequency domain plot 
    
    #Calculate band powers
    beta_power = compute_band_power(filtered_beta, fft_data, freqs, beta_band[0], beta_band[1])
    gamma_power = compute_band_power(filtered_gamma, fft_data, freqs, gamma_band[0], gamma_band[1])
    
    #Update bar heights
    beta_bar.set_height(beta_power)
    gamma_bar.set_height(gamma_power)
    ax3.set_ylim(0, max(1000, beta_power * 1.2, gamma_power * 1.2))
    
    return line_time, line_fft, beta_bar, gamma_bar

def read_serial_data():
    try:
        with serial.Serial(PORT, BAUD_RATE) as ser:
            print(f"Connected to {PORT} at {BAUD_RATE} baud")
            ser.flushInput()
            time.sleep(2)
            
            while True:
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        #Check if it's the header line
                        if line == "raw,voltage,filtered":
                            continue
                            
                        #Parse data line
                        raw, voltage, filtered = map(float, line.split(','))
                        EEG_buffer.append(filtered)
                        time_buffer.append(time.time())
                        
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing data: {e}")
                time.sleep(0.001)  #Short delay to prevent CPU overload
                
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        return

if __name__ == "__main__":
    import threading
    
    #Start serial reading in background thread
    serial_thread = threading.Thread(target=read_serial_data, daemon=True)
    serial_thread.start()
    
    #Start animation
    ani = FuncAnimation(fig, update, init_func=init, 
                       interval=100, blit=True, cache_frame_data=False)
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)

    plt.show()

