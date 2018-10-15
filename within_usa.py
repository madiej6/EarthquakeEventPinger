# Continental USA coordinates
UStop = 49.3457868 # north lat
USleft = -124.7844079 # west long
USright = -66.9513812 # east long
USbottom =  24.7433195 # south lat

# Alaska coordinates
AKtop = 71.60 # north lat
AKleft = -168.44 # west long
AKright = -140.49 # east long
AKbottom =  54.20 # south lat

# Hawai'i coordinates
HAtop = 22.38 # north lat
HAleft = -160.34 # west long
HAright = -154.66 # east long
HAbottom =  18.71 # south lat

# Puerto Rico & USVI coordinates
PRtop = 18.60 # north lat
PRleft = -67.39 # west long
PRright = -64.29 # east long
PRbottom =  17.63 # south lat

def check_within_us(lng, lat):
    
    if USbottom <= lat <= UStop and USleft <= lng <= USright:
        return True
    elif AKbottom <= lat <= AKtop and AKleft <= lng <= AKright:
        return True
    elif HAbottom <= lat <= HAtop and HAleft <= lng <= HAright:
        return True
    elif PRbottom <= lat <= PRtop and PRleft <= lng <= PRright:
        return True
    else:
        return None
