import pandas as pd
import numpy as np
import os
import re


def clean_column_name(col: str) -> str:
    """Clean column names: remove newlines, extra spaces, trim."""
    if not isinstance(col, str):
        return str(col)
    # Replace newlines and multiple spaces with single space
    col = re.sub(r'\s+', ' ', col).strip()
    return col


def normalize(table: pd.DataFrame, source: str) -> pd.DataFrame: 
    """
    Normalize input DataFrame to global ALIGN format.
    Handles messy multi-line column names from CIQUAL.
    """
    # === Load reference CSV ===
    ref_path = os.path.join(os.path.dirname(__file__), 'reference.csv') \
               if '__file__' in globals() else '/home/workdir/attachments/reference.csv'
    
    link = pd.read_csv(ref_path, sep=';')
    
    # Clean reference
    link.columns = link.columns.str.strip()
    for col in link.columns:
        if link[col].dtype == "object":
            link[col] = link[col].str.strip()
    
    # === Find source column ===
    source = str(source).strip()
    source_col = next((col for col in link.columns if col.lower() == source.lower()), None)
    if source_col is None:
        raise ValueError(f"Source '{source}' not found.")

    # Build mapping from ALIGN to source column (cleaned)
    mapping = {}
    for _, row in link.iterrows():
        align_col = clean_column_name(row['ALIGN'])
        src_name = clean_column_name(row[source_col]) if pd.notna(row[source_col]) else ""
        if src_name and src_name.lower() != "none":
            mapping[align_col] = src_name
        else:
            mapping[align_col] = None

    align_columns = [clean_column_name(col) for col in link['ALIGN']]

    # === Clean input table columns ===
    if table.empty:
        align_df = pd.DataFrame(columns=['source'] + align_columns)
        return align_df

    table = table.copy()
    table.columns = [clean_column_name(col) for col in table.columns]

    # === Build normalized DataFrame ===
    rows = []
    for _, row in table.iterrows():
        new_row = {}
        for align_col in align_columns:
            src_col = mapping.get(align_col)
            if src_col and src_col in table.columns:
                val = row[src_col]
                # Convert French decimal comma to dot if needed
                if isinstance(val, str) and ',' in val and not any(c.isalpha() for c in val):
                    val = val.replace(',', '.')
                new_row[align_col] = val
            else:
                new_row[align_col] = np.nan
        rows.append(new_row)

    align_df = pd.DataFrame(rows, columns=align_columns)
    
    # Insert source as first column
    align_df.insert(0, 'source', source.upper())
    
    # Smart Name fallback
    if align_df['Name'].isna().all() or align_df['Name'].eq('').all():
        name_candidates = ['alim_nom_fr', 'Name', 'name', 'product_name', 'description', 'alim_nom_fr']
        for cand in name_candidates:
            if cand in table.columns:
                align_df['Name'] = table[cand].values
                break

    return align_df