i_c= [['5\n'], ['COMPARE M(0)', 'JUMP+ M(6,0:19)\n'], ['LOAD MQ, M(7)', 'LOAD M(0)\n'], ['MUL M(0)', 'STOR M(7)\n'], ['LOAD M(0)', 'DEC\n'], ['STOR M(0)', 'JUMP + M(2,0:19)\n'], ['NOP', 'HALT\n'], ['1\n']]
j = []
def best(n):
    b_r = bin(n)[2:]
    b_p = '0' * (40 - len(b_r))
    r_b = b_p + b_r
    return r_b
def opcode(s):
    if s == 'DEC\n':
        return '11111111'
    elif s == 'LOAD MQ, M()\n':
        return '00001001'
    elif s == 'STOR M()\n':
        return '00100001'
    elif s == 'LOAD M()\n':
        return '00000001'
    elif s == 'JUMP+ M(,:)\n':
        return '00001111'
    elif s == 'MUL M()\n':
        return '10001011'
    elif s == 'NOP\n': 
        return '00000000'
    elif s == 'DEC':
        return '11111111'
    elif s == 'LOAD MQ, M()':
        return '00001001'
    elif s == 'STOR M()':
        return '00100001'
    elif s == 'LOAD M()':
        return '00000001'
    elif s == 'JUMP+ M(,:)':
        return '00001111'
    elif s == 'MUL M()':
        return '10001011'
    elif s == 'NOP':  
        return '00000000'
    elif s == 'HALT':
        return '10101010'
    elif s == 'HALT\n':
        return '10101010'
    elif s == 'COMPARE M()':
        return '11110000'
    elif s == 'COMPARE M()\n':
        return '11110000'      
s = []
def bry(n):
    s = ''
    for i in range(12):
        x = n % 2
        n = n // 2
        s = str(x) + s
    return s
def r_s(i_s):
    r_st = ''.join(char for char in i_s if not char.isdigit())
    return r_st
def r_s1(i_s):
        r_st = ''.join(char for char in i_s if char.isdigit())
        return r_st
for i in i_c:
    if len(i) == 1:
        j.append(r_s1(i[0])) 
    elif len(i) == 2:
        for k in i:
            j.append(r_s1(k))
j.remove("")
j.remove("")
j.remove("")
j[2] = "7"
j[9] = "3"
for delta in i_c:
    if len(delta) == 1:
        s.append(best(int(delta[0].strip())))
    elif len(delta) == 2:
        for alpha in delta:
            alpha = r_s(alpha)
            alpha.replace('\n', "")
            s.append(opcode(alpha))
            if alpha != 'DEC' and alpha != 'NOP':
                a = j[0]
                a = int(a)
                s.append(bry(a))
                a = str(a)
                j.remove(a)
            else:
                s.append('000000000000')
i_l = s
o_l = []
i_l[19] = "00001111"
i = 0
while i < len(i_l):
    c_e = i_l[i]
    c_e_l = len(c_e)
    if c_e_l == 8:
        s_v = c_e + i_l[i + 1] + i_l[i + 2] + i_l[i + 3]
        o_l.append(s_v)
        i += 4
    else:
        o_l.append(c_e)
        i += 1
for element in o_l:
    print(element)
