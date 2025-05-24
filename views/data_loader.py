import pandas as pd

def load_sheets(excel_file_path, selected_sheets):
    xls = pd.ExcelFile(excel_file_path)
    df_list = []
    for sheet in selected_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        df["Series"] = sheet
        df_list.append(df)
    return pd.concat(df_list, ignore_index=True)