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

# Function to update vehicle details
def update_vehicle_details(vehicle_id, name, details):
    data = load_data()
    for vehicle in data["vehicles"]:
        if vehicle["id"] == vehicle_id:
            vehicle["name"] = name
            vehicle["details"] = details
            break
    save_data(data)

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
    app_mode = st.sidebar.radio("Choose the app mode", ["View Vehicles", "Add Vehicle", "Edit Vehicle", "Add Part", "Edit Part"])

    if app_mode == "View Vehicles":
        view_vehicles()
    elif app_mode == "Add Vehicle":
        add_vehicle_form()
    elif app_mode == "Edit Vehicle":
        edit_vehicle()
    elif app_mode == "Add Part":
        add_part()
    elif app_mode == "Edit Part":
        edit_part()

def view_vehicles():
    data = load_data()
    vehicles = data["vehicles"]

    st.header("Vehicle List")

    if not vehicles:
        st.info("No vehicles found. Please add a vehicle.")
        return

    for idx, vehicle in enumerate(vehicles, start=1):
        with st.expander(f"{idx}. {vehicle['name']}"):
            st.write(f"**Details:** {vehicle['details']}")
            st.markdown("**Parts:**")
            parts = vehicle.get("parts", [])
            if parts:
                parts_df = pd.DataFrame(parts)
                parts_df['Total Cost'] = parts_df['quantity'] * parts_df['unit_cost']
                st.dataframe(parts_df[['part_name', 'description', 'quantity', 'unit_cost', 'Total Cost']])
                grand_total = parts_df['Total Cost'].sum()
                st.markdown(f"**Grand Total:** ${grand_total:,.2f}")
            else:
                st.info("No parts added yet.")

def add_vehicle_form():
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
                st.experimental_rerun()

def edit_vehicle():
    data = load_data()
    vehicles = data["vehicles"]

    st.header("Edit Vehicle Details")

    if not vehicles:
        st.info("No vehicles found. Please add a vehicle first.")
        return

    vehicle_names = [vehicle["name"] for vehicle in vehicles]
    selected_vehicle_name = st.selectbox("Select a vehicle to edit", ["-- Select --"] + vehicle_names)

    if selected_vehicle_name != "-- Select --":
        vehicle = next((v for v in vehicles if v["name"] == selected_vehicle_name), None)
        if vehicle:
            with st.form("edit_vehicle_form"):
                new_name = st.text_input("Vehicle Name", value=vehicle["name"], max_chars=50)
                new_details = st.text_area("Vehicle Details", value=vehicle["details"], height=100)
                submitted = st.form_submit_button("Update Vehicle")
                if submitted:
                    if new_name.strip() == "":
                        st.error("Vehicle name cannot be empty.")
                    else:
                        update_vehicle_details(vehicle["id"], new_name, new_details)
                        st.success(f"Vehicle '{new_name}' updated successfully!")
                        st.experimental_rerun()

def add_part():
    data = load_data()
    vehicles = data["vehicles"]

    st.header("Add New Part to a Vehicle")

    if not vehicles:
        st.info("No vehicles found. Please add a vehicle first.")
        return

    vehicle_names = [vehicle["name"] for vehicle in vehicles]
    selected_vehicle_name = st.selectbox("Select a vehicle to add a part to", ["-- Select --"] + vehicle_names)

    if selected_vehicle_name != "-- Select --":
        vehicle = next((v for v in vehicles if v["name"] == selected_vehicle_name), None)
        if vehicle:
            with st.form("add_part_form"):
                part_name = st.text_input("Part Name")
                description = st.text_input("Description")
                quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
                unit_cost = st.number_input("Unit Cost ($)", min_value=0.0, step=0.1, value=0.0)
                submitted = st.form_submit_button("Add Part")
                if submitted:
                    if part_name.strip() == "":
                        st.error("Part name cannot be empty.")
                    else:
                        # Check if part already exists
                        if part_name in [part["part_name"] for part in vehicle["parts"]]:
                            st.error(f"Part '{part_name}' already exists in '{vehicle['name']}'. Please use the Edit Part section to update it.")
                        else:
                            new_part = {
                                "part_name": part_name,
                                "description": description,
                                "quantity": quantity,
                                "unit_cost": unit_cost
                            }
                            vehicle["parts"].append(new_part)
                            update_vehicle_parts(vehicle["id"], vehicle["parts"])
                            st.success(f"Part '{part_name}' added to '{vehicle['name']}' successfully!")
                            st.experimental_rerun()

def edit_part():
    data = load_data()
    vehicles = data["vehicles"]

    st.header("Edit Existing Part of a Vehicle")

    if not vehicles:
        st.info("No vehicles found. Please add a vehicle first.")
        return

    vehicle_names = [vehicle["name"] for vehicle in vehicles]
    selected_vehicle_name = st.selectbox("Select a vehicle to edit a part", ["-- Select --"] + vehicle_names)

    if selected_vehicle_name != "-- Select --":
        vehicle = next((v for v in vehicles if v["name"] == selected_vehicle_name), None)
        if vehicle:
            parts = vehicle.get("parts", [])
            if not parts:
                st.info(f"No parts found for vehicle '{vehicle['name']}'. Please add a part first.")
                return

            part_names = [part["part_name"] for part in parts]
            selected_part_name = st.selectbox("Select a part to edit", ["-- Select --"] + part_names)

            if selected_part_name != "-- Select --":
                part = next((p for p in parts if p["part_name"] == selected_part_name), None)
                if part:
                    with st.form("edit_part_form"):
                        new_description = st.text_input("Description", value=part["description"])
                        new_quantity = st.number_input("Quantity", min_value=1, step=1, value=part["quantity"])
                        new_unit_cost = st.number_input("Unit Cost ($)", min_value=0.0, step=0.1, value=part["unit_cost"])
                        submitted = st.form_submit_button("Update Part")
                        if submitted:
                            if new_description.strip() == "":
                                st.error("Description cannot be empty.")
                            else:
                                # Update part details
                                part["description"] = new_description
                                part["quantity"] = new_quantity
                                part["unit_cost"] = new_unit_cost
                                update_vehicle_parts(vehicle["id"], parts)
                                st.success(f"Part '{selected_part_name}' updated successfully!")
                                st.experimental_rerun()

def delete_vehicle_confirmation(vehicle_id):
    confirm = st.checkbox("Are you sure you want to delete this vehicle?", key=f"delete_confirm_{vehicle_id}")
    if confirm:
        if st.button("Confirm Delete", key=f"confirm_delete_{vehicle_id}"):
            delete_vehicle(vehicle_id)
            st.success("Vehicle deleted successfully!")
            st.experimental_rerun()

def delete_part_confirmation(vehicle, part_name, index):
    if st.button(f"Delete Part: {part_name}", key=f"delete_part_{index}"):
        vehicle["parts"] = [part for part in vehicle["parts"] if part["part_name"] != part_name]
        update_vehicle_parts(vehicle["id"], vehicle["parts"])
        st.success(f"Part '{part_name}' deleted successfully!")
        st.experimental_rerun()

if __name__ == "__main__":
    main()
