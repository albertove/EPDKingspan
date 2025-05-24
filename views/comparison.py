import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_sheets

def compare_products(df1, df2, series, dimension, pipe_type1, pipe_type2):
    """
    Compare two products with the same series and dimension
    """
    # Filter both dataframes for the specified series and dimension
    product1 = df1[(df1['Series'] == series) & (df1['DN'] == dimension)].copy()
    product2 = df2[(df2['Series'] == series) & (df2['DN'] == dimension)].copy()
    
    if product1.empty or product2.empty:
        return None, "No matching products found for the selected criteria"
    
    # Add a source column to each
    product1['Source'] = 'recase' if 'recase' in str(pipe_type1).lower() else 'non-recase'
    product2['Source'] = 'recase' if 'recase' in str(pipe_type2).lower() else 'non-recase'
    
    # Combine the filtered dataframes
    combined = pd.concat([product1, product2])
    
    # Create labels for the products with recase information
    combined['Product'] = combined.apply(
        lambda row: f"{row['Series']} - DN{row['DN']} (Recase)" if row['Source'] == 'recase' else f"{row['Series']} - DN{row['DN']}",
        axis=1
    )
    
    return combined, None

def show():
    st.title("Kingspan EPD Dashboard")

    comparison_mode = st.radio(
        "Select mode:",
        ["Single Product View", "Compare Products"],
        horizontal=True
    )

    if comparison_mode == "Single Product View":
        pipe_type = st.selectbox("Select Pipe Type:", ["Single", "Twin", "Single Recase", "Twin Recase"])
        
        # Map pipe types to their corresponding Excel files
        file_mapping = {
            "Single": "data/EPD_singel_series_kingspan.xlsx",
            "Twin": "data/EPD_twin_series_kingspan.xlsx",
            "Single Recase": "data/EPD_singel_series_recase_kingspan.xlsx",
            "Twin Recase": "data/EPD_twin_series_recase_kingspan.xlsx"
        }
        
        excel_file_path = file_mapping[pipe_type]
        
        xls = pd.ExcelFile(excel_file_path)
        sheet_names = xls.sheet_names

        selected_sheets = st.multiselect(
            "Select one or more Series (Sheets) to display:",
            options=sheet_names,
            default=sheet_names
        )

        if not selected_sheets:
            st.warning("Please select at least one sheet.")
            return

        combined_df = load_sheets(excel_file_path, selected_sheets)
        
    else:  # Compare Products mode
        st.subheader("Select Products to Compare")
        
        # First product selection
        col1, col2 = st.columns(2)
        with col1:
            pipe_type1 = st.selectbox("Select First Pipe Type:", ["Single", "Single Recase", "Twin", "Twin Recase"])
            file1 = "data/EPD_singel_series_kingspan.xlsx" if pipe_type1 == "Single" else \
                   "data/EPD_singel_series_recase_kingspan.xlsx" if pipe_type1 == "Single Recase" else \
                   "data/EPD_twin_series_kingspan.xlsx" if pipe_type1 == "Twin" else \
                   "data/EPD_twin_series_recase_kingspan.xlsx"
            
            df1 = load_sheets(file1, pd.ExcelFile(file1).sheet_names)
            
        with col2:
            pipe_type2 = st.selectbox("Select Second Pipe Type:", ["Single", "Single Recase", "Twin", "Twin Recase"])
            file2 = "data/EPD_singel_series_kingspan.xlsx" if pipe_type2 == "Single" else \
                   "data/EPD_singel_series_recase_kingspan.xlsx" if pipe_type2 == "Single Recase" else \
                   "data/EPD_twin_series_kingspan.xlsx" if pipe_type2 == "Twin" else \
                   "data/EPD_twin_series_recase_kingspan.xlsx"
            
            df2 = load_sheets(file2, pd.ExcelFile(file2).sheet_names)
        
        # Get common series and dimensions
        common_series = list(set(df1['Series'].unique()) & set(df2['Series'].unique()))
        if not common_series:
            st.error("No common series found between the selected products")
            return
            
        selected_series = st.selectbox("Select Series:", common_series)
        
        # Get dimensions for the selected series
        dimensions1 = df1[df1['Series'] == selected_series]['DN'].unique()
        dimensions2 = df2[df2['Series'] == selected_series]['DN'].unique()
        common_dimensions = sorted(list(set(dimensions1) & set(dimensions2)))
        
        if not common_dimensions:
            st.error("No common dimensions found for the selected series")
            return
            
        selected_dimension = st.selectbox("Select Dimension:", common_dimensions)
        
        # Compare the products
        combined_df, error = compare_products(df1, df2, selected_series, selected_dimension, pipe_type1, pipe_type2)
        if error:
            st.error(error)
            return

    # Common code for both modes
    all_columns = list(combined_df.columns)
    selected_columns = st.multiselect(
        "Select columns to view in the table:",
        options=all_columns,
        default=all_columns
    )

    if not selected_columns:
        st.warning("No columns selected for the table. Please pick at least one.")
        return

    display_df = combined_df[selected_columns]

    st.subheader("Filter")
    dimension_col = st.selectbox(
        "Select a column to filter or choose 'No filter':",
        options=["No filter"] + selected_columns,
        index=0
    )

    if dimension_col != "No filter":
        unique_values = display_df[dimension_col].dropna().unique().tolist()
        unique_values.sort()
        selected_value = st.selectbox(f"Select a value in '{dimension_col}':", unique_values)
        display_df = display_df[display_df[dimension_col] == selected_value]

    st.subheader("Resulting Table")
    st.dataframe(display_df, use_container_width=True)

    st.subheader("Create a Bar Chart - Compare Selected Rows")

    bar_chart_candidates = ["A1", "A2", "A3", "A1–A3", "A4", "A5", "B1-B7", "C1", "C2", "C3", "C4","D"]
    available_for_bar = [c for c in bar_chart_candidates if c in display_df.columns]

    selected_bar_cols = st.multiselect(
        "Select impact categories for the Bar Chart:",
        options=available_for_bar,
        default=available_for_bar
    )

    # Create row labels for selection using the Product column
    row_labels = display_df['Product'] if 'Product' in display_df.columns else display_df.apply(
        lambda row: f"DN{row['DN']} - {row['Series']} {'(Recase)' if (comparison_mode == 'Compare Products' and (('recase' in str(pipe_type1).lower() and getattr(row, 'source_file', None) == 'file1') or ('recase' in str(pipe_type2).lower() and getattr(row, 'source_file', None) == 'file2'))) or (comparison_mode != 'Compare Products' and 'recase' in str(pipe_type).lower()) else ''}" if 'DN' in row and 'Series' in row else str(row.name),
        axis=1
    )
    
    # Create a mapping of labels to indices
    label_to_index = dict(zip(row_labels, display_df.index))
    
    selected_labels = st.multiselect(
        "Select one or more rows to visualize in the chart:",
        options=row_labels,
        default=[],
        format_func=lambda x: x
    )
    
    # Convert selected labels back to indices
    selected_rows = [label_to_index[label] for label in selected_labels]

    chart_type = st.radio(
        "Select chart type:",
        ["Bar Chart", "Line Chart"],
        horizontal=True
    )

    if st.button("Create Chart"):
        if not selected_bar_cols:
            st.warning("Please select at least one impact category for the chart.")
        elif not selected_rows:
            st.warning("Please select at least one row to display in the chart.")
        else:
            # Get the data for the chart
            df_for_chart = display_df.loc[selected_rows, selected_bar_cols]
            
            # Get the labels from the Product column
            row_labels = display_df.loc[selected_rows]['Product'] if 'Product' in display_df.columns else display_df.loc[selected_rows].apply(
                lambda row: f"DN{row['DN']} - {row['Series']} {'(Recase)' if (comparison_mode == 'Compare Products' and (('recase' in str(pipe_type1).lower() and getattr(row, 'source_file', None) == 'file1') or ('recase' in str(pipe_type2).lower() and getattr(row, 'source_file', None) == 'file2'))) or (comparison_mode != 'Compare Products' and 'recase' in str(pipe_type).lower()) else ''}" if 'DN' in row and 'Series' in row else str(row.name),
                axis=1
            )
            
            # Convert selected columns to numeric, coercing errors to NaN
            df_for_chart[selected_bar_cols] = df_for_chart[selected_bar_cols].apply(pd.to_numeric, errors='coerce')
            df_for_chart['Total'] = df_for_chart[selected_bar_cols].sum(axis=1)
            
            # Add the row labels to the chart dataframe
            df_for_chart['RowID'] = row_labels
            
            df_for_chart_melted = df_for_chart.melt(
                id_vars=['RowID', 'Total'],
                value_vars=selected_bar_cols,
                var_name='Category',
                value_name='Value'
            )

            # Add the total to the melted DataFrame
            df_for_chart_melted = pd.concat([
                df_for_chart_melted,
                pd.DataFrame({
                    'RowID': df_for_chart['RowID'],
                    'Category': 'Total',
                    'Value': df_for_chart['Total']
                })
            ])

            # Create the figure based on selected chart type
            if chart_type == "Bar Chart":
                fig = px.bar(
                    df_for_chart_melted,
                    x='Category',
                    y='Value',
                    color='RowID',
                    barmode='group',
                    title='Comparison of Selected Rows',
                    labels={'RowID': 'Pipe Specification'}
                )
            else:  # Line Chart
                fig = px.line(
                    df_for_chart_melted,
                    x='Category',
                    y='Value',
                    color='RowID',
                    markers=True,
                    title='Comparison of Selected Rows',
                    labels={'RowID': 'Pipe Specification'}
                )

            # Update layout to make the chart more readable
            fig.update_layout(
                showlegend=True,
                legend_title_text='Pipe Specification',
                xaxis_title='Impact Category',
                yaxis_title='Value',
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)