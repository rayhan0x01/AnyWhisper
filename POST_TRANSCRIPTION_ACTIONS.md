# Post-Transcription Actions

This feature allows you to automatically press keys after transcription based on patterns in your spoken text.

## How It Works

1. **Speak your text** with a trigger phrase (e.g., "send a message hit enter")
2. **Transcription happens** → "send a message hit enter"
3. **Pattern matching** → Detects "hit enter" at the end
4. **Text is cleaned** → "send a message" 
5. **Text is typed** → "send a message"
6. **Key is pressed** → ENTER key is sent

## Configuration

Edit `/path/to/AnyWhisper/config.py` to customize:

### ENABLE_TRANSCRIPTION_ACTIONS

Switch to enable/disable post-transcription actions:

```python
ENABLE_TRANSCRIPTION_ACTIONS = True  # Enable post-transcription action processing
```

When `False`, all post-transcription actions are disabled and text is typed as-is without any pattern matching or key pressing.

### POST_TRANSCRIPTION_OPT_DOT

Handle automatic periods that Whisper adds:

```python
POST_TRANSCRIPTION_OPT_DOT = True  # Automatically handle optional period at end
```

When `True`, patterns ending with `$` will also match an optional period.

**Example:**
- Pattern: `r'hit enter$'`
- With `OPT_DOT = True`: Matches both "hit enter" and "hit enter."
- With `OPT_DOT = False`: Only matches "hit enter"

This is useful because Whisper sometimes adds a period to complete sentences.

### POST_TRANSCRIPTION_ACTIONS

Map regex patterns to key actions:

```python
POST_TRANSCRIPTION_ACTIONS = {
    r'hit enter$': 'ENTER',        # Matches "hit enter" at end of text
    r'^enter$': 'ENTER',           # Matches only "enter" (entire text)
    r'press enter$': 'ENTER',      # Matches "press enter" at end
    r'new line$': 'ENTER',         # Matches "new line" at end
    r'hit tab$': 'TAB',            # Matches "hit tab" at end
    r'press tab$': 'TAB',          # Matches "press tab" at end
    r'hit escape$': 'ESCAPE',      # Matches "hit escape" at end
    r'press escape$': 'ESCAPE',    # Matches "press escape" at end
}
```

**Pattern syntax** (Python regex):
- `^` = Start of text
- `$` = End of text
- `.*` = Any characters
- Case-insensitive matching

### YDOTOOL_KEY_CODES

Map key names to ydotool/xdotool key codes:

```python
YDOTOOL_KEY_CODES = {
    'ENTER': '28:1 28:0',          # Enter key
    'ESCAPE': '1:1 1:0',           # Escape key
    'ESC': '1:1 1:0',              # Escape (alias)
    'TAB': '15:1 15:0',            # Tab key
    'BACKSPACE': '14:1 14:0',      # Backspace key
    'SPACE': '57:1 57:0',          # Space bar
    'UP': '103:1 103:0',           # Up arrow
    'DOWN': '108:1 108:0',         # Down arrow
    'LEFT': '105:1 105:0',         # Left arrow
    'RIGHT': '106:1 106:0',        # Right arrow
    'HOME': '102:1 102:0',         # Home key
    'END': '107:1 107:0',          # End key
    'PAGEUP': '104:1 104:0',       # Page Up
    'PAGEDOWN': '109:1 109:0',     # Page Down
    'DELETE': '111:1 111:0',       # Delete key
    'INSERT': '110:1 110:0',       # Insert key
}
```

**Format:** `keycode:1 keycode:0`
- `:1` = Key press
- `:0` = Key release

## Usage Examples

### Example 1: Send a Message
**Say:** "Hello, how are you doing today? hit enter"

**Transcription:** "Hello, how are you doing today? hit enter." (note the period)

**Result:**
- Pattern matches: `r'hit enter$'` (with optional period handling)
- Types: "Hello, how are you doing today?"
- Presses: ENTER

### Example 2: Navigate with Tab
**Say:** "username@example.com hit tab"

**Result:**
- Types: "username@example.com"
- Presses: TAB (moves to next field)

### Example 3: Just Press Enter
**Say:** "enter"

**Result:**
- Types: nothing (pattern matches entire text)
- Presses: ENTER

### Example 4: Multiple Words
**Say:** "create a new file called test.txt press enter"

**Result:**
- Types: "create a new file called test.txt"
- Presses: ENTER

### Example 5: Escape Dialogs
**Say:** "cancel hit escape"

**Result:**
- Types: "cancel"
- Presses: ESCAPE

## Adding Custom Actions

### Add a New Pattern

