#!/usr/bin/env python3
'''
test for the assist module.
'''

from test_base import PschedTestBase

from pscheduler.assist import assist


class TestAssist(PschedTestBase):
    '''
    Assist tests.
    '''

    def test_assist(self):
        '''Assist tests'''

        # Basic validation and early returns

        self.assertRaises(AssertionError, assist, 1234, [], {})
        self.assertRaises(AssertionError, assist, '.host', None, {})
        self.assertRaises(AssertionError, assist, '.host', [], None)

        self.assertEqual(assist(None), None)
        self.assertRaises(ValueError, assist, '')
        self.assertEqual(assist('foo.example.net'), 'foo.example.net')

        # Command Line

        assist_option = '.source,host,dest'
        args = [
            '--foo',
            '--bar',
            '--host-separate', 'separate',
            '--host-assign=assign',
            '--baz',
            '--end'
        ]

        # Command Line

        self.assertRaises(ValueError, assist, '.foo', ['--foo='])
        self.assertEqual(assist('.host-assign', args), 'assign')
        self.assertEqual(assist('.host-separate', args), 'separate')
        # Over the end with no following arg
        self.assertRaises(ValueError, assist, '.end', args)

        # Parameters
        params = {
            'host-param': 'param',
            'host-assign': 'should-not-be-used'
        }
        self.assertEqual(assist('.host-param', args, params), 'param')
        self.assertRaises(ValueError, assist, '.notastring', args, { '.notastring': 3 })
        # This should come from args.
        self.assertEqual(assist('.host-assign', args, params), 'assign')
        
        # Not present anywhere
        self.assertRaises(ValueError, assist, '.not-present', args, params)

        # Make sure stripping works
        self.assertEqual(assist('. foo , bar,baz ', [], { 'foo': 'param' }), 'param')
        self.assertEqual(assist('. foo , bar,baz ', [], { 'bar': 'param' }), 'param')
        self.assertEqual(assist('. foo , bar,baz ', [], { 'baz': 'param' }), 'param')


if __name__ == '__main__':
    unittest.main()
