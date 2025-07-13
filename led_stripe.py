import machine, neopixel, time

# LED Matrix configuration
MATRIX_WIDTH = 8
MATRIX_HEIGHT = 32
LED_COUNT = MATRIX_WIDTH * MATRIX_HEIGHT  # 256 LEDs
LED_PIN = 5

# Initialize NeoPixel
np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

# 7x4 font for digits (0-9) and colon/dot - rotated 90 degrees for horizontal display
DIGIT_FONT = {
    '0': [
        [1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1],
        [1,0,0,0,0,0,1],
        [1,1,1,1,1,1,1]
    ],
    '1': [
        [0,0,0,0,0,0,0],
        [0,1,0,0,0,0,1],
        [1,1,1,1,1,1,1],
        [0,0,0,0,0,0,0]
    ],
    '2': [
        [1,0,0,1,1,1,1],
        [1,0,0,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,1,0,1,0,0,1]
    ],
    '3': [
        [1,0,0,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,1,1,1,1,1,1]
    ],
    '4': [
        [1,1,1,1,0,0,0],
        [0,0,0,1,0,0,0],
        [0,0,0,1,0,0,0],
        [1,1,1,1,1,1,1]
    ],
    '5': [
        [1,1,1,0,0,0,1],
        [1,0,0,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,0,1,1,1,1,1]
    ],
    '6': [
        [1,1,1,1,1,1,1],
        [1,0,0,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,0,0,1,1,1,1]
    ],
    '7': [
        [1,0,0,0,0,0,0],
        [1,0,0,0,0,0,0],
        [1,0,0,0,0,0,0],
        [1,1,1,1,1,1,1]
    ],
    '8': [
        [1,1,1,1,1,1,1],
        [1,0,0,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,1,1,1,1,1,1]
    ],
    '9': [
        [1,1,1,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,0,0,1,0,0,1],
        [1,1,1,1,1,1,1]
    ],
    ':': [
        [0,0,1,0,1,0,0]
    ],
    '.': [
        [0,0,0,0,0,0,1]
    ]
}

def xy_to_index(x, y):
    """Convert x,y coordinates to LED strip index for 8x32 matrix"""
    # Assuming serpentine wiring (zigzag pattern)
    if y % 2 == 0:  # Even rows go left to right
        return y * MATRIX_WIDTH + x
    else:  # Odd rows go right to left
        return y * MATRIX_WIDTH + (MATRIX_WIDTH - 1 - x)

def clear_matrix():
    """Clear the entire matrix"""
    for i in range(LED_COUNT):
        np[i] = OFF

def draw_char(char, start_x, start_y, color):
    """Draw a character at specified position"""
    if char not in DIGIT_FONT:
        return
    
    char_pattern = DIGIT_FONT[char]
    for y in range(len(char_pattern)):
        for x in range(len(char_pattern[y])):
            if char_pattern[y][x] == 1:
                pixel_x = start_x + x
                pixel_y = start_y + y
                if 0 <= pixel_x < MATRIX_WIDTH and 0 <= pixel_y < MATRIX_HEIGHT:
                    index = xy_to_index(pixel_x, pixel_y)
                    np[index] = color

def display_timer():
    """Main timer display function"""
    start_time = time.ticks_ms()
    
    while True:
        # Calculate elapsed time
        current_time = time.ticks_ms()
        elapsed_ms = time.ticks_diff(current_time, start_time)
        
        # Convert to minutes, seconds, and milliseconds
        total_seconds = elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = elapsed_ms % 1000  # Show full milliseconds (0-999)
        
        # Format time string MM:SS.nnn
        time_str = "{:02d}:{:02d}.{:03d}".format(minutes % 100, seconds, milliseconds)
        
        # Clear matrix
        clear_matrix()
        
        # Display horizontally using the 32-pixel height as width
        # Each digit is 4 pixels wide, separators are 1 pixel wide
        # Total: 4+4+1+4+4+1+4+4+4 = 30 pixels (fits in 32)
        y_pos = 1  # Start with 1 pixel margin
        
        for i, char in enumerate(time_str):
            if char == ':' or char == '.':
                draw_char(char, 1, y_pos, BLUE if char == ':' else GREEN)
                y_pos += 1  # 1 pixel width for separators
            else:
                draw_char(char, 1, y_pos, RED)
                y_pos += 4  # 4 pixels width for digits
        
        # Update display
        np.write()
        
        # Small delay to prevent excessive updates
        time.sleep_ms(50)

# Start the timer display
print("Starting LED Matrix Timer...")
display_timer()
