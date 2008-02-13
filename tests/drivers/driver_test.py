
import unittest
from peephole.drivers.driver import replace_text

class ReplaceTextTest(unittest.TestCase):
    def testReplaceText(self):
        row =          "  Hello Computer    "
        replace_with = "  Bye"
        replace_at = 2 # zero-based
        final_text   = "    Bye Computer    "
        self.assertEqual(len(row), 20)
        self.assertEqual(len(final_text), 20)
        result = replace_text(row,
                              replace_with,
                              replace_at, 20)
        self.assertEqual(len(result), 20)

        self.assertEqual(final_text, result)

    def testReplaceTextTooLong(self):
        row =          "  Hello Computer    "
        replace_with = "  Bye.  It was nice knowing you.  This is overly verbose."
        replace_at = 2
        #final_text   = "    Bye. It was nice"
        got_exception = False
        result = ""
        self.assertEqual(len(row), 20)
        #self.assertEqual(len(final_text), 20)
        try:
            result = replace_text(row,
                                  replace_with,
                                  replace_at, 20)
        except ValueError:
            got_exception = True
        self.assertEqual(got_exception, True)
        #self.assertEqual(len(result), 20)
        #self.assertEqual(final_text, result)

    def testReplaceTextAlmostTooLong(self):
        row =          "  Hello Computer    "
        replace_with =         "Computerdude"
        replace_at = 8
        final_text =   "  Hello Computerdude"
        self.assertEqual(len(row), 20)
        self.assertEqual(len(final_text), 20)
        result = replace_text(row,
                              replace_with,
                              replace_at, 20)
        self.assertEqual(len(result), 20)
        self.assertEqual(final_text, result)
