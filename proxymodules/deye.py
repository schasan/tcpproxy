#!/usr/bin/env python3
import os.path as path
import json

class Module:
    def fn10(self, buf, a, l):
        return int.from_bytes(buf[a:a + l], byteorder='little') / 10.0

    def fn100(self, buf, a, l):
        return int.from_bytes(buf[a:a + l], byteorder='little') / 100.0

    def fn1000(self, buf, a, l):
        return int.from_bytes(buf[a:a + l], byteorder='little') / 1000.0

    def fn10ascii(self, buf, a, l):
        s = buf[a:a + l].decode("utf-8")
        return s

    def __init__(self, incoming=False, verbose=False, options=None):
        # extract the file name from __file__. __file__ is proxymodules/name.py
        self.name = path.splitext(path.basename(__file__))[0]
        self.description = 'Decode Deye Inverter Upload'
        self.incoming = incoming  # incoming means module is on -im chain
        self.len = 16
        self.dfn42 = {
            'inv.serial.ascii': {'adr':  21, 'len': 10, 'f': self.fn10ascii},
            'pv.v.1': {'adr': 85, 'len': 2, 'f': self.fn10},
            'pv.i.1': {'adr': 87, 'len': 2, 'f': self.fn10},
            'pv.kWh_today.1': {'adr': 136, 'len': 2, 'f': self.fn10},
            'pv.kWh_total.1': {'adr': 145, 'len': 2, 'f': self.fn10},
            'pv.v.2': {'adr': 89, 'len': 2, 'f': self.fn10},
            'pv.i.2': {'adr': 91, 'len': 2, 'f': self.fn10},
            'pv.kWh_today.2': {'adr': 138, 'len': 2, 'f': self.fn10},
            'pv.kWh_total.2': {'adr': 149, 'len': 2, 'f': self.fn10},
            'grid.active_power_w': {'adr': 59, 'len': 4, 'f': self.fn10},
            'grid.kWh_today': {'adr': 33, 'len': 4, 'f': self.fn100},
            'grid.kWh_total': {'adr': 37, 'len': 4, 'f': self.fn10},
            'grid.v': {'adr': 45, 'len': 2, 'f': self.fn10},
            'grid.i': {'adr': 51, 'len': 2, 'f': self.fn10},
            'grid.hz': {'adr': 57, 'len': 2, 'f': self.fn100},
            'inv.degc': {'adr': 62, 'len': 2, 'f': self.fn1000}
        }
        if options is not None:
            if 'length' in options.keys():
                self.len = int(options['length'])


    def decode_payload(self, mesg_type, payload):
        res = {}
        match mesg_type:
            case 0x41:
                print('Handshake request')
            case 0x42:
                print('Data request')
                for k, v in self.dfn42.items():
                    res[k] = self.dfn42[k]['f'](payload, self.dfn42[k]['adr'], self.dfn42[k]['len'])
                print(json.dumps(res, indent=2))
            case 0x43:
                print('wifi info? request')
            case 0x47:
                print('Heartbeat request')
            case 0x11:
                print('Handshare response')
            case 0x12:
                print('Data response')
            case 0x13:
                print('wifi info reply?')
            case 0x17:
                print('Heartbeat response')
            case _:
                print('Unknown:', hex(mesg_type))

    def decode_packet(self, pkg):
        header_len = 11
        footer_len = 2
        magic = pkg[0]
        payloadLength = int.from_bytes(pkg[1:3], byteorder='little')
        unknown1 = pkg[3]
        mesg_type = pkg[4]
        msgIDResponse = pkg[5]
        msgIDRequest = pkg[6]
        loggerSerial = int.from_bytes(pkg[7:11], byteorder='little')
        footer_magic = pkg[-1]
        footer_chksum = pkg[-2]
        print(f'Serial: {loggerSerial} {msgIDRequest} {msgIDResponse} {mesg_type}')
        print(f'Length: {payloadLength + header_len + footer_len} {len(pkg)}')
        payload = pkg[header_len:-footer_len]
        self.decode_payload(mesg_type, payload)

    def help(self):
        return '\tlength: bytes per line (int)'

    def execute(self, data):
        # this is a pretty hex dumping function directly taken from
        # http://code.activestate.com/recipes/142812-hex-dumper/
        result = []
        if self.incoming:
            result.append('--- Deye IN ---')
        else:
            result.append('--- Deye OUT ---')
        digits = 2
        for i in range(0, len(data), self.len):
            s = data[i:i + self.len]
            hexa = ' '.join(['%0*X' % (digits, x) for x in s])
            text = ''.join([chr(x) if 0x20 <= x < 0x7F else '.' for x in s])
            result.append("%04X   %-*s   %s" % (i, self.len * (digits + 1), hexa, text))
        self.decode_packet(data)
        print("\n".join(result))

        return data


if __name__ == '__main__':
    print ('This module is not supposed to be executed alone!')
