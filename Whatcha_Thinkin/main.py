import subprocess
import time
import os
import sys
import signal

def main():
    print("Starting EEG-controlled Game System")
    print("===================================")
    print("Two separate windows will open:")
    print("1. EEG visualization window")
    print("2. Game window")
    print("\nControls:")
    print("- Beta waves control horizontal movement")
    print("- Gamma waves control jumping")
    print("- Press TAB in game window to toggle between EEG/keyboard control")
    print("- Close either window to exit both programs")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    #Get the current directory where main.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    eeg_script = os.path.join(current_dir, 'modified_eeg_processing.py')
    game_script = os.path.join(current_dir, 'final_game', 'modified_game.py')
    
    #Verify if files exist
    if not os.path.exists(eeg_script):
        print(f"ERROR: {eeg_script} not found!")
        return
    if not os.path.exists(game_script):
        print(f"ERROR: {game_script} not found!")
        return
    
    print(f"Using EEG script: {eeg_script}")
    print(f"Using Game script: {game_script}")
    
    #Start both processes
    try:
        #Start the EEG processing
        eeg_process = subprocess.Popen([sys.executable, eeg_script])
        print("EEG visualization started (PID: {})".format(eeg_process.pid))
        
        #Wait a moment to ensure EEG processing has started
        time.sleep(2)
        
        #Start the game
        game_process = subprocess.Popen([sys.executable, game_script])
        print("Game started (PID: {})".format(game_process.pid))
        
        #Monitor processes
        while eeg_process.poll() is None and game_process.poll() is None:
            time.sleep(0.5)
        
        #If one process ends, terminate the other
        if eeg_process.poll() is not None:
            print("EEG processing stopped, terminating game...")
            if os.name == 'nt':  
                try:
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(game_process.pid)])
                except:
                    print(f"Could not terminate game process {game_process.pid}")
            else:  
                try:
                    os.kill(game_process.pid, signal.SIGTERM)
                except:
                    print(f"Could not terminate game process {game_process.pid}")
        
        if game_process.poll() is not None:
            print("Game stopped, terminating EEG processing...")
            if os.name == 'nt':  
                try:
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(eeg_process.pid)])
                except:
                    print(f"Could not terminate EEG process {eeg_process.pid}")
            else:  
                try:
                    os.kill(eeg_process.pid, signal.SIGTERM)
                except:
                    print(f"Could not terminate EEG process {eeg_process.pid}")
    
    except KeyboardInterrupt:
        print("\nTerminating all processes...")
        if 'eeg_process' in locals() and eeg_process.poll() is None:
            if os.name == 'nt':  
                try:
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(eeg_process.pid)])
                except:
                    pass
            else:  
                try:
                    os.kill(eeg_process.pid, signal.SIGTERM)
                except:
                    pass
        
        if 'game_process' in locals() and game_process.poll() is None:
            if os.name == 'nt':  
                try:
                    subprocess.call(['taskkill', '/F', '/T', '/PID', str(game_process.pid)])
                except:
                    pass
            else: 
                try:
                    os.kill(game_process.pid, signal.SIGTERM)
                except:
                    pass
    
    finally:
        print("Both programs terminated. Thanks for playing!")



main()
