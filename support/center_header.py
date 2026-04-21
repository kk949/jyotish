from reportlab.platypus import Flowable
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib import colors
from reportlab.lib.units import mm

class CenteredHeader(Flowable):
    def __init__(self, text, font='Helvetica-Bold', font_size=14, 
                 line_color=colors.HexColor("#D3A900"), 
                 text_color=colors.HexColor("#2E4053")):
        super().__init__()
        self.text = text
        self.font = font
        self.font_size = font_size
        self.line_color = line_color
        self.text_color = text_color

    def draw(self):
        canvas = self.canv
        width = self._width or canvas._pagesize[0] - 60  # usable page width
        
        text_width = stringWidth(self.text, self.font, self.font_size)
        padding = 12 * mm
        box_width = text_width + padding
        padding_vertical = 6
        rect_height = self.font_size + (padding_vertical * 2)
        y = 0  

        canvas.setStrokeColor(self.line_color)
        canvas.setLineWidth(1)

        # Left line
        canvas.line(0, y, (width - box_width) / 2 - 5, y)

        # Right line
        canvas.line((width + box_width) / 2 + 5, y, width, y)

        # Rounded Text Box
        canvas.roundRect((width - box_width) / 2,y - (rect_height / 2),box_width,rect_height,rect_height * 0.4,stroke=1,fill=0)

        # Draw Text
        canvas.setFont(self.font, self.font_size)
        canvas.setFillColor(self.text_color)
        canvas.drawCentredString(width / 2, y - (self.font_size / 3), self.text)

    def wrap(self, availWidth, availHeight):
        self._width = availWidth
        return availWidth, 20