```python
POST_TRANSCRIPTION_ACTIONS = {
    # ... existing patterns ...
    r'send it$': 'ENTER',           # "send it" at end
    r'next field$': 'TAB',          # "next field" at end
    r'go back$': 'ESCAPE',          # "go back" at end
    r'delete this$': 'BACKSPACE',   # "delete this" at end
}
```

### Add a New Key Code

Find Linux input event codes in `/usr/include/linux/input-event-codes.h` or online.

```python
YDOTOOL_KEY_CODES = {
    # ... existing keys ...
    'F1': '59:1 59:0',         # F1 key
    'F2': '60:1 60:0',         # F2 key
    'CTRL': '29:1 29:0',       # Left Ctrl
    'ALT': '56:1 56:0',        # Left Alt
}
```

## Common Linux Input Event Codes

| Key | Code | ydotool Format |
|-----|------|----------------|
| ESC | 1 | `1:1 1:0` |
| 1-9 | 2-10 | `2:1 2:0` to `10:1 10:0` |
| 0 | 11 | `11:1 11:0` |
| BACKSPACE | 14 | `14:1 14:0` |
| TAB | 15 | `15:1 15:0` |
| Q-P | 16-25 | `16:1 16:0` to `25:1 25:0` |
| ENTER | 28 | `28:1 28:0` |
| CTRL | 29 | `29:1 29:0` |
| A-L | 30-38 | `30:1 30:0` to `38:1 38:0` |
| SHIFT | 42 | `42:1 42:0` |
| Z-M | 44-50 | `44:1 44:0` to `50:1 50:0` |
| SPACE | 57 | `57:1 57:0` |
| ALT | 56 | `56:1 56:0` |

## Troubleshooting

### Feature Not Working

**Problem:** Patterns don't seem to be working at all.

**Solution:**
1. Check if `ENABLE_TRANSCRIPTION_ACTIONS = True` in config.py
2. If disabled, enable it and restart daemon
3. Verify daemon restarted: `systemctl --user restart any-whisper`

### Pattern Not Matching

**Problem:** You say "hit enter" but nothing happens.

**Solution:** 
1. Check console output for transcription
2. Verify the exact transcription text (Whisper might add a period)
3. Make sure `POST_TRANSCRIPTION_OPT_DOT = True` (handles automatic periods)
4. Adjust regex pattern to match actual transcription
5. Remember: matching is case-insensitive

**Common Issue:** Whisper adds a period:
- Transcription: "hit enter." (with period)
- Pattern: `r'hit enter$'` 
- Solution: Enable `POST_TRANSCRIPTION_OPT_DOT = True` (default)

### Key Not Pressing

**Problem:** Text types correctly but key doesn't press.

**Solution:**
1. Check if key code is defined in `YDOTOOL_KEY_CODES`
2. Verify ydotoold is running: `pgrep ydotoold`
3. Test manually: `./ydotool key 28:1 28:0` (should press Enter)
4. Check console for error messages

### Wrong Key Pressed

**Problem:** Different key is pressed than expected.

**Solution:**
1. Verify the key code is correct
2. Test the key code manually with ydotool
3. Check `/usr/include/linux/input-event-codes.h` for correct codes

## Advanced Usage

### Multiple Patterns for Same Action

```python
POST_TRANSCRIPTION_ACTIONS = {
    r'hit enter$': 'ENTER',
    r'press enter$': 'ENTER',
    r'send it$': 'ENTER',
    r'submit$': 'ENTER',
    # All trigger ENTER key
}
```

### Patterns at Start or Anywhere

```python
POST_TRANSCRIPTION_ACTIONS = {
    r'^enter$': 'ENTER',           # Only "enter" (full match)
    r'.*hit enter$': 'ENTER',       # "hit enter" at end (explicit)
    r'hit enter': 'ENTER',          # "hit enter" anywhere
}
```

### Platform Support

- **Wayland:** Uses ydotool for key simulation
- **X11:** Uses xdotool for key simulation
- Key codes are automatically handled per platform

## Examples for VibeCoding

### Prompt Input

**Say:** "Center the div, make no mistakes hit enter"

**Result:**
```
Center the div, make no mistakes
[ENTER pressed - your AI agent starts working]
```

### Quick Searches

**Say:** "how to use numpy arrays press enter"

**Result:**
```
how to use numpy arrays
[ENTER pressed - search starts]
```

### Form Navigation

**Say:** "john.doe@example.com hit tab"

**Result:**
```
john.doe@example.com
[TAB pressed - moves to next field]
```

### File Creation

**Say:** "mkdir new_project press enter"

**Result:**
```
mkdir new_project
[ENTER pressed - directory created]
```

## Restart After Changes

After modifying `config.py`, restart the daemon:

```bash
# If running manually
Ctrl+C to stop
./start_daemon.sh

# If using systemd
systemctl --user restart any-whisper
```

