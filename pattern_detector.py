#!/usr/bin/env python3
"""
MaxedHealth Pattern Detector - Phase 14
Learns lifestyle patterns from 2-4 days of data and generates wearable signals
"""

import json
import csv
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

class PatternDetector:
    def __init__(self, master_csv_path: str, combined_csv_path: str, today_log_json: str):
        """
        Initialize pattern detector with paths to data files
        
        Args:
            master_csv_path: Path to master.csv (daily nutrition totals)
            combined_csv_path: Path to combined.csv (wearable data)
            today_log_json: Path to backup JSON containing todayLog
        """
        self.master_csv = master_csv_path
        self.combined_csv = combined_csv_path
        self.today_log_json = today_log_json
        self.meals = []
        self.wearable_data = {}
        
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date from DD/MM/YY format (master.csv) or YYYY-MM-DD (combined.csv)"""
        for fmt in ["%d/%m/%y", "%Y-%m-%d"]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def load_meal_data(self, days_back: int = 4) -> List[Dict]:
        """
        Load meal timing data from backup JSON
        Returns list of dicts: {date, time, description, kcal, protein, fat, carbs}
        """
        try:
            with open(self.today_log_json, 'r') as f:
                backup = json.load(f)
            
            meals = []
            today_log = backup.get('state', {}).get('todayLog', [])
            
            # Parse today's meals
            today_date = datetime.now().strftime("%d/%m/%y")
            for entry in today_log:
                time_str = entry.get('time')
                if time_str:
                    meals.append({
                        'date': today_date,
                        'time': time_str,
                        'description': entry.get('description', ''),
                        'kcal': entry.get('kcal', 0),
                        'protein': entry.get('protein', 0),
                        'fat': entry.get('fat', 0),
                        'carbs': entry.get('carbs', 0)
                    })
            
            self.meals = meals
            return meals
        except Exception as e:
            print(f"Error loading meal data: {e}")
            return []
    
    def load_wearable_data(self, days_back: int = 7) -> Dict[str, Dict]:
        """
        Load wearable data from combined.csv - use most recent available days
        Returns dict: {date_str -> {steps, sleep_duration, bedtime, wake_time, hrv, ...}}
        """
        try:
            wearable = {}
            
            with open(self.combined_csv, 'r') as f:
                reader = csv.DictReader(f)
                # Load all rows first
                all_rows = list(reader)
            
            # Keep only the most recent days_back rows with data
            for row in all_rows[-days_back:]:
                date_str = row.get('date', '')
                if date_str:
                        
                        try:
                            steps = int(float(row.get('steps', 0))) if row.get('steps') else 0
                        except:
                            steps = 0
                        
                        try:
                            hrv = float(row.get('hrv', 0)) if row.get('hrv') else 0
                        except:
                            hrv = 0
                        
                        try:
                            spo2 = int(float(row.get('spo2', 0))) if row.get('spo2') else 0
                        except:
                            spo2 = 0
                        
                        try:
                            sleep_duration = float(row.get('sleep_duration', 0)) if row.get('sleep_duration') else 0
                        except:
                            sleep_duration = 0
                        
                        wearable[date_str] = {
                            'steps': steps,
                            'sleep_duration': sleep_duration,
                            'bedtime': row.get('bedtime', ''),
                            'wake_time': row.get('wake_time', ''),
                            'hrv': hrv,
                            'spo2': spo2,
                            'sleep_deep': float(row.get('sleep_deep', 0)) if row.get('sleep_deep') else 0,
                            'sleep_light': float(row.get('sleep_light', 0)) if row.get('sleep_light') else 0,
                            'sleep_rem': float(row.get('sleep_rem', 0)) if row.get('sleep_rem') else 0,
                        }
            
            self.wearable_data = wearable
            return wearable
        except Exception as e:
            print(f"Error loading wearable data: {e}")
            return {}
    
    def detect_meal_windows(self) -> Dict[str, str]:
        """
        Detect meal timing patterns by clustering meal times
        Returns {meal_type: "HH:MM-HH:MM", ...}
        """
        if not self.meals:
            return {}
        
        # Extract times and convert to minutes since midnight
        times = []
        for meal in self.meals:
            time_str = meal['time']
            try:
                h, m = map(int, time_str.split(':'))
                minutes = h * 60 + m
                times.append(minutes)
            except:
                continue
        
        if not times:
            return {}
        
        times.sort()
        
        # Simple clustering: group times within 90 minutes
        clusters = []
        current_cluster = [times[0]]
        
        for t in times[1:]:
            if t - current_cluster[-1] <= 90:
                current_cluster.append(t)
            else:
                clusters.append(current_cluster)
                current_cluster = [t]
        clusters.append(current_cluster)
        
        # Label clusters as breakfast/lunch/dinner based on time
        meal_windows = {}
        labels = ['Breakfast', 'Lunch', 'Dinner', 'Snacks']
        
        for i, cluster in enumerate(clusters):
            if i < len(labels):
                avg_minutes = sum(cluster) // len(cluster)
                start_h, start_m = avg_minutes // 60, avg_minutes % 60
                
                # Window spans 90 minutes around cluster
                min_time = min(cluster)
                max_time = max(cluster)
                min_h, min_m = min_time // 60, min_time % 60
                max_h, max_m = max_time // 60, max_time % 60
                
                meal_windows[labels[i]] = f"{min_h:02d}:{min_m:02d}-{max_h:02d}:{max_m:02d}"
        
        return meal_windows
    
    def detect_sleep_circadian(self) -> Dict[str, str]:
        """
        Detect sleep pattern from RingConn wearable data
        Returns {duration, deep_sleep_pct, light_sleep_pct, rem_pct, quality, regularity}
        """
        if not self.wearable_data:
            return {}
        
        durations = []
        deep_pcts = []
        light_pcts = []
        rem_pcts = []
        
        for date_str, data in sorted(self.wearable_data.items()):
            # RingConn sleep data is in minutes
            duration = data['sleep_duration']
            deep = data['sleep_deep']
            light = data['sleep_light']
            rem = data['sleep_rem']
            
            # Only include nights with data
            if duration > 0:
                durations.append(duration)
                total_sleep = deep + light + rem
                if total_sleep > 0:
                    deep_pcts.append((deep / total_sleep) * 100)
                    light_pcts.append((light / total_sleep) * 100)
                    rem_pcts.append((rem / total_sleep) * 100)
        
        result = {}
        
        if durations:
            # Convert from minutes to hours
            avg_duration_mins = sum(durations) / len(durations)
            avg_duration_hours = avg_duration_mins / 60
            hours = int(avg_duration_hours)
            minutes = int((avg_duration_hours - hours) * 60)
            result['duration'] = f"{hours}h{minutes}m"
            
            # Regularity score (0-100): how consistent sleep duration is
            if len(durations) > 1:
                variance = sum((d - avg_duration_mins)**2 for d in durations) / len(durations)
                std_dev = variance ** 0.5
                # Convert std dev to regularity score (lower variance = higher score)
                regularity = max(0, 100 - (std_dev / 60 * 15))  # Scale for minutes
                result['regularity'] = f"{int(regularity)}%"
            
            # Sleep staging breakdown
            if deep_pcts:
                result['deep_sleep'] = f"{sum(deep_pcts)/len(deep_pcts):.0f}%"
            if light_pcts:
                result['light_sleep'] = f"{sum(light_pcts)/len(light_pcts):.0f}%"
            if rem_pcts:
                result['rem_sleep'] = f"{sum(rem_pcts)/len(rem_pcts):.0f}%"
            
            # Sleep quality inference
            avg_deep = sum(deep_pcts)/len(deep_pcts) if deep_pcts else 0
            if avg_deep > 20:
                result['quality'] = "Excellent"
            elif avg_deep > 15:
                result['quality'] = "Good"
            elif avg_deep > 10:
                result['quality'] = "Fair"
            else:
                result['quality'] = "Light"
        
        return result
    
    def detect_activity_patterns(self) -> Dict[str, str]:
        """
        Detect exercise/activity patterns from step data
        Returns {avg_steps, high_activity_days, pattern_notes}
        """
        if not self.wearable_data:
            return {}
        
        steps = [data['steps'] for data in self.wearable_data.values() if data['steps']]
        if not steps:
            return {}
        
        avg_steps = sum(steps) // len(steps)
        high_threshold = avg_steps * 1.3  # 30% above average
        high_activity_count = sum(1 for s in steps if s > high_threshold)
        
        result = {
            'avg_steps': f"{avg_steps:,}",
            'high_activity_days': f"{high_activity_count}/{len(steps)}"
        }
        
        if high_activity_count > 0:
            result['pattern'] = "Regular exercise detected"
        else:
            result['pattern'] = "Moderate activity pattern"
        
        return result
    
    def detect_hrv_baseline(self) -> Dict[str, str]:
        """
        Detect HRV baseline and status
        Returns {baseline_hrv, status, note}
        """
        if not self.wearable_data:
            return {}
        
        hrv_values = [data['hrv'] for data in self.wearable_data.values() if data['hrv']]
        if not hrv_values:
            return {}
        
        baseline = sum(hrv_values) / len(hrv_values)
        latest = hrv_values[-1] if hrv_values else baseline
        
        # HRV interpretation
        if baseline > 30:
            status = "Excellent"
        elif baseline > 25:
            status = "Good"
        elif baseline > 20:
            status = "Fair"
        else:
            status = "Low"
        
        return {
            'baseline_hrv': f"{baseline:.0f}ms",
            'latest_hrv': f"{latest:.0f}ms",
            'status': status
        }
    
    def generate_current_signals(self) -> Dict:
        """
        Generate signals based on whatever data actually exists right now —
        no fixed 'day 2' assumption. Reports exactly which signals are
        genuinely available, how many distinct days of data that's built
        from, and an honest status message reflecting real completeness
        rather than a hardcoded day count. Nothing here is invented or
        backfilled — a signal that has no underlying data simply isn't
        included, same as before.
        """
        self.load_meal_data()
        self.load_wearable_data()

        meal_windows   = self.detect_meal_windows()
        sleep_circadian = self.detect_sleep_circadian()
        activity_pattern = self.detect_activity_patterns()
        hrv_baseline   = self.detect_hrv_baseline()

        # Distinct calendar days actually backing this data - the real
        # "day number" a user is at, not an assumption.
        meal_days = {m['date'] for m in self.meals}
        wearable_days = set(self.wearable_data.keys())
        days_with_any_data = meal_days | wearable_days
        day_number = max(len(days_with_any_data), 1)

        signals_available = {
            'meal_windows':    bool(meal_windows),
            'sleep':           bool(sleep_circadian.get('duration')),
            'sleep_regularity': bool(sleep_circadian.get('regularity')),  # needs 2+ nights
            'activity':        bool(activity_pattern.get('avg_steps')),
            'hrv':             bool(hrv_baseline.get('baseline_hrv')),
        }
        ready_count = sum(1 for k, v in signals_available.items() if v and k != 'sleep_regularity')
        total_core = 4  # meal_windows, sleep, activity, hrv (regularity is a bonus, not core)

        if ready_count == 0:
            status = "No data yet — log a meal or sync your watch to get started."
        elif ready_count < total_core:
            missing = [k.replace('_', ' ') for k, v in signals_available.items()
                       if not v and k != 'sleep_regularity']
            status = f"{ready_count} of {total_core} signals ready — still waiting on {', '.join(missing)}."
        else:
            status = f"All {total_core} signals ready" + (
                " · still building your sleep regularity baseline (needs a 2nd night)"
                if not signals_available['sleep_regularity'] else "."
            )

        return {
            'timestamp': datetime.now().isoformat(),
            'confidence': 'learning' if ready_count < total_core else 'established',
            'meal_windows': meal_windows,
            'sleep_circadian': sleep_circadian,
            'activity_pattern': activity_pattern,
            'hrv_baseline': hrv_baseline,
            'day_number': day_number,
            'signals_available': signals_available,
            'status': status
        }

    def generate_day_2_signals(self) -> Dict:
        """
        Deprecated name, kept as an alias so existing callers (e.g. server.py's
        /pattern-signals endpoint) keep working without changes. Despite the
        name, this no longer assumes day 2 - it delegates to
        generate_current_signals(), which reports whatever's actually there.
        """
        return self.generate_current_signals()
    
    def generate_full_pattern_report(self) -> Dict:
        """
        Generate comprehensive pattern report. 'day_number' and 'confidence'
        now reflect actual data span rather than assuming day 5+ has been
        reached - same honesty principle as generate_current_signals().
        """
        self.load_meal_data()
        self.load_wearable_data()

        meal_days = {m['date'] for m in self.meals}
        wearable_days = set(self.wearable_data.keys())
        day_number = max(len(meal_days | wearable_days), 1)
        confidence = 'high' if day_number >= 5 else 'learning'

        report = {
            'timestamp': datetime.now().isoformat(),
            'confidence': confidence,
            'learned_patterns': {
                'meal_windows': self.detect_meal_windows(),
                'sleep_circadian': self.detect_sleep_circadian(),
                'activity': self.detect_activity_patterns(),
                'hrv': self.detect_hrv_baseline(),
            },
            'lifestyle_context': self.infer_lifestyle_context(),
            'day_number': day_number,
            'status': 'Full pattern analysis ready' if confidence == 'high' else f'Building pattern history — day {day_number} of 5 needed for full confidence.'
        }
        
        return report
    
    def infer_lifestyle_context(self) -> Dict[str, str]:
        """
        Infer lifestyle patterns (exercise routines, travel, shift work, etc.)
        Returns flags for detected lifestyle patterns
        """
        activity = self.detect_activity_patterns()
        context = {}
        
        if 'high_activity_days' in activity:
            context['exercise_pattern'] = activity['high_activity_days']
        
        # Could add more sophisticated detection here:
        # - Travel detection (sudden changes in sleep/steps)
        # - Shift work detection (varying sleep times)
        # - Weekend vs weekday patterns
        
        return context


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: pattern_detector.py <master.csv> <combined.csv> <backup.json>")
        sys.exit(1)
    
    detector = PatternDetector(sys.argv[1], sys.argv[2], sys.argv[3])
    
    # Generate Day 2 signals
    signals = detector.generate_day_2_signals()
    print("=== DAY 2 SIGNALS ===")
    print(json.dumps(signals, indent=2))
    
    # Generate full report
    report = detector.generate_full_pattern_report()
    print("\n=== FULL PATTERN REPORT ===")
    print(json.dumps(report, indent=2))
