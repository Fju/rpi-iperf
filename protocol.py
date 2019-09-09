# Shared constants for protocolled communication between client and server
# IMPORTANT: The communication relies on the fact that the response or query
#            code is only one byte long. This means that the constants which
#            are defined here should only contain ONE character inside a string
#            (and should start with b). It doesnt matter what character is inside
#            the strings AS LONG AS it is in the ASCII charset. The other characters
#            have a two or three byte representation and would thus be sent
#            as three bytes instead of one which, in the end, would mess up the 
#            comparision on the client side.

QUERY_STATUS = b"1"
QUERY_IPERF = b"2"
QUERY_PROVOKE_ERROR = b"3"

RESPONSE_OK = b"0"
RESPONSE_UNKNOWN = b"1"
