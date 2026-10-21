import hashlib
import ssl
from unittest import TestCase

import certifi
import requests.certs
from botocore.httpsession import get_cert_path


class TlsTrustTestCase(TestCase):
    def test_outbound_clients_do_not_trust_compromised_emsign_chains(self):
        # Trust anchors listed by the incident response team, including cross-signs:
        # https://emudhra.we-have-a-problem.com/roots.json
        affected_roots = {
            "7dd78d5f4f13459a83dff9abbba62edbaf6f2d102bf257fd712f4d9f2746ed8d",
            "f2edaaff3d9b701fb4d14c9f285f8c0bad90fc3bcc1fa07d47f4718edaba34a5",
            "d7a7a0fb5d7e2731d771e9484ebcdef71d5f0c3e0a2948782bc83ee0ea699ef4",
            "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b",
        }
        bundles = {
            "certifi": certifi.where(),
            "requests (CMS notifications and tutorials)": requests.certs.where(),
            "botocore (S3 media)": get_cert_path(True),
        }
        for client, bundle in bundles.items():
            with self.subTest(client=client):
                context = ssl.create_default_context(cafile=bundle)
                fingerprints = {
                    hashlib.sha256(certificate).hexdigest() for certificate in context.get_ca_certs(binary_form=True)
                }
                self.assertTrue(fingerprints, "The CA bundle must not be empty")
                self.assertFalse(affected_roots & fingerprints)
