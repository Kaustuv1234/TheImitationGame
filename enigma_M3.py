# ACTUAL SIMULATOR - https://www.cryptool.org/en/cto/enigma/, use this to verify code
# Enigma specificaitons - https://www.cryptomuseum.com/crypto/enigma/wiring.htm


ROTORS = {'I':"EKMFLGDQVZNTOWYHXUSPAIBRCJ", 
           'II':"AJDKSIRUXBLHWTMCQGZNPYFVOE", 
           'III':"BDFHJLCPRTXVZNYEIWGAKMUSQO", 
           'IV':"ESOVPZJAYQUIRHXLNFTGKDCMWB", 
           'V':"VZBRGITYUPSDNHLXAWMJQOFECK"}

NOTCHES = {'I':'Q', 'II':'E', 'III':'V', 'IV':'J', 'V':'Z'}

REFLECTORS = {'A':"EJMZALYXVBWFCRQUONTSPIKHGD",
               'B':"YRUHQSLDPXNGOKMIEBFZCWVJAT",
               'C':"FVPJIAOYEDRZXWGCTKUQSBNMHL"}


class EnigmaM3:
    def __init__(self, 
                ROTOR_WHEEL_SETTING, 
                REFLECTOR_SETTING, 
                RING_SETTING, 
                INIT_POS_SETTING, 
                PLUG_CONNECTIONS):
        
        # create mapping table for each rotor position
        ROTOR_ORDER = [ROTORS[r] for r in ROTOR_WHEEL_SETTING]
        # mapping table before reflector (i.e signal moves from right to left rotors)
        self.FWD_MAP_LFT = [ord(c) - 65 for c in ROTOR_ORDER[0]]
        self.FWD_MAP_MID = [ord(c) - 65 for c in ROTOR_ORDER[1]]
        self.FWD_MAP_RHT = [ord(c) - 65 for c in ROTOR_ORDER[2]]

        # mapping table after reflector (i.e signal moves from left to right rotors)
        # invert the forward mapping tables 
        self.REV_MAP_LFT = [0] * 26
        self.REV_MAP_MID = [0] * 26
        self.REV_MAP_RHT = [0] * 26
        for i in range(26):
            self.REV_MAP_LFT[self.FWD_MAP_LFT[i]] = i
            self.REV_MAP_MID[self.FWD_MAP_MID[i]] = i
            self.REV_MAP_RHT[self.FWD_MAP_RHT[i]] = i

        # create mapping table for reflector
        self.REFLECTOR = [ord(c) - 65 for c in REFLECTORS[REFLECTOR_SETTING]]

        NOTCH = [NOTCHES[r] for r in ROTOR_WHEEL_SETTING]
        self.NOTCH_LFT, self.NOTCH_MID, self.NOTCH_RHT = [ord(c) - 65 for c in NOTCH]

        # the ring settings offset the letters relative to the internal wiring and notches
        # the rotor notch and wirings are fixed together and cannot be changed
        self.RING_LFT, self.RING_MID, self.RING_RHT = [ord(c) - 65 for c in RING_SETTING]

        self.POS_LFT, self.POS_MID, self.POS_RHT = [(ord(pos) - ord(ring)) % 26 for pos, ring in zip(INIT_POS_SETTING, RING_SETTING)]

        # first map each element to itself
        self.PLUG_MAP = list(range(26)) 
        # then map each element to its plug connection
        for pc in PLUG_CONNECTIONS:
            self.PLUG_MAP[ord(pc[0])-65] = ord(pc[1])-65
            self.PLUG_MAP[ord(pc[1])-65] = ord(pc[0])-65
    
    def encrypt(self, msg) -> str:
        secret = ""

        for inp_char in msg:

            # when key is pressed, the rotors move first
            if self.POS_MID == (self.NOTCH_MID+1)%26:
                self.POS_LFT = (self.POS_LFT + 1) % 26
                self.POS_MID = (self.POS_MID + 1) % 26
            elif self.POS_RHT == (self.NOTCH_RHT+1)%26:
                self.POS_MID = (self.POS_MID + 1) % 26
            self.POS_RHT = (self.POS_RHT + 1) % 26

            idx = ord(inp_char) - 65

            # first pass through plugboard
            idx = self.PLUG_MAP[idx]

            # idx will refer to absolute positions, it doesnt depend on rotor movement
            # forward pass(right to left)
            idx = (self.FWD_MAP_RHT[(idx+self.POS_RHT) % 26] - self.POS_RHT) % 26
            idx = (self.FWD_MAP_MID[(idx+self.POS_MID) % 26] - self.POS_MID) % 26
            idx = (self.FWD_MAP_LFT[(idx+self.POS_LFT) % 26] - self.POS_LFT) % 26

            idx = self.REFLECTOR[idx]
            
            # reverse pass(left to right)
            idx = (self.REV_MAP_LFT[(idx+self.POS_LFT) % 26] - self.POS_LFT) % 26
            idx = (self.REV_MAP_MID[(idx+self.POS_MID) % 26] - self.POS_MID) % 26
            idx = (self.REV_MAP_RHT[(idx+self.POS_RHT) % 26] - self.POS_RHT) % 26

            # second pass through plugboard
            idx = self.PLUG_MAP[idx]

            print(f'[{chr(65+self.POS_LFT-self.RING_LFT)} {chr(65+self.POS_MID-self.RING_MID)} {chr(65+self.POS_RHT-self.RING_RHT)}]  output={chr(idx+65)}')
            secret += chr(idx+65)

        return secret



        
ROTOR_WHEEL_SETTING = ["I", "II", "III"] # left to right
REFLECTOR_SETTING = 'B'
RING_SETTING = "AAB"
INIT_POS_SETTING = "AAA"
PLUG_CONNECTIONS = ["AZ", "CD"]

enigma = EnigmaM3(ROTOR_WHEEL_SETTING, REFLECTOR_SETTING, RING_SETTING, INIT_POS_SETTING, PLUG_CONNECTIONS)

plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
ciphertext = enigma.encrypt(plaintext)
print(f'{ciphertext=}')
