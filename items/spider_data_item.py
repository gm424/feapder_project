from feapder import Item
from datetime import datetime
class SpiderDataItem(Item):

    # __unique_key__ = ["product_id", "platform"]
    def __init__(self, *args, **kwargs):
        self.create_time = None
        self.company = None
        self.img_url = None
        self.name = None
        self.id = None
        self.address = None
        self.store_name = None

    def pre_to_db(self):
        """
        入库前的处理
        """
        self.create_time = datetime.now()