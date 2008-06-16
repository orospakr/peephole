# Peephole - a D-Bus service providing access to small LCD panels
# Copyright (C) 2007-2008 Andrew Clunis

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class VUMeter(object):

    def __init__(self, picolcd):
        self.picolcd = picolcd

    def generateBar(self, num):
        '''Generate a bar with a given height in PicoLCD character format.

        num -- the number of rows that should be darkened, starting from the
               bottom.

        Should be factored out somewhere.'''
        bar = ''
        for row in range(0,8):
            # I subtract one because this the row addressing is zero-based
            if row <= (num - 1):
                bar += '\x00'
            else:
                bar += '\x1F'
        return bar

    def writeVUBars(self):
        '''Writes a sequence of VU meter bars to the PicoLCD CG RAM with
        addresses 1 through 7.  0 is left unused.

        Should be factored out somewhere.
        '''
        #self.upload_char(0, "\x1F\x1F\x1F\x1F\x1F\x1F\x1F")
        #self.upload_char(0, "936578f")
        # we skip the first char ID because we don't need it, and so can use it
        # for something else.
        for char_id in range(1,8):
            character = self.generateBar(char_id - 1)
            #character = "1234567"
            self.picolcd.upload_char(char_id, character)
