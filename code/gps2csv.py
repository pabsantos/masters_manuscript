#!/usr/bin/python3
import pynmea2, sys, getopt
import pandas as pd
import arrow

import functions as fct

def addRowInDataFrame(raw_row, df):
    df_concat = []
    for ignore, msg in enumerate(raw_row):
        mtype = type(msg).__name__

        if mtype in fct.functions:
            getDataFunction = fct.functions[mtype]

            rows = getDataFunction(msg)
            cols = fct.columns[mtype]

            df_concat.append(pd.DataFrame([rows], columns=cols))
        else:
            continue

    try:
        df_row = pd.concat(df_concat, axis=1)
        valid = df_row.get('Valid?')[0]

        # Concat row in DataFrame if it is valid
        if valid:
            df = pd.concat([df, df_row])

        return df
    except:
        return df

help_str = ("Usage: gps2csv.py -i <input> -o <output>\n"
            "Convert .nmea to .csv\n"
            "\n"
            "  -h, --help   Print this help message and exit\n"
            "  -i, --input  Read data from <input> file\n"
            "  -o, --output Write processed data in <output> file\n"
)

def getCommandLineArgs(argv):
    if len(argv) == 0:
        return None

    cmdline = {}

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["help", "input=", "output="])
    except getopt.GetoptError:
        print(help_str)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print(help_str)
            sys.exit()
        elif opt in ('-i', '--input'):
            cmdline['i'] = arg
        elif opt in ('-o', '--output'):
            cmdline['o'] = arg

    if not ('i' in cmdline and 'o' in cmdline):
        print(help_str)
        sys.exit(2)

    return cmdline['i'], cmdline['o']

def main(filename='test.nmea', output='out.csv'):
    e = []
    row = []
    first = None
    data = pd.DataFrame()

    total_lines = 0
    with open(filename, 'r') as f:
        for line in f:
            total_lines += 1

    print('Input file: "{}" ({} lines)'.format(filename, total_lines))
    print('Output file: "{}"'.format(output))

    print('')

    with open(filename, 'r') as f:
        i = 0
        for line in f:
            i += 1
            print('Line {}/{}'.format(i, total_lines), end='\r')
            try:
                msg = pynmea2.parse(line)
                if type(msg).__name__ != 'TXT':
                    if first == None:
                        first = msg
                    elif type(msg) == type(first):
                        data = addRowInDataFrame(row, data)
                        row = []

                    row.append(msg)
            except:
                e.append('{}: {}'.format(i, sys.exc_info()[1]))

    if len(row) > 1:
        data = addRowInDataFrame(row, data)

    print('')
    print('')
    print('Saving into "{}"'.format(output))
    print('')

    ## Variation of Time - 'S'
    time = pd.to_timedelta(data['Time'])
    S_value = time.diff().fillna(pd.Timedelta(0.0))
    data['S'] = S_value.apply(lambda x: (x.to_pytimedelta().seconds))

    ## Cumulative sum of Time - 'TIME_ACUM'
    data['TIME_ACUM'] = S_value.cumsum().apply(
        lambda x: (x.to_pytimedelta().seconds)
    )

    ## Filename
    data['GPS_FILE'] = filename[:-5]

    data.to_csv(output, index=False)

    if len(e) == 0:
        print('Ok')
    else:
        print('There were some errors')
        for err in e:
            print(err)

if __name__ == '__main__':
    cmdline = getCommandLineArgs(sys.argv[1:])
    if cmdline:
        main(cmdline[0], cmdline[1])
    else:
        main()
