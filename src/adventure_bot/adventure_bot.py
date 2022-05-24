from src.bot.bot import Bot
from src.services.location import LocationService
class AdventureBot(Bot):
    def __init__(self):
        super().__init__()
        self.locationService = LocationService()
        calendar = self.locationService.read()
        print(calendar.text)
