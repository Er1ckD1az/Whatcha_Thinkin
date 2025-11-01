import os
import json
from pathlib import Path

class EEGDataBridge:   
    def __init__(self, data_file='eeg_data.json'):
        self.data_file = Path(data_file)
        self.data = {
            'beta_power': 0,
            'gamma_power': 0,
            'is_game_running': False,
            'is_eeg_running': False
        }
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not self.data_file.exists():
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f)
    
    def update_eeg_data(self, beta_power, gamma_power):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            
            self.data['beta_power'] = beta_power
            self.data['gamma_power'] = gamma_power
            self.data['is_eeg_running'] = True
            
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f)
                
            return True
        except Exception as e:
            print(f"Error updating EEG data: {e}")
            return False
    
    def read_eeg_data(self):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            return self.data
        except Exception as e:
            print(f"Error reading EEG data: {e}")
            return self.data
    
    def set_game_status(self, is_running):
        try:
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
            
            self.data['is_game_running'] = is_running
            
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f)
                
            return True
        except Exception as e:
            print(f"Error updating game status: {e}")

            return False
