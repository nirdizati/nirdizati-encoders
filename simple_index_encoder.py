import csv
import datetime
import json
import time
import encoder
from os.path import isfile

import pandas as pd
import numpy as np

class SimpleIndexEncoder:

	def __init__(self):
		self.log = None

	def set_log(self, log):
		self.log = log

	def encode_trace(self, data):
		data_encoder = encoder.Encoder()
		events = data_encoder.get_events(data).tolist()
		cases = data_encoder.get_cases(data)

		max_length = max(data['event_nr'])
		columns = []
		columns.append("case_id")
		columns.append("event_nr")
		columns.append("remaining_time")
		columns.append("elapsed_time")
		for i in range(1, max_length):
			columns.append("prefix_"+str(i))

		encoded_data = []

		for case in cases:
			df = data[data['case_id'] == case]
			for event_length in range(1, max(df['event_nr'])):
				case_data = []
				case_data.append(case)
				case_data.append(event_length)
				remaining_time = data_encoder.calculate_remaining_time(df, event_length)
				case_data.append(remaining_time)
				elapsed_time = data_encoder.calculate_elapsed_time(df, event_length)
				case_data.append(elapsed_time)

				case_events = df[df['event_nr'] <= event_length]['activity_name'].tolist()
				for e in case_events:
					case_data.append(events.index(e)+1)
				encoded_data.append(case_data)

		df = pd.DataFrame(columns=columns, data=encoded_data)
		return df
