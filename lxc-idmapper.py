#!/usr/bin/python3
import argparse
import sys
import json
import itertools
import logging

from pprint import pprint as pp
from pprint import pformat as ppf


# maps cont to host
uid_map = {}
gid_map = {}


def range_str_to_range(val):
    pre, post = val.split("-")
    return range(int(pre), int(post))


def range_sorter(val):
    if isinstance(val, range):
        return (val.start, val.stop, len(val))
    try:
        for a in val:
            return range_sorter(a)
    except TypeError:
        pass
    return 0


def range_overlaps(a, b):
    """
    if anything in range a is in range b
    """
    # logging.debug(f"a {a} :: b {b}")
    try:
        logging.debug(f"b start {b.start}, a start {a.start} b stop {b.stop-1}")
        b.index(a.start)
        return True
    except ValueError:
        pass
    try:
        logging.debug(f"b start {b.start}, a stop {a.stop-1} b stop {b.stop-1}")
        b.index(a.stop-1)
        return True
    except ValueError:
        pass
    return False


def id_map_func(val):
    if ":" in val:
        cont, host = val.split(":")
        if bool("-" in host) ^ bool("-" in cont):
            raise Exception("one input is a range and one isn't")
        if "-" in host and "-" in cont:
            host = range_str_to_range(host)
            cont = range_str_to_range(cont)
        else:
            host = int(host)
            cont = int(cont)
            host = range(host, host+1)
            cont = range(cont, cont+1)
    elif "-" in val:
        host = range_str_to_range(val)
        cont = range_str_to_range(val)
    if len(host) != len(cont):
        raise Exception(f"host range {host} ({len(host)}) and cont range {cont} ({len(cont)}) are different lengths")
    return {cont: host}


if __name__ == "__main__":
    num_ids = 65536

    cli_args = argparse.ArgumentParser(epilog="format cont[-cont]:host[-host] or id-id.\n IDs are [x-y), its exclusive of the ending ID")
    cli_args.add_argument("--uid", type=id_map_func, action='append',
                            nargs="+", default=None)
    cli_args.add_argument("--gid", type=id_map_func, action='append',
                            nargs="+", default=None)
    cli_args.add_argument("--default_host_map_start", default=100000, type=int, help="default 100000")
    cli_args.add_argument("--mapping_user", default="root", help="user to create subuid and subgid files for\ndefault: root")
    cli_args.add_argument("mappings", type=id_map_func, action='append',
                            nargs="+", default=None, help="format cont[-cont]:host[-host] or id-id" )
    cli_args.add_argument("--log_level", choices=list(logging.getLevelNamesMapping().keys()), type=str.upper, default="INFO")

    args = cli_args.parse_args()
    logging.basicConfig(level=logging.getLevelName(args.log_level))

    default_range = range(args.default_host_map_start, args.default_host_map_start + num_ids)

    # any arb mappings for uids
    if args.uid:
        args.uid = itertools.chain(*args.uid)
        for m in args.uid:
            uid_map = {**uid_map, **m}
    # any arb mappings for gids
    if args.gid:
        args.gid = itertools.chain(*args.gid)
        for m in args.gid:
            gid_map = {**gid_map, **m}

    # arb mappings that apply to both uids and gids
    args.mappings = itertools.chain(*args.mappings)
    if args.mappings:
        try:
            for m in args.mappings:
                uid_map = {**uid_map, **m}
                gid_map = {**gid_map, **m}
        except TypeError:
            pass

    # overlap check
    for name, mapping in zip(["uid", "gid"], [uid_map, gid_map]):
        for range_check in [list(mapping.keys()), list(mapping.values())]:
            while len(range_check):
                for check in range_check[1:]:
                    if range_overlaps(range_check[0], check):
                        raise Exception(f"{name} range {range_check[0]} overlaps {check}")
                    if range_overlaps(check, range_check[0]):
                        raise Exception(f"{name} range {check} overlaps {range_check[0]}")
                range_check = range_check[1:]

    # if we are here, all mappings are valid

    # for mapping in [uid_map, gid_map]:
    logging.debug(f"uids {ppf(uid_map)}")
    logging.debug(f"gids {ppf(gid_map)}")
    
    # add beginning and end of ranges to maps
    for name, mapping in zip(["uid", "gid"], [uid_map, gid_map]):
        mapping_sorted_list = list(sorted(mapping.items(), key=range_sorter))

        # since there are a lot of vars and i am bad at programming, i scope it so i don't make mistakes
        # c++ {} style
        def do_first_map():
            logging.debug(f"sorted {name}s\n{ppf(mapping_sorted_list)}")
            cont_first, host_first = mapping_sorted_list[0]
            cont_zero_to_first = range(0, cont_first.start)
            host_zero_to_first = range(default_range[0], default_range[cont_first.start])
            logging.debug(("first", name, cont_first, host_first))
            logging.debug(("first", name, cont_zero_to_first, host_zero_to_first))
            if len(cont_zero_to_first):
                mapping[cont_zero_to_first] = host_zero_to_first
        do_first_map()

        # since there are a lot of vars and i am bad at programming, i scope it so i don't make mistakes
        # c++ {} style
        def do_last_map():
            cont_last, host_last = mapping_sorted_list[-1]
            cont_last_to_end = range(cont_last.stop, num_ids)
            host_last_to_end = range(default_range[cont_last.stop], default_range[num_ids-1])
            logging.debug(("last", name, cont_last, host_last))
            logging.debug(("last", name, cont_last_to_end, host_last_to_end))
            if len(cont_last_to_end):
                mapping[cont_last_to_end] = host_last_to_end
        do_last_map()

        logging.debug(f"{name}s\n{ppf(sorted(mapping.items(), key=range_sorter))}")
 
    # # fill in the range gaps
    logging.debug("filling in map gaps")
    for name, mapping in zip(["uid", "gid"], [uid_map, gid_map]):
        mapping_sorted_it = iter(sorted(mapping.items(), key=range_sorter))
        try:
            cont_a, host_a = next(mapping_sorted_it)
            cont_b, host_b = next(mapping_sorted_it)
            while True:
                logging.debug((f"{name}_a", cont_a, host_a))

                gap = range(cont_a.stop, cont_b.start)
                if len(gap):
                    mapping[gap] = range(default_range[gap.start], default_range[gap.stop])
                    logging.debug(("gap  ", gap, mapping[gap]))

                logging.debug((f"{name}_b", cont_b, host_b))

                cont_a, host_a = (cont_b, host_b)
                cont_b, host_b = next(mapping_sorted_it)
        except StopIteration:
            pass


    for name, mapping in zip(["uid", "gid"], [uid_map, gid_map]):
        logging.info(f"final {name}s\n{ppf(list(sorted(mapping.items(), key=range_sorter)))}")
    
    print("# lxc file")
    for name, mapping in zip(["uid", "gid"], [uid_map, gid_map]):
        for cont, host in sorted(mapping.items(), key=range_sorter):
            print(f"lxc.idmap {name[0]} {cont.start:5d} {host.start:6d} {len(cont):5d}")
        print()
    
    for file, mapping in zip(["# /etc/subuid", "# /etc/subgid"], [uid_map, gid_map]):
        print(file)
        for host in sorted(mapping.values(), key=range_sorter):
            print(f"{args.mapping_user}:{host.start}:{len(host)}")
        print()
