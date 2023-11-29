import cv2

from bot.base.common import ImageMatchConfig


class Template:
    template_name: str
    template_image: object
    resource_path: str
    image_match_config: ImageMatchConfig

    def __init__(self,
                 template_name: str,
                 resource_path: str,
                 image_match_config: ImageMatchConfig = ImageMatchConfig()):
        self.resource_path = resource_path
        self.template_name = template_name
        self.template_image = cv2.imread("resource" + self.resource_path + "/" + template_name.lower() + ".png", 0)
        self.image_match_config = image_match_config


_not_found_ui = '__NOT_FOUND_UI__'


class UI:
    ui_name = None
    check_exist_template_list: list[Template] = []
    check_non_exist_template_list: list[Template] = []
    check_on_template_list: list[Template] = []
    check_pass_count = 99

    def __init__(self, ui_name, check_exist_template_list: list[Template] = None,
                 check_non_exist_template_list: list[Template] = None,
                 check_on_template_list: list[Template] = None,
                 check_pass_count=None
                 ):
        if _not_found_ui == ui_name:
            self.ui_name = ui_name
            return

        self.ui_name = ui_name

        if check_exist_template_list is not None:
            self.check_exist_template_list = check_exist_template_list

        if check_non_exist_template_list is not None:
            self.check_non_exist_template_list = check_non_exist_template_list

        if check_on_template_list is not None:
            self.check_on_template_list = check_on_template_list

        if check_pass_count is not None:
            self.check_pass_count = check_pass_count
        else:
            self.check_pass_count = 1

        if len(self.check_on_template_list) + len(self.check_exist_template_list) == 0:
            raise Exception("UI " + self.ui_name + " not set check template")


NOT_FOUND_UI = UI(_not_found_ui, [], [])
