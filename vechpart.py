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
            save_data(data)
            break

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
                st.experimental_rerun()

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
    st.markdown("### Add/Edit Parts")

    # Initialize session state for parts
    if "current_parts" not in st.session_state:
        st.session_state["current_parts"] = parts_df.copy()

    # Part input fields
    with st.form("parts_form"):
        part_name = st.text_input("Part Name")
        description = st.text_input("Description")
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
        unit_cost = st.number_input("Unit Cost ($)", min_value=0.0, step=0.1, value=0.0)
        add_part = st.form_submit_button("Add/Update Part")

        if add_part:
            if part_name.strip() == "":
                st.error("Part name cannot be empty.")
            else:
                # Check if part already exists
                existing = parts_df[parts_df['part_name'] == part_name]
                if not existing.empty:
                    # Update existing part
                    parts_df.loc[parts_df['part_name'] == part_name, 'description'] = description
                    parts_df.loc[parts_df['part_name'] == part_name, 'quantity'] = quantity
                    parts_df.loc[parts_df['part_name'] == part_name, 'unit_cost'] = unit_cost
                    st.success(f"Part '{part_name}' updated successfully!")
                else:
                    # Add new part
                    new_part = {
                        "part_name": part_name,
                        "description": description,
                        "quantity": quantity,
                        "unit_cost": unit_cost
                    }
                    parts_df = parts_df.append(new_part, ignore_index=True)
                    st.success(f"Part '{part_name}' added successfully!")

                # Update session state
                st.session_state["current_parts"] = parts_df.copy()
                st.experimental_rerun()

    # Allow editing of parts
    st.markdown("### Edit Existing Parts")
    edited_parts = st.experimental_data_editor(
        st.session_state["current_parts"],
        num_rows="dynamic",
        use_container_width=True,
        key="edited_parts"
    )

    if st.button("Save Changes to Parts"):
        # Update vehicle parts
        new_parts = edited_parts.to_dict(orient="records")
        update_vehicle_parts(vehicle["id"], new_parts)
        st.success("Parts updated successfully!")
        st.experimental_rerun()

    # Optionally, provide a button to delete the vehicle
    if st.button("Delete Vehicle", key="delete_vehicle"):
        confirm = st.warning("Are you sure you want to delete this vehicle?", icon="⚠️")
        if st.button("Yes, Delete", key="confirm_delete"):
            delete_vehicle(vehicle["id"])
            st.success("Vehicle deleted successfully!")
            st.experimental_rerun()

if __name__ == "__main__":
    main()
