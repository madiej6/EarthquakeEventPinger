from shapely.geometry import Polygon, Point

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
HItop = 22.38 # north lat
HIleft = -160.34 # west long
HIright = -154.66 # east long
HIbottom =  18.71 # south lat

# Puerto Rico & USVI coordinates
PRtop = 18.60 # north lat
PRleft = -67.39 # west long
PRright = -64.29 # east long
PRbottom =  17.63 # south lat

def coords_to_polygon(left: float, right: float, top: float, bottom: float):
    """Converts a list of coordinates to a WKT polygon"""

    # Define the coordinates for the polygon (list of tuples)
    coordinates = [
        (left, bottom),  # bottom left
        (right, bottom),   # bottom right
        (right, top),   # top right
        (left, top)   # top left
    ]

    # Return a polygon using the coordinates
    return Polygon(coordinates)


def check_within_us(lon: float, lat: float) -> bool:
    """Given a lat/lon, determine whether or not the point is in the USA."""

    point = Point(lon, lat)
    
    US = coords_to_polygon(USleft, USright, UStop, USbottom)
    AK = coords_to_polygon(AKleft, AKright, AKtop, AKbottom)
    HI = coords_to_polygon(HIleft, HIright, HItop, HIbottom)
    PR = coords_to_polygon(PRleft, PRright, PRtop, PRbottom)

    for bounds in [US, AK, HI, PR]:
        # Check if the point is within the polygon
        if bounds.contains(point):
            print("Lat/Lon is within the USA!")
            return True

    print("Lat/Lon is NOT within the USA.")
    return False

if __name__ == "__main__":
    # AustinTx = (30.266666, -97.733330)
    check_within_us(lon=-1197.733330, lat=30.266666)