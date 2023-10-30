from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..PyKrita import *
else:
    from krita import *
    from PyQt5.QtWidgets import QMessageBox


app = Krita.instance()
current_document = app.activeDocument()
current_document.setBatchmode(True)
current_doc_path = Path(current_document.fileName()).parent
current_doc_name = Path(current_document.fileName()).stem

MESSAGE_TITLE = "Krita Macro"
SUCCESSFUL_EXPORT = "A imagem foi exportada com sucesso."


def export_image(extension: Literal["png", "jpg"]):
    """Exports the image in the current active document to either JPG or PNG
    with some defined parameters."""
    export_parameters = InfoObject()

    if extension == "png":
        export_parameters.setProperties(
            {
                "alpha": True,
                "compression": 9,
                "forceSRGB": False,
                "indexed": False,
                "interlaced": False,
                "saveSRGBProfile": False,
                "transparencyFillcolor": [255, 255, 255],
            }
        )
    elif extension == "jpg":
        export_parameters.setProperties(
            {
                "baseline": True,
                "exif": True,
                "filters": False,
                "forceSRGB": False,
                "iptc": True,
                "isSRGB": False,
                "optimize": True,
                "progressive": False,
                "quality": 100,
                "saveProfile": True,
                "smoothing": 0,
                "subsampling": 3,
                "xmp": True,
                "transparencyFillcolor": [255, 255, 255],
            }
        )

    new_file_path = str(current_doc_path / (current_doc_name + f".{extension}"))

    status = current_document.exportImage(new_file_path, export_parameters)
    return status


file_formats = ["jpg", "png"]
status = []

for format in file_formats:
    export_status = export_image(format)
    status.append(export_status)

if False not in status:
    message_box = QMessageBox()
    message_box.setWindowTitle(MESSAGE_TITLE)
    message_box.setText(SUCCESSFUL_EXPORT)
    message_box.setIcon(QMessageBox.Information)
    message_box.exec_()
