import sys

if __name__ == "__main__":
    try:
        bot = sys.argv[1]
        if bot == 'francis':
            from francis import launch as francis_launch
            francis_launch
        elif bot == 'oz':
            from oz import launch as oz_launch
            oz_launch
        else:
            print('Specify a bot to run (francis/oz)')
    except IndexError:
        print('Specify a bot to run (francis/oz)')
