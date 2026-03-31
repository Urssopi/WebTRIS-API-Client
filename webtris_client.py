# Import appropriate libraries 
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from datetime import datetime, date, time

# Class representing individual traffic observation 
class TrafficObservation:

    #Initialize a single traffic observation
    def __init__(self, 
                 site_name: str,
                 report_date: date,
                 time_period_ending: time,
                 avg_mph: float | None,
                 total_volume: int | None
                 ) -> None:
        """
        Initialize a single traffic observation

        Args: 
            Site Name, Report Date, Time Period Ending, Average MPH, Total Volume
            
        Returns:
            None
        """
        self.site_name = site_name
        self.report_date = report_date
        self.time_period_ending = time_period_ending
        self.avg_mph = avg_mph
        self.total_volume = total_volume

    # Checks if a record contains complete data
    def is_valid_data(self) -> bool:
        """
        Checks if data giving is valid

        Args: 
            Self
            
        Returns:
            Returns True if all conditions of the data are not None or not an empty string, else False"
        """
        return all([
        self.site_name not in (None, ""),
        self.report_date is not None,
        self.time_period_ending is not None,
        self.avg_mph is not None,
        self.total_volume is not None
    ])

    # Equality comparison operator 
    def __eq__(self, value: object) -> bool:
        """
        Allows for equality comparion between objects

        Args: 
            Value: Another object
            
        Returns:
            Returns NotImplemented if object is not an instance, else, returns true if site name, report date, and time period are equal
        """
        if not isinstance(value, TrafficObservation):
            return NotImplemented
        return self.site_name == value.site_name and self.report_date == value.report_date and self.time_period_ending == value.time_period_ending
        
    # Less than comparison operation
    def __lt__(self, other) -> bool:
        """
        Allows for value comparison 

        Args: 
            Other
            
        Returns:
            Returns NotImplemented if object is not an instance, else, true if one object is less than another
        """

        if not isinstance(other, TrafficObservation):
            return NotImplemented
        return (self.report_date, self.time_period_ending, self.site_name) < (other.report_date, other.time_period_ending, other.site_name)
    
    # Readable string represetation 
    def __str__(self) -> str:
        """
        Allows for value comparison 

        Args: 
            Self
            
        Returns:
            Returns readable string representation of data
        """
        return (
        f'Site Name: {self.site_name}\n'
        f'Report Date: {self.report_date}\n'
        f'Time Period: {self.time_period_ending}\n'
        f'Average Miles per hour: {self.avg_mph}\n' 
        f'Total Volume: {self.total_volume}\n'
        f' '
        )

# Class for communicating with API   
class TrafficAPIClient:

    def __init__(self) -> None:
        """
        Initialize Client class

        Args: 
            Self
            
        Returns:
            None
        """
        self.base_url = "https://webtris.nationalhighways.co.uk/api/v1.0"

    def parse_row(self, data: dict) -> TrafficObservation:
        """
        Parses row values into proper python types 

        Args: 
            the data dictionary
            
        Returns:
            A traffic observation with converted types
        """
        site_name_raw = data.get("Site Name", "")
        report_date_raw = data.get("Report Date", "")
        time_raw = data.get("Time Period Ending", "")
        avg_mph_raw = data.get("Avg mph", "")
        total_volume_raw = data.get("Total Volume", "")

        if site_name_raw == "" or report_date_raw == "" or time_raw == "":
            raise ValueError("Missing required row fields.")

        report_date = datetime.strptime(report_date_raw, "%Y-%m-%dT%H:%M:%S").date()
        time_period_ending = datetime.strptime(time_raw, "%H:%M:%S").time()

        if avg_mph_raw == "":
             avg_mph = None
        else:
            avg_mph = float(avg_mph_raw)

        if total_volume_raw == "":
            total_volume = None
        else:
            total_volume = int(total_volume_raw)

        return TrafficObservation(
            site_name=site_name_raw,
            report_date=report_date,
            time_period_ending=time_period_ending,
            avg_mph=avg_mph,
            total_volume=total_volume
            )

    def fetch_daily_observations(self, site_id: int, target_date: str) -> list[TrafficObservation]:
        """
        Fetches all daily observations for site and a day

        Args: 
            Site ID, Target date
            
        Returns:
            A list of parsed traffic observations from the API
        """
        try:
            response = requests.get(
                f"{self.base_url}/reports/daily",
                params = {
                "sites": site_id,
                "start_date": target_date,
                "end_date": target_date,
                "page": 1,
                "page_size": 500
                },
                timeout = 10
            )
            response.raise_for_status()
        except Timeout as e:
            raise ConnectionError("Request timed out.") from e
        except HTTPError as e:
            raise ValueError(f"WebTRIS returned HTTP error {e.response.status_code}.") from e
        except RequestException as e:
            raise ConnectionError("Failed to connect to the WebTRIS API.") from e

        data = response.json()  
        if "Rows" not in data:
            raise ValueError("API response did not contain 'Rows'.")
        rows = data["Rows"]
        
        return [self.parse_row(row) for row in rows]

