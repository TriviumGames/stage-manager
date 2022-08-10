import unittest
import pivid_server

server_url = "http://pivid-test-2.local:31415"

class MyTestCase(unittest.TestCase):
    def test_something(self):
        server = pivid_server.PividServer(server_url)
        duration1 = server.get_media_duration("jellyfish-3-mbps-hd-hevc.mkv")
        self.assertAlmostEqual(30.096999999999998, duration1, 4)  # add assertion here
        duration2 = server.get_media_duration("jellyfish-3-mbps-hd-hevc.mkv")
        self.assertEqual(duration1, duration2)

if __name__ == '__main__':
    unittest.main()
