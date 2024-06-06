# lxc-idmapper
I hate lxc.idmap statements, here's python to make it easier

# Usage
```
./lxc-idmapper.py --help
```
```
usage: lxc-idmapper.py [-h] [--uid UID [UID ...]] [--gid GID [GID ...]] [--default_host_map_start DEFAULT_HOST_MAP_START]
                       [--mapping_user MAPPING_USER] [--log_level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}]
                       mappings [mappings ...]

positional arguments:
  mappings              format cont[-cont]:host[-host] or id-id

options:
  -h, --help            show this help message and exit
  --uid UID [UID ...]
  --gid GID [GID ...]
  --default_host_map_start DEFAULT_HOST_MAP_START
                        default 100000
  --mapping_user MAPPING_USER
                        user to create subuid and subgid files for default: root
  --log_level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}

format cont[-cont]:host[-host] or id-id. IDs are [x-y), its exclusive of the ending ID
```

## examples
### simple range, one specific map
```
./lxc-idmapper.py --log_level WARNING 8101:101 4000-6000
```
```
# lxc file
lxc.idmap u     0 100000  4000
lxc.idmap u  4000   4000  2000
lxc.idmap u  6000 106000  2101
lxc.idmap u  8101    101     1
lxc.idmap u  8102 108102 57434

lxc.idmap g     0 100000  4000
lxc.idmap g  4000   4000  2000
lxc.idmap g  6000 106000  2101
lxc.idmap g  8101    101     1
lxc.idmap g  8102 108102 57434

# /etc/subuid
root:101:1
root:4000:2000
root:100000:4000
root:106000:2101
root:108102:57433

# /etc/subgid
root:101:1
root:4000:2000
root:100000:4000
root:106000:2101
root:108102:57433
```

### more complex ranges
```
./lxc-idmapper.py --log_level warning 200-300:1200-1300 4000-6000 --uid 6101:101
```
```
# lxc file
lxc.idmap u     0 100000   200
lxc.idmap u   200   1200   100
lxc.idmap u   300 100300  3700
lxc.idmap u  4000   4000  2000
lxc.idmap u  6000 106000   101
lxc.idmap u  6101    101     1
lxc.idmap u  6102 106102 59434

lxc.idmap g     0 100000   200
lxc.idmap g   200   1200   100
lxc.idmap g   300 100300  3700
lxc.idmap g  4000   4000  2000
lxc.idmap g  6000 106000 59536

# /etc/subuid
root:101:1
root:1200:100
root:4000:2000
root:100000:200
root:100300:3700
root:106000:101
root:106102:59433

# /etc/subgid
root:1200:100
root:4000:2000
root:100000:200
root:100300:3700
root:106000:59535
```