# Class representing a single sites daily data
class Trafficsite:
    def __init__(self, site_id: int, site_name: str, observations: list[TrafficObservation]) -> None:
        """
        Initalize daily traffic site class

        Args: 
            Site Id, Site Name, List of Traffic Observaitons
        Returns:
            None
        """
        self.site_id = site_id
        self.site_name = site_name
        self.observations = observations

    def load_traffic_data(self, api: TrafficAPIClient, target_date: str) -> None:
        """
        Loads traffic data from TrafficAPIClient class 

        Args: 
            API class, target date
        Returns:
            None
        """
        print(f'Loading observations for {self.site_id}.')
        self.observations = api.fetch_daily_observations(self.site_id, target_date)

    def average_traffic_speed(self) -> float | None:
        """
        Checks if speed are valid, if so, takes the average of all speeds

        Args: 

        Returns:
            The average speed of observations 
        """
        valid_speeds = [observation.avg_mph for observation in self.observations if observation.avg_mph is not None]
        if len(valid_speeds) == 0:
            return None

        return sum(valid_speeds) / len(valid_speeds)

    def total_traffic_volume(self) -> int:
        """
        Total vehicle volume across all observations 

        Args: 

        Returns:
            The sum of all total volumes for all observatios
        """
        return sum(observation.total_volume for observation in self.observations if observation.total_volume is not None)

    def traffic_records_for_hour(self, hour: int) -> list[TrafficObservation]:
        """
        List comprehesion of all records for an hour

        Args: 
            The desired hour as an integer
        Returns:
            A list of traffic observations in the hour
        """
        return [observation for observation in self.observations if observation.time_period_ending.hour == hour]

    def average_traffic_speed_for_hour(self, hour: int) -> float | None:
        """
        Creates list of observations in a specific hour and finds the average speed
    
        Args: 
            The desired hour as an integer

        Returns:
            The average speed of observations as a float or None
        """
        valid_speeds = [observation.avg_mph for observation in self.traffic_records_for_hour(hour) if observation.avg_mph is not None]
        if len(valid_speeds) == 0:
            return None

        return sum(valid_speeds) / len(valid_speeds)

    def total_traffic_volume_for_hour(self, hour: int) -> int:
        """
        Find the sum of all volumes within a given hour

        Args:  
            The desired hour 
        Returns:
            the sum of all traffic volume in the hour
        """
        return sum(observation.total_volume for observation in self.traffic_records_for_hour(hour) if observation.total_volume is not None)

    def peak_hour(self) -> int | None:
        """
        Find the hour with the hihgest traffic volume

        Args: 
            Self
        Returns:
            The hour with highest traffic volume
            
        """
        if len(self.observations) == 0:
            return None
        hours = {observation.time_period_ending.hour for observation in self.observations}
        return max(hours, key=self.total_traffic_volume_for_hour)

    #Iteration over records in chronological order
    def __iter__(self):
        """
        Creates an iteroator for the class

        Args: 
            Self
        Returns:
            an iterator with a sorted list
        """
        return iter(sorted(self.observations))

    # Number of records in colletion
    def __len__(self) -> int:
        """
        " Allows to check for length of object"

        Args: 
            Self
        Returns:
            the lenght of the traffic observation list
        """
        return len(self.observations)