#!/usr/bin/env python

import time

import click
import pyperclip
from Quartz.CoreGraphics import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap


DELETE = object()
CAPS_LOCK = object()
SHIFT = object()
CONTROL = object()
OPTION = object()
COMMAND = object()

KEY_CODES = [
    [0x32, 0x12, 0x13, 0x14, 0x15, 0x17, 0x16, 0x1A, 0x1C, 0x19, 0x1D, 0x1B, 0x18, 0x33],
    [0x30, 0x0c, 0x0d, 0x0e, 0x0f, 0x11, 0x10, 0x20, 0x22, 0x1f, 0x23, 0x21, 0x1e, 0x2a],
    [0x39, 0x00, 0x01, 0x02, 0x03, 0x05, 0x04, 0x26, 0x28, 0x25, 0x29, 0x27, 0x24],
    [0x38, 0x06, 0x07, 0x08, 0x09, 0x0b, 0x2d, 0x2e, 0x2b, 0x2f, 0x2c, 0x3c],
    [0x3b, 0x3a, 0x37, 0x31, 0x37, 0x3d, 0x3e]
]

QWERTY = {
    'unshifted': [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', DELETE],
        ['\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
        [DELETE, 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '\n'],
        [SHIFT, 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', SHIFT],
        [CONTROL, OPTION, COMMAND, ' ', COMMAND, OPTION, CONTROL]
    ],
    'shifted':  [
        ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', DELETE],
        ['\t', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '|'],
        [DELETE, 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', '\n'],
        [SHIFT, 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', SHIFT],
        [CONTROL, OPTION, COMMAND, ' ', COMMAND, OPTION, CONTROL]
    ]
}

COLEMAK = {
    'unshifted': [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', DELETE],
        ['\t', 'q', 'w', 'f', 'p', 'g', 'j', 'l', 'u', 'y', ';', '[', ']', '\\'],
        [DELETE, 'a', 'r', 's', 't', 'd', 'h', 'n', 'e', 'i', 'o', '\'', '\n'],
        [SHIFT, 'z', 'x', 'c', 'v', 'b', 'k', 'm', ',', '.', '/', SHIFT],
        [CONTROL, OPTION, COMMAND, ' ', COMMAND, OPTION, CONTROL]
    ],
    'shifted':  [
        ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', DELETE],
        ['\t', 'Q', 'W', 'F', 'P', 'G', 'J', 'L', 'U', 'Y', ':', '{', '}', '|'],
        [DELETE, 'A', 'R', 'S', 'T', 'D', 'H', 'N', 'E', 'I', 'O', '"', '\n'],
        [SHIFT, 'Z', 'X', 'C', 'V', 'B', 'K', 'M', '<', '>', '?', SHIFT],
        [CONTROL, OPTION, COMMAND, ' ', COMMAND, OPTION, CONTROL]
    ]
}


def char_to_key_code(c, layout=QWERTY):
    for i, row in enumerate(layout['unshifted']):
        if c in row:
            j = row.index(c)
            return KEY_CODES[i][j], False

    for i, row in enumerate(layout['shifted']):
        if c in row:
            j = row.index(c)
            return KEY_CODES[i][j], True

    raise ValueError(f'{c} is not supported')


def key_press(c, layout=QWERTY):
    key_code, shift = char_to_key_code(c, layout=layout)
    time.sleep(0.0001)

    if shift:
        CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, 0x38, True))
        time.sleep(0.0001)

    CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, key_code, True))
    time.sleep(0.0001)

    CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, key_code, False))
    time.sleep(0.0001)

    if shift:
        CGEventPost(kCGHIDEventTap, CGEventCreateKeyboardEvent(None, 0x38, False))
        time.sleep(0.0001)


def prime_keyboard(layout=QWERTY):
    for _ in range(10):
        key_press('a', layout=layout)
        key_press(DELETE, layout=layout)


@click.command()
@click.argument(
    'text',
    required=False
)
@click.option(
    '--delay',
    default=3,
    type=int,
    show_default=True,
    help='The typing delay.'
)
@click.option(
    '--prime/--no-prime',
    default=True,
    help='Prime the keyboard before typing.'
)
@click.option(
    '--layout',
    default='qwerty',
    type=click.Choice(['qwerty', 'colemak']),
    help='Set the keyboard layout.'
)
def main(text, delay, prime, layout):
    layout = {
        'qwerty': QWERTY,
        'colemak': COLEMAK
    }[layout]

    if not text:
        text = pyperclip.paste()
        click.echo('Extracted text from clipboard')

    click.echo(f'Delaying typing for {delay} seconds...')
    time.sleep(3)

    if prime:
        click.echo(f'Priming keyboard')
        prime_keyboard()

    click.echo('Typing...')
    for char in text:
        key_press(char, layout=layout)

    print('Done!')


if __name__ == '__main__':
    main()
