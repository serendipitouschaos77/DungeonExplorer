import random


class Item:
    """Represents an item the player can pick up and use."""

    def __init__(self, name, description, heal_amount=0):
        self.name = name
        self.description = description
        self.heal_amount = heal_amount

    def __str__(self):
        return f"{self.name}: {self.description}"


class Enemy:
    """Represents an enemy in a room."""

    def __init__(self, name, health, damage):
        self.name = name
        self._health = max(health, 0)
        self.damage = damage

    def is_alive(self):
        return self._health > 0

    def take_damage(self, amount):
        self._health = max(0, self._health - amount)

    def get_health(self):
        return self._health

    def __str__(self):
        status = "alive" if self.is_alive() else "defeated"
        return f"{self.name} (HP: {self._health}, DMG: {self.damage}, {status})"


class Room:
    """Represents a room in the dungeon."""

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}      # direction -> Room
        self.items = []      # list[Item]
        self.enemies = []    # list[Enemy]

    def connect(self, other_room, direction):
        """Connect this room to another in a given direction."""
        self.exits[direction] = other_room

    def add_item(self, item):
        self.items.append(item)

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def get_alive_enemies(self):
        return [e for e in self.enemies if e.is_alive()]

    def describe(self):
        print(f"\n== {self.name} ==")
        print(self.description)

        if self.items:
            print("\nItems here:")
            for item in self.items:
                print(f" - {item.name}")

        alive_enemies = self.get_alive_enemies()
        if alive_enemies:
            print("\nEnemies here:")
            for enemy in alive_enemies:
                print(f" - {enemy}")

        if self.exits:
            print("\nExits:")
            for direction in self.exits:
                print(f" - {direction}")


class Player:
    """Represents the player."""

    def __init__(self, name, starting_room):
        self.name = name
        self._health = 100
        self.inventory = []
        self.current_room = starting_room

    def get_health(self):
        return self._health

    def is_alive(self):
        return self._health > 0

    def move(self, direction):
        if direction in self.current_room.exits:
            self.current_room = self.current_room.exits[direction]
            print(f"\nYou move {direction} into {self.current_room.name}.")
            self.current_room.describe()
        else:
            print("\nYou can't go that way.")

    def take_damage(self, amount):
        self._health = max(0, self._health - amount)
        print(f"\nYou take {amount} damage! Health: {self._health}")

    def heal(self, amount):
        old = self._health
        self._health = min(100, self._health + amount)
        print(f"\nYou heal for {self._health - old} HP. Health: {self._health}")

    def pick_up(self, item_name):
        for item in self.current_room.items:
            if item.name.lower() == item_name.lower():
                self.inventory.append(item)
                self.current_room.items.remove(item)
                print(f"\nYou picked up {item.name}.")
                return
        print("\nNo such item here.")

    def use_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                if item.heal_amount > 0:
                    self.heal(item.heal_amount)
                    self.inventory.remove(item)
                else:
                    print("\nThat item can't be used.")
                return
        print("\nYou don't have that item.")

    def attack(self, enemy_name):
        enemies = self.current_room.get_alive_enemies()
        target = None
        for e in enemies:
            if e.name.lower() == enemy_name.lower():
                target = e
                break

        if not target:
            print("\nNo such enemy here.")
            return

        damage = random.randint(10, 25)
        print(f"\nYou attack {target.name} for {damage} damage!")
        target.take_damage(damage)

        if not target.is_alive():
            print(f"{target.name} is defeated!")
        else:
            # Enemy counterattacks
            print(f"{target.name} strikes back for {target.damage} damage!")
            self.take_damage(target.damage)


class Game:
    """Main game controller."""

    def __init__(self):
        self.player = None
        self._setup_world()

    def _setup_world(self):
        # Create rooms
        entrance = Room("Entrance", "A dimly lit stone archway. The air is cold.")
        hall = Room("Hall", "A long corridor with flickering torches.")
        armory = Room("Armory", "Rusty weapons line the walls.")
        lair = Room("Lair", "The final room. You sense danger.")

        # Connect rooms
        entrance.connect(hall, "north")
        hall.connect(entrance, "south")
        hall.connect(armory, "east")
        hall.connect(lair, "north")
        armory.connect(hall, "west")
        lair.connect(hall, "south")

        # Add items
        entrance.add_item(Item("Apple", "A small red apple. Restores a bit of health.", heal_amount=15))
        armory.add_item(Item("Medkit", "A basic medkit. Restores more health.", heal_amount=35))

        # Add enemies
        hall.add_enemy(Enemy("Goblin", 40, 8))
        lair.add_enemy(Enemy("Dragon Whelp", 80, 15))

        # Create player
        self.player = Player("Hero", entrance)

    def _print_help(self):
        print("""
Commands:
  look                 - describe the current room
  go <direction>       - move north/south/east/west
  take <item>          - pick up an item
  use <item>           - use an item from inventory
  attack <enemy>       - attack an enemy in the room
  inv                  - show inventory
  stats                - show your health
  help                 - show this help
  quit                 - exit the game
""")

    def _print_inventory(self):
        if not self.player.inventory:
            print("\nYour inventory is empty.")
            return
        print("\nInventory:")
        for item in self.player.inventory:
            print(f" - {item}")

    def _check_win_loss(self):
        if not self.player.is_alive():
            print("\nYou have fallen in the dungeon. Game over.")
            return True

        # Win condition: all enemies defeated
        # (In a bigger game, you'd track them differently; here we just check lair enemy)
        # For simplicity, we'll say: if player reaches lair and all enemies there are dead → win
        room = self.player.current_room
        if room.name == "Lair" and not room.get_alive_enemies():
            print("\nYou have defeated the dungeon's final guardian. You win!")
            return True

        return False

    def run(self):
        print("Welcome to Dungeon Explorer!")
        self.player.current_room.describe()
        self._print_help()

        while True:
            if self._check_win_loss():
                break

            cmd = input("\n> ").strip().lower()
            if not cmd:
                continue

            parts = cmd.split()
            verb = parts[0]

            if verb == "quit":
                print("\nGoodbye.")
                break
            elif verb == "help":
                self._print_help()
            elif verb == "look":
                self.player.current_room.describe()
            elif verb == "stats":
                print(f"\nHealth: {self.player.get_health()}")
            elif verb == "inv":
                self._print_inventory()
            elif verb == "go" and len(parts) > 1:
                self.player.move(parts[1])
            elif verb == "take" and len(parts) > 1:
                self.player.pick_up(" ".join(parts[1:]))
            elif verb == "use" and len(parts) > 1:
                self.player.use_item(" ".join(parts[1:]))
            elif verb == "attack" and len(parts) > 1:
                self.player.attack(" ".join(parts[1:]))
            else:
                print("\nI don't understand that command. Type 'help' for options.")


if __name__ == "__main__":
    game = Game()
    game.run()
