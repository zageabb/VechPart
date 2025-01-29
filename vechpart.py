import streamlit as st
import json
import os
import uuid
import pandas as pd

# Define the path for the data file
DATA_FILE = "data.json"

# Initialize data if not present
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"vehicles": []}, f)

# Function to load data
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Function to save data
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Function to add a new vehicle
def add_vehicle(name, details):
    data = load_data()
    vehicle = {
        "id": str(uuid.uuid4()),
        "name": name,
        "details": details,
        "parts": []
    }
    data["vehicles"].append(vehicle)
    save_data(data)

# Function to get vehicle by ID
def get_vehicle(vehicle_id):
    data = load_data()
    for vehicle in data["vehicles"]:
        if vehicle["id"] == vehicle_id:
            return vehicle
    return None

# Function to update vehicle parts
def update_vehicle_parts(vehicle_id, parts):
    data = load_data()
    for vehicle in data["vehicles"]:
        if vehicle["id"] == vehicle_id:
            vehicle["parts"] = parts
            break
    save_data(data)

# Function to delete a vehicle
def delete_vehicle(vehicle_id):
    data = load_data()
    data["vehicles"] = [v for v in data["vehicles"] if v["id"] != vehicle_id]
    save_data(data)

# Streamlit App
def main():
    st.set_page_config(page_title="Vehicle Cost Manager", layout="wide")
    st.title("🚗 Vehicle Cost Manager")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose the app mode", ["Main", "Add Vehicle"])

    if app_mode == "Main":
        show_main_screen()
    elif app_mode == "Add Vehicle":
        show_add_vehicle_screen()

def show_main_screen():
    data = load_data()
    vehicles = data["vehicles"]

    st.header("Vehicle List")

    if not vehicles:
        st.info("No vehicles found. Please add a vehicle.")
        return

    # Display vehicles in a selectable list
    vehicle_names = [vehicle["name"] for vehicle in vehicles]
    selected_vehicle_name = st.selectbox("Select a vehicle to view details", ["-- Select --"] + vehicle_names)

    if selected_vehicle_name != "-- Select --":
        # Find the selected vehicle
        vehicle = next((v for v in vehicles if v["name"] == selected_vehicle_name), None)
        if vehicle:
            show_vehicle_details(vehicle)

def show_add_vehicle_screen():
    st.header("Add New Vehicle")
    with st.form("add_vehicle_form"):
        name = st.text_input("Vehicle Name", max_chars=50)
        details = st.text_area("Vehicle Details", height=100)
        submitted = st.form_submit_button("Add Vehicle")
        if submitted:
            if name.strip() == "":
                st.error("Vehicle name cannot be empty.")
            else:
                add_vehicle(name, details)
                st.success(f"Vehicle '{name}' added successfully!")
                # After form submission, Streamlit naturally reruns the script

def show_vehicle_details(vehicle):
    st.subheader(f"Details for: {vehicle['name']}")
    st.text_area("Vehicle Details", value=vehicle["details"], height=100, disabled=True)

    st.markdown("### Parts and Costs")

    # Prepare parts data
    parts = vehicle.get("parts", [])
    if not parts:
        parts = []

    # Convert parts to DataFrame for easier handling
    parts_df = pd.DataFrame(parts)
    if parts_df.empty:
        parts_df = pd.DataFrame(columns=["part_name", "description", "quantity", "unit_cost"])

    # Display parts table with Total Cost
    st.markdown("#### Existing Parts")
    if not parts_df.empty:
        parts_df['Total Cost'] = parts_df['quantity'] * parts_df['unit_cost']
        st.dataframe(parts_df[['part_name', 'description', 'quantity', 'unit_cost', 'Total Cost']])
        grand_total = parts_df['Total Cost'].sum()
        st.markdown(f"**Grand Total:** ${grand_total:,.2f}")
    else:
        st.info("No parts added yet.")

    st.markdown("---")
    st.markdown("### Add New Part")

    # Form to add a new part
    with st.form("add_part_form"):
        part_name = st.text_input("Part Name")
        description = st.text_input("Description")
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
        unit_cost = st.number_input("Unit Cost ($)", min_value=0.0, step=0.1, value=0.0)
        add_part = st.form_submit_button("Add Part")

        if add_part:
            if part_name.strip() == "":
                st.error("Part name cannot be empty.")
            else:
                # Check if part already exists
                if part_name in parts_df['part_name'].values:
                    st.error(f"Part '{part_name}' already exists. Please use the edit functionality to update it.")
                else:
                    # Add new part
                    new_part = {
                        "part_name": part_name,
                        "description": description,
                        "quantity": quantity,
                        "unit_cost": unit_cost
                    }
                    parts_df = parts_df.append(new_part, ignore_index=True)
                    update_vehicle_parts(vehicle['id'], parts_df.to_dict(orient='records'))
                    st.success(f"Part '{part_name}' added successfully!")
                    # After form submission, Streamlit naturally reruns the script

    st.markdown("---")
    st.markdown("### Edit or Delete Existing Parts")

    if not parts_df.empty:
        for index, row in parts_df.iterrows():
            with st.expander(f"{row['part_name']}"):
                st.write(f"**Description:** {row['description']}")
                st.write(f"**Quantity:** {row['quantity']}")
                st.write(f"**Unit Cost:** ${row['unit_cost']:.2f}")
                st.write(f"**Total Cost:** ${row['quantity'] * row['unit_cost']:.2f}")

                # Form to edit part
                with st.form(f"edit_part_form_{index}"):
                    new_description = st.text_input("Description", value=row['description'])
                    new_quantity = st.number_input(
                        "Quantity", 
                        min_value=1, 
                        step=1, 
                        value=row['quantity'], 
                        key=f"quantity_{index}"
                    )
                    new_unit_cost = st.number_input(
                        "Unit Cost ($)", 
                        min_value=0.0, 
                        step=0.1, 
                        value=row['unit_cost'], 
                        key=f"unit_cost_{index}"
                    )
                    update_part = st.form_submit_button("Update Part")

                    if update_part:
                        parts_df.at[index, 'description'] = new_description
                        parts_df.at[index, 'quantity'] = new_quantity
                        parts_df.at[index, 'unit_cost'] = new_unit_cost
                        update_vehicle_parts(vehicle['id'], parts_df.to_dict(orient='records'))
                        st.success(f"Part '{row['part_name']}' updated successfully!")
                        # After form submission, Streamlit naturally reruns the script

                # Button to delete part
                delete_key = f"delete_part_{index}"
                if st.button(f"Delete Part: {row['part_name']}", key=delete_key):
                    parts_df = parts_df.drop(index).reset_index(drop=True)
                    update_vehicle_parts(vehicle['id'], parts_df.to_dict(orient='records'))
                    st.success(f"Part '{row['part_name']}' deleted successfully!")
                    # After button click, Streamlit naturally reruns the script

    st.markdown("---")
    # Optionally, provide a button to delete the vehicle
    st.markdown("### Delete Vehicle")
    if st.button("Delete Vehicle", key="delete_vehicle"):
        confirm = st.checkbox("Are you sure you want to delete this vehicle?")
        if confirm:
            delete_vehicle(vehicle["id"])
            st.success("Vehicle deleted successfully!")
            # After interaction, Streamlit naturally reruns the script

if __name__ == "__main__":
    main()
