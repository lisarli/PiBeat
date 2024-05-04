#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import numpy as np


class RunMatrix(SampleBase):
    def __init__(self, matrixone, matrixtwo, *args, **kwargs):
        super(RunMatrix, self).__init__(*args, **kwargs)
        self.matrixone = matrixone
        self.matrixtwo = matrixtwo


    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        pos = offscreen_canvas.width

        while True:
            offscreen_canvas.Clear()
            pos += 1
            # Transfer text_matrix to the canvas
            
            for x in range(offscreen_canvas.width):
                for y in range(offscreen_canvas.height):
                    if pos % 2 == 0:
                        r, g, b = self.matrixone[x][y]
                    else:
                        r, g, b = self.matrixtwo[x][y]
                    offscreen_canvas.SetPixel(x, y, r, g, b)

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    # Create a 32x16 matrix for RGB LEDs
    led_matrix = np.zeros((32, 16, 3), dtype=np.uint8)

    # Draw a rectangle
    led_matrix[5:15, 5:11] = [255, 0, 0]  # Red

    # Draw a square
    led_matrix[17:22, 5:10] = [0, 255, 0]  # Green


    led_lights = np.zeros((32, 16, 3), dtype=np.uint8)

    # Draw triangles with cool colors
    for i in range(5, 16):  # Vertical position of triangles
        for j in range(5, 27, 2):  # Horizontal position of triangles
            r = np.random.randint(0, 128) + 128
            g = np.random.randint(128, 256)
            b = np.random.randint(128, 256)
            color = [r, g, b]  # Random cool color
            for k in range(0, 11):  # Height of triangle
                for l in range(j - k, j + k + 1):  # Width of triangle
                    if l >= 0 and l < 16:  # Check if within matrix bounds
                        led_lights[i + k, l] = color

    run_text = RunMatrix(led_matrix, led_lights)
    if (not run_text.process()):
        run_text.print_help()
