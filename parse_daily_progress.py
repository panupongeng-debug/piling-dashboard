#!/usr/bin/env python3
"""Parse Daily Progress Text Files to JSON"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

DAILY_PROGRESS_DIR = r'C:\Users\panup\The Siam Cement Public Company Limited\INTERNAL_B-26-6530_RISE Project - INTERNAL (P&C Package)\08.Construction\04.PICTURE PROGRESS'
JSON_FILE = r'D:\Daily Report\Rise-dashboard\Data\daily_progress_data.json'

def parse_daily_report(file_path):
    """Parse a single daily report text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract date from filename (DDMMYY format or DDMMYY[AM])
        filename = os.path.basename(file_path)

        # Try to match DDMMYY[AM] first
        date_match = re.search(r'(\d{6})[AM]', filename)

        # If not found, try to match just DDMMYY (for files without M/A suffix)
        if not date_match:
            date_match = re.search(r'(\d{6})', filename)

        # Determine shift: A=Afternoon, M=Morning, or Daily Report (no M/A)
        is_afternoon = filename.endswith('A.txt')
        is_morning = filename.endswith('M.txt')

        if is_afternoon:
            shift = 'Afternoon'
        elif is_morning:
            shift = 'Morning'
        else:
            shift = 'Daily Report'  # No M/A suffix = full day report

        # Format date as DD/MM/YY
        date_str = ''
        if date_match:
            ddmmyy = date_match.group(1)
            date_str = f"{ddmmyy[0:2]}/{ddmmyy[2:4]}/{ddmmyy[4:6]}"

        data = {
            'date': date_str,
            'shift': shift,
            'weather': '',
            'repco_personnel': 0,
            'state_workers_m': 0,
            'state_workers_w': 0,
            'state_workers_total': 0,
            'equipment': [],
            'activity_goals': [],
            'progress': [],
            'photos': 0,
            'hours': 0
        }

        # Parse Weather
        weather_match = re.search(r'🌤️\s*(.+?)(?:\n|$)', content)
        if weather_match:
            data['weather'] = weather_match.group(1).strip()

        # Parse Time (hours)
        time_match = re.search(r'⏱\s*(\d+):(\d+)\s*–\s*(\d+):(\d+)\s*\((\d+)\s*hrs?\)', content)
        if time_match:
            data['hours'] = int(time_match.group(5))

        # Parse REPCO Personnel
        repco_match = re.search(r'👨‍💼\s*REPCO PERSONNEL.*?รวม:\s*(\d+)', content, re.DOTALL)
        if repco_match:
            data['repco_personnel'] = int(repco_match.group(1))

        # Parse State Personnel
        state_section = re.search(r'👥\s*STATE PERSONNEL(.*?)(?=🚜|$)', content, re.DOTALL)
        if state_section:
            state_text = state_section.group(1)
            m_match = re.search(r'Worker\s*\(M\)\s*:(\d+)', state_text)
            w_match = re.search(r'Worker\s*\(W\)\s*:(\d+)', state_text)
            total_match = re.search(r'รวม:\s*(\d+)', state_text)

            if m_match:
                data['state_workers_m'] = int(m_match.group(1))
            if w_match:
                data['state_workers_w'] = int(w_match.group(1))
            if total_match:
                data['state_workers_total'] = int(total_match.group(1))

        # Parse Equipment
        equipment_section = re.search(r'🚜\s*EQUIPMENT(.*?)(?=🎯|$)', content, re.DOTALL)
        if equipment_section:
            equipment_text = equipment_section.group(1)
            equipment_lines = equipment_text.strip().split('\n')
            for line in equipment_lines:
                line = line.strip()
                if line and line.startswith('•'):
                    data['equipment'].append(line[2:].strip())

        # Parse Daily Activity & Goals
        activity_section = re.search(r'🎯\s*DAILY ACTIVITY & GOALS(.*?)(?=📊|$)', content, re.DOTALL)
        if activity_section:
            activity_text = activity_section.group(1)
            activity_lines = activity_text.strip().split('\n')
            for line in activity_lines:
                line = line.strip()
                if line and line.startswith('-'):
                    data['activity_goals'].append(line[2:].strip())

        # Parse Progress
        progress_section = re.search(r'📊\s*PROGRESS(.*?)(?=📸|$)', content, re.DOTALL)
        if progress_section:
            progress_text = progress_section.group(1)
            progress_lines = progress_text.strip().split('\n')
            for line in progress_lines:
                line = line.strip()
                if line and line.startswith('-'):
                    data['progress'].append(line[2:].strip())

        # Parse Photos count
        photos_match = re.search(r'📸\s*(\d+)\s*รูป', content)
        if photos_match:
            data['photos'] = int(photos_match.group(1))

        return data
    except Exception as e:
        print(f"❌ Error parsing {file_path}: {e}")
        return None

def update_daily_progress_data():
    """Read all daily report files and export to JSON"""
    try:
        print("📖 Reading Daily Progress files...")
        print(f"📁 Directory: {DAILY_PROGRESS_DIR}\n")

        daily_reports = []

        # Find all .txt files (A.txt, M.txt, or just DDMMYY.txt)
        for root, dirs, files in os.walk(DAILY_PROGRESS_DIR):
            for file in sorted(files):
                if file.endswith('.txt') and re.match(r'\d{6}[AM]?\.txt$', file):
                    file_path = os.path.join(root, file)
                    print(f"📄 Reading: {file}")
                    report = parse_daily_report(file_path)
                    if report:
                        daily_reports.append(report)

        print(f"\n✓ Loaded {len(daily_reports)} daily reports")
        print(f"📄 Dates before sort: {[r['date'] for r in daily_reports[:5]]}")

        # Sort by date and shift - convert DD/MM/YY to comparable format
        daily_reports.sort(key=lambda x: (x['date'].split('/')[2], x['date'].split('/')[1], x['date'].split('/')[0], x['shift']))

        print(f"📄 Dates after sort: {[r['date'] for r in daily_reports[:5]]}")

        # Calculate summary
        total_photos = sum(r['photos'] for r in daily_reports)
        avg_workers = sum(r['state_workers_total'] for r in daily_reports) / len(daily_reports) if daily_reports else 0
        avg_equipment = sum(len(r['equipment']) for r in daily_reports) / len(daily_reports) if daily_reports else 0

        summary = {
            'total_reports': len(daily_reports),
            'date_range_start': daily_reports[0]['date'] if daily_reports else '',
            'date_range_end': daily_reports[-1]['date'] if daily_reports else '',
            'total_photos': total_photos,
            'avg_workers': round(avg_workers, 1),
            'avg_equipment_types': round(avg_equipment, 1)
        }

        # Prepare data for export
        data = {
            'summary': summary,
            'daily_reports': daily_reports
        }

        # Save to JSON
        os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Saved {len(daily_reports)} reports to JSON")
        print(f"✓ File: {JSON_FILE}")

        print(f"\n📊 Summary:")
        print(f"  Total Reports: {summary['total_reports']}")
        print(f"  Date Range: {summary['date_range_start']} - {summary['date_range_end']}")
        print(f"  Total Photos: {summary['total_photos']}")
        print(f"  Avg Workers/Day: {summary['avg_workers']}")
        print(f"  Avg Equipment Types/Day: {summary['avg_equipment_types']}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Daily Progress Data Parser")
    print("=" * 60)
    print()

    success = update_daily_progress_data()

    print()
    if success:
        print("✓ Update completed successfully!")
        print("➜ Open dashboard to see the latest data")
    else:
        print("❌ Update failed. Check error messages above.")

    print()
    input("Press Enter to close...")
