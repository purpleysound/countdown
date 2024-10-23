import heapq


def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

def multiply(a: int, b: int) -> int:
    return a * b

def divide(a: int, b: int) -> int | bool:
    if b == 0:
        return False
    div = a / b
    if div.is_integer():
        return int(div)
    return False

operation_symbols = {
    add: "+",
    subtract: "-",
    multiply: "*",
    divide: "/"
}


class Solution:
    def __init__(self, numbers: list[int], target: int, steps: list[str] = []):
        self.numbers = numbers
        self.target = target
        self.steps = steps

    def __str__(self):
        return "\n".join(self.steps)
    
    def make_step(self, numbers: tuple[int, int], operation: callable) -> int:
        result = operation(*numbers)
        self.steps.append(f"{numbers[0]} {operation_symbols[operation]} {numbers[1]} = {result}")
        return result
    
    def copy(self):
        return Solution(self.numbers.copy(), self.target, self.steps.copy())
    
    def __eq__(self, other):
        return self.numbers == other.numbers and self.target == other.target
    
    def __lt__(self, other):
        """lesser is better"""
        return min(abs(num - self.target) for num in self.numbers) < min(abs(num - other.target) for num in other.numbers)
    

def numbers_solver(numbers: list[int], target: int) -> Solution | None:
    q = [Solution(numbers, target, [])]
    while q:
        solution = heapq.heappop(q)
        if target in solution.numbers:
            return solution
        if len(solution.numbers) == 1:
            continue
        for i, num1 in enumerate(solution.numbers):
            for j, num2 in enumerate(solution.numbers):
                if i == j:
                    continue
                for operation in (add, subtract, multiply):
                    new_solution = solution.copy()
                    new_solution.numbers.pop(max(i, j))
                    new_solution.numbers.pop(min(i, j))
                    new_solution.numbers.append(new_solution.make_step((num1, num2), operation))
                    heapq.heappush(q, new_solution)
                if divide(num1, num2):
                    new_solution = solution.copy()
                    new_solution.numbers.pop(max(i, j))
                    new_solution.numbers.pop(min(i, j))
                    new_solution.numbers.append(new_solution.make_step((num1, num2), divide))
                    heapq.heappush(q, new_solution)
    return None
            
    
if __name__ == "__main__":
    import time
    import random
    NUMBERS = [25, 50, 75, 100] + list(range(1, 11)) * 2
    while True:
        t0 = time.time()
        numbers = random.sample(NUMBERS, 6)
        target = random.randint(100, 999)
        print(numbers, target)
        solution = numbers_solver(numbers, target)
        print(solution)
        print(time.time() - t0)
        input()
