#!/usr/bin/env python3
"""Update Pile Dashboard Data from Excel to JSON"""

import pandas as pd
import json
import os

EXCEL_FILE = r'C:\Users\panup\The Siam Cement Public Company Limited\B-26-6530_RISE Project - STC-REPCO\1.STC to REPCO\5.Others\Pile Progress Summary\Pile Log VBA.xlsm'
JSON_FILE = r'D:\Daily Report\Rise-dashboard\Data\pile_data.json'

def update_data():
    try:
        print("📖 Reading Excel file...")

        df = pd.read_excel(EXCEL_FILE, sheet_name=0, header=0)
        header_row = df.iloc[0]
        df.columns = header_row
        df = df.iloc[1:].reset_index(drop=True)

        col_mapping = {
            'PILE \nNUMBER': 'pile_number',
            'N': 'n',
            'E': 'e',
            'AREA': 'area',
            'RIG.': 'rig',
            'RIG.\nCode': 'rig_code',
            'TYPE': 'type',
            'SIZE': 'size',
            'LENGTH(m.)': 'length',
            'LENGTH(m.)\n(Actual)': 'actual_length',
            'แผนวันที่ตอก': 'planned_date',
            'วันที่ตอก': 'piled_date',
            'Weld \nInspection': 'weld_inspection',
            'REMARK': 'remark'
        }

        df.rename(columns=col_mapping, inplace=True)
        df['piled_date'] = pd.to_datetime(df['piled_date'], errors='coerce')
        df['planned_date'] = pd.to_datetime(df['planned_date'], errors='coerce')
        df['pile_number'] = pd.to_numeric(df['pile_number'], errors='coerce').fillna(0).astype(int)
        df['rig'] = pd.to_numeric(df['rig'], errors='coerce').fillna(0).astype(int)
        df['n'] = pd.to_numeric(df['n'], errors='coerce')
        df['e'] = pd.to_numeric(df['e'], errors='coerce')
        df['actual_length'] = pd.to_numeric(df['actual_length'], errors='coerce')

        df = df[df['pile_number'] > 0].reset_index(drop=True)

        def get_status(row):
            # Pilot piles (01-04) are always Completed
            if row['pile_number'] in [2068, 1527, 1177, 1263]:
                return 'Completed'

            remark = str(row['remark']).lower() if pd.notna(row['remark']) else ''

            # Check for Corrected keywords (piles that were corrected/reworked)
            if 'ตอกแซม' in remark or 'ซ่อม' in remark or 'ตอกใหม่' in remark:
                return 'Corrected'
            # Check for Defected
            elif pd.notna(row['remark']) and str(row['remark']).strip() not in ['nan', '']:
                return 'Defected'
            elif pd.notna(row['weld_inspection']) and row['weld_inspection'] == 'Accept':
                return 'Completed'
            elif pd.notna(row['piled_date']):
                return 'Completed'
            else:
                return 'Pending'

        df['status'] = df.apply(get_status, axis=1)

        df_export = df[['pile_number', 'n', 'e', 'area', 'rig', 'rig_code', 'type', 'size', 'length', 'actual_length', 'planned_date', 'piled_date', 'status', 'remark']].copy()
        df_export['planned_date'] = df_export['planned_date'].dt.strftime('%Y-%m-%d').where(pd.notna(df_export['planned_date']), '')
        df_export['piled_date'] = df_export['piled_date'].dt.strftime('%Y-%m-%d').where(pd.notna(df_export['piled_date']), '')
        df_export['remark'] = df_export['remark'].fillna('')
        df_export['rig'] = df_export['rig'].astype(int)
        df_export['type'] = df_export['type'].fillna('')

        data = df_export.to_dict(orient='records')

        # Convert NaN to None for JSON serialization
        for record in data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None

        # Save to JSON
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ Saved {len(data)} pile records to JSON")
        print(f"✓ File: {JSON_FILE}")

        # Statistics
        completed = sum(1 for p in data if p['status'] == 'Completed')
        pending = sum(1 for p in data if p['status'] == 'Pending')
        defected = sum(1 for p in data if p['status'] == 'Defected')
        corrected = sum(1 for p in data if p['status'] == 'Corrected')

        print(f"\n📊 Statistics:")
        print(f"  Total: {len(data)}")
        print(f"  Completed: {completed}")
        print(f"  Pending: {pending}")
        print(f"  Defected: {defected}")
        print(f"  Corrected: {corrected}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Piling Dashboard Data Updater")
    print("=" * 60)
    print()

    success = update_data()

    print()
    if success:
        print("✓ Update completed successfully!")
        print("➜ Refresh your browser to see the latest data")
    else:
        print("❌ Update failed. Check error messages above.")

    print()
    input("Press Enter to close...")
