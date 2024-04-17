#!/usr/bin/env python3
import os.path as path
import json

class Module:
    def fn1(self, buf, a, l):
        return int.from_bytes(buf[a:a + l], byteorder='little')

    def fn10(self, buf, a, l):
        return int.from_bytes(buf[a:a + l], byteorder='little') / 10.0

    def fn100(self, buf, a, l):
        return int.from_bytes(buf[a:a + l], byteorder='little') / 100.0

    def fn1000(self, buf, a, l):
        return int.from_bytes(buf[a:a + l], byteorder='little') / 1000.0

    def fnascii(self, buf, a, l):
        s = buf[a:a + l].decode("utf-8")
        return s

    def fnDT(self, buf, a, l):
        return f'{int(buf[a])+2000}-{int(buf[a+1]):02d}-{int(buf[a+2]):02d}:{int(buf[a+3]):02d}:{int(buf[a+4]):02d}:{int(buf[a+3]):02d}'

    def __init__(self, incoming=False, verbose=False, options=None):
        # extract the file name from __file__. __file__ is proxymodules/name.py
        self.loggerSerial = 0
        self.name = path.splitext(path.basename(__file__))[0]
        self.description = 'Decode Deye Inverter Upload'
        self.incoming = incoming  # incoming means module is on -im chain
        self.len = 16
        self.dfn42 = {
            'inv.serial.ascii':
                {'adr':  21, 'len': 10, 'f': self.fnascii},
            'pv.v.1':
                {'adr': 85, 'len': 2, 'f': self.fn10},
            'pv.i.1':
                {'adr': 87, 'len': 2, 'f': self.fn10},
            'pv.kWh_today.1':
                {'adr': 136, 'len': 2, 'f': self.fn10},
            'pv.kWh_total.1':
                {'adr': 145, 'len': 2, 'f': self.fn10},
            'pv.v.2':
                {'adr': 89, 'len': 2, 'f': self.fn10},
            'pv.i.2':
                {'adr': 91, 'len': 2, 'f': self.fn10},
            'pv.kWh_today.2':
                {'adr': 138, 'len': 2, 'f': self.fn10},
            'pv.kWh_total.2':
                {'adr': 149, 'len': 2, 'f': self.fn10},
            'grid.active_power_w':
                {'adr': 59, 'len': 4, 'f': self.fn1},
            'grid.kWh_today':
                {'adr': 33, 'len': 4, 'f': self.fn100},
            'grid.kWh_total':
                {'adr': 37, 'len': 4, 'f': self.fn10},
            'grid.v':
                {'adr': 45, 'len': 2, 'f': self.fn10},
            'grid.i':
                {'adr': 51, 'len': 2, 'f': self.fn10},
            'grid.hz':
                {'adr': 57, 'len': 2, 'f': self.fn100},
            'inv.degc':
                {'adr': 63, 'len': 2, 'f': self.fn100},
            #'meta.rated_power_w':
            #    {'adr': 129, 'len': 2, 'f':self.fn10},
            'meta.mppt_count':
                {'adr': 131, 'len': 1, 'f': self.fn1},
            'meta.phases':
                {'adr': 132, 'len': 1, 'f': self.fn1},
            #'meta.startup_self_check_time':
            #    {'adr': 243, 'len': 2, 'f': self.fn1},
            'meta.current_time':
                {'adr': 245, 'len': 6, 'f': self.fnDT},
            #'meta.grid_freq_hz_overfreq_load_reduction_starting_point':
            #    {'adr': 223, 'len': 2, 'f': self.fn100},
            #'meta.grid_overfreq_load_reduction_percent':
            #    {'adr': 225, 'len': 2, 'f': self.fn1},
            #'meta.grid_v_limit_upper':
            #    {'adr': 235, 'len': 2, 'f': self.fn10},
            #'meta.grid_v_limit_lower':
            #    {'adr': 237, 'len': 2, 'f': self.fn10},
            #'meta.grid_freq_hz_limit_upper':
            #    {'adr': 239, 'len': 2, 'f': self.fn100},
            #'meta.grid_freq_hz_limit_lower':
            #    {'adr': 241, 'len': 2, 'f': self.fn100},
            'meta.protocol_ver':
                {'adr': 101, 'len': 8, 'f': self.fnascii},
            'meta.dc_master_fw_ver':
                {'adr': 109, 'len': 8, 'f': self.fnascii},
            'meta.ac_fw_ver':
                {'adr': 117, 'len': 8, 'f': self.fnascii}
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
                print('Data request, data packet schema:', hex(payload[1]))
                # k = 'inv.serial.ascii'
                # '2072329677' # Relay
                # '2305047249' # Inverter, the interesting one
                # '3927428152' # Device, in packet header
                # if self.dfn42[k]['f'](payload, self.dfn42[k]['adr'], self.dfn42[k]['len']) == '2305047249':
                match payload[1]:
                    case 0x08:  # microinverter
                        for k, v in self.dfn42.items():
                            res[k] = self.dfn42[k]['f'](payload, self.dfn42[k]['adr'], self.dfn42[k]['len'])
                        print(json.dumps(res, indent=2))
                    case 0x11:  # hybrid inverter
                        pass
                    case 0x13:  # relay module
                        pass
                    case _:
                        print('Unknown data packet schema:', payload[1])
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
        self.loggerSerial = int.from_bytes(pkg[7:11], byteorder='little')
        footer_magic = pkg[-1]
        footer_chksum = pkg[-2]
        print(f'Serial: {self.loggerSerial} {msgIDRequest} {msgIDResponse} {mesg_type}')
        print(f'Length: {payloadLength + header_len + footer_len} {len(pkg)}')
        payload = pkg[header_len:-footer_len]
        self.decode_payload(mesg_type, payload)

    def help(self):
        return '\tlength: bytes per line (int)'

    def execute(self, data):
        # this is a pretty hex dumping function directly taken from
        # http://code.activestate.com/recipes/142812-hex-dumper/
        '''
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
        print("\n".join(result))
        '''

        self.decode_packet(data)
        return data


if __name__ == '__main__':
    print ('This module is not supposed to be executed alone!')
