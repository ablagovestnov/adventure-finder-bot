from src.services.api import Api
class LocationService(Api):
    secondary_path = 'event/json-calendar'
    def __init__(self):
        super().__init__()
        print(self.path)