import sys
from PIL import Image
import os
import random
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile, QObject
from PySide2.QtGui import QPixmap
import tempfile


class Palette_Maker(QObject):
    def resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def __init__(self, ui_file, parent=None):

        # display UI
        super(Palette_Maker, self).__init__(parent)
        ui_file = QFile(self.resource_path(ui_file))
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()

        self.source_text = self.window.source_label
        self.palette_name_text = self.window.palette_label

        self.source_images = self.window.source_selection_cb
        self.palette_name = self.window.palette_name_le

        self.generate_button = self.window.generate_btn
        self.show_result = self.window.result_label
        self.show_text_result = self.window.result_text_label
        self.colour_values = self.window.colour_values_le

        self.source_image_display = self.window.srcimg_label
        self.source_images.addItems(self.get_source_images())
        self.generate_button.pressed.connect(self.main_func)

        self.window.show()

    # get image files from the folder where tool is
    def get_source_images(self):
        current_folder = os.getcwd()
        get_all_items = os.listdir(current_folder)
        img_list = []
        extensions = (".png", ".jpg", ".jpeg")
        for i in get_all_items:
            if i.lower().endswith(extensions):
                img_list.append(i)
        return img_list

    # get source image that user selected to make a palette from
    def get_selection(self):
        current_selection = self.source_images.currentText()
        return current_selection

    # get desired palette name from the user input
    def get_palette_name(self):
        custom_name = self.palette_name.text() + ".png"
        default_name = "my_palette.png"
        if self.palette_name.text() == "":
            palette_name = default_name
        else:
            palette_name = custom_name
        return palette_name

    # function where palette is made, images are displayed and rgb values are printed
    def main_func(self):
        # open source image and create a base(8x8) image to pick colours from
        your_selection = self.get_selection()
        your_palette_name = self.get_palette_name()
        my_img = Image.open(your_selection).convert("RGB")

        # max size for the thumbnail of the source image
        max_size = 256
        src_width, src_height = my_img.size
        # calculate the scale for the thumbnail
        scale = max_size / max(src_width, src_height)

        # calculate new dimensions for the thumbnail
        new_width = int(src_width * scale)
        new_height = int(src_height * scale)
        resized_img = my_img.resize((new_width, new_height), Image.LANCZOS)
        # save thumbnail in the temp directory
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "temp_image_thumbnail.png")
        resized_img.save(temp_path)

        # create an img that will hold palette colours
        imgSmall = my_img.resize((8, 8), resample=Image.Resampling.BILINEAR)
        imgSmall.save("smallSource.png")

        # get pixel colors from the base image
        all_px = list(imgSmall.getdata())

        reds = []
        greens = []
        blues = []
        all_rgb = []

        all_rgb.append(reds)
        all_rgb.append(greens)
        all_rgb.append(blues)
        dict_rgb = {}

        # sort the pixel colors based on dominant channel
        for i in all_px:
            index = i.index(max(i))
            if index == 0:
                reds.append(i)
            elif index == 1:
                greens.append(i)
            else:
                blues.append(i)

        # create a dictionary with number of items in each channel
        # 0 = red, 1 = green, 2 = blue
        for i in all_rgb:
            dict_rgb.update({all_rgb.index(i): len(i)})
        # descending by value
        dict_rgb = dict(sorted(dict_rgb.items(), key=lambda kv: kv[1], reverse=True))
        # remove entries whose value == 0, meaning no dominant colour
        dict_rgb = {k: v for k, v in dict_rgb.items() if v != 0}

        palette = []
        # based on number of remaining channels, select random pixel color from the channels
        # in case there is only one channel, select all 6 pixel colours from it
        # in case of 2 dominant colours, select 3 each
        # else divide pixel colour as 3-2-1 based on dominance
        if len(dict_rgb) == 1:
            amount = 6
            for key in dict_rgb:
                b = random.choices(all_rgb[key], k=amount)
                palette.append(b)

        elif len(dict_rgb) == 2:
            amount = 3
            for key in dict_rgb:
                b = random.choices(all_rgb[key], k=amount)
                palette.append(b)

        elif len(dict_rgb) == 3:
            amount = 3
            for key in dict_rgb:
                b = random.choices(all_rgb[key], k=amount)
                palette.append(b)
                amount -= 1

        # flatten the list
        palette = [item for sublist in palette for item in sublist]

        # create a palette image from the pixels selected and put them in a row
        my_ind = 0
        new_palette = Image.new("RGB", (6, 1))
        for x in range(6):
            new_palette.putpixel((x, 0), palette[my_ind])
            my_ind += 1

        # make a final palette image by upscaling the new_palette
        result = new_palette.resize((450, 100), Image.Resampling.NEAREST)
        result.save(your_palette_name)
        res = "Your palette " + your_palette_name + " is generated"
        os.remove("smallSource.png")

        # print rgb values that correspond to each colour in the palette
        self.show_text_result.setText(res)
        self.colour_values.setText(str(palette))

        # display thumbnail of the source image
        src_pixmap = QPixmap(temp_path)
        self.source_image_display.setPixmap(src_pixmap)

        # display the image palette
        pixmap = QPixmap(your_palette_name)
        self.show_result.setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    form = Palette_Maker("PM.ui")
    sys.exit(app.exec_())
