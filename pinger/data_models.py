from dataclasses import dataclass
from datetime import datetime

@dataclass
class EarthquakeEvent:
    # event id (ex: us6000nm4i)
    event_id: str

    # epicenter lat/lon & depth
    lat: float
    lon: float
    depth: float
    
    # magnitude
    mag: float

    # description of earthquake location
    # ex: '70 km SE of False Pass, Alaska'
    place: str

    # timestamps
    timestamp: int
    updated_timestamp: int
    
    # URLs and status
    overview_url: str
    data_url: str
    status: str

    # human readable timestamps
    # ex: `Tue Aug 27 17:12:02 2024`
    time_str: str = ''
    updated_time_str: str = ''
    
    # string descriptor of earthquake mag & location
    # ex: 'M 4.8 - 70 km SE of False Pass, Alaska'
    name: str = ''
   
    def __post_init__(self):
        self.time_str = datetime.fromtimestamp(int(self.timestamp/1000)).strftime('%c')
        self.updated_time_str = datetime.fromtimestamp(self.updated_timestamp/1000).strftime('%c')
        self.name = f'M {self.mag} - {self.place}'