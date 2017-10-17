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

encoder = encoder.Encoder()
encoder.set_path(".")
filename = "Productiontrim.xes"
encoder.xes_to_csv(filename)
encoder.write_df_to_csv(encoder.df, "xes_to_csv_"+filename+".csv")

encoded_trace = boolean_encode(encoder.df)
encoder.write_df_to_csv(encoded_trace, "boolean_encode_"+filename+".csv")

encoded_trace = frequency_encode(encoder.df)
encoder.write_df_to_csv(encoded_trace, "frequency_encode_"+filename+".csv")

encoded_trace = simple_index_encode(encoder.df, 2)
encoder.write_df_to_csv(encoded_trace, "simple_index_encode_"+filename+".csv")

encoded_trace = index_latest_payload_encode(encoder.df, encoder.event_attributes, 2)
encoder.write_df_to_csv(encoded_trace, "index_latest_payload_encode_"+filename+".csv")

encoded_trace = complex_encode(encoder.df, encoder.event_attributes, 2)
encoder.write_df_to_csv(encoded_trace, "complex_encode_"+filename+".csv")
