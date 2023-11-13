from gupb.controller.ancymon.environment import Environment
from gupb.controller.ancymon.strategies.path_finder import Path_Finder
from gupb.model import characters
from gupb.model.coordinates import Coords

POSSIBLE_ACTIONS = [
    characters.Action.TURN_LEFT,
    characters.Action.TURN_RIGHT,
    characters.Action.STEP_FORWARD,
    characters.Action.ATTACK,
]


class Hunter:
    def __init__(self, environment: Environment, path_finder: Path_Finder):
        self.environment: Environment = environment
        self.path_finder: Path_Finder = path_finder
        self.poi: Coords = Coords(0, 0)
        self.next_target = None
        self.next_target_coord: Coords = None

    def decide2(self):
        decision = None

        if self.is_enemy_neer(1) == False and self.can_attack():
            # print("LONG RANGE ATTACK", self.environment.weapon)
            return characters.Action.ATTACK, None

        self.is_target_on_same_position()

        tmp = self.neerest_enemy_list()

        if len(tmp) > 0:
            decision, path = self.path_finder.calculate_next_move(tmp[0])


        return decision, None

    def decide(self):

        if self.is_enemy_neer(1) == False and self.can_attack():
            print("LONG RANGE ATTACK", self.environment.weapon)
            return characters.Action.ATTACK, None

        if self.is_enemy_neer(3) and (
                self.environment.champion.health >= self.next_target.health or self.is_menhir_neer()):

            if self.can_attack():
                print("CAN ATTACK WITH", self.environment.weapon)
                return characters.Action.ATTACK, None

            cord_position_to_atack = self.find_coord_to_attack_spot()
            print("CHASING")

            return self.path_finder.calculate_next_move(cord_position_to_atack)
        return None, None

    def is_menhir_neer(self):
        if self.environment.menhir:
            margin = self.environment.enemies_left
            if len(self.environment.discovered_map[self.environment.position].effects) > 0:
                margin = 1
            return (abs(self.environment.menhir[0] - self.environment.position.x) < margin and
                    abs(self.environment.menhir[1] - self.environment.position.y) < margin)

    def is_target_on_same_position(self):
        if self.next_target and self.next_target_coord:
            enemy_field = self.environment.discovered_map.get(self.next_target_coord)
            if enemy_field and enemy_field.character:
                return
        self.next_target = None
        self.next_target_coord: Coords = None

    def neerest_enemy_list(self) -> list[Coords]:
        enemy_coords_list = []

        for coords, description in self.environment.discovered_map.items():
            coords = Coords(coords[0], coords[1])
            if description.character and description.character.controller_name != self.environment.champion.controller_name:
                enemy_coords_list.append(coords)
        return sorted(enemy_coords_list, key=lambda x: self.path_finder.calculate_path_length(x))

    def is_enemy_neer(self, size_of_searched_area: int = 3):
        for x in range(-size_of_searched_area, size_of_searched_area + 1):
            for y in range(-size_of_searched_area, size_of_searched_area + 1):
                field = self.environment.discovered_map.get(self.environment.position + Coords(x, y))
                if field != None and field.character != None and field.character.controller_name != self.environment.champion.controller_name:
                    self.next_target = field.character
                    self.next_target_coord = Coords(x, y) + self.environment.position
                    return True
        self.next_target = None
        self.next_target_coord = None
        return False

    def is_character_on_visible_field(self, further_position: Coords) -> bool:
        return self.environment.visible_map.get(further_position) and self.environment.visible_map.get(
            further_position).character

    def can_attack(self) -> bool:
        position = self.environment.position
        further_position = position + self.environment.champion.facing.value

        if self.environment.weapon.name == 'knife':
            if self.is_character_on_visible_field(further_position):
                return True
            return False

        if self.environment.weapon.name == 'sword':
            for i in range(3):
                if self.is_character_on_visible_field(further_position):
                    return True
                further_position += self.environment.champion.facing.value
            return False

        if self.environment.weapon.name == 'bow_loaded' or self.environment.weapon.name == 'bow_unloaded':
            while (self.environment.visible_map.get(further_position)):
                if self.environment.visible_map.get(further_position).character:
                    return True
                further_position += self.environment.champion.facing.value
            return False

        if self.environment.weapon.name == 'amulet':
            for direction in [Coords(1, 1), Coords(-1, -1), Coords(1, -1), Coords(-1, 1)]:
                further_position = position
                for i in range(2):
                    further_position += direction
                    if self.is_character_on_visible_field(further_position):
                        return True
            return False

        if self.environment.weapon.name == 'axe':
            if (
                    (further_position.x != position.x and (
                            self.environment.visible_map[further_position].character or
                            self.environment.visible_map[
                                Coords(further_position.x, further_position.y + 1)].character or
                            self.environment.visible_map[Coords(further_position.x, further_position.y - 1)].character
                    )) or
                    (further_position.y != position.y and (
                            self.environment.visible_map[further_position].character or
                            self.environment.visible_map[
                                Coords(further_position.x + 1, further_position.y)].character or
                            self.environment.visible_map[Coords(further_position.x - 1, further_position.y)].character
                    ))
            ):
                return True
            return False

        return False

    def find_coord_to_attack_spot(self):

        new_attack_spot_dist = float('inf')
        new_attack_spot = self.next_target_coord

        if self.environment.weapon.name == 'knife':
            return self.next_target_coord

        elif self.environment.weapon.name == 'sword':
            for direction in [Coords(0, 1), Coords(0, -1), Coords(1, 0), Coords(-1, 0)]:
                further_position = self.next_target_coord
                for i in range(2):
                    further_position += direction
                    spot = self.environment.discovered_map.get(further_position)
                    if spot and spot.type == 'land':
                        spot_dist = self.path_finder.calculate_path_length(further_position)
                        if (new_attack_spot == None or spot_dist < new_attack_spot_dist):
                            new_attack_spot_dist = spot_dist
                            new_attack_spot = further_position

        elif self.environment.weapon.name == 'amulet':
            for direction in [Coords(1, 1), Coords(1, -1), Coords(-1, 1), Coords(-1, -1)]:
                further_position = self.next_target_coord
                for i in range(2):
                    further_position += direction
                    spot = self.environment.discovered_map.get(further_position)
                    if spot and spot.type == 'land':
                        spot_dist = self.path_finder.calculate_path_length(further_position)
                        if (new_attack_spot == None or spot_dist < new_attack_spot_dist):
                            new_attack_spot_dist = spot_dist
                            new_attack_spot = further_position

        elif self.environment.weapon.name == 'axe':
            for direction in [Coords(0, 1), Coords(0, -1)]:
                further_position = self.next_target_coord
                for direction_2 in [Coords(0, 0), Coords(1, 0), Coords(-1, 0)]:
                    further_position = further_position + direction + direction_2
                    spot = self.environment.discovered_map.get(further_position)
                    if spot and spot.type == 'land':
                        spot_dist = self.path_finder.calculate_path_length(further_position)
                        if new_attack_spot is None or spot_dist < new_attack_spot_dist:
                            new_attack_spot_dist = spot_dist
                            new_attack_spot = further_position

            for direction in [Coords(1, 0), Coords(-1, 0)]:
                further_position = self.next_target_coord
                for direction_2 in [Coords(0, 0), Coords(0, 1), Coords(0, -1)]:
                    further_position = further_position + direction + direction_2
                    spot = self.environment.discovered_map.get(further_position)
                    if spot and spot.type == 'land':
                        spot_dist = self.path_finder.calculate_path_length(further_position)
                        if new_attack_spot is None or spot_dist < new_attack_spot_dist:
                            new_attack_spot_dist = spot_dist
                            new_attack_spot = further_position

        print(new_attack_spot)
        return new_attack_spot
