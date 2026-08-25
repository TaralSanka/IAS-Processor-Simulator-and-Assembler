#global ac,ir,ibr,mar,mbr,mq,pc
pc = 1
ir = ''
t = 0 # toggle terminate
mq = 0
def fetch():
    global pc,mar,mbr, memory
    mar = pc
    mbr = memory[mar]
    pc =  pc+1
    mq=0


def decode():
    global ir,mar,ibr,mbr,t
    ir = mbr[0:8]
    mar = int(mbr[8:20],2)
    ibr = mbr[20:40]
    execute(ir,mar)
    ir=ibr[0:8]
    mar=int(ibr[8:20],2)
    mq=0
    execute(ir,mar)

def execute(ir,mar):
    global mbr, memory, mbr, mq, pc, ac
    if ir == '00001001':    #LOAD MQ, M()
        mbr = memory[mar]
        mq = int(mbr,2)
    elif ir == '00100001':   #STOR M()
        mbr = bin(ac)[2:].zfill(40)
        memory[mar] = mbr
    elif ir == '00000001':   #LOAD M()
        mbr = memory[mar]
        ac = int(mbr,2)
    elif ir == '10001011':   #MUL M()
        mbr = memory[mar]
        ac = mq * int(mbr,2)
    elif ir == '11111111':   #DEC
        ac = ac - 1
    elif ir == '00001111':   #JUMP+ M(,:)
        if ac>0:
            pc = mar
    elif ir == '10101010':   #COMPARE M()
        if int(memory[mar],2)>0:
            ac = -1
        else:
            ac = 1
    elif ir == '00000000':   #NOP
        pass
    elif ir == '10000000':   #HALT
        print("the end")
    print(f"mar = {bin(mar)[2:].zfill(12)}\n mbr = {mbr}\n ibr = {ibr}\n ir = {ir}\n ac = {bin(ac)[2:].zfill(40)}\n mq = {bin(mq)[2:].zfill(40)}")
memory=[]
with open('binaryCode.txt','r') as f:
    for line in f:
        memory.append(line.strip())
    print(memory)

while(ir !='10000000'):
    fetch()
    decode()
   #print(f"mar = {bin(mar)[2:].zfill(12)}\n mbr = {mbr}\n ibr = {ibr}\n ir = {ir}\n ac = {bin(ac)[2:].zfill(40)}\n mq = {bin(mq)[2:].zfill(40)}")
print(f" result = {int(memory[7],2)}")   
   