## Debug 
```
./lxc-idmapper.py --log_level DEBUG 8101:101 4000-6000
```
```
DEBUG:root:b start 4000, a start 8101 b stop 5999
DEBUG:root:b start 4000, a stop 8101 b stop 5999
DEBUG:root:b start 8101, a start 4000 b stop 8101
DEBUG:root:b start 8101, a stop 5999 b stop 8101
DEBUG:root:b start 4000, a start 101 b stop 5999
DEBUG:root:b start 4000, a stop 101 b stop 5999
DEBUG:root:b start 101, a start 4000 b stop 101
DEBUG:root:b start 101, a stop 5999 b stop 101
DEBUG:root:b start 4000, a start 8101 b stop 5999
DEBUG:root:b start 4000, a stop 8101 b stop 5999
DEBUG:root:b start 8101, a start 4000 b stop 8101
DEBUG:root:b start 8101, a stop 5999 b stop 8101
DEBUG:root:b start 4000, a start 101 b stop 5999
DEBUG:root:b start 4000, a stop 101 b stop 5999
DEBUG:root:b start 101, a start 4000 b stop 101
DEBUG:root:b start 101, a stop 5999 b stop 101
DEBUG:root:uids {range(4000, 6000): range(4000, 6000), range(8101, 8102): range(101, 102)}
DEBUG:root:gids {range(4000, 6000): range(4000, 6000), range(8101, 8102): range(101, 102)}
DEBUG:root:sorted uids
[(range(4000, 6000), range(4000, 6000)), (range(8101, 8102), range(101, 102))]
DEBUG:root:('first', 'uid', range(4000, 6000), range(4000, 6000))
DEBUG:root:('first', 'uid', range(0, 4000), range(100000, 104000))
DEBUG:root:('last', 'uid', range(8101, 8102), range(101, 102))
DEBUG:root:('last', 'uid', range(8102, 65536), range(108102, 165535))
DEBUG:root:uids
[(range(0, 4000), range(100000, 104000)),
 (range(4000, 6000), range(4000, 6000)),
 (range(8101, 8102), range(101, 102)),
 (range(8102, 65536), range(108102, 165535))]
DEBUG:root:sorted gids
[(range(4000, 6000), range(4000, 6000)), (range(8101, 8102), range(101, 102))]
DEBUG:root:('first', 'gid', range(4000, 6000), range(4000, 6000))
DEBUG:root:('first', 'gid', range(0, 4000), range(100000, 104000))
DEBUG:root:('last', 'gid', range(8101, 8102), range(101, 102))
DEBUG:root:('last', 'gid', range(8102, 65536), range(108102, 165535))
DEBUG:root:gids
[(range(0, 4000), range(100000, 104000)),
 (range(4000, 6000), range(4000, 6000)),
 (range(8101, 8102), range(101, 102)),
 (range(8102, 65536), range(108102, 165535))]
DEBUG:root:filling in map gaps
DEBUG:root:('uid_a', range(0, 4000), range(100000, 104000))
DEBUG:root:('uid_b', range(4000, 6000), range(4000, 6000))
DEBUG:root:('uid_a', range(4000, 6000), range(4000, 6000))
DEBUG:root:('gap  ', range(6000, 8101), range(106000, 108101))
DEBUG:root:('uid_b', range(8101, 8102), range(101, 102))
DEBUG:root:('uid_a', range(8101, 8102), range(101, 102))
DEBUG:root:('uid_b', range(8102, 65536), range(108102, 165535))
DEBUG:root:('gid_a', range(0, 4000), range(100000, 104000))
DEBUG:root:('gid_b', range(4000, 6000), range(4000, 6000))
DEBUG:root:('gid_a', range(4000, 6000), range(4000, 6000))
DEBUG:root:('gap  ', range(6000, 8101), range(106000, 108101))
DEBUG:root:('gid_b', range(8101, 8102), range(101, 102))
DEBUG:root:('gid_a', range(8101, 8102), range(101, 102))
DEBUG:root:('gid_b', range(8102, 65536), range(108102, 165535))
INFO:root:final uids
[(range(0, 4000), range(100000, 104000)),
 (range(4000, 6000), range(4000, 6000)),
 (range(6000, 8101), range(106000, 108101)),
 (range(8101, 8102), range(101, 102)),
 (range(8102, 65536), range(108102, 165535))]
INFO:root:final gids
[(range(0, 4000), range(100000, 104000)),
 (range(4000, 6000), range(4000, 6000)),
 (range(6000, 8101), range(106000, 108101)),
 (range(8101, 8102), range(101, 102)),
 (range(8102, 65536), range(108102, 165535))]
# lxc file
lxc.idmap u     0 100000  4000
lxc.idmap u  4000   4000  2000
lxc.idmap u  6000 106000  2101
lxc.idmap u  8101    101     1
lxc.idmap u  8102 108102 57434

lxc.idmap g     0 100000  4000
lxc.idmap g  4000   4000  2000
lxc.idmap g  6000 106000  2101
lxc.idmap g  8101    101     1
lxc.idmap g  8102 108102 57434

# /etc/subuid
root:101:1
root:4000:2000
root:100000:4000
root:106000:2101
root:108102:57433

# /etc/subgid
root:101:1
root:4000:2000
root:100000:4000
root:106000:2101
root:108102:57433
```
