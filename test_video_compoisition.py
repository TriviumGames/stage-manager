import unittest
import video_composition
import pivid_server
import math

server_url = 'http://pivid-test-2.local:31415'
server = pivid_server.PividServer(server_url)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        comp = video_composition.VideoComposition(server)
        comp.load_json('test_data/basic_config_test.json')
        self.assertAlmostEqual(0.9676343009676344, comp.get_scene_duration('cit_005'), 5)
        self.assertAlmostEqual(math.inf, comp.get_scene_duration('cit_010a'), 5)


if __name__ == '__main__':
    unittest.main()
