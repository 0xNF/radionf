import hmac, base64, hashlib
import time
import json


signingKey = "zphbG1sXK5Ebndyq5ey+IdYfM1CAQSGUR0WCBI52EKL6EBCdNcTmBpn+NFYS6qXDIeEBh8sBFUiLPCpZjgzhVY94SQStRYHJ7Y8pGtzGUdJFZpSuPA0GL87VKWM4YhgncC4hBY8+gIOq6KWQMAAlvUZBWg6sdo0qmsBxCPr0J0w="

def verifySignature(string_to_verify, signature, shared_secret):
    hm = hmac.new(shared_secret, string_to_verify, hashlib.sha512)
    hmd = hm.digest()
    return ct_compare(hmd, signature)

def verifyTime(timestamp):
    if int(time.time()) - timestamp > 30:
        return False
    return True

def ct_compare(a, b):
    if len(a) != len(b):
        return False

    result = 0
    for ch_a, ch_b in zip(a, b):
        # result |= ord(ch_a) ^ ord(ch_b)
        result |= ch_a ^ ch_b
    return result == 0


def verify(data, signature):
    decoded_data = bytes(json.dumps(data), encoding="utf-8")
    decoded_signature = base64.urlsafe_b64decode(signature)

    b64Key = base64.urlsafe_b64decode(signingKey)
    if verifySignature(decoded_data, decoded_signature, b64Key):
        print('Valid signature')
        # Verify timestamp
        if not verifyTime(time.time()): # todo fetch real timestamp
            print("Timestamp too far back.")
            return False
        print('Timestamp verified')
        return True
    print("invalid signature")
    return False

    