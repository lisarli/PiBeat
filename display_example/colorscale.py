#!/usr/bin/env python
from samplebase import SampleBase
import time


class ColorScale(SampleBase):
    def __init__(self, color, *args, **kwargs):
        super(ColorScale, self).__init__(*args, **kwargs)
        self.color = color

    def run(self):
        sub_blocks = 40
        width = 16
        height = 5
        y_step = max(1, height / sub_blocks)
        count = 0
        color = [i/255 for i in self.color] 

        while count < height:
            for y in range(0, height):
                for x in range(0, width):
                    if count % height < y:
                        c = sub_blocks * int(y / y_step) 
                        self.matrix.SetPixel(y+ 32-height, x, color[0] * c, color[1] * c, color[2] * c)
                    else:
                        self.matrix.SetPixel(y+ 32-height, x,0,0,0)

            count += 1
            time.sleep(0.2)


# Main function
if __name__ == "__main__":
    colorscale = ColorScale( (255,235,59))
    colorscale.process()
