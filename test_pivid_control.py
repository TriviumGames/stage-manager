import unittest
import pivid_control

class MyTestCase(unittest.TestCase):
    def test_something(self):
        dict_a = {
            "scenes": {
                "a": {
                    "media": "a"
                },
                "b": {
                    "media": "b"
                }
            }
        }
        dict_b = {
            "scenes": {
                "c": {
                    "media": "c"
                },
                "d": {
                    "media": "d"
                }
            }
        }
        print(pivid_control.PividControl.merge_dicts(dict_a, dict_b))


if __name__ == '__main__':
    unittest.main()
