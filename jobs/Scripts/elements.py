import os


class ElementLocation:
    def __init__(self, location, element_name):
        self.location = location
        self.element_name = element_name

    def build_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Elements", self.location, self.element_name) + ".png")


class MaterialXLocation(ElementLocation):
    def __init__(self, element_name):
        super().__init__("", element_name)


class MaterialXElements:
    ADVANCED_SETTINGS = MaterialXLocation("advanced_settings")
    DRAW_ENVIRONMENT = MaterialXLocation("draw_environment")
    LOAD_ENVIRONMENT = MaterialXLocation("load_environment")
    LOAD_MATERIAL = MaterialXLocation("load_material")
    LOAD_MESH = MaterialXLocation("load_mesh")
