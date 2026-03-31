# Import Appropriate Libraries
import requests
from datetime import date, time 
import pytest
from unittest.mock import patch, Mock
from webtris_client import TrafficObservation, TrafficAPIClient, Trafficsite

# *** Example Fixtures ***


@pytest.fixture
def sample_row():
    """
        Fixture of a complete example row

        Args: 
            None
        Returns:
            A complete sample row
        """
    return {
        "Site Name": "M25/4432A",
        "Report Date": "2025-10-19T00:00:00",
        "Time Period Ending": "00:14:00",
        "Avg mph": "65",
        "Total Volume": "182"
    }

@pytest.fixture
def sample_row_missing_values():
    """
        Fixture of a row with missing values

        Args: 
            None

        Returns:
            An example row with missing values
        """
    return {
        "Site Name": "M25/4432A",
        "Report Date": "2025-10-19T00:00:00",
        "Time Period Ending": "00:29:00",
        "Avg mph": "",
        "Total Volume": ""
    }

@pytest.fixture
def mock_success_response(sample_row):
    """
        A fixture with a mock response

        Args: 
            None

        Returns:
            A response of a successful api call
        """
    response = Mock(status_code = 200)
    response.json.return_value = {"Rows": [sample_row]}
    response.raise_for_status = Mock()
    return response

@pytest.fixture
def mock_missing_rows_response():
    """
        A fixture with a mock response with missing rows

        Args: 
            None

        Returns:
            A repsonse of a succesful api call 
        """
    response = Mock(status_code = 200)
    response.json.return_value = {"Header": {}}
    response.raise_for_status = Mock()
    return response

@pytest.fixture
def observation_one():
    """
        A fixture of a complete traffic observation

        Args: 
            None
            
        Returns:
            A complete traffic observation object
            
        """
    return TrafficObservation(
    site_name = "M25/4432A",
    report_date = date(2025, 10, 19),
    time_period_ending = time(0, 14),
    avg_mph = 65.0,
    total_volume = 182
    )

@pytest.fixture
def observation_two():
    """
        A fixture of a complete traffic observation

        Args: 
            None
            
        Returns:
            A complete traffic observaiton object
        """
    return TrafficObservation(
    site_name = "M25/4432A",
    report_date = date(2025, 10, 19),
    time_period_ending = time(1, 14),
    avg_mph = 55.0,
    total_volume = 120
    )

@pytest.fixture
def observation_three():
    """
        A fixture of an incomplete traffic observation

        Args: 
            None
            
        Returns:
            An incomplete traffic observaiton object
        """
    return TrafficObservation(
    site_name = "M25/4432A",
    report_date = date(2025, 10, 19),
    time_period_ending = time(1, 29),
    avg_mph = None,
    total_volume = 100
    )

@pytest.fixture
def traffic_site(observation_one, observation_two, observation_three):
    """
        A fixture of an example traffic site 

        Args: 
            Three traffic observation fixtures
            
        Returns:
            A complete Trafficsite object 
        """
    return Trafficsite(
    site_id = 461,
    site_name = "M25/4432A",
    observations = [observation_one, observation_two, observation_three]
)

# *** TrafficObservation tests ***

def test_observation_is_valid(observation_one):
    """
        Tests if observation one has valid data

        Args: 
            Traffic observation object 
            
        Returns:
            Succesusful if the observation has valid data
        """
    assert observation_one.is_valid_data() is True

def test_observation_is_not_valid_when_missing_speed(observation_three):
    """
        Tests if observation three has valid data

        Args: 
            Traffic observation object 
            
        Returns:
            Unsuccessful if the obervation has invalid data 
        """
    assert observation_three.is_valid_data() is False

def test_observation_equality(observation_one):
    """
        Tests if two observations are equal

        Args: 
            Traffic observation object
            
        Returns:
            Successful if both objects are equal
        """
    other = TrafficObservation(
    site_name = "M25/4432A",
    report_date = date(2025, 10, 19),
    time_period_ending = time(0, 14),
    avg_mph = 70.0,
    total_volume = 200
    )
    assert observation_one == other

