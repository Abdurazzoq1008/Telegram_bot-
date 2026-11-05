def max_son(a, b):
    if a > b :
      return a  
    else:
      return b 
    

# print(max_son(input("a : "), input("b : ")))        


def juft_mi(son):
    a = son % 2 
    if a == 0 :
        return True
    else:
        return False

print(juft_mi(32))