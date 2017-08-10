import csv
import datetime
import json
import time
from os.path import isfile

import pandas as pd
import untangle
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

class IndexBasedEncoder:

	def __init__(self):
		self.log = None
		self.events = None

	def set_log(self, log):
		self.log = log

	def encode_trace(self, trace, out):
		case_id = ''
		if type(trace.string) is list:
			for i in range(0, len(trace.string)):
				if u"concept:name" == trace.string[i]['key']:
					case_id = trace.string[i]['value']
		else:
			# only has 1 value, so it automatically becomes the case id
			case_id = trace.string['value']

		#first event timestamp
		first_event = trace.event[0]
		first_event_timestamp = self.get_timestamp_from_event(first_event)

		#last event timestamp
		last_event = trace.event[len(trace.event) - 1]
		last_event_timestamp = self.get_timestamp_from_event(last_event)
		activity_name = ''
		activities_executed = 0
		for event in trace.event:
			for i in range(0, len(event.string)):
				if u"concept:name" == event.string[i]['key']:
					activity_name += str(self.events.index(event.string[i]['value'])+1) + '_'
					activities_executed += 1

			event_timestamp = self.get_timestamp_from_event(event)
			if event_timestamp == None:
				continue

		if out == 0:
			activity_name.rstrip('_')
			history = d[len(d) - 1].split("_")
			history_data = []
			for i in range(0, activities_executed):
				if len(history) > i:
					history_data.append(history[i])
				else:
					history_data.append(0)
				return [case_id, last_event_timestamp - event_timestamp, event_timestamp - first_event_timestamp, history_data]
		else:
			return [case_id, last_event_timestamp - event_timestamp, event_timestamp - first_event_timestamp, activities_executed, activity_name.rstrip('_')]

	def remaining_time_encode(self):
		filename = self.log
		print filename
		obj = untangle.parse(filename)

		traces = obj.log.trace

		header = ['id', 'remainingTime', 'elapsedTime', 'executedActivities']
		data = []

		events = self.get_all_events(traces)
		with open("events_"+filename+".csv", "w") as output:
			writer = csv.writer(output, lineterminator='_')
			for val in events:
				writer.writerow([val])

		longest_trace = 0;
		for trace in traces:
			to_append = self.encode_trace(trace, 1)
			data.append(to_append)
			activities_executed = to_append[len(to_append)-2]
			if longest_trace < activities_executed:
				longest_trace = activities_executed

		#rewrite data
		new_data = []
		for d in data:
			history = d[len(d) - 1].split("_")
			history_data = []
			for i in range(0, longest_trace):
				if len(history) > i:
					history_data.append(history[i])
				else:
					history_data.append(0)

			new_data.append(d[0:4] + history_data)

		for i in range(0, longest_trace):
			header.append("prefix_"+str(i+1))

		df = pd.DataFrame(columns=header, data=new_data)
		self.write_pandas_to_csv(df, filename+'.csv')
		return json.dumps(data)

	def get_all_events(self, traces):
		events = []
		for trace in traces:
			for event in trace.event:
				for i in range(0, len(event.string)):
					if u"concept:name" == event.string[i]['key']:
						activity_name = event.string[i]['value']
						if activity_name not in events:
							events.append(activity_name)
		self.events = events
		return events

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

		timestamp = time.mktime(datetime.datetime.strptime(date_time[0:19], "%Y-%m-%dT%H:%M:%S").timetuple())

		return timestamp

	def write_pandas_to_csv(self, df, filename):
		df.to_csv("indexbased_"+filename,sep=',',mode='w+', index=False)
		return filename
