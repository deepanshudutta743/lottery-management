import random

def generate_ticket_numbers():
    return sorted(random.sample(range(1, 50), 6))

def draw_winning_numbers():
    return sorted(random.sample(range(1, 50), 6))
