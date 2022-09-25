
from math import floor, log


SEPARATOR = '-' * 50


def main():
    available_commands = list(filter(lambda el: not el.startswith('_'), BinaryTranslator.__dict__))

    print('Input ALL numbers WITH sign bit at the start(first bit will be used as sign one)')
    print(SEPARATOR)

    while True:
        command = input('Input action(type "help" to get list of available commands):\n').lower()

        if command in available_commands:
            number = input('Input number:\n').replace(',', '.')
            print_steps = input('Print steps? y/n(enter is equal to "n"):\n').lower() == 'y'

            if 'ieee' in command:
                register = input('Input register(32 or 64 bit)(enter is equal to 32):\n')
                register = int(register) if register else 32

                print()
                print(f'result: {getattr(BinaryTranslator, command)(number, register, print_steps)}', sep='\n')

            else:
                print()
                print(f'result: {getattr(BinaryTranslator, command)(number, print_steps)}', sep='\n')

        elif command == 'help':
            print('\n'.join(available_commands))

        else:
            print('Wrong command! Type "help" to get list of them.')

        print(SEPARATOR)


class BinaryTranslator:
    register = {
        32: {
            'len': 8,
            'mantissa_len': 23,
            'offset': 127
        },

        64: {
            'len': 8,
            'mantissa_len': 52,
            'offset': 1023
        },
    }

    @staticmethod
    def reverse(number: str, _) -> str:
        return number[0] + ''.join(['1' if char == '0' else '0' if char == '1' else char for char in number[1:]])

    @staticmethod
    def additional(number: str, _) -> str:
        sign_bit = number[0]
        number = list(reversed(number[1:]))

        for i, char in enumerate(number):
            if char == '0':
                number[i] = '1'
                return sign_bit + ''.join(reversed(number))

            number[i] = '0'

    @staticmethod
    def bin_to_dec(number: str, print_steps: bool = False) -> str:
        sign_bit = '+' if number[0] == '0' else '-'
        number = number[1:]

        if print_steps:
            result = []
            num = number.split('.')[0]

            print(f'{num}(bin):')

            for i, char in enumerate(reversed(number)):
                if char == '1':
                    result.append(f'2 ^ {i}')

            print(' + '.join(result) + f' = {int(num, 2)}\n')

        if '.' in number:
            real_part, fractional_part = number.split('.')

            return (
                sign_bit +
                str(int(real_part, 2) + float(BinaryTranslator.bin_to_fractional(fractional_part, print_steps)))
            )

        else:
            return sign_bit + str(int(number, 2))

    @staticmethod
    def dec_to_bin(number: str, print_steps: bool = False) -> str:
        sign_bit = str(int(number.startswith('-')))
        number = number.replace('-', '')

        if print_steps:
            num = int(number.split('.')[0])
            result = []

            print(f'{num}(dec):')

            while num > 0:
                max_power = floor(log(num, 2))
                result.append(f'{num} - {2 ** max_power}')
                num -= 2 ** max_power

            result.append('0')
            print(' = '.join(result) + '\n')

        if '.' in number:
            real_part, fractional_part = number.split('.')

            return (
                sign_bit + bin(int(real_part)).replace('0b', '') + '.' +
                BinaryTranslator.fractional_to_bin(fractional_part, print_steps).replace('0.', '')
            )

        else:
            return sign_bit + bin(int(number)).replace('0b', '')

    @staticmethod
    def bin_to_fractional(number: str, print_steps: bool = False) -> str:
        result = sum([2 ** -(i + 1) for i, symbol in enumerate(number) if symbol == '1'])

        if print_steps:
            print(f'0.{number}(bin):')

            print(
                ' + '.join([f'2 ^ {-(i + 1)}' for i, symbol in enumerate(number) if symbol == '1']) + f' = {result}\n'
            )

        return str(result)

    @staticmethod
    def fractional_to_bin(number: str, print_steps: bool = False) -> str:
        if not number.startswith('0.'):
            number = '0.' + number

        number = float(number)
        result = ''

        if print_steps:
            print(f'{number}(dec):')

        for i in range(10):
            number = round(number * 2, 3)

            if print_steps:
                print(f'{i + 1}) {number / 2} * 2 = {number} (real part - {int(number >= 1)})')

            result += str(int(number >= 1))
            number -= number >= 1

        if print_steps:
            print()

        return result

    @staticmethod
    def bin_to_ieee(number: str, register: int = 32, print_steps: bool = False) -> str:
        current_register = BinaryTranslator.register.get(register)

        sign_bit = number[0]
        number = number[1:]

        real_part = number.split('.')[0]
        offset = len(real_part) - 1

        order = BinaryTranslator.dec_to_bin(str(127 + offset))[1:]

        mantissa = (
            number.replace('.', '')[1:] +
            '0' * (current_register.get('mantissa_len') - len(number.replace('.', '')[1:]))
        )

        if print_steps:
            print(f'Sign: {sign_bit}')
            print(f'Order: {order}')
            print(f'Offset: {offset}')
            print(f'Mantissa before moving dot: 1.{number[current_register.get("len"):]}')
            print(f'Mantissa after moving dot: {mantissa}\n')

        return sign_bit + order + mantissa

    @staticmethod
    def ieee_to_bin(number: str, register: int = 32, print_steps: bool = False) -> str:
        current_register = BinaryTranslator.register.get(register)

        sign_bit = number[0]
        number = number[1:]

        order = number[:current_register.get('len')]
        offset = int(BinaryTranslator.bin_to_dec('0' + order)) - 127

        mantissa = (
            '1' +
            number[current_register.get('len'): current_register.get('len') + offset] +
            '.' +
            number[current_register.get('len') + offset:]
        )

        if print_steps:
            print(f'Sign: {sign_bit}')
            print(f'Order: {order}')
            print(f'Offset: {offset}')
            print(f'Mantissa before moving dot: 1.{number[current_register.get("len"):]}')
            print(f'Mantissa after moving dot: {mantissa}\n')

        return sign_bit + mantissa

    @staticmethod
    def dec_to_ieee(number: str, register: int = 32, print_steps: bool = False) -> str:
        return BinaryTranslator.bin_to_ieee(BinaryTranslator.dec_to_bin(number, print_steps), register, print_steps)

    @staticmethod
    def ieee_to_dec(number: str, register: int = 32, print_steps: bool = False) -> str:
        return BinaryTranslator.bin_to_dec(BinaryTranslator.ieee_to_bin(number, register, print_steps), print_steps)


if __name__ == '__main__':
    main()
