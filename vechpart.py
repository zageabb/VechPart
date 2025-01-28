import streamlit as st
import json
import os
import uuid

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

# Streamlit App
def main():
    st.set_page_config(page_title="Vehicle Cost Manager", layout="wide")
    st.title("🚗 Vehicle Cost Manager")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox("Choose the app mode", ["Main", "Add Vehicle"])

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
    selected_vehicle = st.selectbox("Select a vehicle to view details", ["-- Select --"] + vehicle_names)

    if selected_vehicle != "-- Select --":
        # Find the selected vehicle
        vehicle = next((v for v in vehicles if v["name"] == selected_vehicle), None)
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

    # Initialize session state for parts
    if "current_parts" not in st.session_state:
        st.session_state["current_parts"] = parts

    # Define the columns for the editor
    columns = ["Part Name", "Description", "Quantity", "Unit Cost", "Total Cost"]
    
    # Prepare data for editor
    editor_data = []
    for part in st.session_state["current_parts"]:
        editor_data.append({
            "Part Name": part.get("part_name", ""),
            "Description": part.get("description", ""),
            "Quantity": part.get("quantity", 1),
            "Unit Cost": part.get("unit_cost", 0.0),
            "Total Cost": part.get("quantity", 1) * part.get("unit_cost", 0.0)
        })

    # Display editable table
    edited_data = st.data_editor(
        editor_data,
        num_rows="dynamic",
        column_config={
            "Part Name": st.column_config.TextColumn(),
            "Description": st.column_config.TextColumn(),
            "Quantity": st.column_config.NumberColumn(),
            "Unit Cost": st.column_config.NumberColumn(),
            "Total Cost": st.column_config.NumberColumn(visible=False)
        },
        key="parts_editor"
    )

    # Update total cost for each part
    for idx, row in edited_data.iterrows():
        try:
            qty = float(row["Quantity"])
        except:
            qty = 0
        try:
            unit = float(row["Unit Cost"])
        except:
            unit = 0
        edited_data.at[idx, "Total Cost"] = qty * unit

    # Calculate grand total
    grand_total = edited_data["Total Cost"].sum()

    st.markdown(f"**Grand Total:** ${grand_total:,.2f}")

    # Save changes
    if st.button("Save Changes"):
        # Prepare parts data to save
        new_parts = []
        for idx, row in edited_data.iterrows():
            if row["Part Name"].strip() == "":
                continue  # Skip empty rows
            new_part = {
                "part_name": row["Part Name"],
                "description": row["Description"],
                "quantity": row["Quantity"],
                "unit_cost": row["Unit Cost"]
            }
            new_parts.append(new_part)
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

def delete_vehicle(vehicle_id):
    data = load_data()
    data["vehicles"] = [v for v in data["vehicles"] if v["id"] != vehicle_id]
    save_data(data)

if __name__ == "__main__":
    main()
