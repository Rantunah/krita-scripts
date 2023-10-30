"""
This script sets up a multi-layered Keyshot render for post production.

The setps are done in the follwing order:
- place all layers inside `Render Passes`
- make groups for `rgba`, `ao` and rename them
- clone those new groups (as `Clone Layers`) and rename them
- create a new `Group Layer` in the root layer named `Post-Production`
- move the previously cloned layers into `Post-Production`
- clone `Render Layers`, toggle the parent's `Passthrough` status and
rename it
- create a new group in `Post-Production` move the `Render Layers`
clone there and rename it
- create a new `Paint Layer` in the previous group's top and rename it 
- set the previous layer's type to `Alpha Darken`
- create a new `Filter Layer` set to specific `Color Adjustment` values
and place it on top of the previous group
- move the group into `Post-Production`, bellow the `rgba` and `ao` clones
- create a new group with 3 `Fill Layers` of 3 diferent colors and rename
each child layer to it's color, as well as the parent layer
- toggle the visibility of the previous layer's children only
- save a `.kra` file with the exact name as the original file in the same
folder
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..PyKrita import *
else:
    from krita import *
    from PyQt5.QtGui import QColor


# Names for new layers
AO_GROUP = "Ambient Occlusion Stack"
AO_CLONE = "Ambient Occlusion"
RGBA_GROUP = "Beauty Pass Stack"
RGBA_CLONE = "Beauty Pass"
RENDER_PASSES_CLONE = "Original Alpha"
ALPHA_MASK_GROUP = "Clipping Mask"
ALPHA_PAINT = "Alpha Paint"
ALPHA_ADJUST = "Alpha Adjust"
BG_GROUP = "Backgrounds"
BG_GREEN = "Green"
BG_WHITE = "White"
BG_GREY = "Grey"
POST_GROUP = "Post-Production"
# Color values for `Backgrounds` layers
RGB_GREEN = (0, 255, 0)
RGB_WHITE = (255, 255, 255)
RGB_GREY = (72, 72, 72)


# Connect to the application
app = Krita.instance()
current_document = app.activeDocument()
# Get the root node object
root_node = current_document.rootNode()
# Get current path and file name
current_doc_path = Path(current_document.fileName()).parent
current_doc_name = Path(current_document.fileName()).stem


def create_grouplayer(
    name: str, parent_layer=root_node, layer_bellow: str | None = None
):
    """Create a `Group Layer` in the root, by default.

    Args:
        `name` (`str`): The name of the new layer.\n
        `parent_layer`(`Krita.Node`): The layer where this new one will be nested on.\n
        `layer_bellow` (`str`): The layer that will be bellow this new one.\n

    Returns:
        `new_group` (`Krita.Node`): The newly created node object.
    """

    # Check if layer position is required and get it's `Node` object
    layer_position = current_document.nodeByName(layer_bellow) if layer_bellow else None
    # Create a new `Group Layer` and relate it to it's parent layer
    new_group = current_document.createGroupLayer(name)
    parent_layer.addChildNode(new_group, layer_position)
    return new_group


def create_paintlayer(
    name: str, parent_layer=root_node, layer_bellow: str | None = None
):
    """Create a `Paint Layer` in the root, by default.

    Returns:
        `new_layer` (`Krita.Node`): The newly created node object.
    """

    # Check if layer position is required and get it's `Node` object
    layer_position = current_document.nodeByName(layer_bellow) if layer_bellow else None
    # Create a new `Paint Layer` and relate it to it's parent layer
    new_layer = current_document.createNode(name, "paintlayer")
    parent_layer.addChildNode(new_layer, layer_position)
    return new_layer


def create_filllayer_color(
    name: str, color: tuple, parent_layer=root_node, layer_bellow: str | None = None
):
    """
    Create a `Fill Layer` in the root node, by default.

    Args:
        `name` (`str`): The name of the new layer.\n
        `color` (`tuple`): a tuple that stores `red`, `green`, `blue` values\n
        `parent_layer`(`Krita.Node`): The layer where this new one will be nested on.\n
        `layer_bellow` (`str`): The layer that will be bellow this new one.\n

    Returns:
        `new_filllayer` (`Krita.Node`): The newly created node object.
    """

    # Check if layer position is required and get it's `Node` object
    layer_position = current_document.nodeByName(layer_bellow) if layer_bellow else None
    # Unpack `color` into each separate color vasriable
    (red, green, blue) = color
    # Setup required objects for `FillLayer` creation
    info_object = InfoObject()
    selection = Selection()
    # Create a color object from `PyQT` with the passed `color` arguments
    color_object = QColor(red, green, blue)
    info_object.setProperty("color", color_object)
    # Select the whole canvas area to fill the layer
    selection.select(0, 0, current_document.width(), current_document.height(), 255)
    new_filllayer = current_document.createFillLayer(
        name, "color", info_object, selection
    )
    # Relate the new `FillLayer` to it's parent layer
    parent_layer.addChildNode(new_filllayer, layer_position)
    new_filllayer.setGenerator("color", info_object)
    return new_filllayer


# TODO: This would be the correct way to create a `perchannel` layer
# but it's not working as of 5.2.0
def create_filterlayer(
    name: str, parent_layer: Node = root_node, layer_bellow: str | None = None
) -> Node:
    """Creates an Adjustment Filter Layer with specific curve values
    hardcoded in this function.

    Args:
        `name` (`str`): Name for the new layer\n
        `parent_layer` (`Node`): The layer where this new one will be nested on.
        Defaults to `root_node`.\n
        `layer_bellow` (`str` | None, optional): The layer that will be bellow this new one.
        Defaults to `None`.\n

    Returns:
        `color_adjust_filterlayer` (`Node`): The node object for the new layer.
    """
    # Check if layer position is required and get it's `Node` object
    layer_position = current_document.nodeByName(layer_bellow) if layer_bellow else None

    # Define the configuration for the filter
    filter_config = InfoObject()
    filter_config.setProperties(
        {
            "nTransfers": 8,
            "curve0": "0,0;1,1;",
            "curve1": "0,0;1,1;",
            "curve2": "0,0;1,1;",
            "curve3": "0,0;1,1;",
            "curve4": "0,0;0.156377,0.0809037;0.850071,0.758355;1,1;",
            "curve5": "0,0;1,1;",
            "curve6": "0,0;1,1;",
            "curve7": "0,0;1,1;",
        }
    )

    # Create a Color Adjust filter and set it's configuration
    color_adjust_filter = Filter()
    color_adjust_filter.setName("perchannel")
    color_adjust_filter.setConfiguration(filter_config)

    # Create a new selection
    selection = Selection()
    selection.select(0, 0, current_document.width(), current_document.height(), 255)

    # Create a new filter layer from the selection and the filter
    color_adjust_filterlayer = current_document.createFilterLayer(
        name, color_adjust_filter, selection
    )
    # Add the new node to the parent layer in the parameters
    parent_layer.addChildNode(color_adjust_filterlayer, layer_position)

    return color_adjust_filterlayer


def clone_layer(name: str, new_name: str):
    """Looks for a layer by it's name, clones it and renames it.

    Args:
        `name` (`str`): Name of the target layer.\n
        `new_name` (`str`): Name of the new cloned layer.\n

    Returns:
        `cloned layer` (`Krita.Node`): The newly created node object.
    """
    # TODO: `Make new_name` optional

    # Select a layer by it's name
    selected_layer = current_document.nodeByName(name)
    # Clone the layer and assign it to a variable
    cloned_layer = current_document.createCloneLayer(new_name, selected_layer)
    # Relate clone and parent nodes
    selected_layer.parentNode().addChildNode(cloned_layer, selected_layer)
    return cloned_layer


def sort_group_bytype(group_name: str, type: str):
    """Moves all layers of the passed type to the bottom of the group's stack

    Args:
        `group_name` (`str`): Name of the group that will be sorted.\n
        `type` (`str`): Name of the type that will be placed on the bottom of the layer stack.\n
        Node types:(https://api.kde.org/krita/html/classNode.html#a58f4025f31c1bb44df0eb6df7b559e70)
    """

    # Select a group and get a list of it's child layers
    selected_group = current_document.nodeByName(group_name)
    child_layers = selected_group.childNodes()
    # Filter the child layers by type
    type_layers = [node for node in child_layers if node.type() == type]
    other_layers = [node for node in child_layers if node.type() != type]
    # Remove the layers that aren't of the chosen type
    for node in other_layers:
        selected_group.removeChildNode(node)
    # Set the new hierarchy of the group by placing the seleced type layers
    # on the bottom of the stack
    selected_group.setChildNodes((type_layers + other_layers))


def nest_one_layer(layer_name: str, group_name: str):
    """Nest a layer node inside a group layer

    Args:
        `layer_name` (`str`): The selected layer's name.\n
        `group_name` (`str`): The selected group's name.\n
    """
    selected_layer = current_document.nodeByName(layer_name)
    selected_group = current_document.nodeByName(group_name)
    duplicate_layer = selected_layer.duplicate()
    selected_group.addChildNode(duplicate_layer, None)
    selected_layer.remove()


def nest_n_layers(layer_list: list, group_name: str):
    """Nest multiple layers inside a group of layers

    Args:
        `layer_list` (`list`): A list of names for the selected layers.\n
        `group_name` (`str`): The selected group's name.\n
    """
    for layer in layer_list:
        nest_one_layer(layer_name=layer, group_name=group_name)


# Main script procedure

# Create a group for all post-process layers in the root node
create_grouplayer(name=POST_GROUP)

# Create a `Group Layer` for `Ambient Occlusion` and `Beauty Pass`
ao_stack = create_grouplayer(
    name="Ambient Occlusion Stack",
    parent_layer=current_document.nodeByName("Render Passes"),
)
rgba_stack = create_grouplayer(
    name="Beauty Pass Stack", parent_layer=current_document.nodeByName("Render Passes")
)

# Create a `Group Layer` for the backgrounds
backgrounds_group = create_grouplayer(name=BG_GROUP, layer_bellow="rgba")

# Move `rgba` to `Beauty Pass Stack`
nest_one_layer("rgba", RGBA_GROUP)
# Move `ao` to `Ambient Occlusion Stack`
nest_one_layer("ao", AO_GROUP)

# Move the new groups to the bottom of `Render Passes`
sort_group_bytype("Render Passes", "grouplayer")

# Creates colored `Fill Layers` and moves them to `Backgrounds`
create_filllayer_color(
    BG_GREY, RGB_GREY, parent_layer=current_document.nodeByName(BG_GROUP)
)
create_filllayer_color(
    BG_WHITE, RGB_WHITE, parent_layer=current_document.nodeByName(BG_GROUP)
)
create_filllayer_color(
    BG_GREEN, RGB_GREEN, parent_layer=current_document.nodeByName(BG_GROUP)
)

# Disable all layers in `Backgrounds` group
for layer in backgrounds_group.childNodes():
    layer.setVisible(False)

# Switch visibility o `Backgrounds` group on an off so that the viewport refreshes correctly
backgrounds_group.setVisible(False)
backgrounds_group.setVisible(True)

# Create `Clone Layers` for `Render Layers`, `Beauty Pass` and `Ambient Occlusion` groups
rgba_clone = clone_layer(RGBA_GROUP, RGBA_CLONE)
ao_clone = clone_layer(AO_GROUP, AO_CLONE)
render_passes_clone = clone_layer("Render Layers", RENDER_PASSES_CLONE)

# Set `Ambient Occlusion` clone layer blending mode and opacity
ao_clone.setBlendingMode("multiply")
ao_clone.setOpacity(128)

# Set alpha inheritance for the clone layers
rgba_clone.setInheritAlpha(True)
ao_clone.setInheritAlpha(True)

# Disable `Passthrough` for `Render Layers` group
current_document.nodeByName("Render Layers").setPassThroughMode(False)

# Create `Clipping Mask` group
alpha_mask_group = create_grouplayer(name=ALPHA_MASK_GROUP)

# Create `Alpha Adjust` and move all alpha related layers into `Clipping Mask`
nest_one_layer(layer_name=RENDER_PASSES_CLONE, group_name=ALPHA_MASK_GROUP)
alpha_paint_layer = create_paintlayer(
    name=ALPHA_PAINT, parent_layer=current_document.nodeByName(ALPHA_MASK_GROUP)
)
# TODO: As of 5.2.0, there is a bug preventing the `perchannel` layer
# from being configured, so this just creates the layer
alpha_adjust_layer = create_filterlayer(
    name=ALPHA_ADJUST, parent_layer=alpha_mask_group, layer_bellow=ALPHA_PAINT
)
alpha_paint_layer.setBlendingMode("alphadarken")

# Move all post-production layers to `Post-Production` group
post_prod_layers = [ALPHA_MASK_GROUP, RGBA_CLONE, AO_CLONE]
nest_n_layers(post_prod_layers, POST_GROUP)

# Refresh the viewport
current_document.refreshProjection()

# Save the file as a `.kra` file in the same place, with the same name
new_file_path = str(current_doc_path / (current_doc_name + ".kra"))
current_document.saveAs(new_file_path)
