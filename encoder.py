import csv
from datetime import datetime
import json
import time
from os.path import isfile

import pandas as pd
import untangle

class Encoder:

	def __init__(self):
		self.events = None
		self.df = None
		self.cases = None

	def read_csv(self, filename):
		self.df = pd.read_csv(filepath_or_buffer=filename, header=0)
		return self.df

	def get_events(self, df):
		self.events = df['activity_name'].unique()
		return self.events

	def get_cases(self, df):
		self.cases = df['case_id'].unique()
		return self.cases

	def calculate_remaining_time(self, trace, event_nr):
		event_timestamp = trace[trace["event_nr"] == event_nr]['time'].item()
		event_timestamp = datetime.strptime(event_timestamp, "%Y-%m-%d %H:%M:%S")
		last_event_timestamp = trace[trace["event_nr"] == len(trace)]['time'].item()
		last_event_timestamp = datetime.strptime(last_event_timestamp, "%Y-%m-%d %H:%M:%S")
		return (last_event_timestamp - event_timestamp).total_seconds()
