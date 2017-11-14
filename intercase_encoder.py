import csv
import datetime
from datetime import datetime as dt
import json
import time
import encoder
from os.path import isfile

import pandas as pd
import numpy as np

class IntercaseEncoder:

	def __init__(self):
		self.log = None

	def set_log(self, log):
		self.log = log

	def add_next_state(self, df):
		pd.options.mode.chained_assignment = None
		df['next_state'] = ''
		df['next_time'] = 0
		df['next_dur'] = 0
		num_rows = len(df)
		for i in range(0, num_rows - 1):
			if df.at[i, 'case_id'] == df.at[i + 1, 'case_id']:
				df.at[i, 'next_state'] = df.at[i + 1, 'activity_name']
				df.at[i, 'next_time'] = df.at[i + 1, 'time']
				df.at[i, 'next_dur'] = df.at[i + 1, 'time'] - df.at[i, 'time']
			else:
				df.at[i, 'next_state'] = 99
				df.at[i, 'next_time'] = df.at[i, 'time']
				df.at[i, 'next_dur'] = 0
		df.at[num_rows-1, 'next_state'] = 99
		df.at[num_rows-1, 'next_time'] = df.at[num_rows-1, 'time']
		df.at[num_rows-1, 'next_dur'] = 0
		return df

	def get_index_position(self, column_data, unique_data):
		converted_values = []
		for i in range(0, len(column_data)):
			converted_values.append(unique_data.index(column_data[i]))
		return converted_values

	def create_initial_log(self, df, name):

		self.add_next_state(df)
		self.add_query_remaining(df)
		# os.path.splitext(path)[0]
		version = "_level_0"+name
		# filename = write_pandas_to_csv(df, version, False)
		return df

	def add_query_remaining(self, df):
		df['elapsed_time'] = 0
		df['total_time'] = 0
		df['remaining_time'] = 0
		df['history'] = ""
		ids = []
		total_Times = []
		num_rows = len(df)
		temp_elapsed = 0
		prefix = str(df.at[0, 'activity_name'])
		df.at[0, 'history'] = prefix

		for i in range(1, num_rows):
			if df.at[i, 'case_id'] == df.at[i - 1, 'case_id']:
				temp_elapsed += df.at[i - 1, 'next_dur']
				df.at[i, 'elapsed_time'] = temp_elapsed
				prefix = prefix + '_' + str(df.at[i, 'activity_name'])
				df.at[i, 'history'] = prefix
			else:
				ids.append(df.at[i - 1, 'case_id'])
				total_Times.append(temp_elapsed)
				temp_elapsed = 0
				prefix = str(df.at[i, 'activity_name'])
				df.at[i, 'history'] = prefix

		ids.append(df.at[num_rows - 1, 'case_id'])
		total_Times.append(df.at[num_rows - 1, 'elapsed_time'])
		for i in range(0, num_rows):
			try:
				ind = ids.index(df.at[i, 'case_id'])
				total_ = total_Times[ind]
				df.at[i, 'total_time'] = total_
				df.at[i, 'remaining_time'] = total_ - df.at[i, 'elapsed_time']
			except ValueError:
				print 'err'
				return ValueError
		return

	def prepare_data(self, data, columns):
		data_encoder = encoder.Encoder()
		events = data_encoder.get_events(data)
		event_timestamp = pd.DatetimeIndex(data['time'])
		event_timestamp = event_timestamp.astype(np.int64)
		data['time'] = event_timestamp
		
		data['activity_name'] = self.get_index_position(data['activity_name'].tolist(), events.tolist())

		data = data[columns]
		return data

	def order_csv_time(self, data):
		data = data.sort_values(by=['time'], ascending=True)
		data = data.reset_index(drop=True)
		return data

	def get_states(self, data):
		state_list = []
		for i in range(0, len(data)):
			pair = data.at[i, 'activity_name']
			try:
				ind = state_list.index(pair)
			except ValueError:
				state_list.append(pair)
		return state_list

	def get_history_len(self, data):
		max_size = -1
		for i in range(0, len(data)):
			if str(data.at[i, 'history']) != "nan":
				parsed = data.at[i, 'history'].split("_")
				if len(parsed) > max_size:
					max_size = len(parsed)
		return max_size

	def history_encoding_new(self, data):
		hist_len = self.get_history_len(data)

		for k in range(0, hist_len):
			data['event_' + str(k)] = -1
		for i in range(0, len(data)):
			if str(data.at[i, 'history']) != "nan":
				parsed_hist = str(data.at[i, 'history']).split("_")
				for k in range(0, len(parsed_hist)):
					data.at[i, 'event_' + str(k)] = int(parsed_hist[k])

		return data, hist_len

	# level 1 and 2 encoding
	def add_queues(self, data, state_list):
		event_queue = []
		tuple = []
		data['total_q'] = 0

		for s in state_list:
			col_name = 'queue' + '_' + str(s)
			data[col_name] = 0
			event_queue.append(tuple)
			tuple = []

		num_rows = len(data)
		for i in range(0, num_rows):
			print (str(i) + ' queueing calculation')
			cur_time = data.at[i, 'time']
			next_time = data.at[i, 'next_time']
			cur_state = data.at[i, 'activity_name']
			ind = state_list.index(cur_state)
			tuple = [cur_time, next_time]
			event_queue[ind].append(tuple)
			self.update_event_queue(event_queue, cur_time)
			total_q = 0
			for j, s in enumerate(state_list):
				col_name1 = 'queue' + '_' + str(s)
				ind = state_list.index(s)
				x = self.find_q_len_ttiq(event_queue[ind], cur_time)
				data.at[i, col_name1] = x
				total_q += x
			data.at[i,'total_q'] = total_q

		return data

	def update_event_queue(self, event_queue, cur_time):
		remove_indices = []
		rem_ind = []

		# going over the different states and getting the rates
		for i, e in enumerate(event_queue):
			for j, q in enumerate(event_queue[i]):
				if q[1] <= cur_time:
					rem_ind.append(j)
			remove_indices.append(rem_ind)

			count_remove = 0
			if len(remove_indices[i]) > 0:
				for index in sorted(remove_indices[i], reverse=True):
					del event_queue[i][index]
			rem_ind = []
		return

	def find_q_len_ttiq(self, event_queue, cur_time):
		q_len = len(event_queue)
		return q_len

	def queue_level(self, data):
		state_list = self.get_states(data)
		data = self.add_queues(data, state_list)
		return data

	# level 3
	def find_mc_q(self, event_queue, cur_time):
		q_len = len(event_queue)
		return q_len

	# level 3 encoding
	def intercase_encode(self, data, state_list, query_name, level):
		cols = ['org:resource']

		data, hist_len = self.history_encoding_new(data)

		for h in range(0,hist_len):
			cols.append('event_'+str(h))

		for c in cols:
			data[c] = data[c].astype('category')

		df_categorical = data[cols]

		dummies = pd.get_dummies(df_categorical)
		cols = ['elapsed_time',query_name]

		if level == 3:
			for k,s in enumerate(state_list):
				cols.append('pref'+'_'+str(k))
		elif level == 2:
			for k,s in enumerate(state_list):
				cols.append('queue'+'_'+str(k))
		elif level == 1:
			for k,s in enumerate(state_list):
				cols.append('queue'+'_'+str(k))

		data = data[cols]
		data = pd.concat([data, dummies], axis=1)

		print data.head(3)

		return data

	def encode_trace(self, data, level=0, columns=None, name=""):
		
		columns = ['case_id','time','activity_name','org:resource']
		data = self.prepare_data(data, columns)
		data = self.create_initial_log(data, name)
		data = self.order_csv_time(data)
		state_list = []
		query_name = 'remaining_time'

		if level == 3:
			print 3
		elif level == 2:
			print 2
		elif level == 1:
			print 1
			data = self.queue_level(data)

		state_list = self.get_states(data)

		self.intercase_encode(data, state_list, query_name, level)

		return data
