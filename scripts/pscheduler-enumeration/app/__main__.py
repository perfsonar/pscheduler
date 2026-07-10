import enumerator

if __name__ == '__main__':
    print('pScheduler Enumeration Simulator\n\nThe following endpoints are supported:\n')
    for endpoint in [
            '/',
            '/pscheduler',
            '/pscheduler/<plugin-type>',
            '/pscheduler/<plugin-type>?expanded',
            '/pscheduler/<plugin-type>/<name>'
    ]:
        print('    ', endpoint)
    print('\nNote that <plugin-type> is plural, e.g., "tests".\n')
    enumerator.main()
