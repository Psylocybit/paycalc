#!/usr/local/bin/python3.8

import sys
import errno
import argparse
import json


DEFAULT_CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'maritalStatus': 'single',
    'dependants': 0,
    'allowances': {
        'federal': 1,
        'state': 1,
        'local': 1
    },
    'taxes': {
        'federal': 0.0917,
        'state': 0.0435,
        'local': 0.0,
        'socialSec': 0.0620,
        'medicare': 0.0145
    }
}


def main(argv):
    (args, parser) = cli(argv)
    
    try:
        with open(args.config) as config_file:
            config = json.load(config_file)
    except (IOError, OSError) as e:
        config = DEFAULT_CONFIG
    
    if args.payrate is None and 'payRate' not in config:
        print('You must specify pay rate in config file or by -p, --payrate arguments.')
        parser.print_help(sys.stderr)
        sys.exit(errno.EINVAL)

    payrate = config['payRate'] if args.payrate is None else args.payrate
    payrate_ot = payrate * args.overtime_modifier

    gross = payrate * args.regular
    gross_ot = payrate_ot * args.overtime
    gross_total = gross + gross_ot
    taxes = calulate_taxes(gross_total, config)
    net_total = compute_net(gross_total, taxes, config)

    hours_reg_str = '{0:.2f} hours'.format(args.regular)
    hours_ot_str = '{0:.2f} hours'.format(args.overtime)
    payrate_str = '${0:.2f}/hr'.format(payrate)
    payrate_ot_str = '${0:.2f}/hr'.format(payrate_ot)
    gross_str = '${0:.2f}'.format(gross)
    gross_ot_str = '${0:.2f}'.format(gross_ot)
    gross_total_str = '${0:.2f}'.format(gross_total)
    net_total_str = '${0:.2f}'.format(net_total)

    print('---------------------------------------------')
    print(f'{hours_reg_str} at {payrate_str}\t==> {gross_str}')
    print(f'{hours_ot_str} at {payrate_ot_str} \t==> {gross_ot_str}')
    print('---------------------------------------------')
    print(f'Total (gross):\t\t\t==> {gross_total_str}')
    print('---------------------------------------------')
    for key in taxes:
        print(f"{key.title()}:  \t\t\t==> {'${0:.2f}'.format(taxes[key])}")
    print('---------------------------------------------')
    print(f'Total (net):\t\t\t==> {net_total_str}')
    print('---------------------------------------------')


class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
                      argparse.RawDescriptionHelpFormatter):
    pass


def cli(argv):
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description='Paycheck calculator program',
        formatter_class=CustomFormatter)

    parser.add_argument('-c', '--config',
                        type=str,
                        required=False,
                        metavar='json_file',
                        default=DEFAULT_CONFIG_FILE,
                        help='specify config file path')

    parser.add_argument('-p', '--payrate',
                        type=float,
                        metavar='pay_rate',
                        help='hourly pay rate')
    
    parser.add_argument('-r', '--regular',
                        type=float,
                        required=True,
                        metavar='hours',
                        help='# of regular hours')
    
    parser.add_argument('-ot', '--overtime',
                        type=float,
                        metavar='hours',
                        default=0.0,
                        help='# of overtime hours')
    
    parser.add_argument('-m', '--overtime-modifier',
                        type=float,
                        metavar='hours',
                        default=1.5,
                        help='overtime pay rate modifier')
    
    parser.add_argument('--version', action='version',
                    version='%(prog)s 1.0')

    args = parser.parse_args(argv[1:])

    return (args, parser)


def load_config(filename):
    try:
        with open(filename) as config_file:
            config = json.load(config_file)
    except (IOError, OSError) as e:
        config = DEFAULT_CONFIG
    return config


def calulate_taxes(gross, config):
    taxes = {}
    for key in config['taxes']:
        taxes[key] = gross * config['taxes'][key]
    return taxes


def compute_net(gross, taxes, config):
    net = gross
    for key in taxes:
        net -= taxes[key]
    return net


if __name__ == "__main__":
    sys.exit(main(sys.argv))