import csv
import datetime
from datetime import datetime as dt
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
		self.event_attributes = None
		self.case_attributes = None

	def read_csv(self, filename):
		self.df = pd.read_csv(filepath_or_buffer=filename, header=0)
		return self.df

	def get_events(self, df):
		self.events = df['activity_name'].unique()
		return self.events

	def get_cases(self, df):
		self.cases = df['case_id'].unique()
		return self.cases

	def set_path(self, path):
		self.path = path

	def get_case_attributes(self, xes):
		traces = self.get_xes_traces(xes)
		attributes = []
		for trace in traces:
			for case_attribute in trace.children:
				attributes.append(case_attribute['key'])
		#remove none and get all unique values
		attributes = list(set([i for i in attributes if i is not None]))
		self.case_attributes = attributes
		attributes.remove(u"concept:name")
		self.event_attributes = attributes
		return attributes

	def get_event_attributes(self, xes):
		traces = self.get_xes_traces(xes)
		attributes = []
		for trace in traces:
			for event in trace.event:
				for event_attribute in event.children:
					attributes.append(event_attribute['key'])
		#remove none
		attributes = [i for i in attributes if i is not None]
		# get unique attributes that are common in the events
		name_count = attributes.count(u"concept:name") 
		unique_attributes = list(set(attributes))

		for unique_attribute in unique_attributes:
			if name_count > attributes.count(unique_attribute):
				unique_attributes.remove(unique_attribute)

		unique_attributes.remove(u"concept:name")
		unique_attributes.remove(u"time:timestamp")
		self.event_attributes = unique_attributes
		return unique_attributes

	def get_xes_traces(self, xes):
		filename = xes
		if self.path != None:
			filename = self.path+"/"+xes
		obj = untangle.parse(filename)
		return obj.log.trace

	def xes_to_csv(self, xes):
		traces = self.get_xes_traces(xes)
		self.get_event_attributes(xes)

		header = ['case_id', 'event_nr', 'time', 'activity_name'] +  self.event_attributes
		data = []

		for trace in traces:
			case_id = ''
			if type(trace.string) is list:
				for i in range(0, len(trace.string)):
					if u"concept:name" == trace.string[i]['key']:
						case_id = trace.string[i]['value']
			else:
				# only has 1 value, so it automatically becomes the case id
				case_id = trace.string['value']
			event_nr = 1
			for event in trace.event:
				if type(event.string) is list:
					for i in range(0, len(event.string)):
						if u"concept:name" == event.string[i]['key']:
							activity_name = event.string[i]['value']
				else:
					# only has 1 value, so it automatically becomes the activity name
					activity_name = event.string['value']

				event_timestamp = self.get_timestamp_from_event(event)
				if event_timestamp == None:
					continue

				row_value = [case_id, event_nr, event_timestamp, activity_name]

				for event_attribute_key in self.event_attributes:
					attribute_value = ''
					for event_attribute in event.children:
						if event_attribute_key == event_attribute['key']:
							attribute_value = event_attribute['value']

					row_value.append(attribute_value)
					# print "key: "+event_attribute_key+"            value:"+event_attribute['value']

				data.append(row_value)
				event_nr += 1

		df = pd.DataFrame(columns=header, data=data)
		self.df = df
		return df

	def get_timestamp_from_event(self, event):
		date_time = ''
		if event is None:
			return None

		if type(event.date) is list:
			for i in range(0, len(event.date)):
				if u"time:timestamp" == event.date[i]['key']:
					date_time = event.date[i]['value']
		else:
			date_time = event.date['value']

		timestamp = datetime.datetime.strptime(date_time[0:19], "%Y-%m-%dT%H:%M:%S")
		return timestamp

	def calculate_remaining_time(self, trace, event_nr):
		event_timestamp = trace[trace["event_nr"] == event_nr]['time'].apply(str).item()
		event_timestamp = dt.strptime(event_timestamp, "%Y-%m-%d %H:%M:%S")
		last_event_timestamp = trace[trace["event_nr"] == len(trace)]['time'].apply(str).item()
		last_event_timestamp = dt.strptime(last_event_timestamp, "%Y-%m-%d %H:%M:%S")
		return (last_event_timestamp - event_timestamp).total_seconds()

	def calculate_elapsed_time(self, trace, event_nr):
		event_timestamp = trace[trace["event_nr"] == event_nr]['time'].apply(str).item()
		event_timestamp = dt.strptime(event_timestamp, "%Y-%m-%d %H:%M:%S")
		first_event_timestamp = trace[trace["event_nr"] == 1]['time'].apply(str).item()
		first_event_timestamp = dt.strptime(first_event_timestamp, "%Y-%m-%d %H:%M:%S")
		return (event_timestamp - first_event_timestamp).total_seconds()

	def write_df_to_csv(self, df, filename):	
		df.to_csv(filename,sep=',',mode='w+', index=False)
		return filename