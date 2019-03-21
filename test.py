import unittest

from bot import get_update_in_grades


class TestSum(unittest.TestCase):
    def test_updated_grades(self):
        
        old_grades = {0:{'name':'subject1','grade':'94'},
                      1:{'name':'subject2','grade':'54'},
                      2:{'name':'subject3','grade':'64'},
                      3:{'name':'subject4','grade':'74'}}
        new_grades = {0:{'name':'subject1','grade':'84'},
                      1:{'name':'subject2','grade':'54'},
                      2:{'name':'subject3','grade':'54'},
                      3:{'name':'subject4','grade':'74'}}       
        
        result = get_update_in_grades(old_grades,new_grades)
        self.assertListEqual(result,[0,2])

if __name__ == '__main__':
    unittest.main()