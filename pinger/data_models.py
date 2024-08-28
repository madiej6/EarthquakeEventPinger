from dataclasses import dataclass
from datetime import datetime

@dataclass
class EarthquakeEvent:
    event_id: str
    # epicenter lat/lon & depth
    lat: float
    lon: float
    depth: float
    
    # magnitude
    mag: float

    place: str

    timestamp: int
    updated_timestamp: int
    
    overview_url: str
    data_url: str
    status: str
    
    # ex: `Tue Aug 27 17:12:02 2024`
    time_str: str = ''
    updated_time_str: str = ''
    
    # string descriptor of earthquake mag & location
    # ex: 'M 4.8 - 70 km SE of False Pass, Alaska'
    name: str = ''
   
    def __post_init__(self):
        # Combine first_name and last_name to populate full_name
        self.time_str = datetime.fromtimestamp(int(self.timestamp/1000)).strftime('%c')
        self.updated_time_str = datetime.fromtimestamp(self.updated_timestamp/1000).strftime('%c')
        self.name = f'M {self.mag} - {self.place}'