"""Text injection utility for inserting transcribed text into active applications."""

import subprocess
import time
import os
import re


class TextInjector:
    """Injects text into the currently focused application."""
    
    def __init__(self):
        self.method = self._detect_display_server()
    
    def _detect_display_server(self):
        """Detect whether the system is using X11 or Wayland."""
        try:
            session_type = subprocess.check_output(
                ['echo', '$XDG_SESSION_TYPE'],
                shell=False
            ).decode().strip()
            
            # Try alternative method
            if not session_type or session_type == '$XDG_SESSION_TYPE':
                with open('/proc/self/environ', 'r') as f:
                    environ = f.read()
                    if 'wayland' in environ.lower():
                        return 'wayland'
                    else:
                        return 'x11'
            
            return session_type
        except:
            # Default to X11 if detection fails
            return 'x11'
    
    def inject_text(self, text, post_action=None):
        """
        Inject text into the currently focused application.
        
        Args:
            text (str): The text to inject
            post_action (str): Optional key action to perform after typing (e.g., 'ENTER')
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not text:
            print("No text to inject.")
            return False
        
        # Give a small delay to allow the user to focus the target window
        # (if they were focused on another window when triggering the shortcut)
        #time.sleep(0.1)
        
        try:
            if self.method == 'x11':
                success = self._inject_x11(text)
            else:
                # Wayland - use wtype or ydotool if available
                success = self._inject_wayland(text)
            
            # Execute post-action if specified and injection was successful
            if success and post_action:
                time.sleep(0.1)  # Small delay before key action
                self._execute_key_action(post_action)
            
            return success
        except Exception as e:
            print(f"Error injecting text: {e}")
            return False
    
    def _inject_x11(self, text):
        """Inject text using xdotool (X11)."""
        try:
            # Check if xdotool is installed
            subprocess.run(['which', 'xdotool'], check=True, capture_output=True)
            
            # Use xdotool to type the text
            subprocess.run(['xdotool', 'type', '--', text], check=True)
            print(f"Text injected successfully using xdotool.")
            return True
        except subprocess.CalledProcessError:
            print("Error: xdotool not found. Please install it: sudo apt install xdotool")
            return False
    
    def _inject_wayland(self, text):
        """Inject text using ydotool or wtype (Wayland)."""
        import os
        
        # Get the script directory to find local ydotool
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_ydotool = os.path.join(script_dir, 'ydotool')
        
        # Try local ydotool first
        if os.path.exists(local_ydotool) and os.access(local_ydotool, os.X_OK):
            try:
                subprocess.run([local_ydotool, 'type', text], check=True)
                print("Text injected successfully using local ydotool.")
                return True
            except subprocess.CalledProcessError:
                pass
        
        # Try system ydotool
        try:
            subprocess.run(['which', 'ydotool'], check=True, capture_output=True)
            subprocess.run(['ydotool', 'type', '--next-delay', '0', '--key-delay', '0', text], check=True)
            print("Text injected successfully using system ydotool.")
            return True
        except subprocess.CalledProcessError:
            pass
        
        # Try wtype as fallback
        try:
            subprocess.run(['which', 'wtype'], check=True, capture_output=True)
            subprocess.run(['wtype', text], check=True)
            print("Text injected successfully using wtype.")
            return True
        except subprocess.CalledProcessError:
            print("Error: Neither ydotool nor wtype found.")
            print("For Wayland, please run setup.sh to download ydotool.")
            return False
    
    def _execute_key_action(self, action):
        """
        Execute a key action (e.g., press ENTER).
        
        Args:
            action (str): Key action name (e.g., 'ENTER', 'TAB')
            
        Returns:
            bool: True if successful, False otherwise
        """
        from config import YDOTOOL_KEY_CODES
        
        # Get key code for the action
        key_code = YDOTOOL_KEY_CODES.get(action.upper())
        if not key_code:
            print(f"Unknown key action: {action}")
            return False
        
        print(f"Executing key action: {action}")
        
        try:
            if self.method == 'x11':
                return self._execute_key_action_x11(action)
            else:
                return self._execute_key_action_wayland(key_code)
        except Exception as e:
            print(f"Error executing key action: {e}")
            return False
    
    def _execute_key_action_x11(self, action):
        """Execute key action using xdotool (X11)."""
        try:
            # xdotool uses key names directly
            subprocess.run(['xdotool', 'key', action], check=True)
            print(f"Key action '{action}' executed successfully using xdotool.")
            return True
        except subprocess.CalledProcessError:
            print(f"Error: Failed to execute key action with xdotool")
            return False
    
    def _execute_key_action_wayland(self, key_code):
        """Execute key action using ydotool (Wayland)."""
        # Get the script directory to find local ydotool
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_ydotool = os.path.join(script_dir, 'ydotool')
        
        # Try local ydotool first
        if os.path.exists(local_ydotool) and os.access(local_ydotool, os.X_OK):
            try:
                subprocess.run([local_ydotool, 'key'] + key_code.split(), check=True)
                print(f"Key action executed successfully using local ydotool.")
                return True
            except subprocess.CalledProcessError:
                pass
        
        # Try system ydotool
        try:
            subprocess.run(['ydotool', 'key'] + key_code.split(), check=True)
            print(f"Key action executed successfully using system ydotool.")
            return True
        except subprocess.CalledProcessError:
            print("Error: Failed to execute key action with ydotool")
            return False
    
    def copy_to_clipboard(self, text):
        """
        Copy text to clipboard as a fallback method.
        
        Args:
            text (str): The text to copy
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try xclip for X11
            try:
                subprocess.run(['which', 'xclip'], check=True, capture_output=True)
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE
                )
                process.communicate(input=text.encode())
                print("Text copied to clipboard using xclip.")
                return True
            except subprocess.CalledProcessError:
                pass
            
            # Try wl-copy for Wayland
            try:
                subprocess.run(['which', 'wl-copy'], check=True, capture_output=True)
                process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
                process.communicate(input=text.encode())
                print("Text copied to clipboard using wl-copy.")
                return True
            except subprocess.CalledProcessError:
                pass
            
            print("Error: No clipboard utility found.")
            return False
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            return False


if __name__ == "__main__":
    # Test the text injector
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python text_injector.py <text_to_inject>")
        sys.exit(1)
    
    text = ' '.join(sys.argv[1:])
    injector = TextInjector()
    
    print(f"Detected display server: {injector.method}")
    print(f"Will inject text in 3 seconds. Focus your target application...")
    time.sleep(3)
    
    success = injector.inject_text(text)
    if not success:
        print("\nFalling back to clipboard...")
        injector.copy_to_clipboard(text)

