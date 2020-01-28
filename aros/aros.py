import os
import sys
import importlib
import pkg_resources
import json
import argparse
from ruamel import yaml
import random
import textwrap
from datetime import datetime

from .logger import Logger

class BC:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class AROS():
    def __init__(self, args=None, init=True):
        if not init:
            return

        self.datetime = datetime
        self.version = pkg_resources.get_distribution('aros').version

        if args == None:
            self.args = vars(self.load_arguments())
        else:
            self.args = args

        self.colors = {
            'purple': BC.PURPLE,
            'blue': BC.BLUE,
            'green': BC.GREEN,
            'yellow': BC.YELLOW,
            'red': BC.RED,
            'reset': BC.RESET,
            'bold': BC.BOLD,
            'underline': BC.UNDERLINE,
        }

        self.color_order = [
            BC.RESET,
            BC.PURPLE,
            BC.BLUE,
            BC.GREEN,
            BC.YELLOW,
            BC.RED,
        ]

        logger_params = {
            'level': self.args['log_level']
        }
        if os.getenv('DEBUG'):
            logger_params['level'] = 'debug'
        self.logger = Logger(**logger_params)

        if 'version' in self.args and self.args['version']:
            self.logger.log(self.version)
            sys.exit(0)

        self.logger.log('AROS version: %s' % self.version, level='debug')
        self.logger.log('Args: %s' % json.dumps(self.args, indent=2, default=str), level='debug')

        self.config = yaml.load(open(self.args['config']), Loader=yaml.Loader)
        # self.logger.log('Config: %s' % json.dumps(self.config, indent=2, default=str), level='debug')
        self.indent = self.config['options']['print_indent'] * ' '
        self.vars = {}

        if 'seed' not in self.args or self.args['seed'] == '':
            self.args['seed'] = ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') for x in range(16))

        self.random = random.Random(self.args['seed'])
        # random.seed(self.args['seed'])
        self.logger.log('Seed: %s' % self.args['seed'])

        # for n in range(20):
        #     print(random.randint(1, 10))
        # print(BC.PURPLE + 'LOL')
        # print(BC.BLUE + 'LOL')
        # print(BC.GREEN + 'LOL')
        # print(BC.YELLOW + 'LOL')
        # print(BC.RED + 'LOL')
        # print(BC.RESET + 'LOL')
        # print(BC.BOLD + 'LOL')
        # print(BC.UNDERLINE + 'LOL')
        # sys.exit(0)

    def load_arguments(self):
        parser = argparse.ArgumentParser(description='AROS options.')

        parser.add_argument('command', metavar='<command>', type=str, help='options are: [generate]')
        parser.add_argument('args', metavar='<args>', type=str, nargs='+', help='arguments for your chosen command')

        parser.add_argument('-c', '--config', default='%s/tables.yaml' % os.path.dirname(os.path.realpath(globals()['__file__'])), help='path to the config file')
        parser.add_argument('-l', '--log_level', default='info', help='set the desired logging level, options are: [info,debug,warn,error]')
        parser.add_argument('-r', '--rolls_on', default=False, action='store_true', help='show rolled values')
        parser.add_argument('-s', '--seed', default='', help='sets the random generator seed')
        parser.add_argument('--spread', default=0, type=int, help='widens the option range for table rolls')
        parser.add_argument('-v', '--version', action='store_true', help='display the package version')

        return parser.parse_args()

    def command_map(self, args):
        self.vars['depth'] = args[0]
        self.vars['depth_value'] = [d['name'] for d in self.config['depths']].index(self.vars['depth']) + 1

        map_size = self.config['options']['map_size']
        plunge_row = self.config['options']['map_plunge_row']
        plunge_col = self.config['options']['map_plunge_col']
        half = int(map_size / 2)
        exit_distance = self.roll_die(die=10, advantage=2)

        rooms = []
        for x in range(map_size):
            rooms.append([{} for y in range(map_size)])

        plunge = self.config['table']['environment'][self.vars['depth']]['plunge']

        rooms[plunge_col][plunge_row] = {
            'location': plunge,
            'hallways': 1 if self.vars['depth'] == 'reef' else 3,
            'exit': exit_distance,
            'distance': 0,
            'halls': [],
            'index': 0,
        }

        self.room_list = [rooms[plunge_col][plunge_row]]
        self.room_index = 0

        if self.vars['depth'] == 'reef':
            barrier_row = plunge_row + 1
            barrier_col = plunge_col
            rooms[plunge_col][plunge_row]['hallways'] = 0
            rooms[plunge_col][plunge_row]['halls'] = ['S']

            barrier = self.config['table']['environment']['reef']['great_barrier']
            rooms[barrier_col][barrier_row] = {
                'location': barrier,
                'hallways': barrier['hallways'] - 1,
                'distance': 0,  # technically should be 1, but reef maps are a little tight
                'halls': ['N'],
                'index': 1,
            }

            self.room_list.append(rooms[barrier_col][barrier_row])
            self.room_index += 1

            map = self.depth_first_map(rooms, self.vars['depth'], barrier_col, barrier_row)
        else:
            map = self.depth_first_map(rooms, self.vars['depth'], plunge_col, plunge_row)

        self.print_map(map, exit_distance)

    def depth_first_map(self, rooms, depth, x, y):
        if rooms[x][y]['distance'] >= self.config['options']['map_max_distance']:
            return

        direction_list = ['W', 'N', 'E', 'S']

        # directions = direction_list.copy()
        # this isn't deterministic, and we need a deterministic order for seeding
        # directions = list(set(directions) - set(rooms[x][y]['halls']))

        directions = []
        for d in direction_list:
            if d not in rooms[x][y]['halls']:
                directions.append(d)

        self.random.shuffle(directions)

        while rooms[x][y]['hallways'] > 0 and len(directions) > 0:
            direction = directions.pop(0)
            opposite_direction = direction_list[(direction_list.index(direction) + 2) % len(direction_list)]

            if direction == 'W' and x - 1 >= 0:
                next_x = x - 1
                next_y = y
            elif direction == 'N' and y - 1 >= 0:
                next_x = x
                next_y = y - 1
            elif direction == 'E' and x + 1 < len(rooms):
                next_x = x + 1
                next_y = y
            elif direction == 'S' and y + 1 < len(rooms[0]):
                next_x = x
                next_y = y + 1
            else:
                self.logger.log('map out of bounds: %s, %s' % (x, y), level='debug')
                continue

            if rooms[next_x][next_y]:
                if rooms[next_x][next_y]['hallways'] <= 0:
                    self.logger.log('room exists and has no hallways...' % rooms[next_x][next_y], level='debug')
                    continue
                else:
                    self.logger.log('room exists, connecting...' % rooms[next_x][next_y], level='debug')
                    rooms[x][y]['halls'].append(direction)
                    rooms[next_x][next_y]['halls'].append(opposite_direction)
                    rooms[x][y]['hallways'] -= 1
                    rooms[next_x][next_y]['hallways'] -= 1
            else:
                room = self.roll_room(depth)
                room['distance'] = rooms[x][y]['distance'] + 1
                rooms[next_x][next_y] = room

                self.logger.log('next room: %s' % rooms[next_x][next_y], level='debug')
                rooms[x][y]['halls'].append(direction)
                rooms[next_x][next_y]['halls'].append(opposite_direction)
                rooms[x][y]['hallways'] -= 1
                rooms[next_x][next_y]['hallways'] -= 1

                self.depth_first_map(rooms, depth, next_x, next_y)

        return rooms

    def roll_room(self, depth):
        self.room_index += 1

        location = self.roll_table(self.config['table']['environment'][depth]['location'])[0].copy()
        self.parse_rolls(location)
        situation = self.roll_table(self.config['table']['situation'])[0].copy()
        self.parse_rolls(situation)

        room = {
            'location': location,
            'situation': situation,
            'index': self.room_index,
            'hallways': location['hallways'],
            'halls': [],
        }

        if isinstance(room['hallways'], str):
            room['hallways'] = self.parse_str_roll(room['hallways'])

        self.room_list.append(room)
        return room

    def command_roll(self, args):
        table = self.dig(self.config['table'], args[0])
        self.roll(label=args[0], table=table)

    def parse_rolls(self, data, root=None):
        if not isinstance(data, dict) or 'roll' not in data:
            return

        if root == None:
            root = data

        self.logger.log('parsing rolls...' % data, level='debug')
        self.logger.log(json.dumps(data, indent=2, default=str), level='debug')

        if not isinstance(data['roll'], list):
            data['roll'] = [data['roll']]

        for roll in data['roll']:
            if not isinstance(roll, dict):
                roll = {'table': roll}

            if 'count' not in roll:
                roll['count'] = 1
            roll['count'] = self.interpolate_value(roll['count'])

            if 'advantage' not in roll:
                roll['advantage'] = 0

            results = []

            if 'result' in roll:
                if not isinstance(roll['result'], list):
                    roll['result'] = [roll['result']]
                results.extend(roll['result'])

            self.logger.log(str(results), level='debug')

            if 'table' in roll:
                if not isinstance(roll['table'], list):
                    roll['table'] = [roll['table']]
                table = [self.dig(self.config['table'], t) for t in roll['table']]

                for c in range(roll['count']):
                    results.extend([self.roll_table(table=t, advantage=roll['advantage']) for t in table])

            elif 'args' in roll:
                roll_results = [self.roll_die(**roll['args'])]

                for r in results:
                    if '%s' in r['name']:
                        r['name'] = r['name'] % roll_results[0]

                results.append(roll_results)

            flat_results = []
            for r in results:
                if isinstance(r, list):
                    for _r in r:
                        flat_results.append(_r)
                else:
                    flat_results.append(r)

            self.logger.log('extended results', level='debug')
            self.logger.log(str(flat_results), level='debug')

            for r in flat_results:
                if isinstance(r, dict):
                    if 'format' in roll:
                        r['format'] = roll['format']
                    if 'type' in r:
                        if r['type'] not in root:
                            root[r['type']] = []
                        root[r['type']].append(r)

            if 'results' not in root:
                root['results'] = []

            root['results'].extend(flat_results)

            for r in flat_results:
                if isinstance(r, dict) and 'roll' in r:
                    self.parse_rolls(r, root)


    def roll(self, label='', table=None):
        if isinstance(table, list) or 'entries' in table:
            result = self.roll_table(table=table, spread=self.args['spread'])
            self.logger.log(' - %s: %s' % (label, result))
        else:
            for key, value in table.items():
                self.roll('%s.%s' % (label, key), value)

    def roll_table(self, table=[], spread=0, advantage=None):
        adv = 0

        if isinstance(table, list):
            table = {'entries': table}

        entries = table['entries'].copy()

        if 'advantage' in table:
            adv = table['advantage']
        if advantage != None:
            adv = advantage

        if isinstance(entries[0], dict):
            expanded_table = []
            for entry in entries:
                if 'frequency' in entry:
                    for n in range(0, entry['frequency']):
                        expanded_table.append(entry)
                else:
                    expanded_table.append(entry)
            entries = expanded_table

        die = len(entries)
        roll = self.roll_die(die, advantage=adv)
        roll -= 1
        rolls = [roll]

        for n in range(1, spread + 1):
            rolls.insert(0, (roll - n) % die)
            rolls.append((roll + n) % die)

        results = []
        for r in rolls:
            if not isinstance(entries[r], dict):
                result = {'name': entries[r]}
            else:
                result = entries[r].copy()

            result['die'] = r + 1

            keys = [
                'advantage',
                'count',
                'format',
                'roll',
                'type',
            ]
            for k in keys:
                if k in table and k not in result:
                    result[k] = table[k]

            results.append(result)

        return results

    # returns 1..N
    def roll_die(self, die, count=1, advantage=0):
        advantage = max(-3, min(advantage, 3))
        count = self.interpolate_value(count)

        valid_dice = [
            2,
            3,
            4,
            6,
            8,
            10,
            12,
            20,
            100,
        ]

        if die not in valid_dice:
            self.logger.log('Invalid roll: must be a valid die roll! Die has %s sides!' % die, level='error')
            sys.exit(1)

        adv_count = count + abs(advantage)

        roll = [self.random.randint(1, die) for c in range(adv_count)]
        final_roll = sorted(roll.copy())

        for n in range(abs(advantage)):
            if advantage > 0:
                final_roll.pop(0)
            else:
                del final_roll[-1]
        roll_sum = sum(final_roll)

        if self.args['rolls_on']:
            adv = ''
            if advantage > 0:
                adv = '+' * advantage
            else:
                adv = '-' * abs(advantage)
            self.logger.log('roll (%sd%s%s) -> %s -> %s -> %s' % (count, die, adv, roll, final_roll, roll_sum))

        return roll_sum

    def dig(self, data, path):
        keys = path.split('.')
        while keys:
            if keys[0].isdigit():
                keys[0] = int(keys[0])

            if keys[0]:
                keys[0] = self.interpolate_value(keys[0])
                data = data[keys[0]]

            keys.pop(0)

        return data

    def interpolate_value(self, value):
        if isinstance(value, str) and value.startswith('$'):
            return self.vars[value[1:]]
        else:
            return value

    def print_map(self, rooms, exit_distance):
        self.logger.log()

        for y in range(len(rooms[0])):
            x_rooms = []
            for x in range(len(rooms)):
                x_rooms.append(rooms[x][y])

            room_lines = [self.print_room_to_lines(r) for r in x_rooms]

            for l in range(self.config['options']['map_print_room_rows']):
                print(''.join([rl[l] for rl in room_lines]))

        self.logger.log()
        self.logger.log('Exit Distance: %s' % self.color(str(exit_distance), BC.BOLD))

        for r in self.room_list:
            self.print_room_description(r)

    def print_room_to_lines(self, room):
        height = self.config['options']['map_print_room_rows']
        width = self.config['options']['map_print_room_cols']
        half_height = int(height / 2)
        half_width = int(width / 2)
        if 'map_print_fill' in self.config['options']:
            fill = self.config['options']['map_print_fill']
        else:
            fill = '░'
        if not isinstance(fill, list):
            fill = [fill]

        # fill = [self.color(f, BC.BLUE) for f in fill]

        lines = []
        for l in range(height):
            lines.append(' ' * width)

        if room:
            if 'danger' in room['location']:
                color = room['location']['danger'] + 3
            else:
                color = 0

            lines[0] = '%s%s%s' % (' ' * half_width, self.color('║', self.color_order[color]) if 'N' in room['halls'] else ' ', ' ' * half_width)
            room_top = '╔%s%s%s╗' % ('═' * (half_width - 2), '╩' if 'N' in room['halls'] else '═', '═' * (half_width - 2))
            lines[1] = ' %s ' % self.color(room_top, self.color_order[color])

            room_bottom = '╚%s%s%s╝' % ('═' * (half_width - 2), '╦' if 'S' in room['halls'] else '═', '═' * (half_width - 2))

            lines[height - 2] = ' %s ' % self.color(room_bottom, self.color_order[color])
            lines[height - 1] = '%s%s%s' % (' ' * half_width, self.color('║', self.color_order[color]) if 'S' in room['halls'] else ' ', ' ' * half_width)

            text_lines = []
            line_format = '{0:<%s.%s}' % (width - 4, width - 4)
            index_format = '{0:>2.2}'
            title_format = '{0:<%s.%s}' % (width - 7, width - 7)
            index = self.color(index_format.format(str(room['index'])), 'bold')
            title = self.color(title_format.format(room['location']['name']), 'underline')
            text_lines.append(index + ' ' + title)
            if 'situation' in room:
                text_lines.append(self.color(line_format.format('%s' % room['situation']['name']), 'blue'))
            if 'exit' in room:
                text_lines.append(line_format.format('Exit: %s' % room['exit']))

            misc_lines = height - 6

            if 'trap' in room['location']:
                if misc_lines > 0:
                    trap_line = ', '.join([t['name'] for t in room['location']['trap']])
                    c = self.config['options']['descriptions']['colors']['trap']
                    text_lines.append(self.color(line_format.format(trap_line), c))
                    misc_lines -= 1

            if 'creature' in room['location']:
                creatures = list(self.chunks(room['location']['creature'], self.config['options']['map_print_creatures_per_line']))
                i = 0
                while misc_lines > 0 and i < len(creatures):
                    creature_line = ', '.join([c['name'] for c in creatures[i]])
                    c = self.config['options']['descriptions']['colors']['creature']
                    text_lines.append(self.color(line_format.format(creature_line), c))
                    i += 1
                    misc_lines -= 1

            for n in range(2, height - 2):
                lines[n] = ''
                if n == half_height and 'W' in room['halls']:
                    lines[n] += self.color('═╣', self.color_order[color])
                else:
                    lines[n] += ' %s' % self.color('║', self.color_order[color])

                if n - 2 < len(text_lines):
                    lines[n] += text_lines[n - 2]
                else:
                    lines[n] += ' ' * (width - 4)

                if n == half_height and 'E' in room['halls']:
                    lines[n] += self.color('╠═', self.color_order[color])
                else:
                    lines[n] += '%s ' % self.color('║', self.color_order[color])

        for l in range(len(lines)):
            for i in range(len(lines[l])):
                if lines[l][i] == ' ':
                    f = (l + i) % len(fill)
                    tmp = list(lines[l])
                    tmp[i] = fill[f]
                    lines[l] = ''.join(tmp)
                elif lines[l][i] not in self.color_order:
                    # print('(%s)' % lines[l][i])
                    break
            for i in reversed(range(len(lines[l]))):
                if lines[l][i] == ' ':
                    f = (l + i) % len(fill)
                    tmp = list(lines[l])
                    tmp[i] = fill[f]
                    lines[l] = ''.join(tmp)
                elif lines[l][i] not in self.color_order:
                    # print('(%s)' % lines[l][i])
                    break

        return lines

    def print_room_description(self, room):
        self.logger.log(json.dumps(room, indent=2, default=str), level='debug')

        danger = ''
        location_color = 0
        if 'danger' in room['location']:
            location_color = room['location']['danger'] + 3
            if room['location']['danger'] > 0:
                danger = '+' * room['location']['danger']
            elif room['location']['danger'] < 0:
                danger = '-' * abs(room['location']['danger'])

        print(self.color_order[location_color])
        print('{0:>2}. {1} {2}'.format(room['index'], room['location']['name'], danger))
        print('--------------------------------')
        print(BC.RESET)
        print(textwrap.indent('{0}'.format(room['location']['description']), self.indent))
        print()
        if 'results' in room['location']:
            self.print_room_results(room['location']['results'])

        if 'situation' in room:
            print(BC.BLUE)
            print(textwrap.indent('Situation: {0}'.format(room['situation']['name']), self.indent))
            print(textwrap.indent('--------------------------------', self.indent))
            print(BC.RESET)
            print(textwrap.indent('{0}'.format(room['situation']['description']), self.indent))
            print()
            if 'results' in room['situation']:
                self.print_room_results(room['situation']['results'])

    def print_room_results(self, results):
        for r in results:
            if not isinstance(r, dict):
                r = {'name': r}

            if 'type' in r:
                if 'format' not in r:
                    r['format'] = r['type'].title() + ': %s'
                if r['type'] in self.config['options']['descriptions']['colors']:
                    print(self.colors[self.config['options']['descriptions']['colors'][r['type']]])
            else:
                print(BC.PURPLE)

            if 'format' not in r:
                r['format'] = 'Roll Result: %s'

            text = ''
            if 'die' in r:
                text += '[%s] ' % r['die']

            if isinstance(r['name'], list):
                text += r['format'] % tuple(r['name'])
            else:
                text += r['format'] % r['name']

            print(textwrap.indent(text, self.indent))
            if 'description' in r:
                print(textwrap.indent(r['description'], self.indent))

        print(BC.RESET)

    def parse_str_roll(self, string):
        count, die = string.split('d')
        return self.roll_die(count=int(count), die=int(die))

    def color(self, text, color):
        if color in self.colors:
            color = self.colors[color]

        return '%s%s%s' % (color, text, BC.RESET)

    def chunks(self, lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def run(self):
        commands = [
            'roll',
            'map',
        ]

        if self.args['command'] not in commands:
            self.logger.log('Invalid command: %s, must be one of %s' % (self.args['command'], commands), level='error')
            sys.exit(1)

        getattr(self, "command_%s" % self.args['command'])(self.args['args'])

def main():
    AROS().run()

if __name__ == '__main__':
    main()
