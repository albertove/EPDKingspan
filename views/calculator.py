import streamlit as st
import pandas as pd

def show():
    st.title("Project CO2 Calculator")

    # Initialize session state for project details
    if 'project_details' not in st.session_state:
        st.session_state.project_details = {
            'company': '',
            'name': '',
            'location': '',
            'co2_budget': 0
        }
    if 'product_list' not in st.session_state:
        st.session_state.product_list = []

    # Load the Excel file and check column names
    excel_file_path = "data/Final_Powerpipe_with_Weight_Product_Filled.xlsx"
    xls = pd.ExcelFile(excel_file_path)
    
    # Get column names from the first sheet
    first_sheet = xls.sheet_names[0]
    df_sample = pd.read_excel(excel_file_path, sheet_name=first_sheet)
    actual_columns = df_sample.columns.tolist()
    
    # Store the actual column names in session state
    if 'actual_columns' not in st.session_state:
        st.session_state.actual_columns = actual_columns

    # Project Details Form
    with st.expander("Project Details", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.session_state.project_details['company'] = st.text_input(
                "Company Name",
                value=st.session_state.project_details['company'],
                placeholder="Enter company name"
            )
        with col2:
            st.session_state.project_details['name'] = st.text_input(
                "Project Name",
                value=st.session_state.project_details['name'],
                placeholder="Enter project name"
            )
        with col3:
            st.session_state.project_details['location'] = st.text_input(
                "Location",
                value=st.session_state.project_details['location'],
                placeholder="Enter project location"
            )
        with col4:
            st.session_state.project_details['co2_budget'] = st.number_input(
                "CO2 Budget (kg CO2 eq.)",
                min_value=0,
                value=int(st.session_state.project_details['co2_budget']),
                step=100
            )

    with st.container():
        st.subheader("Add Product to Project")
        col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

        with col1:
            # Get unique product types from all sheets
            all_types = set()
            all_series = set()
            for sheet in xls.sheet_names:
                df = pd.read_excel(excel_file_path, sheet_name=sheet)
                if 'Type' in df.columns:
                    all_types.update(df['Type'].unique())
                if 'Series' in df.columns:
                    all_series.update(df['Series'].unique())
            
            # Convert to sorted list for the selectbox
            product_types = sorted(list(all_types))
            selected_type = st.selectbox("Type:", options=product_types, key="calc_type")

        with col2:
            # Get series numbers for the selected type
            series_numbers = []
            for sheet in xls.sheet_names:
                df = pd.read_excel(excel_file_path, sheet_name=sheet)
                if 'Type' in df.columns and 'Series' in df.columns:
                    series_in_sheet = df[df['Type'] == selected_type]['Series'].unique()
                    series_numbers.extend(series_in_sheet)
            
            # Remove duplicates and sort
            series_numbers = sorted(list(set(series_numbers)))
            selected_series = st.selectbox("Series:", options=series_numbers, key="calc_series")

        with col3:
            # Get the sheet that contains the selected type and series
            selected_sheet = None
            for sheet in xls.sheet_names:
                df = pd.read_excel(excel_file_path, sheet_name=sheet)
                if 'Type' in df.columns and 'Series' in df.columns:
                    if ((df['Type'] == selected_type) & (df['Series'] == selected_series)).any():
                        selected_sheet = sheet
                        break
            
            if selected_sheet is None:
                st.error("Could not find data for the selected type and series")
                return
                
            df = pd.read_excel(excel_file_path, sheet_name=selected_sheet)
            
            # Filter DN values for the selected type and series
            dn_values = df[(df['Type'] == selected_type) & (df['Series'] == selected_series)]['DN'].unique()
            selected_dn = st.selectbox("DN:", options=dn_values, key="calc_dn")

        with col4:
            # Get the default length from the data
            try:
                # Find the length column name
                length_col = next((col for col in df.columns if 'length' in col.lower()), 'Length (m)')
                default_length = df[(df['Type'] == selected_type) & (df['DN'] == selected_dn)][length_col].iloc[0]
                product_length = st.number_input(
                    "Length (m):", 
                    min_value=0.1, 
                    value=float(default_length), 
                    step=0.1, 
                    key="calc_length"
                )
            except Exception as e:
                st.warning(f"Error getting length from data: {str(e)}. Using default value of 1.0m")
                product_length = st.number_input(
                    "Length (m):", 
                    min_value=0.1, 
                    value=1.0, 
                    step=0.1, 
                    key="calc_length"
                )

        with col5:
            quantity = st.number_input(
                "Quantity:", 
                min_value=1, 
                value=1, 
                step=1, 
                key="calc_quantity"
            )

        # Add button in a new row with status message
        button_col, status_col = st.columns([1, 5])
        with button_col:
            add_clicked = st.button("Add to Project", use_container_width=True)

        if add_clicked:
            try:
                # Get the correct sheet for the selected type and series
                selected_sheet = None
                for sheet in xls.sheet_names:
                    df = pd.read_excel(excel_file_path, sheet_name=sheet)
                    if 'Type' in df.columns and 'Series' in df.columns:
                        if ((df['Type'] == selected_type) & (df['Series'] == selected_series)).any():
                            selected_sheet = sheet
                            break
                
                if selected_sheet is None:
                    st.error("Could not find data for the selected type and series")
                    return
                
                # Load the correct sheet's data
                df = pd.read_excel(excel_file_path, sheet_name=selected_sheet)
                
                # Get the specific product data
                product_data = df[(df['Type'] == selected_type) & 
                                 (df['Series'] == selected_series) & 
                                 (df['DN'] == selected_dn)].iloc[0]
                
                try:
                    # Get the A1-A3 value from the correct column
                    a1a3_value = float(product_data['A1-A3 (kg CO2e)'])
                    # Calculate total CO2: A1-A3 × Length × Quantity
                    total_co2 = a1a3_value * product_length * quantity
                except (ValueError, TypeError) as e:
                    st.error(f"Error reading A1-A3 value: {str(e)}")
                    return

                new_product = {
                    'Type': selected_type,
                    'Series': selected_series,
                    'DN': selected_dn,
                    'Length': product_length,
                    'Quantity': quantity,
                    'Total CO2 (A1-A3)': round(total_co2, 0)  # No decimals
                }

                # Add new product at the beginning of the list
                st.session_state.product_list.insert(0, new_product)
                st.success("Product added to project!")
            except Exception as e:
                st.error(f"Error adding product: {str(e)}")

    st.subheader("Project Products")
    if st.session_state.product_list:
        col1, col2 = st.columns([4, 1])

        with col1:
            for idx, product in enumerate(st.session_state.product_list):
                cols = st.columns([1, 2, 1, 1, 1, 1, 2])
                with cols[0]:
                    if st.button("❌", key=f"delete_{idx}", help="Delete this product"):
                        st.session_state.product_list.pop(idx)
                        st.rerun()
                with cols[1]:
                    st.write(product['Type'])
                with cols[2]:
                    st.write(f"Series {product['Series']}")
                with cols[3]:
                    st.write(f"DN{product['DN']}")
                with cols[4]:
                    st.write(f"{product['Length']} m")
                with cols[5]:
                    st.write(f"{product['Quantity']}")
                with cols[6]:
                    st.write(f"{product['Total CO2 (A1-A3)']:.0f} kg CO2eq.")

        with col2:
            total_project_co2 = sum(product['Total CO2 (A1-A3)'] for product in st.session_state.product_list)
            
            # Display total CO2 and budget comparison
            st.metric(
                "Total Project CO2 (A1-A3)", 
                f"{total_project_co2:.0f} kg CO2eq.",
                delta_color="inverse"
            )
            
            if st.session_state.project_details['co2_budget'] > 0:
                budget_remaining = st.session_state.project_details['co2_budget'] - total_project_co2
                st.metric(
                    "Budget Remaining",
                    f"{budget_remaining:.0f} kg CO2eq.",
                    delta=f"{budget_remaining:.0f}",
                    delta_color="normal" if budget_remaining >= 0 else "inverse"
                )
                
                # Progress bar for budget usage
                budget_usage = min(total_project_co2 / st.session_state.project_details['co2_budget'], 1.0)
                st.progress(budget_usage, text=f"Budget Usage: {budget_usage*100:.1f}%")

            if st.button("Clear Project", use_container_width=True, type="secondary"):
                st.session_state.product_list = []
                st.rerun()
    else:
        st.info("No products added to the project yet.")
