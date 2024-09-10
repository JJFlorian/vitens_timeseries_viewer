import streamlit as st
from datetime import datetime

from lizard import get_lizard_locations, get_lizard_timeseries, get_timeserie_metadata, get_event_data
from config import WINDOW_OPTIONS

def main() -> None:
    st.set_page_config(
        page_title="Vitens Grondwater Viewer",
        layout="centered",
    )

    if "location_name" not in st.query_params:
        st.query_params["location_name"] = ""

    if "timeserie_name" not in st.query_params:
        st.query_params["timeserie_name"] = None

    st.title('Vitens Grondwater Viewer')


    # Step 1: the user has to fill in the first characters of a lizard location.
    # This avoids having to import all locations everytime the dashboard is initialized.
    location_search_input = st.text_input(
        label="Zoek een Lizard locatie:",
        value=st.query_params["location_name"],
        key="location_search",
        help="Gebruik deze zoekoptie om een locatie in Lizard te vinden.",
        placeholder="Location naam.."
    )      

    if not location_search_input:
        st.info("Vul de eerste karakters van een locatie naam om te zoeken.")

    else:
        location_search_results = get_lizard_locations(location_search_input)

    if location_search_input and not location_search_results:
        st.warning('Er zijn geen locaties gevonden die starten met deze karakterss.')

    if location_search_input and location_search_results:  
        # Step 2: The user should select a location from the results of the search query        
        location_options = list(location_search_results.keys())
    
        # Determine index based on input parameter
        try:
            index = location_options.index(location_search_input)
        except ValueError:
            index = None  # Default index if not found

        selected_location = st.selectbox(
            label="Selecteer een locatie:",
            options=location_options,
            index=index,
        )

        if selected_location:
            timeseries_options = get_lizard_timeseries(location_search_results[selected_location])
            timeseries_options_list = list(timeseries_options.keys())

            # Determine index based on input parameter
            try:
                index = timeseries_options_list.index(st.query_params["timeserie_name"])
            except ValueError:
                index = None  # Default index if not found
            
            # Step 3: The user should select a timeserie
            selected_timeserie = st.selectbox(
                label="Selecteer een timeserie:",
                options=timeseries_options,
                index=index,
            )

            st.divider()

            if selected_timeserie:
                timeserie_metadata = get_timeserie_metadata(timeseries_options[selected_timeserie])
                if not timeserie_metadata["start"] and not timeserie_metadata["end"]:
                    st.warning("Er is geen tijdseriedata gevonden voor deze tijdserie")
                else:
                    col1, col2 = st.columns(2)

                    with col1:
                        start_date = st.date_input(
                            label="Kies een startdatum:",
                            value=datetime.strptime(timeserie_metadata["start"], '%Y-%m-%dT%H:%M:%SZ'),
                            min_value=datetime.strptime(timeserie_metadata["start"], '%Y-%m-%dT%H:%M:%SZ'),
                            max_value=datetime.strptime(timeserie_metadata["end"], '%Y-%m-%dT%H:%M:%SZ'),
                        )

                    with col2:
                        end_date = st.date_input(
                            label="Kies een einddatum:",
                            value=datetime.strptime(timeserie_metadata["end"], '%Y-%m-%dT%H:%M:%SZ'),
                            min_value=start_date,
                            max_value=datetime.strptime(timeserie_metadata["end"], '%Y-%m-%dT%H:%M:%SZ'),
                        )

                    window = st.selectbox(
                        label="Laat data zien per:",
                        options=WINDOW_OPTIONS,
                        index=0,
                    )

                    event_data = get_event_data(timeseries_options[selected_timeserie], start_date, end_date, WINDOW_OPTIONS[window])

                    if not event_data.empty:
                        st.line_chart(
                            event_data,
                            x='time',
                            y='avg',
                            x_label="Tijd",
                            y_label=timeserie_metadata["observation_type"]["unit"], 
                        )

if __name__ == "__main__":
    main()