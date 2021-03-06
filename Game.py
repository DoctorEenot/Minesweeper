
import time
import random

import Resources





MAX_MISTAKES = 5
AFK_TIME = 180

MAX_SIZE = (62,33)
MIN_SIZE = (5,5)

MAX_MISTAKES = 5

UNLUCKY = 2

'''
0-empty
1,2,3,... - not empty
-1 - bomb
-2 - flag
'''



class game:
    def __init__(self,user_id,size=(10,10),number_of_bombs = 50,private=True):
        if not self.check_size(size):
            raise Exception('Wrong size')
        self.size = size
        self.user_id = user_id
        self.private = private
        if number_of_bombs > (self.size[0]*self.size[1])//2:
            self.number_of_bombs = (self.size[0]*self.size[1])//2
        else:
            self.number_of_bombs = number_of_bombs


        self.available_flags = self.number_of_bombs+5

        self.pole = []
        for y in range(self.size[1]):
            self.pole.append([0]*self.size[0])

        self.pole_opened = []
        for y in range(self.size[1]):
            self.pole_opened.append([False]*self.size[0])

        self.flags = []
        for y in range(self.size[1]):
            self.flags.append([False]*self.size[0])

        self.last_change = time.time()

        self.started = time.time()

        self.alive = True
            
        self.mistakes = 0

        self.last_messages = []


    def update_time(self):
        self.last_change = time.time()

    def new_message(self,ids):
        for id in ids:
            self.last_messages.append(id)
        #self.last_messages = ids

    def check_size(self,size)->bool:
        if (size[0]<MIN_SIZE[0] or size[0]>MAX_SIZE[0]) or (size[1]<MIN_SIZE[1] or size[1]>MAX_SIZE[1]):
            return False
        return True

    def is_bomb(self,position):
        if self.pole[position[1]][position[0]] == -1:
            return True
        return False

    def is_bomb_(self,x,y):
        if x<0 or x>=self.size[0] or y<0 or y>=self.size[1]:
            return False
        if self.pole[y][x] == -1:
            return True
        return False

    def get_weight(self,position:tuple):

        weight = 0
        for y in range(position[1]-1,position[1]+2):
            if y < 0 or y >= self.size[1]:
                continue
            for x in range(position[0]-1,position[0]+2):
                if x < 0 or x >= self.size[0]:
                    continue
                if self.is_bomb((x,y)):
                    weight += 1

        return weight

    def get_limits(self,quarter):
        half_y = (self.size[1]//2)
        half_x = (self.size[0]//2)

        to_return = ()

        if quarter == 0:
            to_return = (0,half_x,0,half_y)
        elif quarter == 1:       
            to_return = (half_x,self.size[0]-1,0,self.size[1]-1)

        elif quarter == 2:
            to_return = (half_x,self.size[0]-1,half_y,self.size[1]-1)


        elif quarter == 3:
            to_return = (0,half_x,half_y,self.size[1]-1)

        return to_return
        

    def generate_map(self):
        quarter = 0
        for i in range(self.number_of_bombs):
            limits = self.get_limits(quarter)
            quarter += 1
            if quarter == 4:
                quarter = 0

            x = random.randint(limits[0],limits[1])
            y = random.randint(limits[2],limits[3])
            #x = random.randint(0,self.size[0]-1)
            #y = random.randint(0,self.size[1]-1)
            while self.pole[y][x] == -1: #or self.get_weight((x,y))>UNLUCKY:
                x = random.randint(limits[0],limits[1])
                y = random.randint(limits[2],limits[3])
                if self.get_weight((x,y))<=UNLUCKY:
                    if (self.is_bomb_(x-1,y) and self.is_bomb_(x-2,y))or (self.is_bomb_(x-1,y) and self.is_bomb_(x+1,y)) or (self.is_bomb_(x+1,y) and self.is_bomb_(x+2,y)) or (self.is_bomb_(x,y-1) and self.is_bomb_(x,y-2)) or (self.is_bomb_(x,y-1) and self.is_bomb_(x,y+1)) or (self.is_bomb_(x,y+1) and self.is_bomb_(x,y+2)):
                        continue
                    break
                
            self.pole[y][x] = -1

        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if self.is_bomb((x,y)):
                    continue
                self.pole[y][x] = self.get_weight((x,y))

    def is_alive(self):
        if time.time() - self.last_change >= AFK_TIME:
            return False
        elif self.mistakes >= MAX_MISTAKES:
            return False
        return self.alive

    def check_win(self):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if self.pole[y][x] == -1 and not self.flags[y][x]:
                    return False

        return True

    def can_be_opened(self,position):
        if (position[0]<0 or position[0]>=self.size[0]) or (position[1]<0 or position[1]>=self.size[1]):
            self.mistakes += 1
            return False
        elif self.pole_opened[position[1]][position[0]]:
            self.mistakes += 1
            return False
        elif self.flags[position[1]][position[0]]:
            self.mistakes += 1
            return False
        return True

    def make_visible(self,position):
        self.pole_opened[position[1]][position[0]] = True

    def visible(self,position):
        return self.pole_opened[position[1]][position[0]]

    def open_tile(self,position):
        if not self.can_be_opened(position):
            return False

        self.update_time()

        if self.is_bomb(position):
            self.alive = False
            self.make_visible(position)
            return True

        stack = []
        stack.append(position)
        
        while len(stack) != 0:
            pos = stack.pop()
            self.make_visible(pos)
            br = False
            for y in range(pos[1]-1,pos[1]+2):
                if y < 0 or y >= self.size[1]:
                    continue

                for x in range(pos[0]-1,pos[0]+2):
                    if x < 0 or x >= self.size[0]:
                        continue
                    if not self.is_bomb((x,y)) and not self.visible((x,y)):
                        
                        if self.flags[y][x]:
                            self.flags[y][x] = False
                            self.pole_opened[y][x] = False
                            self.available_flags += 1

                        if self.pole[pos[1]][pos[0]] == 0:
                            self.make_visible((x,y))

                        if self.pole[y][x] == 0:
                            stack.append(pos)
                            stack.append((x,y))
                            br = True
                            break
                        else:
                            continue
                if br:
                    break

        return True


    def render_to_emodji(self):
        to_return = ''
        to_return += 'Time(minutes): '+str(round((time.time()-self.started)/60,2))+'\nFlags left:'+str(self.available_flags)+'\n'
        
        for i in range(self.size[0]+1):
            to_return += str(i)+' '*Resources.margins_x[i]
        to_return += '\n'

        first = True

        for y in range(1,self.size[1]+1):
            _y = y % 10
            
            to_return += str(_y)

            if _y == 1:
                to_return += ' '
                        
            for x in range(0,self.size[0]):
                actual_y = y - 1
                if self.pole_opened[actual_y][x]:
                    if self.pole[actual_y][x] == -1 and not self.flags[actual_y][x]:
                        to_return += Resources.BOMB
                    elif self.flags[actual_y][x]:
                        to_return += Resources.FLAG
                    else:
                        to_return += Resources.NUMBERS[self.pole[actual_y][x]]
                else:
                    to_return += Resources.UNOPENED
            to_return += '\n'

        return to_return

    def put_flag(self,position):
        if self.available_flags == 0:
            return False

        if not self.can_be_opened(position):
            return False

        self.flags[position[1]][position[0]] = True
        self.pole_opened[position[1]][position[0]] = True
        self.available_flags -= 1
        self.update_time()
        return True

    def remove_flag(self,position):
        if not self.flags[position[1]][position[0]]:
            return False

        if (position[0]<0 or position[0]>=self.size[0]) or (position[1]<0 or position[1]>=self.size[1]):
            self.mistakes += 1
            return False
        

        self.flags[position[1]][position[0]] = False
        self.pole_opened[position[1]][position[0]] = False
        self.available_flags += 1
        self.update_time()
        return True



    #def place_flag(self,position):
    #    if not self.can_be_opened(position):
    #        return False

    #    self.update_time()


        
        
        





if __name__ == '__main__':
    gm = game(1,(10,10),number_of_bombs=1)
    gm.generate_map()
    
    gm.open_tile((0,5))

    data = gm.render_to_emodji().split('\n')

    print(1)




