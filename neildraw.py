

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import matplotlib.pyplot as plt


def neildraw(filepath = 'YPOPUP_data.csv', reservation_time = 1.5, number_of_tables = {4: 4, 6: 4,}, num_reservations = 16):

    from os import name
    df = pd.read_csv(filepath)

    # Parse party sizes and time slots (assuming they are stored as comma-separated strings)
    df['party_sizes'] = df['party_sizes'].replace({'Party Size of 4': '4', 'Party Size of 6': '6', 'Party Size of 4;Party Size of 6': '4;6'}).apply(lambda x: sorted([int(size) for size in x.split(';')], reverse=True))
    df['time_slots'] = df['time_slots'].apply(lambda x: [slot for slot in x.split(';')])


    # Initialize the available table sizes and time slots
    time_slots = [f"{hour % 12}:{minute:02d}" for hour in range(5, 8) for minute in range(0, 60, 15) if not (hour == 7 and minute > 0)]


    # Create a dictionary to track table reservations
    reservations = {time: {size: [list() for _ in range(number_of_tables[size])] for size in list(number_of_tables.keys())} for time in time_slots}

    # Function to find a nearby available slot
    def find_nearby_slot(preferred_slots, party_size):
        for time_slot in time_slots:
            if time_slot not in preferred_slots:
                for table_idx, table in enumerate(reservations[time_slot][party_size]):
                    if len(table) == 0:
                        subsequent_slots = get_subsequent_slots(time_slot)
                        valid_subsequent_slots = [slot for slot in subsequent_slots if slot in reservations]
                        all_slots_free = all([len(reservations[slot][party_size][table_idx]) == 0 for slot in valid_subsequent_slots])
                        if all_slots_free:
                            return time_slot, table_idx
        return None, None

    # Function to return the subsequent slots covering the specified duration
    def get_subsequent_slots(time_slot):
        start_time = datetime.strptime(time_slot, "%H:%M")
        end_time = start_time + timedelta(hours=reservation_time)
        current_time = start_time
        subsequent_slots_list = []
        
        while current_time < end_time:
            current_time += timedelta(minutes=15)
            # Format the time without leading zeros for hours less than 10
            formatted_time = current_time.strftime("%-H:%M") if sys.platform != "win32" else current_time.strftime("%#H:%M")
            subsequent_slots_list.append(formatted_time)
        
        return subsequent_slots_list[:-1]

    # Randomly select people from the list
    # selected_people = df.sample(n=num_reservations)

    # Function to adjust weight
    def calculate_probability_weight(times_applied, recent_reservation):
        # Give 50% chance if selected within the past 4 pop-ups
        if recent_reservation <= 4:
            return 0.5
        
        # Exponentially increase chance to be selected given number of times applied
        weight_applied = 1 + (times_applied - 1) * times_applied
        return weight_applied

    # Apply the function to the entire dataframe and get the weights
    df['probability_weight'] = df.apply(lambda row: calculate_probability_weight(row['times_applied'], row['recent_reservation']), axis=1)

    # Normalize the weights
    total_weight = df['probability_weight'].sum()
    df['normalized_weight'] = df['probability_weight'] / total_weight

    # Randomly select people based on the normalized weights
    selected_people = df.sample(n=num_reservations, weights=df['normalized_weight'])

    # Iterate through selected people and find space for them in reservations schedule
    for idx, person in selected_people.iterrows():

        # Edge cases
        if not person['time_slots'] or not person['party_sizes']:
            print(f"Skipping {person['name']} due to missing preferred slots or party sizes.")
            continue

        allocated = False

        # Iterate through selected time slots
        for time_slot in [slot for slot in person['time_slots'] if slot in reservations]:
            for party_size in person['party_sizes']:

                # Iterate through selected party sizes
                for table_idx in range(len(reservations[time_slot][party_size])):
                    if len(reservations[time_slot][party_size][table_idx]) == 0:

                        # Check that table is available for full duration and mark table as reserved
                        subsequent_slots = get_subsequent_slots(time_slot)
                        valid_subsequent_slots = [slot for slot in subsequent_slots if slot in list(reservations.keys())]
                        all_slots_free = all([len(reservations[slot][party_size][table_idx]) == 0 for slot in valid_subsequent_slots])
                        if all_slots_free:
                            reservations[time_slot][party_size][table_idx] = [person]
                            for slot in (valid_subsequent_slots):
                                if datetime.strptime(slot, "%H:%M") > datetime.strptime("7:00", "%H:%M"):
                                    break
                                reservations[slot][party_size][table_idx] = [person]
                            print(f"Allocated {person['name']} at {time_slot} for a party size of {party_size} at table: {table_idx} ")  # Debug info
                            allocated = True
                            break
                        table_idx+= 1
                if allocated:
                    break
            if allocated:
                break

        # Edge case where no exact match is found
        if not allocated:
                
            # Try to allocate a nearby slot if preferred slots are not available
                for party_size in person['party_sizes']:
                    nearby_slot, table_idx = find_nearby_slot(person['time_slots'], party_size)
                    if nearby_slot:
                        subsequent_slots = get_subsequent_slots(nearby_slot)
                        reservations[nearby_slot][party_size][table_idx] = [person]
                        for slot in subsequent_slots:

                            # Ensure that the time does not exceed 7:00
                            if datetime.strptime(slot, "%H:%M") > datetime.strptime("7:00", "%H:%M"):
                                break
                            reservations[slot][party_size][table_idx] = [person]
                        print(f"Couldn't find exact match, so allocated {person['name']} at {nearby_slot} for a party size of {party_size} at table: {table_idx} ")  # Debug info
                        allocated = True
                        break
        
        # No available slot 
        if not allocated:
            print(f"Failed to allocate for {person['name']}!") 



    # Organize and print selected tables
    columns = [f"Table {size} - {i+1}" for size in list(number_of_tables.keys()) for i in range(number_of_tables[size])]
    reservation_df = pd.DataFrame(index=time_slots, columns=columns)

    reservation_df = reservation_df.fillna("")

    # Populate DataFrame to be printed
    for time, sizes in reservations.items():
        for size, tables in sizes.items():
            for idx, table in enumerate(tables):
                if table:
                    column_name = f"Table {size} - {idx+1}"
                    reservation_df.at[time, column_name] = table[0]['name']

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.axis('off')

    reserved_color = "lightblue"
    available_color = "lightgray"

    # Draw table cell borders and background color
    for i in range(len(time_slots) + 1):
        ax.axhline(i, color='black', linewidth=1)
    for j in range(len(columns) + 1):
        ax.axvline(j, color='black', linewidth=1)

    # Display table values
    for i, idx in enumerate(reservation_df.index):
        for j, col in enumerate(reservation_df.columns):
            cell_value = reservation_df.at[idx, col]
            cell_color = reserved_color if cell_value else available_color
            rect = plt.Rectangle((j, len(time_slots) - i - 1), 1, 1, facecolor=cell_color)
            ax.add_patch(rect)
            if cell_value:
                ax.text(j + 0.5, len(time_slots) - i - 0.5, cell_value, ha='center', va='center', color='black')

    # Display column titles
    for j, col in enumerate(reservation_df.columns):
        ax.text(j + 0.5, len(time_slots), col, ha='center', va='center', fontweight='bold', color='black')

    # Display row titles
    for i, idx in enumerate(reservation_df.index):
        ax.text(-0.5, len(time_slots) - i - 0.5, idx, ha='center', va='center', fontweight='bold', color='black')

    plt.show()

    # Alternate printing options:
    #
    # for time_slot, tables in reservations.items():
    #     for table_size, table_list in tables.items():
    #         for i, table in enumerate(table_list):
    #             if len(table) > 0:
    #                 print(f"\nTime slot: {time_slot}, Table size: {table_size}, Table #{i+1}, Reservations: {reservations[time_slot][table_size][i][0]['name']}")
    # print(reservations)



if __name__ == "__main__":
    neildraw()