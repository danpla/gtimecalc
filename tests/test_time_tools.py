
import unittest
import operator

from gtimecalc import time_tools


class TestTimeTools(unittest.TestCase):

    def test_join_units(self):
        join = time_tools.join_units

        self.assertEqual(join(1, 2, 3, 4), 3723004)
        self.assertEqual(join(-1, 2, 3, 4), -3476996)
        self.assertEqual(join(1, -2, 3, 4), 3483004)
        self.assertEqual(join(1, 2, -3, 4), 3717004)
        self.assertEqual(join(1, 2, 3, -4), 3722996)
        self.assertEqual(join(-1, -2, -3, -4), -3723004)

        self.assertEqual(join(4, 3, 2, 1), 14582001)
        self.assertEqual(join(-4, 3, 2, 1), -14217999)
        self.assertEqual(join(4, -3, 2, 1), 14222001)
        self.assertEqual(join(4, 3, -2, 1), 14578001)
        self.assertEqual(join(4, 3, 2, -1), 14581999)
        self.assertEqual(join(-4, -3, -2, -1), -14582001)

    def test_split_units(self):
        split = time_tools.split_units

        self.assertEqual(split(0), (0, 0, 0, 0))
        self.assertEqual(split(1), (0, 0, 0, 1))
        self.assertEqual(split(1001), (0, 0, 1, 1))
        self.assertEqual(split(61001), (0, 1, 1, 1))
        self.assertEqual(split(3661001), (1, 1, 1, 1))

        self.assertEqual(split(-1), (0, 0, 0, -1))
        self.assertEqual(split(-1001), (0, 0, -1, -1))
        self.assertEqual(split(-61001), (0, -1, -1, -1))
        self.assertEqual(split(-3661001), (-1, -1, -1, -1))

        self.assertEqual(split(-14582001), (-4, -3, -2, -1))
        self.assertEqual(split(-3723004), (-1, -2, -3, -4))

        self.assertEqual(split(3723004), (1, 2, 3, 4))
        self.assertEqual(
            split(-12345678), tuple(map(operator.neg, split(12345678))))

    def test_ms_to_str(self):
        to_str = time_tools.ms_to_str

        self.assertEqual(to_str(0), '00:00:00.000')
        self.assertEqual(to_str(1), '00:00:00.001')
        self.assertEqual(to_str(1001), '00:00:01.001')
        self.assertEqual(to_str(61001), '00:01:01.001')
        self.assertEqual(to_str(3661001), '01:01:01.001')

        self.assertEqual(to_str(3723004), '01:02:03.004')
        self.assertEqual(to_str(-3723004), '-01:02:03.004')

        # Unicode symbols
        self.assertEqual(
            to_str(3723004, True),
            '01\N{RATIO}02\N{RATIO}03.004')
        self.assertEqual(
            to_str(-3723004, True),
            '\N{MINUS SIGN}01\N{RATIO}02\N{RATIO}03.004')

    def test_str_to_ms(self):
        to_ms = time_tools.str_to_ms

        self.assertEqual(to_ms(''), 0)
        self.assertEqual(to_ms('   '), 0)
        self.assertEqual(to_ms(':'), 0)
        self.assertEqual(to_ms('::'), 0)
        self.assertEqual(to_ms(':::'), 0)
        self.assertEqual(to_ms(',\N{RATIO}:'), 0)
        self.assertEqual(to_ms('  ,  \N{RATIO}  :  '), 0)

        self.assertRaises(ValueError, to_ms, 'abc')
        self.assertRaises(ValueError, to_ms, 'a:b:c')
        self.assertRaises(ValueError, to_ms, 'a:b:1')
        self.assertRaises(ValueError, to_ms, 'a:1:1')
        self.assertRaises(ValueError, to_ms, 'a1:1:1')
        self.assertRaises(ValueError, to_ms, '-')
        self.assertRaises(ValueError, to_ms, ':-:')
        self.assertRaises(ValueError, to_ms, ':-:1')
        self.assertRaises(ValueError, to_ms, '--1')
        self.assertRaises(ValueError, to_ms, '1-')
        self.assertRaises(ValueError, to_ms, '1.:')
        self.assertRaises(ValueError, to_ms, '1.0:')
        self.assertRaises(ValueError, to_ms, '1.::')
        self.assertRaises(ValueError, to_ms, '1.0::')

        self.assertEqual(to_ms('1'), 1000)
        self.assertEqual(to_ms('-1'), -1000)
        self.assertEqual(to_ms(':1'), 1000)
        self.assertEqual(to_ms(':0:1'), 1000)
        self.assertEqual(to_ms('0:0:1'), 1000)
        self.assertEqual(to_ms('1.'), 1000)
        self.assertEqual(to_ms('1.000'), 1000)
        self.assertEqual(to_ms('1.001'), 1001)
        self.assertEqual(to_ms('1.002'), 1002)

        self.assertEqual(to_ms('1:'), 60000)
        self.assertEqual(to_ms(':1:'), 60000)
        self.assertEqual(to_ms(':-1:'), -60000)

        self.assertEqual(to_ms('1::'), 3600000)
        self.assertEqual(to_ms(':1::'), 3600000)
        self.assertEqual(to_ms(':-1::'), -3600000)

        self.assertEqual(to_ms('1:::'), 0)
        self.assertEqual(to_ms('abc:::'), 0)

        # Subtraction
        self.assertEqual(to_ms('1:-60'), 0)
        self.assertEqual(to_ms('-1:-60'), -120000)
        self.assertEqual(to_ms('1:-120'), -60000)
        self.assertEqual(to_ms('1:-60:'), 0)
        self.assertEqual(to_ms('-1:-60:'), -7200000)
        self.assertEqual(to_ms('1:-59:-60'), 0)
        self.assertEqual(to_ms('-1:59:60'), 0)
        self.assertEqual(to_ms('-1:-59:-60'), -7200000)
        self.assertEqual(to_ms('1:-61:60'), 0)
        self.assertEqual(to_ms('-1:61:-60'), 0)

        # Leading nulls
        self.assertEqual(to_ms('01:02:03.004'), 3723004)
        self.assertEqual(to_ms('1:2:3.004'), 3723004)
        self.assertEqual(to_ms('0001:0002:0003.004'), 3723004)

        self.assertEqual(to_ms('\N{MINUS SIGN}01:02:03.004'), -3476996)

        # Separators
        self.assertEqual(to_ms('01\N{RATIO}02\N{RATIO}03.004'), 3723004)
        self.assertEqual(to_ms('01,02,03.004'), 3723004)
        self.assertEqual(to_ms('01 02 03.004'), 3723004)
        self.assertEqual(to_ms('01\t02\t03.004'), 3723004)
        self.assertEqual(to_ms('01\t \N{RATIO} \t02 \t , \t 03.004'), 3723004)
        self.assertEqual(to_ms('1   2   3.004'), 3723004)
        self.assertEqual(to_ms(' \t1\t \t2 \t 3.004\t '), 3723004)


if __name__ == '__main__':
    unittest.main()
