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

    # Define the columns for the editor (excluding 'Total Cost')
    columns = ["Part Name", "Description", "Quantity", "Unit Cost"]
    
    # Prepare data for editor
    editor_data = []
    for part in st.session_state["current_parts"]:
        editor_data.append({
            "Part Name": part.get("part_name", ""),
            "Description": part.get("description", ""),
            "Quantity": part.get("quantity", 1),
            "Unit Cost": part.get("unit_cost", 0.0),
        })

    # Display editable table without 'Total Cost'
    edited_data = st.data_editor(
        editor_data,
        num_rows="dynamic",
        column_config={
            "Part Name": st.column_config.TextColumn(),
            "Description": st.column_config.TextColumn(),
            "Quantity": st.column_config.NumberColumn(),
            "Unit Cost": st.column_config.NumberColumn(),
        },
        key="parts_editor"
    )

    # Calculate total cost for each part and grand total
    grand_total = 0.0
    for idx, row in edited_data.iterrows():
        try:
            qty = float(row["Quantity"])
        except:
            qty = 0
        try:
            unit = float(row["Unit Cost"])
        except:
            unit = 0
        total_cost = qty * unit
        grand_total += total_cost
        st.write(f"**Total Cost for Part {idx + 1}:** ${total_cost:,.2f}")

    st.markdown(f"### **Grand Total:** ${grand_total:,.2f}")

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
