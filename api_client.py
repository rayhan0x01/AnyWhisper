"""API client for communicating with the Whisper transcription service."""

import requests
import json
from config import WHISPER_API_URL


class WhisperAPIClient:
    """Client for interacting with the Whisper API."""
    
    def __init__(self, api_url=None):
        self.api_url = api_url or WHISPER_API_URL
    
    def transcribe_audio(self, audio_file_path):
        """
        Send audio file to Whisper API for transcription.
        
        Args:
            audio_file_path (str): Path to the audio file to transcribe
            
        Returns:
            str: Transcribed text, or None if transcription failed
        """
        try:
            with open(audio_file_path, 'rb') as audio_file:
                files = {'file': audio_file}
                
                print(f"Sending audio to Whisper API at {self.api_url}...")
                response = requests.post(self.api_url, files=files, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get('text', '').strip()
                    print(f"Transcription received: {text}")
                    return text
                else:
                    print(f"API error: {response.status_code} - {response.text}")
                    return None
        
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to Whisper API. Is the Docker container running?")
            return None
        except requests.exceptions.Timeout:
            print("Error: Request to Whisper API timed out.")
            return None
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
    
    def check_api_health(self):
        """
        Check if the Whisper API is accessible.
        
        Returns:
            bool: True if API is accessible, False otherwise
        """
        try:
            # Try to connect to the API
            response = requests.get(self.api_url.rsplit('/', 1)[0], timeout=5)
            return True
        except:
            return False


if __name__ == "__main__":
    # Test the API client
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python api_client.py <audio_file_path>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    client = WhisperAPIClient()
    
    print("Checking API health...")
    if not client.check_api_health():
        print("Warning: Cannot reach Whisper API. Make sure Docker container is running.")
    
    text = client.transcribe_audio(audio_file)
    if text:
        print(f"\nTranscribed text:\n{text}")
    else:
        print("Transcription failed.")