def test_observation_less_than(observation_one, observation_two):
    """
        Tests if one observation is less than another

        Args: 
            Two traffic observation objects 
            
        Returns:
            Succesful if the object is less than the other
        """
    assert observation_one < observation_two

def test_observation_string_contains_values(observation_one):
    """
        Tests if an observations str represention is correct

        Args: 
            TrafficObservation
            
        Returns:
            Succesful if the string representiation is correct 
        """
    result = str(observation_one)
    assert "M25/4432A" in result
    assert "2025-10-19" in result
    assert "00:14:00" in result
    assert "65.0" in result
    assert "182" in result

# *** TrafficAPIClient tests ***

def test_parse_row_returns_observations(sample_row):
    """
        Tests if the client can parse rows properly

        Args: 
            A singe Sample row of data 
            
        Returns:
            Successful if all the data if properly parsed to the correct types
        """
    client = TrafficAPIClient()
    observation = client.parse_row(sample_row)

    assert observation.site_name == "M25/4432A"
    assert observation.report_date == date(2025, 10, 19)
    assert observation.time_period_ending == time(0,14)
    assert observation.avg_mph == 65.0
    assert observation.total_volume == 182

def test_parse_row_missing_values(sample_row_missing_values):
    """
        Tests if the parse row function can handle missing values

        Args: 
            A sample row with missing values
            
        Returns:
            Successful if missing values are None
        """
    client = TrafficAPIClient()
    observation = client.parse_row(sample_row_missing_values)

    assert observation.avg_mph is None
    assert observation.total_volume is None

def test_parse_row_missing_required_fields():
    """
        Tests if parse row can handle missing fields

        Args: 
            None
            
        Returns:
            Successful if it properly handels the data 
        """
    client = TrafficAPIClient()
    bad_row = {
        "Site Name": "",
        "Report Date": "2025-10-19T00:00:00",
        "Time Period Ending": "00:14:00",
        "Avg mph": "65",
        "Total Volume": "182"
    }
    try:
        client.parse_row(bad_row)
        assert False
    except ValueError as e:
        assert str(e) == "Missing required row fields."


@patch("webtris_client.requests.get")
def test_fetch_daily_observations(mock_get, mock_success_response):
    """
        Tests if api client can fetch daily observations

        Args: 
            Mock_get, Mock_succes_response
            
        Returns:
            Successful if it properly fetches data for a site and a date
        """
    mock_get.return_value = mock_success_response

    client = TrafficAPIClient()
    results = client.fetch_daily_observations(461, "19102025")

    assert len(results) == 1
    assert isinstance(results[0], TrafficObservation)
    assert results[0].site_name == "M25/4432A"

@patch("webtris_client.requests.get")
def test_fetch_daily_observations_raises_missing_rows(mock_get, mock_missing_rows_response):
    """
        Tests if api client raises error for missing rows

        Args: 
            Mock_get, Mock_missing_rows_response
            
        Returns:
            Succesful returns false, or if error is raised
        """
    mock_get.return_value = mock_missing_rows_response

    client = TrafficAPIClient()

    try:
        client.fetch_daily_observations(461, "19102025")
        assert False
    except ValueError as e:
        assert "Rows" in str(e)

@patch("webtris_client.requests.get")
def test_fetch_daily_observations_handles_timeout(mock_get):
    """
        Tests if fetch observations handle timeout error

        Args: 
            mock_get
            
        Returns:
            Succesful if error is raised
        """
    mock_get.side_effect = requests.Timeout("Connection timed out")

    client = TrafficAPIClient()

    try:
        client.fetch_daily_observations(461, "19102025")
        assert False
    except ConnectionError as e:
        assert "timed out" in str(e)

