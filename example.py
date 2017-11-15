import encoder

def boolean_encode(data):
	import boolean_encoder
	encoding_method = boolean_encoder.BooleanEncoder()
	encoded_trace = encoding_method.encode_trace(data)
	return encoded_trace

def frequency_encode(data):
	import frequency_encoder
	encoding_method = frequency_encoder.FrequencyEncoder()
	encoded_trace = encoding_method.encode_trace(data)
	return encoded_trace

def simple_index_encode(data, prefix):
	import simple_index_encoder
	encoding_method = simple_index_encoder.SimpleIndexEncoder()
	print data
	encoded_trace = encoding_method.encode_trace(data, prefix)
	return encoded_trace

def index_latest_payload_encode(data, attributes, prefix):
	import index_latest_payload_encoder
	encoding_method = index_latest_payload_encoder.IndexLatestPayloadEncoder()
	encoded_trace = encoding_method.encode_trace(data, attributes, prefix)
	return encoded_trace

def complex_encode(data, attributes, prefix):
	import complex_encoder
	encoding_method = complex_encoder.ComplexEncoder()
	encoded_trace = encoding_method.encode_trace(data, attributes, prefix)
	return encoded_trace

def intercase_encode(data, filename, level):
	import intercase_encoder
	encoding_method = intercase_encoder.IntercaseEncoder()
	encoded_trace = encoding_method.encode_trace(data, level, filename, ['org:resource'])
	return encoded_trace

encoder = encoder.Encoder()
encoder.set_path(".")
filename = "Production.xes"
encoder.xes_to_csv(filename)
encoder.write_df_to_csv(encoder.df, "xes_to_csv_"+filename+".csv")

# uncomment to test the other encoding methods
# encoded_trace = boolean_encode(encoder.df)
# encoder.write_df_to_csv(encoded_trace, "boolean_encode_"+filename+".csv")

# encoded_trace = frequency_encode(encoder.df)
# encoder.write_df_to_csv(encoded_trace, "frequency_encode_"+filename+".csv")

# encoded_trace = simple_index_encode(encoder.df, 5)
# print encoded_trace
# encoder.write_df_to_csv(encoded_trace, "simple_index_encode_"+filename+".csv")

# encoded_trace = index_latest_payload_encode(encoder.df, encoder.event_attributes, 2)
# encoder.write_df_to_csv(encoded_trace, "index_latest_payload_encode_"+filename+".csv")

# encoded_trace = complex_encode(encoder.df, encoder.event_attributes, 2)
# encoder.write_df_to_csv(encoded_trace, "complex_encode_"+filename+".csv")

# level 0, 1, 2 and 3 only
level = 2
encoded_trace = intercase_encode(encoder.df, filename, level=level)
train, test = encoder.split_data(encoded_trace)
encoder.write_df_to_csv(encoded_trace, "intercase_encode_"+filename+"_level"+str(level)+".csv")
encoder.write_df_to_csv(train, "intercase_encode_train"+filename+"_level"+str(level)+".csv")
encoder.write_df_to_csv(test, "intercase_encode_test"+filename+"_level"+str(level)+".csv")