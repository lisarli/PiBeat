#!/usr/bin/env python
# Display a runtext with double-buffering.
from samplebase import SampleBase
from rgbmatrix import graphics
import time


class RunText(SampleBase):
    def __init__(self, matrix, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.text_matrix = matrix

    def run(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        pos = offscreen_canvas.width

        while True:
            offscreen_canvas.Clear()
            pos += 1
            # Transfer text_matrix to the canvas
            for x in range(offscreen_canvas.width):
                for y in range(offscreen_canvas.height):
                  r, g, b = self.text_matrix[x][y]
                  offscreen_canvas.SetPixel(x, y, r, g, b)

            time.sleep(0.05)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    cooler_flower_matrix = [
        [(0, 0, 0)] * 16 for _ in range(32)
    ]

    # Petals
    for i in range(4, 28):
        for j in range(6, 14):
            if ((i - 16) ** 2 + (j - 10) ** 2 <= 50) or ((i - 16) ** 2 + (j - 12) ** 2 <= 50):
                cooler_flower_matrix[i][j] = (255, 204, 255)  # Light Purple

    # Inner circle
    for i in range(11, 21):
        for j in range(10, 14):
            if (i - 16) ** 2 + (j - 12) ** 2 <= 16:
                cooler_flower_matrix[i][j] = (255, 255, 0)  # Yellow

    # Stem
    for i in range(20, 28):
        for j in range(12, 14):
            cooler_flower_matrix[i][j] = (0, 255, 0)  # Green

    # Additional decorations (optional)
    # Leaves
    for i in range(5, 9):
        for j in range(5, 9):
            cooler_flower_matrix[i][j] = (0, 153, 0)  # Dark Green

    # Flower center
    cooler_flower_matrix[16][12] = (255, 102, 102)  # Light Red
                
    run_text = RunText(cooler_flower_matrix)
    if (not run_text.process()):
        run_text.print_help()
