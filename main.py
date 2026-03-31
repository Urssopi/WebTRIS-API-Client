from webtris_client import TrafficAPIClient, Trafficsite

# Main function
def main() -> None:
    
    api = TrafficAPIClient()

# Example Site ID
    site_id = 461

# Check if site id is an integer
    try:
        site_id = int(site_id)
    except ValueError:
        print("Site ID must be an integer")
        return

# Example Site name
    site_name = "M25/4432A"

# Check if site name is entered
    if not site_name:
        print("No site name entered.")
        return 

# Example Target Date  
    target_date = "19102025"

# Check if target date is enterd
    if not target_date:
        print("No date entered.")
        return

# Example site   
    site = Trafficsite(site_id, site_name, [])

# Loads traffic data from API
    try:
        site.load_traffic_data(api, target_date)
    except Exception as e:
        print(f"Error loading traffic data: {e}")
        return

    if len(site) == 0:
        print("No traffic observations were found.")
        return 

# Prints general info about the entered site   
    print(f"\n       ###### Traffic summary for {site.site_name} (site {site.site_id}) on {target_date} ######\n")
    print(f"Number of observations: {len(site)}")
    print(f"Average Traffic Speed: {site.average_traffic_speed()}")
    print(f"Total Traffic Volume: {site.total_traffic_volume()}")
    print(f"Peak hour: {site.peak_hour()}")

   
    print("\nHourly Record for peak hour: \n")

# Print reocrds for peak hour   
    peak = site.peak_hour()
    if peak is not None:
        for record in site.traffic_records_for_hour(peak):
            print(record)

if __name__ == "__main__":
    main()