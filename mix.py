#!/usr/bin/python
# encoding: utf-8


config_list = [
    {'path': "work/1T-4t 3-alles F20.gcode", 'start': 0, 'stop': 30},
    {'path': "work/1T-4t 3-alles F100.gcode", 'start': 30, 'stop': 60},
    {'path': "work/1T-4t 3-alles F20.gcode", 'start': 60, 'stop': None}
]


def find_start_line(config_item):
    if config_item['start'] == 0:
        return 0
    else:
        return find_layer_line(config_item['path'], config_item['start'])


def find_layer_line(path, layer):
    lines = open(path).readlines()
    for index, line in enumerate(lines):
        if "LAYER:" + `layer` in line:
            return index

    raise ValueError('Following layer could not be found', layer)


def parse_extrusion(line):
    extrusion = line.split(" ")[-1]
    value = float(extrusion[1:])
    return value


def does_line_contain_extrusion(line):
    return line.startswith("G") and "E" in line


def find_last_extrusion_before_layer(path, last_layer):
    last_layer_index = find_layer_line(path, last_layer)
    lines = open(path).readlines()
    for line in reversed(lines[0:last_layer_index]):
        if does_line_contain_extrusion(line):
            return parse_extrusion(line)
    raise ValueError('No last extrusion value could be found for file before layer', path, last_layer)


def find_last_extrusion_value(path):
    lines = open(path).readlines()
    for line in reversed(lines):
        if does_line_contain_extrusion(line):
            return parse_extrusion(line)
    raise ValueError('No last extrusion value could be found for file', path)


def get_line_for_extrusion(new_extrusion, line):
    return " ".join(line.split(" ")[:-1]) + " E" + '{0:.5f}'.format(new_extrusion) + "\n"


def append_to_file(output_file_name, config_item, previous_extrusion, baseline_extrusion):
    output_file = open(output_file_name, "a")
    lines = open(config_item['path']).readlines()
    start_line_index = find_start_line(config_item)

    if config_item['stop'] is None:
        end_line_index = len(lines)
    else:
        end_line_index = find_layer_line(config_item['path'], config_item['stop'])

    # print "start_line_index: " + `start_line_index`
    # print "end_line_index: " + `end_line_index`

    for index, line in enumerate(lines):
        if start_line_index <= index < end_line_index:

            if previous_extrusion is not None and baseline_extrusion is not None and does_line_contain_extrusion(line):
                current_extrusion = parse_extrusion(line)
                difference = current_extrusion - previous_extrusion
                new_extrusion = baseline_extrusion + difference
                line = get_line_for_extrusion(new_extrusion, line)

            output_file.write(line)
    output_file.close()


output_file_name = "work/output.gcode"
open(output_file_name, "w").close()  # empty out file

for index, config_item in enumerate(config_list):
    baseline_extrusion = None
    previous_extrusion = None

    if index > 0:
        previous_extrusion = find_last_extrusion_before_layer(config_item['path'], config_item['start'])
        previous_config = config_list[index - 1]

        if index == 1:
            baseline_extrusion = find_last_extrusion_before_layer(previous_config['path'], previous_config['stop'])
        elif index >= 1:
            baseline_extrusion = find_last_extrusion_value(output_file_name)

    print "File: " + `config_item['path']`
    print "baseline_extrusion: " + `baseline_extrusion`
    print "previous_extrusion: " + `previous_extrusion`
    print ""

    append_to_file(output_file_name, config_item, previous_extrusion, baseline_extrusion)

print "DONE"