@patch("webtris_client.requests.get")
def test_fetch_daily_observations_handles_http_error(mock_get):
    """
        Tests if fetch observation handles http error

        Args: 
            mock_get
            
        Returns:
            Succesful if error is raised
        """
    mock_response = Mock(status_code = 500)
    mock_response.raise_for_status.side_effect = requests.HTTPError(response = mock_response)
    mock_get.return_value = mock_response

    client = TrafficAPIClient()

    try:
        client.fetch_daily_observations(461, "19102025")
        assert False
    except ValueError as e:
        assert "WebTRIS returned HTTP error" in str(e)

@patch("webtris_client.requests.get")
def test_fetch_daily_observations_handles_request_exception(mock_get):
    """
        Tests if fetch observtions handles request exception

        Args: 
            mock_get
            
        Returns:
            Sucesful if error is raised
        """
    mock_get.side_effect = requests.RequestException("Failed to connect")

    client = TrafficAPIClient()

    try:
        client.fetch_daily_observations(461, "19102025")
        assert False
    except ConnectionError as e:
        assert "Failed to connect" in str(e)

# *** Trafficsite tests ***

def test_load_traffic_data():
    """
        Tests if data gets properly loaded

        Args: 
            None
            
        Returns:
            Succesful is data is equal to expected data 
        """
    site = Trafficsite(461, "M25/4432A", [])
    api = Mock()

    expected_result = [
        TrafficObservation(
            site_name="M25/4432A",
            report_date=date(2025, 10, 19),
            time_period_ending=time(0, 14),
            avg_mph=65.0,
            total_volume=182
        )
    ]

    api.fetch_daily_observations.return_value = expected_result
    site.load_traffic_data(api, "19102025")

    assert site.observations == expected_result

def test_average_traffic_speed(traffic_site):
    """
        Tests if average speed is correct

        Args: 
            traffic_site
            
        Returns:
            Succesful if average is correctly calcualted
        """
    assert traffic_site.average_traffic_speed() == (65.0 + 55.0) / 2


def test_total_traffic_volume(traffic_site):
    """
        Tets if total volume is correct

        Args: 
            traffic_site
            
        Returns:
            Successful if total volume is correctly calculated
        """
    assert traffic_site.total_traffic_volume() == 402

def test_traffic_records_for_hour(traffic_site):
    """
        Tests if traffic records for an hour is corrent

        Args: 
            traffic_site
            
        Returns:
            Successful if lenfht of the list is 2 and if they all have values
        """
    records = traffic_site.traffic_records_for_hour(1)
    assert len(records) == 2
    assert all(record.time_period_ending.hour == 1 for record in records)


def test_average_speed_for_hour(traffic_site):
    """
        Tests if average speed for an hour is correct

        Args: 
            traffic_site
            
        Returns:
            Successful if average speed is correctly calculated
        """
    assert traffic_site.average_traffic_speed_for_hour(1) == 55.0


def test_total_volume_for_hour(traffic_site):
    """
        Tests if total volume for an hour is corrent

        Args: 
            traffic_site
            
        Returns:
            Successful if total volume is correctly calculated
        """
    assert traffic_site.total_traffic_volume_for_hour(1) == 220


def test_peak_hour(traffic_site):
    """
        Tests peak hour

        Args: 
            traffic_site
            
        Returns:
            Succesful if peak hour is correct
        """
    assert traffic_site.peak_hour() == 1


def test_peak_hour_returns_none_when_empty():
    """
        Tests when peak hour is none or empty

        Args: 
            none
            
        Returns:
            Succesful if peak hour is none
        """
    site = Trafficsite(461, "M25/4432A", [])
    assert site.peak_hour() is None


def test_iter_returns_sorted_observations(traffic_site):
    """
        Tests if __iter__ returns a sorted list

        Args: 
            traffic_site
            
        Returns:
            Succesful if a sorted list matches the time
        """
    records = list(traffic_site)
    assert records[0].time_period_ending == time(0, 14)
    assert records[1].time_period_ending == time(1, 14)
    assert records[2].time_period_ending == time(1, 29)


def test_len_returns_number_of_observations(traffic_site):
    """
        Tests if __len__ works on list 

        Args: 
            traffic_site
            
        Returns:
            Succesful if length of list is correct
        """
    assert len(traffic_site) == 3