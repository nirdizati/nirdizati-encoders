import encoder

encoder = encoder.Encoder()

encoder.read_csv("sample_trace.csv")

import frequency_encoder

frequency_encoder = frequency_encoder.FrequencyEncoder()
encoded_trace = frequency_encoder.encode_trace(encoder.df)

print encoded_trace