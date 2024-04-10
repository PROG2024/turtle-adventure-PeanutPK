"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
import random
import time
from turtle import RawTurtle
from gamelib import Game, GameElement


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x - 10, self.y - 10,
                               self.x + 10, self.y + 10)
            self.canvas.coords(self.__id2, self.x - 10, self.y + 10,
                               self.x + 10, self.y - 10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int],
                 size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown",
                                                 width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x - self.size / 2, self.x + self.size / 2
        y1, y2 = self.y - self.size / 2, self.y + self.size / 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("black")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):
        """
        Check whether the enemy is hitting the player
        """
        return (
                (
                        self.x - self.size / 2 < self.game.player.x < self.x + self.size / 2)
                and
                (
                        self.y - self.size / 2 < self.game.player.y < self.y + self.size / 2)
        )


class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color,
                                            outline='black')

    def update(self) -> None:
        self.x += 1
        self.y += 1
        if self.hits_player():
            self.game.game_over_lose()
            self.delete()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class RandomWalkEnemy(Enemy):
    """
    Randomly walk enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.waypoint = Waypoint(self.game)
        self.generate_waypoint()

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)
        if self.x == 0 and self.y == 0:
            self.random_spawn()

    def random_spawn(self):
        num_x = random.randint(0, self.canvas.winfo_width())
        num_y = random.randint(0, self.canvas.winfo_height())
        while (self.game.player.x - 100 < num_x < self.game.player.x + 100 or
               self.game.player.y - 100 < num_y < self.game.player.y + 100):
            num_x = random.randint(0, self.canvas.winfo_width())
            num_y = random.randint(0, self.canvas.winfo_height())
        self.x = num_x
        self.y = num_y

    def generate_waypoint(self):
        num_x = random.randint(0, self.canvas.winfo_width())
        num_y = random.randint(0, self.canvas.winfo_height())
        self.waypoint.activate(num_x, num_y)

    def update(self) -> None:
        if self.x < self.waypoint.x:
            self.x += 1
        elif self.x > self.waypoint.x:
            self.x -= 1
        if self.y < self.waypoint.y:
            self.y += 1
        elif self.y > self.waypoint.y:
            self.y -= 1
        if self.x == self.waypoint.x and self.y == self.waypoint.y:
            self.generate_waypoint()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class ChasingEnemy(Enemy):
    """
    Chasing square enemy that walk faster when you are far away
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color)
        if self.x == 0 and self.y == 0:
            self.random_spawn()

    def random_spawn(self):
        num_x = random.randint(0, self.canvas.winfo_width())
        num_y = random.randint(0, self.canvas.winfo_height())
        while (self.game.player.x - 100 < num_x < self.game.player.x + 100 or
               self.game.player.y - 100 < num_y < self.game.player.y + 100):
            num_x = random.randint(0, self.canvas.winfo_width())
            num_y = random.randint(0, self.canvas.winfo_height())
        self.x = num_x
        self.y = num_y

    def update(self) -> None:
        player_pos_x = self.game.player.x
        player_pos_y = self.game.player.y

        if abs(player_pos_x - self.x) > 80:
            speed_x = 5
        else:
            speed_x = 2
        if abs(player_pos_y - self.y) > 80:
            speed_y = 5
        else:
            speed_y = 2

        if player_pos_x > self.x:
            self.x += speed_x
        elif player_pos_x < self.x:
            self.x -= speed_x
        if player_pos_y > self.y:
            self.y += speed_y
        elif player_pos_y < self.y:
            self.y -= speed_y
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class FencingEnemy(Enemy):
    """
    Fencing enemy wondering around the finish line
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.__state = self.down
        self.enemy_num = 1
        self.speed = 5
        self.distance_x, self.distance_y = 40, 40
        self.rad_x, self.rad_y = 40, 40
        self.finish_x = self.game.home.x
        self.finish_y = self.game.home.y

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color,
                                            outline='black')
        self.x = self.game.home.x - self.distance_x
        self.y = self.game.home.y - self.distance_y

    def left(self) -> None:
        if self.x == self.finish_x - self.rad_x:
            self.__state = self.down
        self.x -= self.speed

    def right(self) -> None:
        if self.x == self.finish_x + self.rad_x:
            self.__state = self.up
        self.x += self.speed

    def up(self) -> None:
        if self.y == self.finish_y - self.rad_y:
            self.__state = self.left
        self.y -= self.speed

    def down(self) -> None:
        if self.y == self.finish_y + self.rad_y:
            self.__state = self.right
        self.y += self.speed

    def update(self) -> None:
        self.__state()
        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class DrunkBouncyEnemy(Enemy):
    """
    Randomly walk enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.x_state = random.choice([self.left_state, self.right_state])
        self.y_state = random.choice([self.up_state, self.down_state])
        self.speed = 3
        self.__id = None

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)
        if self.x == 0 and self.y == 0:
            self.random_spawn()

    def random_spawn(self):
        num_x = random.randint(0, self.canvas.winfo_width())
        num_y = random.randint(0, self.canvas.winfo_height())
        while (self.game.player.x - 100 < num_x < self.game.player.x + 100 or
               self.game.player.y - 100 < num_y < self.game.player.y + 100):
            num_x = random.randint(0, self.canvas.winfo_width())
            num_y = random.randint(0, self.canvas.winfo_height())
        self.x = num_x
        self.y = num_y

    def create_dupe(self, x_state, y_state):
        new_enemy = DrunkBouncyEnemy(self.game, 10, "pink")
        new_enemy.x_state = eval(f"new_enemy.{x_state}")
        new_enemy.y_state = eval(f"new_enemy.{y_state}")
        if self.x <= 0:
            new_enemy.x = 1
            new_enemy.y = self.y
        elif self.x >= self.canvas.winfo_width():
            new_enemy.x = self.canvas.winfo_width() - 1
            new_enemy.y = self.y
        elif self.y <= 0:
            new_enemy.y = 1
            new_enemy.x = self.x
        elif self.y >= self.canvas.winfo_height():
            new_enemy.y = self.canvas.winfo_height() - 1
            new_enemy.x = self.x
        self.game.add_element(new_enemy)

    def update(self) -> None:
        self.x_state()
        self.y_state()
        if self.hits_player():
            self.game.game_over_lose()

    def left_state(self):
        self.x -= self.speed
        if self.x <= 0:
            self.create_dupe("right_state", "up_state")
            self.create_dupe("right_state", "down_state")
            self.game.delete_element(self)

    def right_state(self):
        self.x += self.speed
        if self.x >= self.canvas.winfo_width():
            self.create_dupe("left_state", "up_state")
            self.create_dupe("left_state", "down_state")
            self.game.delete_element(self)

    def up_state(self):
        self.y -= self.speed
        if self.y <= 0:
            self.create_dupe("left_state", "down_state")
            self.create_dupe("right_state", "down_state")
            self.game.delete_element(self)

    def down_state(self):
        self.y += self.speed
        if self.y >= self.canvas.winfo_height():
            self.create_dupe("left_state", "up_state")
            self.create_dupe("right_state", "up_state")
            self.game.delete_element(self)

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level
        self.create_enemy()

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        for i in range(5):
            self.create_random_enemy()
        self.game.after(600, self.create_chasing_enemy)
        self.create_my_enemy()
        timer = 400
        for i in range(self.level):
            self.game.after(timer, self.create_random_enemy)
            self.game.after(timer // 2, self.create_fencing_enemy)
            timer += timer

    def create_my_enemy(self) -> None:
        for enemy_num in range(self.level):
            new_enemy = DrunkBouncyEnemy(self.__game, 10, "pink")
            self.game.add_element(new_enemy)

    def create_random_enemy(self) -> None:
        """
        Create a random walk enemy, possibly based on the game level
        """
        for enemy_num in range(self.level):
            size = random.choice([20, 30, 40])
            new_enemy = RandomWalkEnemy(self.__game, size, "#AFD198")
            self.game.add_element(new_enemy)

    def create_chasing_enemy(self) -> None:
        """
        Create a chasing enemy, possibly based on the game level
        """
        for enemy_num in range(int(self.level / 2)):
            size = random.choice([20, 30, 40])
            new_enemy = ChasingEnemy(self.__game, size, "#8644A2")
            self.game.add_element(new_enemy)

    def create_fencing_enemy(self) -> None:
        """
        Create four fencing enemies on each corner.
        """
        new_enemy = FencingEnemy(self.__game, 20, "red")
        self.game.add_element(new_enemy)


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int,
                 level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height - 1,
                                          self.screen_width - 1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self,
                         (self.screen_width - 100, self.screen_height // 2),
                         20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>",
                         lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height // 2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Win Level " + str(self.level),
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Lose",
                                font=font,
                                fill="red")
        self.level = 0
