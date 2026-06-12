import pathlib, json, vpk
from tf2_parser_config import *

classes = {
     "demoman" : "demo",
    "engineer" : "engineer",
       "heavy" : "heavy",
       "medic" : "medic",
        "pyro" : "pyro",
       "scout" : "scout",
      "sniper" : "sniper",
     "soldier" : "soldier",
         "spy" : "spy"
}

def b2int(b):
    return int.from_bytes(b, byteorder="little")

def b2str(b):
    return b.decode("utf-8")

SPEAK_INDEX = 5004

def get_animation_sequences():
    print("Getting animation sequenes...")
    
    tf2_misc_dir_vpk = vpk.open(tf2_misc_dir_vpk_path)
    
    # Read x number of bytes from data
    def get(amount):
        nonlocal cur
        prev = cur
        cur = cur + amount
        return fd[prev:cur]

    # Jump to offset
    def seek(offset):
        nonlocal cur
        cur = offset

    # Read null-terminated string from current position
    def readstr(maxlen = 256):
        out = ""
        char = ""
        i = 0
        char = b2str(get(1))
        while char != "\0" and i < maxlen:
            out += char
            char = b2str(get(1))
            i += 1
        return out

    class_seqs = {}

    for full_class_name,class_name in classes.items():
        print_line = full_class_name[0].upper() + full_class_name[1:] + "..."
        print("Getting animation sequences for", print_line)
        mdl_seqs = {}
        cur = 0
        
        fp = "models/player/" + class_name + "_animations.mdl"
        f = tf2_misc_dir_vpk.get_file(fp)
        fd = f.read()
    
        mdl_id = get(4)
        
        get(4 + 4 + 64 + 4 + (12 * 6) + 4)
        get(4 * 8)
        
        mdl_numlocalseq = b2int(get(4))
        mdl_localseqoffset = b2int(get(4))
        
        seek(mdl_localseqoffset)
        for i in range(mdl_numlocalseq):
            seq_startposition = cur
            seq_baseheaderoffset = b2int(get(4))
            seq_nameoffset = b2int(get(4))

            get(4*4)

            seq_eventcount = b2int(get(4))
            seq_eventoffset = b2int(get(4))
            #print(seq_eventcount, seq_eventoffset)
            
            get(180)

            seq_endposition = cur

            # Start looking for sequence subdata

            # Sequence name
            seek(seq_startposition + seq_nameoffset)
            
            seq_name = readstr()

            # Sequence events
            seek(seq_startposition + seq_eventoffset)
            seq_event_list = []
            for j in range(seq_eventcount):
                event_startposition = cur
                _ = get(4)
                event_index = b2int(get(4))
                event_type = b2int(get(4))
                event_options = b2str(get(64)).strip("\0")
                if event_index == SPEAK_INDEX:
                    seq_event_list.append(event_options)
                event_nameoffset = b2int(get(4))
                
                event_endposition = cur

            if len(seq_event_list) > 0:
                mdl_seqs[seq_name] = seq_event_list
            
            seek(seq_endposition)
        class_seqs[full_class_name] = mdl_seqs

    return class_seqs
