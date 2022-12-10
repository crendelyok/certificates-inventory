# # Template of parser package
# import os
# import socket
# import ssl
# import sys
# import tempfile
# from constants import CERTIFICATE_PUBLIC_KEY_TYPES
#
# import cryptography.hazmat.backends.openssl
#
# if __name__ == "__main__":
#     hostname = sys.argv[1]
#     port = int(sys.argv[2])
#
#     # socket
#     myctx = ssl.create_default_context()
#     myctx.check_hostname = False
#     myctx.verify_mode = ssl.CERT_NONE
#     s = myctx.wrap_socket(socket.socket(), server_hostname=hostname)
#     s.connect((hostname, port))
#
#     # get binary certificate
#     bcert = s.getpeercert(binary_form=True)
#     with tempfile.TemporaryFile() as f:
#         f.write(ssl.DER_cert_to_PEM_cert(bcert))
#         cert_dict = ssl._ssl._test_decode_cert(f.name)
#
#     cert = cryptography.x509.load_der_x509_certificate(
#         bcert,
#         cryptography.hazmat.backends.openssl.backend
#     )
#
#
#     pprint(cert_dict)
#     print(cert.signature_hash_algorithm.name)
#     print(cert.public_key())
#     print(cert)