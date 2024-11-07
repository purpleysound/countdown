import socketserver
import numbers_solver
import random
import threading

        
def generate_numbers() -> tuple[list[int, int, int, int, int, int], int, numbers_solver.Solution]:
    """Generates 6 numbers for the game and a target number"""
    while True:
        BIG_NUMBERS = [25, 50, 75, 100]
        SMALL_NUMBERS = list(range(1, 11)) * 2
        big_count = random.randint(0, 4)
        small_count = 6 - big_count
        numbers = random.sample(BIG_NUMBERS, big_count) + random.sample(SMALL_NUMBERS, small_count)
        target = random.randint(100, 999)

        solution = numbers_solver.number_solver_gives_up(numbers, target, 1)
        if solution is not None:
            return numbers, target, solution
        

class CountdownManager:
    def __init__(self):
        self._numbers, self._target, _ = generate_numbers()
        self._players = [None, None]
        self._full = False
        self._ready = [False, False]
        self._finished = False
        self._winner = None

    def add_player(self, username: str) -> int:
        if self._players[0] is None:
            self._players[0] = username
            return 0
        if self._players[1] is None:
            self._players[1] = username
            self._full = True
            return 1
        
    def is_full(self):
        return self._full
        
    def get_numbers(self) -> tuple[list[int, int, int, int, int, int], int]:
        return self._numbers, self._target
    
    def get_username(self, player_idx: int) -> str:
        return self._players[player_idx]
    
    def reset(self):
        self._numbers, self._target, _ = generate_numbers()
        self._players = [None, None]
        self._full = False
        self._ready = [False, False]
        self._finished = False

    def toggle_ready(self, player_idx: int):
        self._ready[player_idx] = not self._ready[player_idx]
        return all(self._ready)
    
    def get_ready(self, player_idx: int):
        return self._ready[player_idx]
        
    def all_ready(self):
        return all(self._ready)
    
    def is_finished(self):
        return self._finished
    
    def finish(self, winner: int):
        self._finished = True
        self._winner = winner

    def get_winner(self):
        return self._winner


class CDHandler(socketserver.BaseRequestHandler):
    cm = CountdownManager()
    acknowledged_finish = [False, False]

    def handle(self):
        self.data, self.sock = self.request
        self.data = self.data.decode().strip()
        command, arg = self.data.split()
        if command == "setname":
            self.set_name(arg)
        elif command == "ready":
            self.ready(int(arg))
        elif command == "finish":
            self.finished(int(arg))
        elif command == "reset":
            self.reset()

    def set_name(self, name: str):
        if CDHandler.cm.is_full():
            self.sock.sendto(b"-1 ", self.client_address)
            return
        player_idx = CDHandler.cm.add_player(name)
        other_player_name = CDHandler.cm.get_username(1-player_idx)
        if other_player_name is None:
            other_player_name = ""
        self.sock.sendto(f"set {player_idx}".encode(), self.client_address)
        self.wait_for_player_name(1-player_idx)
        self.wait_for_ready(1-player_idx)

    def ready(self, player_idx: int):
        CDHandler.cm.toggle_ready(player_idx)
        self.sock.sendto(f"ready {player_idx}".encode(), self.client_address)
        self.wait_for_all_ready()
        self.wait_for_finish(player_idx)

    def finished(self, player_idx: int):
        CDHandler.cm.finish(player_idx)
        self._finished = True
        self.wait_for_all_finish()

    def wait_for_player_name(self, player_idx: int):
        def fun():
            while CDHandler.cm.get_username(player_idx) is None:
                pass
            self.sock.sendto(f"name {CDHandler.cm.get_username(player_idx)}".encode(), self.client_address)
        t = threading.Thread(target=fun)
        t.start()

    def wait_for_ready(self, player_idx: int):
        def fun():
            while not CDHandler.cm.get_ready(player_idx):
                pass
            self.sock.sendto(f"ready {player_idx}".encode(), self.client_address)
        t = threading.Thread(target=fun)
        t.start()

    def wait_for_all_ready(self):
        def fun():
            while not CDHandler.cm.all_ready():
                pass
            self.sock.sendto(f"start {CDHandler.cm.get_numbers()}".encode(), self.client_address)  # e.g. "start ([1, 2, 3, 4, 5, 6], 123)"
        t = threading.Thread(target=fun)
        t.start()

    def wait_for_finish(self, player_idx: int):
        def fun():
            while not CDHandler.cm.is_finished():
                pass
            self.sock.sendto(f"finish {CDHandler.cm.get_winner()}".encode(), self.client_address)
            CDHandler.acknowledged_finish[player_idx] = True
        t = threading.Thread(target=fun)
        t.start()

    def wait_for_all_finish(self):
        def fun():
            while not all(CDHandler.acknowledged_finish):
                pass
            CDHandler.cm.reset()
        t = threading.Thread(target=fun)
        t.start()

    def reset():
        CDHandler.cm.reset()


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # set cwd to the directory of this file
    try:
        with open("host_address.txt", "r") as file:
            host = file.read().strip() 
    except FileNotFoundError:
        raise FileNotFoundError("host_address.txt needs to be made in server directory with the host address before running")
    
    with socketserver.ThreadingUDPServer((host, 6779), CDHandler) as server:
        server.allow_reuse_address = True
        server.serve_forever()
