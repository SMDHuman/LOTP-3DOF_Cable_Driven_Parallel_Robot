from time import time_ns, sleep
from math import sqrt

@micropython.native
def cbrt(x: float) -> float:
    return(x**(1.0/3.0))

class TOMP:
    S: float = 0
    Vmax: float = 0
    Amax: float = 0
    Jmax: float = 0
    end: bool = False
    ts: list[float]
    @micropython.native
    def __init__(self, target: float, Vmax: float, Amax: float, Jmax: float) -> None:
        self.end = False
        self.S = abs(target)
        self.S_sign = -1 if target < 0 else 1
        self.Vmax = Vmax
        self.Amax = Amax
        self.Jmax = Jmax
        # 1
        self.Va = (self.Amax**2)/self.Jmax
        self.Sa = (2*self.Amax**3)/(self.Jmax**2)
        self.M = int(self.Vmax*self.Jmax < self.Amax**2)
        self.N = int(not self.M)
        self.Sv = self.Vmax*(self.M*(2*sqrt(self.Vmax/self.Jmax)) + self.N*((self.Vmax/self.Amax)+(self.Amax/self.Jmax)))
        # 1-2
        if(self.Vmax <= self.Va and self.S > self.Sa): # Shape 1
            Tj = sqrt(self.Vmax/self.Jmax)
            Ta = Tj
            Tv = self.S/self.Vmax
        elif(self.Vmax > self.Va and self.S <= self.Sa): # Shape 2
            Tj = cbrt(self.S/(2*self.Jmax))
            Ta = Tj
            Tv = 2*Tj
        elif(self.Vmax <= self.Va and self.S <= self.Sa and self.S > self.Sv): # Shape 3
            Tj = sqrt(self.Vmax/self.Jmax)
            Ta = Tj
            Tv = self.S/self.Vmax
        elif(self.Vmax <= self.Va and self.S <= self.Sa and self.S <= self.Sv): # Shape 4
            Tj = cbrt(self.S/(2*self.Jmax))
            Ta = Tj
            Tv = 2*Tj
        elif(self.Vmax > self.Va and self.S > self.Sa and self.S > self.Sv): # Shape 5
            Tj = self.Amax/self.Jmax
            Ta = self.Vmax/self.Amax
            Tv = self.S/self.Vmax
        elif(self.Vmax > self.Va and self.S > self.Sa and self.S <= self.Sv): # Shape 6
            Tj = self.Amax/self.Jmax
            Ta = (sqrt((4*self.S*self.Jmax**2+self.Amax**3)/(self.Amax*self.Jmax**2))-(self.Amax/self.Jmax))/2
            Tv = Ta+Tj
        else:
            print("Shape error")
            return
        # 3
        t0 = 0
        t1 = Tj
        t2 = Ta
        t3 = Ta+Tj
        t4 = Tv
        t5 = Tv+Tj
        t6 = Tv+Ta
        t7 = Tv+Tj+Ta
        self.ts = [t0, t1, t2, t3, t4, t5, t6, t7]
    
    # 4
    @micropython.native
    def acc(self, t: float, i: int = -1) -> float:
        if(i == -1):
            i = int(t)
            t = self.ts[i]
        if(i == 1):
            return(self.Jmax*(t-self.ts[0]))
        elif(i == 2):
            return(self.acc(1))
        elif(i == 3):
            return(self.acc(2)-self.Jmax*(t-self.ts[2]))
        elif(i == 4):
            return(0)
        elif(i == 5):
            return(-self.Jmax*(t-self.ts[4]))
        elif(i == 6):
            return(self.acc(5))
        elif(i == 7):
            return(self.acc(6)+self.Jmax*(t-self.ts[6]))
        return(0.0)
    #...
    @micropython.native
    def vel(self, t: float, i: int = -1) -> float:
        if(i == -1):
            i = int(t)
            t = self.ts[i]
        if(i == 1):
            return((self.Jmax*(t-self.ts[0])**2)/2)
        elif(i == 2):
            return(self.vel(1)+self.acc(1)*(t-self.ts[1]))
        elif(i == 3):
            return(self.vel(2)+self.acc(2)*(t-self.ts[2])+(-self.Jmax*(t-self.ts[2])**2)/2)
        elif(i == 4):
            return(self.vel(3))
        elif(i == 5):
            return(self.vel(4)+(-self.Jmax*(t-self.ts[4])**2)/2)
        elif(i == 6):
            return(self.vel(5)+self.acc(5)*(t-self.ts[5]))
        elif(i == 7):
            return(self.vel(6)+self.acc(6)*(t-self.ts[6])+(self.Jmax*(t-self.ts[6])**2)/2)
        return(0.0)
    #...
    @micropython.native
    def pos(self, t: float, i: int = -1) -> float:
        if(i == -1):
            i = int(t)
            t = self.ts[i]
        if(i == 1):
            return((self.Jmax*(t-self.ts[0])**3)/6)
        elif(i == 2):
            return(self.pos(1)+self.vel(1)*(t-self.ts[1])+(self.acc(1)*(t-self.ts[1])**2)/2)
        elif(i == 3):
            return(self.pos(2)+self.vel(2)*(t-self.ts[2])+(self.acc(2)*(t-self.ts[2])**2)/2+(-self.Jmax*(t-self.ts[2])**3)/6)
        elif(i == 4):
            return(self.pos(3)+self.vel(3)*(t-self.ts[3]))
        elif(i == 5):
            return(self.pos(4)+self.vel(4)*(t-self.ts[4])+(-self.Jmax*(t-self.ts[4])**3)/6)
        elif(i == 6):
            return(self.pos(5)+self.vel(5)*(t-self.ts[5])+(self.acc(5)*(t-self.ts[5])**2)/2)
        elif(i == 7):
            return(self.pos(6)+self.vel(6)*(t-self.ts[6])+(self.acc(6)*(t-self.ts[6])**2)/2+(self.Jmax*(t-self.ts[6])**3)/6)
        return(0.0)
    #...
    @micropython.native
    def get_pos(self, t: float) -> float:
        for i in range(0, 7):
            if(self.ts[i] <= t < self.ts[i+1]):
                return(self.pos(t, i+1) * self.S_sign)
        if(t <= 0):
            return(0)
        if(t >= self.ts[7]):
            self.end = True
            return(self.S * self.S_sign)
        return(0.0)
    #...
    @micropython.native
    def get_path_time(self)->float:
        return(self.ts[-1])

if(__name__ == "__main__"):
    tomp = TOMP()
    tomp.config(360, 360, 360, 360)

    t = 0
    old_pos = 0
    while(not tomp.end):
        pos = tomp.get_pos(t)
        #print(f"{round(t, 1)}s >>> {pos}")
        print(f"speed >>> {pos - old_pos}")
        old_pos = pos
        t += 0.1